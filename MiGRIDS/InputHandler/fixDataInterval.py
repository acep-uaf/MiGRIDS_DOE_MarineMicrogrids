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

from MiGRIDS.InputHandler.badDictAdd import badDictAdd
import pandas as pd
import numpy as np
import multiprocessing as mp
MAXUPSAMPLEINTERVAL = 21600 #this is 6 hours
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

    eColumns = data.eColumns

    def fixDataFrameInterval(dataframe, interval):
        '''

        :param dataframe: a dataframe with datetime index
        :param interval: pandas deltatime
        :return: dataframe
        '''

        # df contains the non-upsampled records. Means and standard deviation come from non-upsampled data.
        df = dataframe.copy()

        # create a list of individual loads, total of power components and environmental measurements to fix interval on
        fixColumns = []

        fixColumns.extend(eColumns)
        # if there are power components fix intervals based on total power and scale to each component
        if df['total_p'].first_valid_index() != None:
            fixColumns.append('total_p')
        if df['total_l'].first_valid_index() != None:
            fixColumns.append('total_l')
        print('before upsampling dataframe is: %s' % len(dataframe))
        print(dataframe.head())
        # up or down sample to our desired interval
        # down sampling results in averaged values
        # this changes the size fo data.fixed[idx], so it no longer matches df rowcount.
        # we start with flooring - so a value 1 second past the desired interval will become the value

        #set the flag now
        flag_columns =[c for c in dataframe.columns if ('flag' in c)]
        other_columns = [c for c in dataframe.columns if 'flag' not in c]

        data1 = dataframe[other_columns].resample(pd.to_timedelta(interval)).mean()
        dataframe = data1.join(dataframe[flag_columns], how='left')

        for f in flag_columns:
            dataframe.loc[pd.isnull(dataframe[f]), f] = 4

        result = mp.Manager().Queue()
        # pool of processes
        pool = mp.Pool(mp.cpu_count())
        for col in fixColumns:
            print("fixing: ", col)
            #dataframe = fixSeriesInterval(col, dataframe, df, interval)
            pool.apply_async(fixSeriesInterval, args=(col,dataframe,df,data,interval, result))

        pool.close()
        pool.join()
        completeDataFrame = pd.DataFrame()
        while not result.empty():
            completeDataFrame = dataframe[flag_columns]
            completeDataFrame = pd.concat([completeDataFrame,result.get()])
        del df

        return completeDataFrame



    try:
        myD = [fixDataFrameInterval(x, interval) for x in data.fixed]
        data.fixed = myD
    except MemoryError as m:

        for i in range(0,len(data.fixed)):
            data.fixed[i] = fixDataFrameInterval(data.fixed[i], interval[i])
    print(data.fixed[0].head())

    data.removeAnomolies(stdNum=5)

    return data

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

