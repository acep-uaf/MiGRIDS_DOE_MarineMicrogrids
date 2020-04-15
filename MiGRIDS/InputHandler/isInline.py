# Projet: MiGRIDS
# Created by: T.Morgan# Created on: 2/25/2018
import numpy as np
import pandas as pd
import datetime

#Functions used for evaluating bad data and replacing it with good data

# checkDataGaps looks for gaps in the timestamp index that is greater than the median sampling interval
# new records will have NA for values
# series -> series
from MiGRIDS.InputHandler.badDictAdd import badDictAdd

MAXSMALLBLOCKDURATION = 1209600
def checkDataGaps(s):
    '''checkDataGaps looks for gaps in the timestamp index that is greater than the median sampling interval
     new records will have NA for values.
    :param s: [pandas.Series] the series to evalutate
    :return: [pandas.Series] series with gaps filled with NA
    '''

    timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff(periods=1)
    
    #shift it up so duration is to the next row
    timeDiff = timeDiff.shift(periods = -1)
    #find the median timestep
   # medians = createMedians(timeDiff)
    #timeDiff = pd.DataFrame(timeDiff)
    #timeDiff['medians'] = medians
    #timeDiff.columns = ['timeDiff','medians']

    #local function to create datetime index
    #r is a row consisting of value and timedelta column named dif
    def makeIndex(r):
        d = pd.date_range(start =pd.to_datetime(r.start), periods=int(r.timeDiff/m), freq=m).tolist()
        return [d]
    
    #filtered is a dataframe of values that need to be filled in because gaps in 
    #timestamps are greater than the median sample interval multiplied by 2
    
    #filtered = timeDiff[timeDiff['timeDiff'] > timeDiff['medians'] * 2]
    m = timeDiff.median()
    timeDiff = pd.DataFrame(timeDiff)
    timeDiff.columns = ['timeDiff']
    filtered = timeDiff[timeDiff.timeDiff > m]
    filtered['start'] = pd.Series(pd.to_datetime(filtered.index),index=filtered.index)
    #list of missing timestamps for each indice in filtered
    missingIndices =filtered.apply(lambda r: makeIndex(r),axis=1)
    if len(missingIndices) > 0:
        #make the indices into a list of dataframes to be concatonated
        indices = missingIndices.iloc[:,0].apply(lambda i:pd.DataFrame(data = None,index = pd.DatetimeIndex(i))).tolist()
        s = s.append(pd.concat(indices))

        #only keep the colums we started with (return df to its original dimensions)
        s = s.iloc[:,0]

        #get rid of duplicate indices created by adding indices   
        s = s[~s.index.duplicated(keep='first')]

        #return a sorted dataframe
        s = s.sort_index(0, ascending=True)
    return s
    
def isInline(s):
    '''
    Itentifies rows of data that are inline (unchanged values) or datagaps (inline due to no data). Returns a series of same length as s of group id's.
     Inline values will all have the same group id.
    :param s: [Series] to be evalueated.
    :return: [Series] group id's for inline values
    '''
    #get rid of na's added through merging seperate files - this happens when timestamps don't match between files
    #these are not actual na's that we want to identify
    s = s.dropna()
    if len(s) > 0:
        #check for datagaps first. Datagaps are treated like inline data. 
        s = checkDataGaps(s)
        #na s identified in checkDataGaps get changed to a nonsense value so they will be grouped as inline data
        s = s.replace(np.nan,-99999)
        
        #group values that repeat over sampling intervals 
        grouping = s.diff().ne(0).cumsum()
       
        #we are only interested in the groups that have more than 1 record or are null
        groups = grouping.groupby(grouping).filter(lambda x: (sum(x) <= 0) or len(x) > 1)
        
        #return na values
        s = s.replace(-99999, np.nan)
        return groups
    
    return pd.Series(s)

def removeChunk(df, i1, i2):
    '''splits a df into 2 dataframes at the specified indices
    df1 will not includ i1, and df 2 will not include i2
    :param df a pandas dataframe
    :param i1 a pandas index that will be the location of the first split
    :param i2 a pandas index that will be the location of the second split'''
    newlist = [df[:i1][:-1],df[i2:][1:]]
    return newlist


