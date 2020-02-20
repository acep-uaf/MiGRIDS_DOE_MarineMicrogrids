# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
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
     data is a DataClass with a pandas dataframe with datetime index.
     interval is the desired interval of data samples as a timedelta value. If this is
     less than what is available in the df a langevin estimator will be used to fill
     in missing times. If the interval is greater than the original time interval
     the mean of values within the new interval will be generated
     We don't upsample to fill more than 6 hours of data - gaps larger than this need to be filled in the fix data method.
    :param data: a DataClass object
    :param interval: pandas Timedelta
    :return: A DataClass object with data filled at consistent time intervals
    '''
    updateSubject = kwargs.get("subject"); #connect to a subject
    def broadCastStatus(progress, task):
        if updateSubject:
            updateSubject.notify(progress/updateSubject.limit,task)
    #integer, numeric, numeric, numeric -> numeric array
    #uses the Langevin equation to estimate records based on provided mean (mu) and standard deviation and a start value

    #dataframe -> integer array, integer array
    #returns arrays of time as seconds and values estimated using the Langevin equation
    #for all gaps of data within a dataframe
    #fix column are total_load, total_power, any other columns that are not flags or a load or power
    loc = data.fixed[0].columns
    fixColumns = [l for l in loc if 'flag' not in l and l not in data.loads and l not in data.power]
    try:
        data.fixed = [fixDataFrameInterval(x, interval,fixColumns, data.loads, data.power) for x in data.fixed]

    except:
        print("could not resample dataframe")
    print(data.fixed[0].head())

    data.removeAnomolies(stdNum=5)

    return data
def fixDataFrameInterval(dataframe, interval, fixColumns, loadColumns, powerColumns):
    '''

    :param dataframe: a dataframe with datetime index
    :param interval: pandas deltatime
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

    for f in flag_columns:
        upSampledDataframe.loc[pd.isnull(upSampledDataframe[f]), f] = 4

    result = mp.Manager().Queue()
    # pool of processes
    pool = mp.Pool(mp.cpu_count())
    for col in fixColumns:
        print("fixing: ", col)

        pool.apply_async(fixSeriesInterval_mp, args=(df[col],upSampledDataframe[col],interval, result))

    pool.close()
    pool.join()

    completeDataFrame = dataframe[flag_columns + [c for c in other_columns if c not in fixColumns]]
    while not result.empty():
        completeDataFrame = pd.concat([completeDataFrame,result.get()],1) #each df will contain a column of data
    del df
    completeDataFrame = spreadFixedSeries(TOTALLOAD,loadColumns,completeDataFrame )
    completeDataFrame = spreadFixedSeries( TOTALPOWER, powerColumns,completeDataFrame)
    completeDataFrame = completeDataFrame.loc[data1.index]
    completeDataFrame = truncateDataFrame(completeDataFrame)
    return completeDataFrame