def fixSeriesInterval(col, dataframe, df, data, interval, result):
    '''

    :param col:
    :param dataframe:
    :param df: DataFrame
    :param data: DataClass
    :param interval: Timedelta
    :param result: mp result
    :return: None
    '''

    df0 = df[[col]].copy()
    # remove rows that are nan for this column, except for the first and last, in order to keep the same first and last
    # time stamps
    df0 = pd.concat([df0.iloc[[0]], df0.iloc[1:-2].dropna(), df0.iloc[[-1]]])
    # get first and last non nan indecies
    idx0 = df0[col].first_valid_index()
    if idx0 != None:
        df0[col][0] = df0[col][idx0]
    idx1 = df0[col].last_valid_index()
    if idx1 != None:
        df0[col][-1] = df0[col][idx1]
    # time interval between consecutive records
    df0['timediff'] = pd.Series(pd.to_datetime(df0.index, unit='s'), index=df0.index).diff(1).shift(-1)
    df0['timediff'] = df0['timediff'].fillna(0)
    # get the median number of steps in a 24 hr period.
    steps1Day = int(pd.to_timedelta(1, unit='d') / np.median(df0['timediff']))
    # make sure it is at least 10
    if steps1Day < 10:
        steps1Day = 10
    # get the total power mean and std
    # mean total power in 24 hour period
    df0[col + '_mu'] = df0[col].rolling(steps1Day, 2).mean()
    # standard deviation
    df0[col + '_sigma'] = df0[col].rolling(steps1Day, 2).std()
    # first records get filled with first valid values of mean and standard deviation
    df0[col + '_mu'] = df0[col + '_mu'].bfill()
    df0[col + '_sigma'] = df0[col + '_sigma'].bfill()
    # if the resampled dataframe is bigger fill in new values
    # Timediff needs to be calculated to next na, not next record
    if len(df0) < len(dataframe):

        # t is the time, k is the estimated value
        t, k = estimateDistribution(df0, interval, col)  # t is number of seconds since 1970
        simulatedDf = pd.DataFrame({'time': t, 'value': k})
        simulatedDf = simulatedDf.set_index(
            pd.to_datetime(simulatedDf['time'] * 1e9))  # need to scale to nano seconds to make datanumber
        simulatedDf = simulatedDf[~simulatedDf.index.duplicated(keep='last')]

        # make sure timestamps for both df's are rounded to the same interval in order to join sucessfully
        dataframe.index = dataframe.index.floor(interval)
        # make sure timezones match - can't join naive and nonnaive times
        tz = dataframe.index.tzinfo
        simulatedDf.index = simulatedDf.index.floor(interval)
        # need to remove duplicate indices genereatd from flooring
        simulatedDf = simulatedDf[~simulatedDf.index.duplicated(keep='first')]
        # .apply(lambda d: timeZone.localize(d, is_dst=useDST))
        simulatedDf.index = simulatedDf.index.tz_localize('UTC')
        # join the simulated values to the upsampled dataframe by timestamp
        dataframe = dataframe.join(simulatedDf, how='left')
        # fill na's for column with simulated values
        dataframe.loc[pd.isnull(dataframe[col]), col] = dataframe['value']

        # component values get calculated based on the proportion that they made up previously if we are working with total_p
        components = []
        if 'total' in col:
            if col == 'total_p':
                components = data.powerComponents
            elif col == 'total_l':
                components = data.loads
            adj_m = dataframe[components].div(dataframe[col], axis=0)
            adj_m = adj_m.ffill()
            dataframe[components] = adj_m.multiply(dataframe[col], axis=0)
            del adj_m
        dataframe = dataframe[components + [col]]
        # get rid of columns added
        #dataframe = dataframe.drop('value', 1)
        #dataframe = dataframe.drop('time', 1)
        print(dataframe.head())

        del df0
        del simulatedDf
    #put modified columns in result
    result.put(dataframe)


def estimateDistribution(df,interval,col):
    import numpy as np
    #feeders for the langevin estimate
    mu = df[col+'_mu']
    start = df[col]
    sigma = df[col+'_sigma']
    records = df['timediff'] / pd.to_timedelta(interval) #records is the number (integer) of values missing between values. We add 1 so intervals are nto missed
    timestep = pd.Timedelta(interval).seconds
    #handle memory error exceptions by working with smaller subsets
    try:
        #return an array of arrays of values
        timeArray, values = getValues(records, start, sigma,timestep)
        return timeArray, values
    except MemoryError:
        handleMemory()
    return
        #steps is an array of timesteps in seconds with length = max(records)
