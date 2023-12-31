# Projet: MiGRIDS
# Created by: T.Morgan# Created on: 9/25/2019
# License: MIT License (see LICENSE file of this package for more information)

'''Technical note. Estimations are always done at the 1 second timestep level
If more values are produced than desired, the extra values are dropped'''
#The max out put file size is 1 year at 1 second samples.
#Reads a dataframe and ouputs a new dataframe with the specified sampling time interval.
#interval is a string with time units. (i.e. '30s' for 30 seconds, '1T' for 1 minute)
#If interval is less than the interval within the dataframe mean values are used to create a down-sampled dataframe
#DataClass, String -> DataClass
from datetime import datetime

from MiGRIDS.InputHandler.Exceptions.ContainsNull import ContainsNullException
from MiGRIDS.InputHandler.badDictAdd import badDictAdd
import pandas as pd
import numpy as np
import multiprocessing as mp

from MiGRIDS.InputHandler.isInline import makeCuts

MAXUPSAMPLEINTERVAL = 21600 #this is 6 hours
TOTALLOAD = 'total_load'
TOTALPOWER = 'total_power'
def fixDataInterval(data, interval, **kwargs):
    '''
     standardizes the time steps within a data object's df attribute, splitting the df attribute if consecutive data can not be generated.
     Puts all resulting dataframes as a list in the fixed attribute of data.
     less than what is available in the df a langevin estimator will be used to fill
     in missing times. If the interval is greater than the original time interval
     the mean of values within the new interval will be generated
     Gaps larger than MAXUPSAMPLEINTERVAL need to be filled with fixBadData. They will result in a split dataframe in fixDataInterval.
    :param data: a DataClass object with a df attribute that is a pandas dataframe with datetime index.
    :param interval: pandas Timedelta interval is the desired interval of data samples as a timedelta value.
    :return: A DataClass object with data filled at consistent time intervals
    '''
    loc = data.fixed[0].columns
    fixColumns = [l for l in loc if 'flag' not in l and l not in data.loads and l not in data.powerComponents]
    try:
        data.fixed = [fixDataFrameInterval(x, interval,fixColumns, data.loads, data.powerComponents) for x in data.fixed]

    except Exception as e:
        print(e)
        print("could not resample dataframe")
    print(data.fixed[0].head())

    data.removeAnomolies(stdNum=5)

    return data
def fixDataFrameInterval(dataframe, interval, fixColumns, loadColumns, powerColumns):
    '''
    up or downsample all series within a single dataframe to the desired interval
    :param dataframe: a dataframe with datetime index
    :param interval: pandas deltatime
    :param fixColumns: string column names of columns within dataframe that get estimated independently
    :param loadColumns: string column names of columns within dataframe that will be estimated based on a total_load column
    :param powerColumns: string column names of columns within dataframe that will be estimated based on a total_pwer column
    :return: dataframe
    '''

    # df contains the non-upsampled records. Means and standard deviation come from non-upsampled data.
    df = dataframe.copy()
    print('before upsampling dataframe is: %s' % len(dataframe))
    print(dataframe.head())
    # up or down sample to our desired interval
    # down sampling results in averaged values
    # this changes the size fo data.fixed[idx], so it no longer matches df rowcount.
    # we start with flooring - so a value 1 second past the desired interval will become the value

    #set the flag now
    flag_columns =[c for c in dataframe.columns if ('flag' in c)]
    other_columns = [c for c in dataframe.columns if 'flag' not in c]

    data1 = dataframe[other_columns].resample(interval).mean()
    upSampledDataframe = data1.join(dataframe[flag_columns], how='left')
    upSampledDataframe.index = upSampledDataframe.index.floor(interval)

    sList = [fixSeriesInterval(df[col], upSampledDataframe[col], interval) for col in fixColumns]
    completeDataFrame = dataframe[flag_columns + [c for c in other_columns if c not in fixColumns]]
    #floor the dataframe or actual values could be lost - if they fall between interval endpoints
    completeDataFrame.index = completeDataFrame.index.floor(interval)
    completeDataFrame = completeDataFrame[~completeDataFrame.index.duplicated(keep='first')]

    completeSeries = pd.concat(sList,1)
    completeDataFrame = completeSeries.join(completeDataFrame, how = 'left')

    for f in flag_columns:
        completeDataFrame.loc[pd.isnull(completeDataFrame[f]), f] = 4

    completeDataFrame = spreadFixedSeries(TOTALLOAD,loadColumns,completeDataFrame)
    completeDataFrame = spreadFixedSeries( TOTALPOWER, powerColumns,completeDataFrame)
    completeDataFrame = completeDataFrame.loc[data1.index]
    completeDataFrame = truncateDataFrame(completeDataFrame)
    return completeDataFrame