def identifyCuts(lod, cname, cutoff, cutStarts):
    '''Evaluates a list of dataframes for gaps in data beyond an acceptable tolerance. Indices returned provide cut points to spit the dataframes at.
    :param lod: [ListOf Dataframe] list of dataframes to evaluate
    :param cname: [String] column within a dataframe to evaluate
    :param cutoff: [pandas.TimeDelta] max duration tolerable without data
    :param cutStarts: pandas.series of indices
    :return: [Listof Indices] a list of indices to split the dataframes at
    '''
    if (len(lod) <= 0):
        return cutStarts
    else:
        s = lod[0][cname]  
        s = s.dropna()
        timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff(periods=1)
        #shift it up so duration is to the next row  
        timeDiff = timeDiff.shift(periods = -1) 
        cutStarts = pd.concat([cutStarts,timeDiff[timeDiff >= cutoff]],axis=0)
        return identifyCuts(lod[1:],cname,cutoff,cutStarts)
    
#listofDataframe, listofString - > listOfDataFrames
def cutUpDataFrame(lod, loc):
    if len(loc)<=0:
        return lod
    else:
        cuts = identifyCuts(lod, loc[0], pd.Timedelta(weeks=2),pd.Series())
        lod = makeCuts(lod,cuts)
        return cutUpDataFrame(lod,loc[1:])

#split a dataframe at cut and return the 2 dataframes as a list
def makeCut(lod, cut,newlist):
    '''cut is index'''
    if len(lod) <= 0:
        return None
    else:
        #if (cut.index[0] in lod[0].index)
        #    newlist = removeChunk(lod[0], cut.index[0], cut[0]) + lod[1:] + newlist
        if (cut[0] in lod[0].index):
            newlist = removeChunk(lod[0], cut[0], cut[:1][0]) + lod[1:] + newlist

            return newlist
        else:
            return makeCut(lod[1:],cut,newlist + lod[:1])

#cuts up a list of dataframes and the specified cuts and returns the new list of dataframes
#listOfDataframes, Series -> listOfDataFrames
def makeCuts(lod, cuts):
    if len(cuts) <= 0:
        return lod
    else:
       nl =  makeCut(lod,cuts[:1],[])
       if nl != None:
           return makeCuts(nl, cuts[1:])
       else:
           return makeCuts(lod, cuts[1:])
           


def findValid(initialTs, d, possibles, s):
    '''
    Finds a datetime indices to be used as the start point for replacing bad data.
    if a valid replacement block is not found the initial timestamp is returned.
    inline values need to become na before this point.
    :param initialTs: pandas datetime is the timestamp for the beginning of the bad data
    :param d: TimeDelta is the duration of the missing data
    :param possibles: A series with index type that matches S and contains possible replacement values
    :param s: pandas.Series series being evaluated.
    :return: pandas.datetime a single datetime that indicates the start of the data block to be used as replacement
    '''
    s = s.copy()
    s.loc[initialTs:initialTs + d,] = np.nan
    if len(possibles) < 1:
        return initialTs
    else:
        totalCoverage = calculateNonNullDuration(pd.to_datetime(possibles.first_valid_index()),pd.to_datetime(possibles.first_valid_index())+d, s)

        if (totalCoverage < d * 0.9 ) | (totalCoverage >  d * 1.2) | (possibles.first_valid_index() == initialTs): #not a fit so keep looking
        #if len(s[pd.to_datetime(possibles.first_valid_index()):pd.to_datetime(possibles.first_valid_index()) + d].dropna()) < len(s[pd.to_datetime(possibles.first_valid_index()):pd.to_datetime(possibles.first_valid_index()) + d]):
            possibles = possibles[possibles.first_valid_index():][1:] #remove the first possible value from consideration
            return findValid(initialTs, d, possibles, s)
        else:
            return possibles.first_valid_index()
            

    #first value is startof missing block
    #second value is end of missing block   
    #third value is list of possible replacement indices