def truncateDataFrame(df):
    '''retains the longest continuous sections of data within a dataframe'''
    NAs = df[pd.isnull(df).any(axis=1)].index #list of bad indices
    lod = makeCuts([df],NAs)
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
def handleMemory():
    """Not implemented yet.
    Prints current memory usage stats.
    """
    import psutil
    import os
    PROCESS = psutil.Process(os.getpid())
    MEGA = 10 ** 6 #convert to megabits

    total, available, percent, used, free = psutil.virtual_memory()
    total, available, used, free = total / MEGA, available / MEGA, used / MEGA, free / MEGA
    proc = PROCESS.memory_info()[1] / MEGA
    print('process = %s total = %s available = %s used = %s free = %s percent = %s'
          % (proc, total, available, used, free, percent))

    raise MemoryError
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
    :param dataframe:
    :param df: DataFrame
    :param data: DataClass
    :param interval: Timedelta
    :param result: mp result
    :return: Series
    '''
    # remove rows that are nan for this column, except for the first and last, in order to keep the same first and last
    # time stamps
    startingSeries = pd.concat([startingSeries.iloc[[0]], startingSeries.iloc[1:-1].dropna(), startingSeries.iloc[[-1]]])
    # get first and last non nan indecies
    idx0 = startingSeries.first_valid_index()
    if idx0 != None:
        startingSeries[0] = startingSeries[idx0]
    idx1 = startingSeries.last_valid_index()
    if idx1 != None:
        startingSeries[-1] = startingSeries[idx1]
    simulatedValues = reSampledSeries
    # if the resampled dataframe is bigger fill in new values
    # Timediff needs to be calculated to next na, not next record
    if len(startingSeries) < len(reSampledSeries):
        # standard deviation
        sigma = startingSeries.rolling(5, 2).std()
        # first records get filled with first valid values of mean and standard deviation
        sigma = sigma.bfill()
        sigma = scaleSigma(sigma)
        simulatedValues = upsample(startingSeries,sigma)
    #put modified columns in result
    reSampledSeries = matchToOriginal(reSampledSeries,simulatedValues,interval)
    return reSampledSeries
def scaleSigma(sigma):
    records = abs(pd.to_timedelta(pd.Series(sigma.index).diff(-1)).dt.total_seconds()) #records is the number of seconds between consecutive values - one record per second
    records = records.rolling(5, 2).mean() #mean number of seconds between intervals used to calculate sigma
    records = records.bfill()
    records[records < 60] = 1
    records[records >= 60] = records/60
    # sigma is the the standard deviation for the existing time interval between records
    #sigma gets arbitrarily scaled to the minute level if records have greater than 1 minute time gaps.
    sigma = np.divide(sigma,records)
    return sigma
def matchToOriginal(originalSeries,simulatedSeries, interval):
    '''

    :param originalSeries:
    :param simulatedSeries:
    :param interval:
    :return:
    '''

    # make sure timezones match - can't join naive and nonnaive times
    tz = originalSeries.index.tzinfo
    simulatedSeries.index = simulatedSeries.index.floor(interval)
    # need to remove duplicate indices genereatd from flooring
    simulatedSeries = simulatedSeries[~simulatedSeries.index.duplicated(keep='first')]
    # .apply(lambda d: timeZone.localize(d, is_dst=useDST))
    #simulatedSeries.index = simulatedSeries.index.tz_localize('UTC')
    simulatedSeries.index = simulatedSeries.index.tz_localize(tz)
    # join the simulated values to the upsampled dataframe by timestamp
    newDF = pd.DataFrame({originalSeries.name:originalSeries,'value':simulatedSeries},index = originalSeries.index)
    #originalDataFrame = originalDataFrame.join(simulatedSeries, how='left')
    # fill na's for column with simulated values
    newDF.loc[pd.isnull(newDF[originalSeries.name]), originalSeries.name] = newDF['value']
    return newDF[originalSeries.name]
def upsample(series, sigma):
    # t is the time, k is the estimated value
    t, k = estimateDistribution(series[pd.notnull(series)], sigma)  # t is number of seconds since 1970
    simulatedSeries = pd.DataFrame({'value': k,'time':pd.to_datetime(t, unit='s')})
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
        handleMemory()
        timeArray, values = processInChunks(series, sigma)
        return timeArray, values
def processInChunks(series,sigma):
    print("chunk processing not implemented yet")
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
    defaultTimestep = 1
    records = abs(pd.to_timedelta(pd.Series(start.index).diff(-1)).dt.total_seconds()) #records is the number of seconds between consecutive values - one record per second
   #n is the number of values that will be estimated -will always be records + 1 unless default Timestep changes
    n = (records * defaultTimestep) + 1 #all estimates are at the 1 seoond timestep
    n = n.fillna(0)
    # find the 95th percentile of number of steps - exclude gaps that are too big to fill
    n95 = int(np.percentile(n[n < MAXUPSAMPLEINTERVAL], 95))
    # find where over the 95th percentile
    idxOver95 = np.where(n > n95)[0]

    # steps is an array of timesteps in seconds with length = max(records)
    steps = np.arange(0, int(n95)*defaultTimestep, defaultTimestep)
    # t is the numeric value of the dataframe timestamps
    t = pd.to_timedelta(pd.Series(pd.to_datetime(start.index.values, unit='s'), index=start.index)).dt.total_seconds()
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
    nRemaining = max([r for r in n[idxOver95] if r < MAXUPSAMPLEINTERVAL],default=0)
    if nRemaining >= 1:
        # individually calc the rest if they are less than the max allowable upsample interval
        start = start[idxOver95]
        mu= mu[idxOver95]
        sigma = sigma[idxOver95]
        time = time_matrix[idxOver95]
        time = time[:,-1] #just the last column, which is the last timestamp filled
        time = time.reshape(len(time),1)
        time_matrix0 = np.arange(0, nRemaining * defaultTimestep,defaultTimestep) # a single row of timesteps
        time_matrix0 = time_matrix0.reshape(1,time_matrix0.shape[0])
        rs = np.array([1, 1])
        rs = rs.reshape(2,1)
        time_matrix0 = time_matrix0 * rs #its now a matrix of times to add to start times
        time_matrix0 = time_matrix0 + time #time2 are our starting times (the last time filled in the previous step)

        x0 = estimateLangValues(defaultTimestep, mu, sigma, start, nRemaining)
        values = np.append(values, x0)
        timeArray = np.append(timeArray,time_matrix0)
        del time_matrix0
        del nRemaining
        del x0
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
def calculateSubColumns(col,components,df):
    '''

    :param col: filled column to subdivide
    :param components: list of components to parse values to.
    :param df: is a dataframe of the components to adjusted based on filled total
    :return:
    '''

    adj_m = df[components].div(df[col], axis=0)
    adj_m = adj_m.ffill()
    df[components] = adj_m.multiply(df[col], axis=0)
    del adj_m
    return df