def truncateDataFrame(df):
    '''retains the longest continuous sections of data within a dataframe
    :param df: a pandas dataframe with or without na's
    :return a dataframe with only contiuous rows of data'''

    #only keep the portion of the dataframe that has data for all components
    first_valid_loc = df.apply(lambda col: col.first_valid_index()).max()
    last_valid_loc = df.apply(lambda col: col.last_valid_index()).min()
    newdf = df[first_valid_loc:last_valid_loc]
    #split up the dataframe if there are remaining gaps in data
    NAs = newdf[pd.isnull(newdf).any(axis=1)].index #list of bad indices
    #group up the nas into timedeltas of contiuous time period with bad data
    NATime = pd.Series(pd.to_datetime(NAs), index=NAs)
    NATime.name = 'natime'
    if len(NATime) > 0:
        dfTime = pd.Series(pd.to_datetime(df[min(NATime.index):max(NATime.index)].index),
                           index=df[min(NATime.index):max(NATime.index)].index)
        dfTime.name = 'dftime'
        bothTime = pd.concat([NATime, dfTime], axis=1)

        mask = bothTime.natime.notna()
        d = bothTime.index.to_series()[mask].groupby((~mask).cumsum()[mask]).agg(['first', 'last'])
        newcuts = pd.Series((d['last'] - d['first']))
        newcuts.index = d['first']
        lod = makeCuts([df],newcuts)
        newdf = returnLargest(lod)
    return newdf

def returnLargest(lod):
    '''returns the dataframe with the most rows from a list of dataframes'''
    df = lod[0]
    while len(lod) > 0:
        if len(lod[0]) > len(df):
            df = lod.pop(0)
        else:
            lod.pop(0)
    return df

def fixSeriesInterval_mp(startingSeries,reSampledSeries,interval,result):
    resultdf = fixSeriesInterval(startingSeries,reSampledSeries,interval)
    result.put(resultdf)

def spreadFixedSeries(col, spreadColumns,df):
    if (col in df.columns):
        df = calculateSubColumns(col,spreadColumns,df)
    return df

def fixSeriesInterval(startingSeries, reSampledSeries,interval):
    '''
    up or downsample a series to reflect the desired interval
    assumes interval to upsample to is small (< 6 hours)
    :param startingSeries: a named pandas series
    :param reSampledSeries: the starting series up or downsampled to the desired interval
    :param interval: a pandas timedelta value of the desired sample interval
    :return: Series with all values filled in by taking the mean between values if downsampled or using a simulation algorithm is upsampled
    '''
    # remove rows that are nan for this column, except for the first and last, in order to keep the same first and last
    # time stamps
    startingSeries = pd.concat([startingSeries.iloc[[0]], startingSeries.iloc[1:-1].dropna(), startingSeries.iloc[[-1]]])
    # get first and last non nan indicies
    idx0 = startingSeries.first_valid_index()
    idx1 = startingSeries.last_valid_index()
    if (idx0 != None) & (idx1 != None):
        startingSeries = startingSeries[idx0:idx1]

    simulatedValues = reSampledSeries[idx0:idx1]
    # if the resampled dataframe is bigger fill in new values
    # Timediff needs to be calculated to next na, not next record
    if len(startingSeries) < len(reSampledSeries):
        # standard deviation
        sigma = startingSeries.rolling(5, 2).std()
        # first records get filled with first valid values of mean and standard deviation
        sigma = sigma.bfill()
        sigma = scaleSigma(sigma)
        simulatedValues = upsample(startingSeries[pd.notnull(startingSeries)],sigma)
    #put modified columns in result
    simulatedValues.loc[simulatedValues<0] = 0
    reSampledSeries = matchToOriginal(reSampledSeries,simulatedValues,interval)
    return reSampledSeries

def scaleSigma(sigma):
    '''Calculates the standard deviation using a rolling window'''
    WINDOW = 5
    records = abs(pd.to_timedelta(pd.Series(sigma.index,index=sigma.index).diff(-1)).dt.total_seconds()) #records is the number of seconds between consecutive values - one record per second
    records = records.rolling(WINDOW, 2).mean() #mean number of seconds between intervals used to calculate sigma
    records = records.bfill()
    records[records < 60] = 1
    records[records >= 60] = records/60
    # sigma is the the standard deviation for the existing time interval between records
    #sigma gets arbitrarily scaled to the minute level if records have greater than 1 minute time gaps.
    sigma = np.divide(sigma,records)
    return sigma