def calculateNonNullDuration(index1,index2, s):
    '''Calculates the time duration of a series, excluding null values '''
    evaluationChunk = s[index1:index2]
    evaluationTime = pd.Series(evaluationChunk.index, index=evaluationChunk.index).diff().astype('timedelta64[ns]')
    if (isinstance(s,pd.Series)):
        evaluationTime.loc[pd.isnull(evaluationChunk)] = 0  # set to 0 where s is null
    else:
        evaluationTime.loc[pd.isnull(evaluationChunk).any(axis=1)] = 0
    totalCoverage = evaluationTime[pd.notnull(evaluationTime)].sum()
    totalCoverage = pd.to_timedelta(totalCoverage, 'h')

    return totalCoverage


def validReplacements(possibleIndices, possibleReplacementValues):
    '''
    Identifies if a specified record is the start of valid replacement block
    :param possibleIndices: DataFrame consisting of first, last and possibles.
    :param possibleReplacementValues: pandas.Series replacement values to evaluate
    :return: [DateTimeIndex]
    '''
    if type(possibleIndices['possibles']) is not list:
        return possibleIndices['first']
    if len(possibleIndices['possibles']) <=1:
        return possibleIndices['first']
    #n is the entire indicesOfinterest dataframe
    p = pd.Series(possibleIndices['possibles'], index=possibleIndices['possibles'])
    p = p[~p.index.duplicated(keep='first')]
    df = pd.concat([possibleReplacementValues, p],
                   keys=['series','possibles'],
                   axis=1, join='inner')
    
    if type(possibleReplacementValues) is pd.DataFrame:
        df = df.drop(possibleReplacementValues.columns, axis=1, level=1)
        #get rid of level 1 index
        df.columns = df.columns.droplevel(1)
        
       
    diff = abs(pd.to_timedelta(pd.Series(df.index) - pd.to_datetime(possibleIndices['first'])))
    diff.index = df.index
    df['diff'] = diff
    df['monthdistance']= abs(possibleIndices['first'].month - df.index.month)
    df['yeardistance'] = ((possibleIndices['first'].year - df.index.year) + 1) * (-1 / len(set(df.index.year)))
    df = df.sort_values(['yeardistance','monthdistance','diff'])
    p = df['possibles']
    v = findValid(possibleIndices['first'], possibleIndices['last'] - possibleIndices['first'], p, possibleReplacementValues)
    return v


#Drop a range of records from a dataframe
def dropIndices(df, listOfRanges):
    if len(listOfRanges) <= 0:
        return df
    else:
       l = removeChunk(df, listOfRanges['first'].iloc[0], listOfRanges['last'].iloc[0])
       if len(l)>1:
           df = l[0].append(l[1])
       return dropIndices(df,listOfRanges.iloc[1:])
   
#

def doReplaceData(groups, df_to_fix, cuts, possibleReplacementValues):
    '''
    replace bad data in a dataframe starting with small missing blocks of data and moving to big blocks of missing data
    df_to_fix and possibleReplacementValues need to have the same columns.
    :param groups: pandas.DataFrame with columns size, first and last, first is the first indixe in a block to replace, last is the last index to replace
    :param df_to_fix: DataFrame the dataframe to fix
    :param cuts: [listOf TimeDeltas] the duration of each block of missing data will fall into a cut timedelta
    :param possibleReplacementValues: DataFrame where replacement values are drawn from. Can be larger than df_to_fix. If possibleReplacmentValues contains null
    then values can be replaced with null
    :return: [DataFrame] with bad values replaced
    '''

    if (len(df_to_fix.shape)) >1 and (df_to_fix.shape[1] > 1):
        if df_to_fix.shape[1] != possibleReplacementValues.shape[1]:
            raise Exception #TODO replace with custom exception

    if(len(groups) <= 0):
        return df_to_fix
     #replace small missing chunks of data first, then large chunks
    else:
        indicesOfInterest = groups[groups['size'] <= cuts[0]]
        #if thera are any blocks of the appropriate size replace them.
        if len(indicesOfInterest) > 0:
            indices = pd.DataFrame(
                {'first': indicesOfInterest['first'].values, 'last': indicesOfInterest['last'].values},
                index=indicesOfInterest.index)

            searchSeries = pd.Series(possibleReplacementValues.index)
            searchSeries.index = searchSeries.values
            #pos = indices.apply(lambda i: getPossibleStarts(i['first'],i['last'], searchSeries),axis=1)
            indices['possibles'] = indices.apply(lambda i: getPossibleStarts(i['first'], i['last'], searchSeries),
                                                  axis=1)
            #pos = pos['first']
            #pos.name = 'possibles'
            indicesOfInterest = pd.concat([indicesOfInterest,indices['possibles']],axis=1)
            replacementStarts = indicesOfInterest.apply(lambda n: validReplacements(n, possibleReplacementValues), axis = 1)
            
            indicesOfInterest.loc[:,'replacementsStarts'] = replacementStarts.values
            indicesOfInterest['replacementsStarts'].dt.tz_localize(indicesOfInterest['first'].dt.tz)
            #replace blocks of nas with blocks of replacementstarts
            df_to_fix = dropIndices(df_to_fix, indicesOfInterest)
            #new values get appended onto the datframe

            df_to_fix = expandDataFrame(indicesOfInterest, df_to_fix)

            
        return doReplaceData(groups[groups['size'] > cuts[0]], df_to_fix, cuts[1:], possibleReplacementValues)

