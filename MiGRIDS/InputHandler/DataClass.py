# Projet: MiGRIDS
# Created by: T.Morgan# Created on: 9/20/2019
from MiGRIDS.InputHandler.Exceptions.DataValidationError import DataValidationError
from MiGRIDS.InputHandler.fixBadData import reallignSingleYear
from MiGRIDS.InputHandler.isInline import *

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pickle
import numpy as np
import os
import pandas as pd

#constants
TOTALP = 'total_power'
TOTALL= 'total_load'
MAXMISSING= '14 days'
FLAGCOLUMN = 'data_flag'
DATAFLAGS={1:'normal',2:'missing value',3:'exceeds min/max', 4:'upsampled'}

class DataClass:
    """A class with access to both raw and fixed dataframes."""


    #DataFrame, timedelta,list,timedelta -> 
    def __init__(self, raw_df,runTimeSteps=None,maxMissing=MAXMISSING):
        if len(raw_df) > 0:
            self.raw = raw_df.copy()
            self.components = []
            #self.fixed is a list of dataframes derived from raw_df split whenever a gap in data greater than maxmissing occurs           
            self.fixed = []
            self.badDataDict = {}
            #df is a single dataframe converted from raw_df
            #once cleaned and split into relevent dataframes it will become fixed
            self.df = pd.DataFrame(raw_df.copy(), raw_df.index, raw_df.columns)
            self.df = self.df.loc[~self.df.index.duplicated(keep='first')]
            self.df[TOTALP] = np.nan
            self.df[TOTALL] = np.nan
            #create data flag columns for all data columns
            for c in self.df.columns:
                self.df[c+'_flag'] = 1

            # all dataframes passed from readData will have a datetime column named DATE

            if 'DATE' in self.df.columns:
                self.df.index = pd.to_datetime(self.df['DATE'], unit='s')
                self.df = self.df.drop('DATE', axis=1)
                
            self.fixed = []
        else:
            self.raw = pd.DataFrame()
            self.rawCopy = pd.DataFrame()
            self.fixed = [pd.DataFrame()]
        
        #self.timeInterval = sampleInterval
        self.powerComponents = []
        self.loads = []
        self.ecolumns = []
        #runTimeSteps is a list of dates that indicate the portion of the dataframe to fix and include in analysis
        self.runTimeSteps = runTimeSteps
        self.maxMissing = maxMissing

        return

    @staticmethod
    def getFlagName(flag):
        return DATAFLAGS[flag]

    def getattribute(self, a):
        return self.__getattribute__(a)

    def dropAllEmpties(self,columns):
        for i in range(len(self.fixed)):
            self.fixed[i] = self.dropEmpties(self.fixed[i],columns)
    def keepOverlapping(self,df):
        componentColumns = [c.column_name for c in self.components]
        df = df[pd.notnull(df[componentColumns]).all(axis=1)]
        return df
    def dropEmpties(self,df,columns):
        df = df[pd.notnull(df[columns]).any(axis=1)]
        return df
    def dropUnused(self):
        if len(self.df[pd.notnull(self.df[TOTALL])])<=0:
            self.df = self.df.drop(TOTALL,axis=1)
        if len(self.df[pd.notnull(self.df[TOTALP])]) <=0 :
            self.df = self.df.drop(TOTALP,axis=1)
    #DataFrame, timedelta ->listOfDataFrame
    #splits a dataframe where data is missing that exceeds maxMissing
    def splitDataFrame(self,columns):
       if len(self.fixed) <= 0:
           self.fixed = [self.df]
       #dataframe splits only occurr for total_p, total load columns
       self.fixed = cutUpDataFrame(self.fixed, columns)
     # summarizes raw and fixed data and print resulting dataframe descriptions
    def summarize(self):
        '''prints basic statistics describing raw and fixed data'''
        print('raw input summary: ')
        print(self.raw.describe())
        print('fixed output summary: ')
        #each seperate dataframe gets described
        print([d.describe() for d in self.fixed])
        return

    # list -> null
    # identifies when there are no generator values
    # if the system can't operate withouth the generators (GEN = True) then values are filled
    # with data from a matching time of day (same as offline values)
    def fixGen(self, componentList):
        '''Identifies records without generator values.
        If the system can't operate without a generator (GEN == True)then values ar filled
        with data from matching time of day from a previous day.
        Alters the data directly in fixed dataframes
        :param componentList a string list of components in the dataset'''
        gencolumns = self.identifyGenColumns(componentList)
        if len(gencolumns) > 0:
            df_to_fix = self.df.copy()
            df_to_fix['hasData'] = (pd.notnull(df_to_fix[gencolumns])).sum(axis=1)
            df_to_fix = df_to_fix[df_to_fix['hasData'] >= 1]
            df_to_fix['gentotal'] = df_to_fix[gencolumns].sum(1)
            
            #group values that repeat over sampling intervals 
            grouping =df_to_fix[df_to_fix['gentotal']==0]['gentotal']
            grouping = pd.notnull(grouping).cumsum()
            if len(grouping[pd.notnull(grouping)]) > 0:
               reps = self.fixOfflineData(gencolumns[0],gencolumns,grouping)
               self.df = self.df.drop(reps.columns, axis=1)
               self.df= pd.concat([self.df,reps],axis=1)   
     
        return
    # list, string -> pdf
    # creates a pdf comparing raw and fixed data values
    def visualize(self, components, setupDir):
        filename = os.path.join(setupDir, *['..','TimeSeriesData', 'fixed_data_compare.pdf'])

        # plot raw and fixed data
        with PdfPages(filename) as pdf:
            # plot the raw data
            plt.figure(figsize=(8, 6))
            plt.plot(pd.to_datetime(self.raw.DATE, unit='s'), self.raw[TOTALP])
            plt.title('Raw data total power')
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()
            # plot the fixed data
            plt.figure(figsize=(8, 6))
            #plot all the fixed dataframes together
            plt.plot(pd.concat(self.fixed).index, pd.concat(self.fixed)[TOTALP], 'b-')
            plt.title('Fixed data total power')
            pdf.savefig()
            plt.close()
    # DataClass string -> pickle
    # pickles the dataframe so it can be restored later
    def preserve(self, setupDir):
        filename = os.path.join(setupDir, *['..','TimeSeriesData', 'fixed_data.pkl'])
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        pickle_out = open(filename, 'wb')
        #pickle.dump(self.fixed, pickle_out)
        pickle.dump(self, pickle_out) #pickle the entire class

        pickle_out.close
        return
    def totalField(self,tfield,sumColumns):
        if len(sumColumns) <=0:
            raise DataValidationError(3)
        self.df[tfield] = self.df[sumColumns].sum(1)
        self.df[tfield] = self.df[tfield].replace(0, np.nan)
        for df in self.fixed:
            df[tfield] = df[sumColumns].sum(1)
            df[tfield] = df[tfield].replace(0, np.nan)

        self.raw[tfield] = self.raw[sumColumns].sum(1)

    def scaleData(self, ListOfComponents):
        '''Sets the datatype in a dataframe so that it matches the component characteristics'''
        for c in ListOfComponents:
           c.setDatatype(self.df)
        return
    # DataClass -> null
    # replaces time interval data where the power output drops or increases significantly
    # compared to overall data characteristics
    def removeAnomolies(self, stdNum = 3):
        # stdNum is defines how many stds from the mean is acceptable. default is 3, but this may be too tight for some data sets.
        if TOTALP in self.df.columns:
            mean = np.mean(self.df[TOTALP])
            std = np.std(self.df[TOTALP])
    
            self.df[(self.df[TOTALP] < mean - stdNum * std) | (self.df[TOTALP] > mean + stdNum * std)] = None
         # replace values with linear interpolation from surrounding values
            self.df = self.df.interpolate()
            self.totalPower()
        return
    def totalPower(self):
        try:
            self.totalField(TOTALP,self.powerComponents)
        except DataValidationError as e:
            print('Dataset does not include any power generating components')
            pass
    def totalLoad(self):
        try:
            self.totalField(TOTALL, self.loads)
        except DataValidationError as e:
            print('Dataset does not include any load components')
            pass
    def setYearBreakdown(self):
        '''

        :return:
        '''
        self.yearBreakdown = yearlyBreakdown(self.df)
        return

    def fixOfflineData(self,columnToCompare, columnsToReplace,groupingColumn):
        '''replaces missing or bad data within df with values found elsewhere in the dataframe
        :param columnToCompare is the column that was used to find bad data - it can represent multiple columns as a single value
        :param columnsToReplace list of columns whose data will be overwritten with replacement values. Must also include columnToCompare
        :param groupingColumn is the column in df that identifies individual groups of missing data'''
        df = self.df[columnsToReplace].copy()
        if len(df[pd.notnull(df[columnToCompare])]) > 0:
            originalRange = [df.first_valid_index(),df.last_valid_index()]
            RcolumnsToReplace = ['R' + c for c in columnsToReplace]
            notReplacedGroups = groupingColumn
            for g in range(len(self.yearBreakdown)):
                subS = df.loc[self.yearBreakdown.iloc[g]['first']:self.yearBreakdown.iloc[g]['last']] #find a single year of data
                #replace missing values by matching dataframe to subset of 1 year
                replacementS, notReplacedGroups = quickReplace(pd.DataFrame(df), subS, self.yearBreakdown.iloc[g]['offset'],notReplacedGroups)
                df = pd.concat([df, replacementS.add_prefix('R')],axis=1, join = 'outer')
                #add to the dictionary
                badDictAdd(columnsToReplace, self.badDataDict, '2.Offline',
                           df[(pd.isnull(df[columnToCompare])) &
                                   (df.index >= min(subS.index)) &
                                   (df.index <= max(subS.index))].index.tolist())

                #set the data value
                df.loc[((pd.notnull(df['R' + columnToCompare])) &
                       (df.index >= min(subS.index)) &
                       (df.index <= max(subS.index))),columnsToReplace] = df.loc[((pd.notnull(df['R' + columnToCompare])) &
                       (df.index >= min(subS.index)) &
                       (df.index <= max(subS.index))),RcolumnsToReplace].values
                df = df.drop(RcolumnsToReplace, axis=1)

            groupingColumn.name = '_'.join([columnToCompare,'grouping'])
            df_to_fix = pd.concat([df,groupingColumn],axis=1,join='outer')
            df_to_fix = df_to_fix[originalRange[0]:originalRange[1]]

            #filling in the more difficult to fill values
            df_to_fix = self.truncateDate(df_to_fix)
            #if there is still data in the dataframe after we have truncated it
            if len(df_to_fix) > 1:
                self.logOfflineBadData(df_to_fix,columnToCompare)
                #remove groups that were replaced
                # find offline time blocks
                #get groups based on column specific grouping column
                groups = pd.Series(pd.to_datetime(df_to_fix.index),index=df_to_fix.index).groupby(df_to_fix['_'.join([columnToCompare,'grouping'])]).agg(['first','last'])
                groups['size'] = groups['last']-groups['first']

                #filter groups we replaced already from the grouping column
                groups= groups[(groups['size'] >= pd.Timedelta(days=5)) |
                        groups.index.isin(notReplacedGroups[pd.notnull(notReplacedGroups)])]
                cuts = groups['size'].quantile([0.25, 0.5, 0.75,1])
                cuts = list(set(cuts.tolist()))
                cuts.sort()
                print("%s groups of missing or inline data discovered for component named %s" %(len(groups), columnToCompare) )
                #don't pass the grouping column to doReplaceData
                df_to_fix = doReplaceData(groups, df_to_fix.loc[pd.notnull(df_to_fix[columnToCompare]),columnsToReplace], cuts,df.loc[pd.notnull(df[columnToCompare]),columnsToReplace])

                return df_to_fix.loc[pd.notnull(df_to_fix[columnToCompare]),columnsToReplace]
        else:
            return df

    def logOfflineBadData(self,df_to_fix, columnToCompare):

        # #set data flags
        df_to_fix[columnToCompare+'_flag'] = 1 #create the flag column
        df_to_fix.loc[pd.isnull(df_to_fix[columnToCompare]),columnToCompare + '_flag'] =2

        #record the data change in the dictionary
        if len(df_to_fix[columnToCompare][pd.isnull(df_to_fix[columnToCompare])].index.tolist()) > 0:
            badDictAdd(columnToCompare, self.badDataDict, '2.Offline',
                   df_to_fix[columnToCompare][pd.isnull(df_to_fix[columnToCompare])].index.tolist())

   #DataFrame, String -> Boolean
   #return true if a column does not contain any values
    def isempty(self, df,column):
        if sum(df[column]) == 0:
            return True
        return False
    #keeps only rows of data that are between the specified runTimeSteps
    #raw data is not affected, only fixed data
    def truncateDate(self,df):
        def makeList():
            newlist = self.runTimeSteps.split()
            return newlist

        if self.runTimeSteps is not None:
            if (self.runTimeSteps != 'None None') & (self.runTimeSteps != 'all') & (self.runTimeSteps == 'None'):
                if type(self.runTimeSteps) is not list:
                    self.runTimeSteps = makeList(self.runTimeSteps)
                elif len(self.runTimeSteps) == 2:
                    df = df[self.runTimeSteps[0]:self.runTimeSteps[1]]
                elif len(self.runTimeSteps) == 1:
                    df = df[:self.runTimeSteps[0]]
                else:
                    df = df[self.runTimeSteps]
        return df
    def truncateAllDates(self):
        for i,df in enumerate(self.fixed):
            df = self.truncateDate(df)
            if len(df) < 1:
                self.fixed.remove(df)
            else:
                self.fixed[i] = df
    # ListOfComponents -> ListOfComponents
    # returns a list of components that are diesel generators (start with 'gen')
    def identifyGenColumns(self, componentList):
        genColumns = []
        for c in componentList:
            if (c[:3].lower() == 'gen') & (c[-1].lower() == 'p'):
                genColumns.append(c)
        return genColumns
    def logBadData(self,folder):
        #write the baddata log
        f = open(os.path.join(folder,"BadDataLog.txt"), "w")
        f.write(str(self.badDataDict))
        f.close()

        return