def matchToOriginal(originalSeries,simulatedSeries, interval):
    '''
    Matches the indices of two series, replacing the values in the first series where they are na.
    The interval is used to floor series to increase the number of matching indices
    :param originalSeries: a pd.series with datetime index of desired time intervals
    :param simulatedSeries: a pd.series with datetime index where there are no na values
    :param interval: the desired time interval between timesteps in the originalSeries
    :return: a pandas series with all previously missing values filled in with simulated values and timesteps floored at the desired interval.
    '''

    # make sure timezones match - can't join naive and nonnaive times
    tz = originalSeries.index.tzinfo
    simulatedSeries.index = simulatedSeries.index.floor(interval)
    # need to remove duplicate indices genereatd from flooring
    simulatedSeries = simulatedSeries[~simulatedSeries.index.duplicated(keep='first')]

    try:
        simulatedSeries.index = simulatedSeries.index.tz_localize(tz)
    except:
        pass
    # join the simulated values to the upsampled dataframe by timestamp
    newDF = pd.DataFrame(originalSeries, index=originalSeries.index)
    simulatedSeries.name = 'value'
    newDF = newDF.join(simulatedSeries, how='inner')

    # fill na's for column with simulated values
    newDF.loc[pd.isnull(newDF[originalSeries.name]), originalSeries.name] = newDF['value']
    return newDF[originalSeries.name]

def upsample(series, sigma):
    '''fills in a 1 second timesteps between time indices with values estimated using a simulation equation.
    The current (1/1/2020) implementation uses langevin for simulation. The value in series is the starting value for the simulated values
    and sigma is the target value.
    :param series any numeric series without nas
    :param Series, any numeric series without na's
    :return pd.Series at 1 second time intervals, new values are filled via simulation'''

    # t is the time, k is the estimated value
    t, k = estimateDistribution(series, sigma)  # t is number of seconds since starttime

    #simulatedSeries = pd.DataFrame({'value': k,'time':pd.to_datetime(t, unit='s')})
    simulatedSeries = pd.DataFrame({'value': k, 'time': series.index[0]+pd.to_timedelta(t,'s')})
    simulatedSeries = simulatedSeries.set_index(simulatedSeries['time'])
    simulatedSeries = simulatedSeries.loc[pd.notnull(simulatedSeries['value']),'value']
    simulatedSeries = simulatedSeries[~simulatedSeries.index.duplicated(keep='first')]

    return simulatedSeries

def estimateDistribution(series, sigma):
    try:
        #return an array of arrays of values
        timeArray, values = getValues(series, sigma)
        return timeArray, values
    except MemoryError:
        # handle memory error exceptions by working with smaller subsets
        print("Memory Error: re-attempting to process.")

        return