#ioi is a single row from indicesOfInterest
#s is the series with na's removed
#returns a dataframe of same shape as s
#generates an empty dataframe with the specified range of indices
def listsToDataframe(ioi,s):
    '''generates an dataframe with the specified range of indices and values drawn from a list provided by ioi
    :param ioi: [namedArray] a single row from a indicesOfInterest Dataframe with columns, first, last and replacementStarts
    :param s: [Series] that replacement values are extracted from
    :return: [DataFrame] filled with values from replacement series
    '''
    firstMissing = ioi['first']
    lastMissing = ioi['last']
    start = ioi['replacementsStarts']
    
    newBlock =s[start:start + (lastMissing - firstMissing)]
    #set the index frequency

    if len(newBlock) > 0:
        f = (lastMissing - firstMissing) / (len(newBlock))
        #index of newBlock gets adjusted to fit into the missing space
        timeDiff = newBlock.index[0] - firstMissing #difference between new and missing
        #newIndex = pd.date_range(start=firstMissing,periods=len(newBlock),freq=f)#create an index that matches the timestamps we are replaceing
        newBlock.index = newBlock.index - timeDiff # assign the new indext to the values we took from elsewhere

    else:
        if (isinstance(s,pd.Series)):
            newBlock = pd.Series(index = pd.date_range(start=firstMissing,periods=2,
                                                      freq =(lastMissing - firstMissing)))
        else:
            newBlock = pd.DataFrame(index = pd.date_range(start=firstMissing,periods=2,
                                                      freq =(lastMissing - firstMissing)))
    return newBlock

#insert blocks of new data into an existing dataframe
#DataFrame,Series -> Series
#idf is a dataframe with first, last, and replacement start timestamps
def expandDataFrame(idf, s):
    '''
    insert blocks of new data into an existing dataframe
    gets number of records from replacement, adds indices between start and end based on number of records
    replacements and s need to be the same shape
    :param idf: [DataFrame] consisting of first, last and replacementstart columns
    :param s: [pandas.Series or pandas.DataFrame] dataframe or series to be expanded
    :return: [pandas.Series or pandas.DataFrame]
    '''
    if len(idf) <= 0:
        return s
    else:
        s = s.append(listsToDataframe(idf.iloc[0], s))
        s = s.sort_index()
        return expandDataFrame(idf.iloc[1:],s)


#returns a list of integer indices sorted by distance from s with length 2 * timeRange
#integer, integer -> listOfInteger
#s is start, timerange is searchrange
def createSearchRange(s,timeRange):
    '''
    creates a search window based on the input timerange and start indice
    :param s: [datetime] the start datetime
    :param timeRange: pandas timedelta the number of seconds to include in the search window
    :return: list the date time range surrounding the start point to use as a search window
    '''
    fullRange =[s - timeRange, s+timeRange]
    return fullRange
    
    
#find possible replacement starts
def getPossibleStarts(missingIndexFirst,missingIndexLast,searchIndex):
    ''' find the possible start indices for replacement data based in the indices of missing data and total duration of missing data.
    If there are multiple years represented in the dataset that possible starts are biassed towards previous years data.

    :param MissingIndexFirst: pandas datetime of the missing block
    :param MissingIndexLast: pandas datetime that is the last value missing in a block
    :param searchIndex: pandas.index of possible replacements
    :return: [ListOf datetimes] the datetime indices of records that could be used as the start point for replacement blocks
    '''
    possibles = calculateStarts([missingIndexFirst,missingIndexLast], searchIndex)
    #possibles get filtered 
    return possibles.tolist()