def getValues(records, start, sigma, timestep):
    '''
    Uses the Langevin equation to estimate records based on provided mean (mu) and standard deviation and a start value
    :param records: [Array of Integers] the number of timesteps to estimate values for
    :param start: [Array of numeric] the start value to initiate the estimator for a given record
    :param sigma: [Array of numeric] the standard deviation to use in the estimator
    :param timestep: [Array of integer] the timestep to use in the estimator
    :return: [Array of timestamps], [Array of numeric] the timestamp and estimated values for each record
    '''
    # sigma is the the standard deviation for 1000 samples at timestep interval
    import numpy as np


    #number of steps
    defaultTimestep = 1
    #records will be the number of values that will be retained for a given timestep
    #n is the number of values that will be estimated
    #if the timestep is 30 seconds, and the timeinterval between 2 records is 2 minutes
    #3 values (records) will be filled in, but 91 (n) values will be generated
    n = (records * timestep) + 1 #all estimates are at the 1 seoond timestep
    # time constant. This value was empirically determined to result in a mean value between
    tau = records*.2
    tau[tau<1] = 1

    #renormalized variables

    # sigma scaled takes into account the difference in STD for different number of samples of data. Given a STD for
    # 1000 data samples (sigma) the mean STD that will be observed is sigmaScaled, base empirically off of 1 second
    sigma_bis = 0.4 * sigma * np.sqrt(2.0/(900*defaultTimestep))
    sqrtdt = np.sqrt(defaultTimestep)
    # find the 95th percentile of number of steps
    n95 = int(np.percentile(n,95))
    # find where over the 95th percentile
    idxOver95 = np.where(n > n95)[0]
    #x is the array that will contain the new values
    x = np.zeros(shape=(len(start), int(n95)))

    # steps is an array of timesteps in seconds with length = max(records)
    steps = np.arange(0, int(n95)*defaultTimestep, defaultTimestep)
    # t is the numeric value of the dataframe timestamps
    t = pd.to_timedelta(pd.Series(pd.to_datetime(start.index.values, unit='s'), index=start.index)).dt.total_seconds()
    # intervals is the steps array repeated for every row of time
    intervals = np.repeat(steps, len(t), axis=0)
    # reshape the interval matrix so each row has every timestep
    intervals_reshaped = intervals.reshape(len(steps), len(t))

    tr = t.repeat(len(steps))
    rs = tr.values.reshape(len(t), len(steps))
    time_matrix = rs + intervals_reshaped.transpose()

    # put all the times in a single array
    #the starter value
    x[:, 0] = start
    # use the next step in the time series as the average value for the synthesized data. The values will asympotically reach this value, resulting in a smooth transition.
    mu = start.shift(-1)
    mu.iloc[-1] = mu.iloc[-2]
    print("starting old method: ", datetime.now())
    oldx = x.copy()
    # mu gets distracted from all 1801 values in each x row. then each value is divided by tau adjusted by sigma
    for i in range(n95 - 1):  #
        oldx[:, i + 1] = oldx[:, i] + defaultTimestep * (-(oldx[:, i] - mu) / tau) + np.multiply(
            sigma_bis.values * sqrtdt, np.random.randn(len(mu)))
    print("completing old method: ", datetime.now())

    print("starting new method: ", datetime.now())
    sigma_bis = sigma_bis.values.reshape(len(start), 1)
    mu = mu.values.reshape(len(start), 1)  # make mu a vertical vector
    # tau = tau.reshape(len(start),1)
    tau = tau.values.reshape(len(start), 1)
    x = estimateValues(defaultTimestep, mu, sigma_bis, sqrtdt, start, tau, x)
    print("completing new method: ", datetime.now())
    #remove the last columnt before adding np.delete(z, -1, 1)
     #TODO mask instead of loop so only values needed are available
    # remove extra values to avoid improper mixing of values when sorting
    for row in range(time_matrix.shape[0]):
        time_matrix[row,int(n[row]):] = None
        x[row,int(n[row]):] = None

    timeArray = np.concatenate(time_matrix)
    values = np.concatenate(x)
    # this can only work as long as fixBadData removes any None values
    values = values[values != None]
    timeArray = timeArray[timeArray != None]

    nRemaining = max(n[idxOver95[idxOver95<MAXUPSAMPLEINTERVAL]])
    # individually calc the rest if they are less than the max allowable upsample interval
    start2 = start[idxOver95]
    mu2 = mu[idxOver95]
    sigma_bis2 = sigma_bis[idxOver95]
    time2 = time_matrix[idxOver95]
    time2 = time2[:,-1] #just the last column, which is the last timestamp filled
    time2 = time2.reshape(len(time2),1)
    time_matrix0 = np.arange(0, nRemaining * defaultTimestep,defaultTimestep) # a single row of timesteps
    time_matrix0 = time_matrix0.reshape(1,time_matrix0.shape[0])
    rs = np.array([1, 1])
    rs = rs.reshape(2,1)
    time_matrix0 = time_matrix0 * rs #its now a matrix of times to add to start times
    time_matrix0 = time_matrix0 + time2 #time2 are our starting times (the last time filled in the previous step)
    x2 = np.zeros(shape=(len(start2), int(nRemaining)))
    x2[:, 0] = start2
    tau2 = tau[idxOver95]


    x0 = estimateValues(defaultTimestep, mu2, sigma_bis2, sqrtdt, start2,tau2, x2)
    values = np.append(values, x0)
    timeArray = np.append(timeArray,time_matrix0)

    # for idx in idxOver95[idxOver95<MAXUPSAMPLEINTERVAL]:
    #     # find remaining values to be calculated
    #     currentN = n[idx]
    #     nRemaining = int(max([n[idx] - n95, 0]))
    #     if nRemaining >=1:
    #         # calc remaining values
    #         x0 = np.zeros(shape = (nRemaining,))
    #         # first value is last value of array
    #         x0[0] = x[idx, -1]
    #
    #         # corresponding time matrix
    #         time_matrix0 = time_matrix[idx,-1] + np.arange(0,nRemaining*defaultTimestep,defaultTimestep)
    #         #TODO change to new method - check inputs
    #         x0 = estimateValues(defaultTimestep[nRemaining],mu[nRemaining],sigma_bis[nRemaining],sqrtdt,start[nRemaining])
    #         # for idx0 in range(1,nRemaining):
    #         #     x0[idx0] = x0[idx0-1] + defaultTimestep * (-(x0[idx0-1] - mu[idx]) / tau[idx]) + np.multiply(sigma_bis.values[idx] * sqrtdt, np.random.randn())
    #
    #         # append to already calculated values
    #         values = np.append(values, x0)
    #         timeArray = np.append(timeArray,time_matrix0)

    tv = np.array(list(zip(timeArray,values)))
    tv = tv[tv[:,0].argsort()] # sort by timeArray

    t, v = zip(*tv)

    #clean up
    del tv
    del values
    del timeArray
    del time_matrix0
    del nRemaining
    del x0
    del idxOver95
    del intervals
    del intervals_reshaped
    del tau
    del sigma
    del sigma_bis
    del steps
    del mu
    del rs
    del tr

    return t,v


def estimateValues(defaultTimestep, mu, sigma_bis, sqrtdt, start, tau, x):

    r = np.random.randn(len(sigma_bis) * len(x[0, :]))
    r = r.reshape(len(sigma_bis), len(x[0, :]))
    mv = np.multiply(sigma_bis * sqrtdt, r)  # random error term
    # mv = mv.reshape(len(start), 1) #make this a matrix?

    b = defaultTimestep * (-1 * np.subtract(x, mu) / tau)
    c = b + mv
    c = np.delete(c, 0, 1)  # delete the first column, because those are our starting values that don't change
    # add a first column to new matrix
    # add x + new matrix - the zero columnn means values are added by shifting 1
    a = np.zeros(len(start)).reshape(len(start), 1)
    # all columns in x are zero except the first one, so by adding we are replacing the values
    # add the zero column to our matrix
    z = np.column_stack((a, c))
    # z = np.delete(z,-1,1)
    x = x + z
    return x