def getValues(start, sigma):
    '''
    Uses the Langevin equation to estimate records based on provided start value and standard deviation.
    All estimates are for a 1 sec time interval and subsequently truncated to match desired timestep
    The total time to be filled between to valid values cannot exceed 6 hours.
    Time gaps that are longer than the typical (95% of time gaps to fill) time gap in the dataset are filled after common time gaps
    :param start: [Array of numeric] the start value to initiate the estimator for a given record
    :param sigma: [Array of numeric] the standard deviation to use in the estimator
    '''

    import numpy as np
    if (len(start[pd.isnull(start)]))>0:
        raise ContainsNullException("Series cannot contain NA")

    #time step of 1 second
    #timesteps must be 1 second if you are combining high resolution and low resolution series!
    defaultTimestep = 1
    records = abs(pd.to_timedelta(pd.Series(start.index).diff(-1)).dt.total_seconds()) #records is the number of seconds between consecutive values - one record per second
   #n is the number of values that will be estimated -will always be records + 1 unless default Timestep changes
    n = round((records * defaultTimestep) + 1,0)#all estimates are at the 1 seoond timestep
    n = n.fillna(0)
    # find the 95th percentile of number of steps - exclude gaps that are too big to fill
    n95 = int(np.percentile(n[n < MAXUPSAMPLEINTERVAL], 95))
    # find where over the 95th percentile
    idxOver95 = np.where(n > n95)[0]

    # steps is an array of timesteps in seconds with length = max(records)
    steps = np.arange(0, int(n95)*defaultTimestep, defaultTimestep)
    # t is the numeric value of the dataframe timestamps in seconds
    #t = pd.to_timedelta(pd.Series(pd.to_datetime(start.index.values, unit='s',tz=start.index.tz), index=start.index)-start.index[0]).dt.total_seconds()
    s = pd.Series(start.index.values - start.index.values[0])
    t = pd.to_timedelta(s).dt.total_seconds()
    # intervals is the steps array repeated for every row of time
    intervals = np.repeat(steps, len(t), axis=0)
    # reshape the interval matrix so each row has every timestep
    intervals_reshaped = intervals.reshape(len(steps), len(t)) #colums are a series of timesteps - 1 column for each start value

    tr = t.repeat(len(steps))
    rs = tr.values.reshape(len(t), len(steps))
    time_matrix = rs + intervals_reshaped.transpose() #each row represents a timeseries for each start value


    # use the next step in the time series as the average value for the synthesized data. The values will asympotically reach this value, resulting in a smooth transition.
    mu = start.shift(-1)
    mu.iloc[-1] = mu.iloc[-2]

    x = estimateLangValues(defaultTimestep, mu, sigma, start, n95)

    # remove extra values to avoid improper mixing of values when sorting
    for row in range(time_matrix.shape[0]):
        time_matrix[row,int(n[row]):] = None
        x[row,int(n[row]):] = None

    timeArray = np.concatenate(time_matrix)
    values = np.concatenate(x)
    # this can only work as long as fixBadData removes any None values
    values = values[values != None]
    timeArray = timeArray[timeArray != None]
    #any time gaps greater than MAXUPSAMPLEINTERVAL will not be filled
    nRemaining = max([r-n95 for r in n[idxOver95] if r < MAXUPSAMPLEINTERVAL],default=0)
    if nRemaining >= 1:
        # individually calc the rest if they are less than the max allowable upsample interval
        start = start[idxOver95]
        mu= mu[idxOver95]
        sigma = sigma[idxOver95]
        time = time_matrix[idxOver95]
        time = time[:,-1] #just the last column, which is the last timestamp filled and will be the start of the next interval of time to fill
        time = time.reshape(len(time),1) #add a column shape value
        time_matrix0 = np.arange(0, nRemaining * defaultTimestep,defaultTimestep) # a single column of timesteps
        #time_matrix0 = time_matrix0.reshape(1,time_matrix0.shape[0]) #make time_matrix a row
        time_matrix0 = time_matrix0.repeat(len(time)) #row of timesteps for every time than needs estimates
        time_matrix0 = time_matrix0.reshape(int(nRemaining),len(time)).transpose() #reshape to timesteps as rows
        #rs = tr.values.reshape(len(t), len(time))
        #rs = np.array([1, 1])
        #rs = rs.reshape(1,2)
        #time_matrix0 = time_matrix0 * rs #its now a matrix of times to add to start times
        time_matrix0 = time_matrix0 + time #time2 are our starting times (the last time filled in the previous step)
        timeArray0 = np.concatenate(time_matrix0)#reshape to single vector to append to previously filled times
        x0 = estimateLangValues(defaultTimestep, mu, sigma, start, nRemaining)
        values = np.append(values, x0)
        timeArray = np.append(timeArray,timeArray0)
        del time_matrix0
        del nRemaining
        del x0
    #put the time and values together s
    tv = np.array(list(zip(timeArray,values)))
    tv = tv[tv[:,0].argsort()] # sort by timeArray

    t, v = zip(*tv)

    #clean up
    del tv
    del values
    del timeArray

    del idxOver95
    del intervals
    del intervals_reshaped
    del sigma
    del steps
    del mu
    del rs
    del tr

    return t,v

def estimateLangValues(timestep, mu, sigma, start, T):
    '''
    :param timestep: integer timestep value
    :param mu: vector of target values
    :param sigma:vector of std values
    :param start: vector of start values
    :param T: total number of timesteps

    :return: a matrix of T/t values per start value - shape is (len(start), T/t)
    '''
    mu = mu.values.reshape(len(start),)
    sigma = sigma.values.reshape(len(start),)
    start = start.values.reshape(len(start),)

    tau = T * 0.2  # tau affects how much noise and variation between timesteps and how quickly the mu value is reached
    n = int(T / timestep)

    sigma_bis = sigma * np.sqrt(2. / tau)
    sqrtdt = np.sqrt(timestep)
    x = np.zeros(n * len(start))
    x = x.reshape(len(start),n)
    x[:, 0] = start
    for i in range(n - 1):  #
        x[:, i + 1] = x[:, i] + timestep * (-(x[:, i] - mu) / tau) + (np.multiply(
            sigma_bis * sqrtdt, np.random.randn(len(start))))
    return x

def calculateSubColumns(total_column, spreadColumns, df):
    '''
    Calculates na values for a list of columns based on the average (calculated with a rolling window) proportion that each column makes up
    of the total colomn.
    :param total_column: filled column to subdivide
    :param spreadColumns: list of components to parse values to.
    :param df: is a dataframe of the components to adjusted based on filled total
    :return: Dataframe with spreadColumn values filled in
    '''
    if len(spreadColumns) ==1:
        df.loc[pd.isnull(df[spreadColumns[0]]), spreadColumns[0]] = df[total_column]
    else:
        adj_m = df[spreadColumns].div(df[total_column], axis=0)
        adj_m = adj_m.ffill()
        df[spreadColumns] = adj_m.multiply(df[total_column], axis=0)
        del adj_m
    return df