#DataFrame -> DataFrame
#input dataframe contains columns start for the start index of a mising block of data in seconds from beginning of dataset
#totalduration is the to time covered in the dataset
#smallBlock is whether the missing block is less than 2 weeks - boolean
def getStartYear(smallBlock, firstMissingIndex,searchIndex):
    ''' Identifies what year to start searching for replacement data in. Prioritizes previous year.
    If it is a large block of missing data then data from the same year is not considered acceptable
    input dataframe contains columns start for the start index of a mising block of data in seconds from beginning of dataset
     totalduration is the to time covered in the dataset
     smallBlock is whether the missing block is less than 2 weeks - boolean
    :param searchIndex: the indices provided for replacement
    :return: df dataframe characteristics of the data to replace
    TimeRange is the duration of time missing
    start is the start index of the potential placement block
    smallblock is wheather or not it is a small block of missing data
    firstmissing is the timestamp at the start of the missing block
    startyear is the valeu the search will begin at
    '''
    #start by going back 1 year
    #subtract a year from the start point
    sy = firstMissingIndex - pd.to_timedelta(31536000,'s')

    #if it goes before the origin try increasing by a year
    if sy < searchIndex.index[0]:
        sy = sy + pd.to_timedelta(31536000,'s')
   
    #anything still below the first possible index go up again
    if sy  < searchIndex.index[0] :
        sy = sy+ pd.to_timedelta(31536000,'s')
    #or any are big blocks and are now at the start year
    if (abs(sy- searchIndex.index[0]) < pd.to_timedelta(31536000,'s')) & (smallBlock == False):
        sy = sy + pd.to_timedelta(31536000,'s')
    # if any are above the range acceptable - go back down
    if (sy > searchIndex.index[-1] ):
        sy = sy - pd.to_timedelta(31536000,'s')
    #if the difference between start year and start is less than a year and smallBlock is false startyear = np.nan
    if (abs(sy - searchIndex.index[0]) < pd.to_timedelta(31536000,'s')) & (smallBlock == False):
        sy =  np.nan
    return sy

def calculateStarts(missingIndex,searchSeries):
    '''
    [], n['smallBlock'], n['startyear'],n['missingIndex'], n['searchIndex']
    finds the possible start points for replacement blocks for a given block of missing data
     :return: [ListOf DatetimeIndices]
    '''
    searchExcluded = pd.concat([searchSeries[:missingIndex[0]], searchSeries[missingIndex[-1]:]], axis=0)
    searchExcluded = searchExcluded[searchExcluded.index.dayofweek == missingIndex[0].dayofweek]
    searchExcluded = searchExcluded[(searchExcluded.index.hour <= (missingIndex[0] + pd.to_timedelta('3 h')).hour) & (
                searchExcluded.index.hour >= (missingIndex[0] - pd.to_timedelta('3 h')).hour)]

    return searchExcluded

#filters the possible times to match day of week and time envelope
def filteredTimes(possibles,missingIndexStart):
    ''' filters the a list of possible times to match day of week and time envelope of a given datetime
    :param possibles: Listof DateTime start and end point of range
    :param firstMissingTimestamp: [DateTime
    :return: [ListOfDateTime]
    '''
    #possibles is  a list of integers to start with
    #set the first value to 0 - this is our start point
    
    # restrict the search to only matching days of the week and time of day
    #day to match
    dayToMatch = missingIndexStart.dayofweek
    
    possibles = possibles.between_time((missingIndexStart - pd.Timedelta(hours=3)).time(),(missingIndexStart + pd.Timedelta(hours=3)).time())
    possibles = pd.Series(pd.to_datetime(possibles.index), index= possibles.index)
    possibles =  possibles.dt.dayofweek
    #5 is a saturday
    if dayToMatch < 5:
        possibles = possibles[possibles < 5]
    else:
        possibles = possibles[possibles >= 5]

    return possibles.index.tolist()

#identify what the year breakdown of the dataframe is
def yearlyBreakdown(df):
    '''
    Identify which records have data in the previous year, or in years following.
    :param df: [pandas.DataFrame]
    :return: [pandas.DataFrame] a dataframe indicating dateranges within df that have previous years of data within the same dataframe
    '''
    yearlies =df.index.to_series().groupby(df.index.year).agg(['first','last'])
    #find the closest offset
    yearlies['offset']= pd.Timedelta(days=7)
    yplus1= yearlies.shift(-1)
    yminus1=yearlies.shift(1)
    y = pd.concat([yearlies,yplus1.add_prefix('plus'),yminus1.add_prefix('minus')], axis=1)
    monthlies = df.index.to_series().groupby([df.index.year,df.index.month]).agg(['first','last'])
    y.index.rename('year', True)
    monthlies.index = monthlies.index.set_names(['year','month'])
    y = y.join(monthlies.add_prefix('month'), how='outer')
    #adjust years to match index years
    y.plusfirst = y.plusfirst + pd.Timedelta(days=-365)
    y.pluslast = y.pluslast + pd.Timedelta(days=-365)
    
    y.minusfirst = y.minusfirst + pd.Timedelta(days=365)
    y.minuslast = y.minuslast + pd.Timedelta(days=365)
    y.loc[((y.monthfirst >= y.minusfirst) &
      (y.monthfirst <=y.minuslast))
    & ((y.monthlast >= y.minusfirst) &
      (y.monthlast <=y.minuslast)), 'offset'] = pd.Timedelta(days=365)
    
    y.loc[((y.monthfirst >= y.plusfirst) &
      (y.monthfirst <=y.pluslast))
    & ((y.monthlast >= y.plusfirst) &
      (y.monthlast <=y.pluslast)), 'offset'] = pd.Timedelta(days=-365)
    
    f=y.monthfirst.groupby(y.offset).agg(['first','last'])
    l= y.monthlast.groupby(y.offset).agg(['first','last'])
    f['offset'] = f.index
    l['offset'] = l.index
    cuts = pd.DataFrame({'offset': l.offset, 'first' :f['first'], 'last' :l['last']})
    return cuts


#df is the complete dataset
#df_to_fix contains a subset of data deemed ok to use quick replace on
#gets fed in in chunks of the original dataframe depending on the offset to apply
#offset is a timedelta
#returns a dataframe of improved values with the same columns as the original input

def quickReplace(df,df_to_fix,offset,grouping):
    '''
    Small groups of missing data are replaced with the most immediate block of acceptable data.
    Groups that were not successfully replaced go through a more extensive search for replacement data.
    :param df: [pandas.DataFrame] datafame containing replacement data
    :param df_to_fix: [pandas.DataFrame] data to be fixed
    :param offset: [pandas.TimeDelta] offset from missing data to pull replacement data from
    :param grouping: [pandas.Series] the group id that a record belongs to. Only bad records have group id's.
    :return: [pandas.DataFrame], [pandas.Series] the dataframe with replaced data and a list of groups that were not succesfully replaced.
    '''
    columns = df.columns
    grouping.name = 'grouping'  
    rcolumns = [c+"r" for c in columns]
    
    #reduce the dataset to just exclude na's unless they are new record fills (have a group id)    
    df_to_fix = pd.concat([df_to_fix,grouping],axis=1, join='outer')
    df_to_fix = df_to_fix[(np.isnan(df_to_fix[columns[0]]) & pd.notnull(df_to_fix['grouping']))|
                          (pd.notnull(df_to_fix[columns[0]]))]
    df_to_fix = df_to_fix.drop('grouping', axis=1)           
    df = df.join(grouping, how='outer')

    df = df[(np.isnan(df[columns[0]]) & pd.notnull(df['grouping']))|
                          (pd.notnull(df[columns[0]]))]
    df = df.drop('grouping', axis=1)
    
    originalDOW = df.index[0].dayofweek
    #offset is backwards
    df = df.shift(periods=1,freq=offset, axis = 1)
    
    #check that the day of the week lines up and adjust if necessary
    diff = df.index[0].dayofweek-originalDOW
    if (diff == -1) | (diff == -6):
        df = df.shift(periods=1, freq = pd.Timedelta(days=1), axis=1)
    elif (diff == 1) | (diff == 6):
        df = df.shift(periods=1, freq = pd.Timedelta(days=-1), axis=1)
    elif (diff in([2,3,4,5,-2,-3,-4,-5])) :
        return
    mergedDf = df_to_fix.join(df, rsuffix="r",how='left')
    #mergedDf =pd.concat([df_to_fix,df.add_prefix('r')], axis = 1, join='outer')
    mergedDf[columns[0] + "copy"] = mergedDf[columns[0]]
    
    #mergedDf = pd.concat([mergedDf,grouping], axis=1, join='outer')
    mergedDf=mergedDf.join(grouping,how='outer')
    #if the row has been assigned to a group then it is a bad value and gets set to nan so it will be replaced
    mergedDf.loc[~np.isnan(mergedDf['grouping']),columns] = np.nan
    #rpelace all the bad values with the value at their offset position
    mergedDf.loc[(np.isnan(mergedDf[columns[0]])) & ~np.isnan(mergedDf.grouping) ,columns] =  mergedDf.loc[(np.isnan(mergedDf[columns[0]]))  & ~np.isnan(mergedDf.grouping),rcolumns].values
    #if not all the values within a group were replaced keep that group to be replaced later
    #badgroups are the ones where not every na was filled
    badGroups = mergedDf[np.isnan(mergedDf[columns[0]])]['grouping']
    
    #records belonging to a bad group get returned to Na to be replaced in a more complicated way
    mergedDf.loc[badGroups[pd.notnull(badGroups)].index,columns] = np.nan

    return mergedDf[columns],badGroups


#bump the year up or down
def cycleYear(dt, up, missinIndexStart, smallBlock = True):
    '''

    Find a start year approrpiate to the starting datetime and missing block size
    :param dt: [DateTime] is the date we are adjusting by a year
    :param up: [Boolean] whether to search up or down from our stop point
    :param missinIndexStart: [DateTime] is our original search start
    :param smallBlock: [boolean] indicates the missing block is less than 2 weeks - 1209600 seconds
    :return:
    '''
    if up:
        t = dt + pd.to_timedelta(31536000,'s')  #seconds in a year
    else: 
       t = dt - pd.to_timedelta(31536000,'s')
    if t < missinIndexStart - pd.to_timedelta(31536000, 's'):
        return cycleYear(t, True, missinIndexStart, smallBlock)
    #if its a big block missing and the test date is in the same year (less than 31536000 seconds away) 
    #bump the test start up a year
    if (t - missinIndexStart < pd.to_timedelta(31536000, 's')) & (smallBlock == False):
       return cycleYear(dt + pd.to_timedelta(31536000,'s'), up, missinIndexStart, smallBlock)
    return t  

#find the median value for timesteps between records
def createMedians(s):
    '''
    Identifies the 25, 50 and 85 percentiles for timesteps between records. Intervals with data gaps larger than the 85%
    replaced last.
    :param s: [pandas.Series] series to evaluate
    :return: [Listof TimeDelta]
    '''
    #Series of time diff values -> list of intervals that make up the majority of the dataset
    #returns a dataframe of group start and end indices and their sample interval
    def defineSampleInterval(s):
        f = s.quantile([0.25, 0.5, 0.85])
        l=f.tolist()
        l.sort()
        return l
    
    #DataFrame to be grouped, list of grouping intervals sorted lowest to highest
    #return dataframe of datasubset indices and their sampling intervals
    def createIntervalGroups(timeDiff,l):
        #timeDiff = pd.Series(pd.to_datetime(s.index, unit='s'), s.index).diff(periods=1)
        timeDiff[pd.to_timedelta(timeDiff) <= l[0] ] = l[0]
        for  i in range(1,len(l)):
            timeDiff[(pd.to_timedelta(timeDiff) <= l[i]) & (pd.to_timedelta(timeDiff) > l[i-1])] = l[i]
        timeDiff[pd.to_timedelta(timeDiff) > l[len(l)-1] ] = l[len(l)-1]  
        #s['timeDiff']= timeDiff
        #dataSubsets =s.index.to_series().groupby(s['timeDiff']).agg(['first','last'])
        return timeDiff
     
    l = list(set(defineSampleInterval(s)))
    medians = createIntervalGroups(s.copy(),l)
        
    return medians
    