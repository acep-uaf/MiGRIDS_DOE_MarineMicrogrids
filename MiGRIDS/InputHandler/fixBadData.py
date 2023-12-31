# Projet: MiGRIDS
# Created by: T.Morgan# Created on: 1/23/2018
# reads dataframe of data input compares values to descriptor xmls and returns a clean dataframe from a DataClass object
# Out of bounds values for each component are replaced first, followed by datagaps and periods of inline data.
# assumes df column headings match header values in setup.xml
# assumes columns names ending in 'P' are power output components
# assumes data is ordered by time ascending and index increases with time
# a log of data that has been replaced will be generated in the TimeSeriesData folder


import xml.etree.ElementTree as ET
import os
import re
import pandas as pd
import numpy as np

from MiGRIDS.InputHandler import EnvironmentAttributeTypes
from MiGRIDS.InputHandler.Exceptions.DataValidationError import DataValidationError
from MiGRIDS.InputHandler.isInline import isInline
from MiGRIDS.InputHandler.badDictAdd import badDictAdd

# constants
DATETIME = 'DATE'  # the name of the column containing sampling datetime as a numeric
TOTALL = 'total_load'
DESCXML = 'Descriptor.xml'  # the suffix of the xml for each component that contains max/min values
TOTALP = 'total_power'  # the name of the column that contains the sum of power output for all components


# dataframe, string, list, list, List/None -> DataClass
# Dataframe is the combined dataframe consisting of all data input (multiple files may have been merged)
# SampleInterval is a list of sample intervals for each input file
# returns a DataClass object with raw and cleaned data and powercomponent information
def fixBadData(data, setupDir, **kwargs):
   '''returns cleaned data Object'''
   if (kwargs.get("flexibleYear")) != None:
       if (kwargs.get("flexibleYear")) & ((data.df.index[-1] - data.df.index[0]) > pd.to_timedelta('365 d')):
           data.df = reallignSingleYear(data.df)

   #look for obvious over and under values
   data.df, data.baddict = checkPowerComponents([c for c in data.components if c in [data.powerComponents + data.loads]],setupDir,data.df,data.badDataDict)
   #over/under values now are nas
   # calculate totals, data gaps will sum to 0.
   data.totalPower()
   data.totalLoad()
  
   #identify groups of missing data
   #totalp is for all power component columns
   #ecolumns and load columns are treated individually
   if (len(data.powerComponents)>0) & (len(data.loads) > 0):
      #columns = data.ecolumns + [TOTALL] + [TOTALP]
      columns = [TOTALL] + [TOTALP]
   elif (len(data.powerComponents) > 0) & (len(data.loads) == 0):
       #columns = data.ecolumns + [TOTALP]
       columns = [TOTALP]
   elif (len(data.powerComponents) == 0) & (len(data.loads) > 0):
       #columns = data.ecolumns + [TOTALL]
        columns = [TOTALL]

   groupings = data.df[columns].apply(lambda c: isInline(c), axis=0)
   #set the yearsplits attribute for the data class
   data.setYearBreakdown()

   #replace the column in the dataframe with clean data
   try:
       if len(data.powerComponents)>0:
           columnsToReplace = [TOTALP] + data.powerComponents
           reps = data.fixOfflineData(TOTALP,columnsToReplace,groupings[TOTALP])
           data.df = data.df.drop(reps.columns, axis=1)
           data.df= reps.join(data.df, how='outer')
   except KeyError as e:
       raise DataValidationError(1) #validation error 1 is missing power

   try:
       if len(data.loads) > 0:
           columnsToReplace=[TOTALL] + data.loads
           # replace the column in the dataframe with cleaned up data
           reps = data.fixOfflineData(TOTALL,columnsToReplace, groupings[TOTALL])
           data.df = data.df.drop(reps.columns, axis=1)
           data.df = pd.concat([reps,data.df],join='outer',axis=1)
   except KeyError as e:
       raise DataValidationError(2) #validation error 2 is missing load

   #now e columns performed individually
   #nas produced from mismatched file timestamps get ignored during grouping - thus not replaced during fixbaddata
   # for c in data.df[data.ecolumns].columns:
   #     reps= data.fixOfflineData(c,[c], groupings[c]) #TODO this needs to follow a different fixing path
   #     data.df = data.df.drop(reps.columns, axis=1) #drop the columns we are going to replace
   #     data.df = reps.join(data.df, how='outer') #add the replacement columns back in

   # fill gen columns with a value if the system needs diesel to operate
   componentIterator = iter(data.components)
   if dieselNeeded(componentIterator,setupDir,data.powerComponents):
       data.fixGen(data.powerComponents)
       data.totalPower()

   data.df = data.dropEmpties(data.df,columns) #this drops rows of all na
   data.df = data.df.sort_index()
   data.totalPower()  # recalculate total power in case na's popped up
   data.totalLoad()
   data.dropUnused()
   # scale data based on units and offset in the component xml file
   data.scaleData(data.components)
   data.splitDataFrame(columns) #this sets data.fixed to a list of dataframes if times are not consecutive
   data.truncateAllDates()
   data.preserve(setupDir) #keep a copy of the fixed data in case we want to inspect or start over
   data.logBadData(setupDir) #write our baddata file
   return data

def reallignSingleYear(df):
    '''identifies the temporal range that has data for all columns
    Not all rows need to have data, but there must be data in all columns within a 2 week temporal window - which is the maximum
    gap size allowed for data replacement.'''

    doy = df.index.dayofyear

    startYear = df.index[0].year
    date = (np.asarray(startYear, dtype='datetime64[Y]') - 1970) + (np.asarray(doy, dtype='timedelta64[D]') - 1)
    dt = pd.Series(date) + pd.to_timedelta(df.index.hour * 3600 + df.index.minute * 60 + df.index.second, unit='s')
    df.index = dt
    newdf = pd.DataFrame(index=dt)
    newdf.index = newdf.index.drop_duplicates(keep='first')
    for c in df.columns:
        s = df.loc[pd.notnull(df[c]),c]
        s.index = s.index.drop_duplicates(keep='first')
        newdf = newdf.join(s,how="left")
    return newdf

def fillComponentTypeLists(ListOfComponents):
    '''
    :param ListOfComponents: List of component objects
    :return:
    '''
    powerColumns = []
    eColumns = []
    loads = []
    # replace out of bounds component values before we use these data to replace missing data
    for c in ListOfComponents:
    # if it has a p attribute it is either a powercomponent or a load and has a min/max value
        if c.attribute == 'P':
            # Power components have a P attribute, but does not include load components
            if c.component_name[0:4] != 'load':  #TODO move away from assumption of component names
                powerColumns.append(c.column_name)
            else:
                loads.append(c.column_name)
        elif c.attribute in [e.name for e in EnvironmentAttributeTypes.EnvironmentAttributeTypes]:
            eColumns.append(c.column_name)

    #return the list of column names by component types
    return eColumns, loads, powerColumns

def checkPowerComponents(components, setupDir, df,badDict):
    for c in components:
        try:
            descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([c.component_name, DESCXML]))
            descriptorxml = ET.parse(descriptorxmlpath)
            df,badDict = checkMinMaxPower(c.column_name, df, descriptorxml,badDict)

        except FileNotFoundError:
            print('Descriptor xml for %s not found' % c.column_name)
    return df, badDict

# supporting functions for fixBadData
def minMaxValid(min,max):
   try:
     if min >= max:
        return False
     if (min is None)|(max is None):
         return False
   except:
       return False
   return True
# reads the component descriptor files and
# returns True if none of the components have isFrequencyReference=True and isVoltageSource =True
def dieselNeeded(myIterator, setupDir,powerComponents):
   def get_next(myiter):
       try:
           return next(myiter)
       except StopIteration:
           return None

   c = get_next(myIterator)
   if c is None:
       return True

   if c.column_name in powerComponents:
        #TODO path should be from lookup not hardcoded
       descriptorxmlpath = os.path.join(setupDir, '..', 'Components',
                                        ''.join([componentNameFromColumn(c.column_name), DESCXML]))
       try:
           descriptorxml = ET.parse(descriptorxmlpath)

           if (descriptorxml.find('isVoltageSource').attrib.get('value') == "TRUE") & \
                   (descriptorxml.find('isFrequencyReference').attrib.get('value') == "TRUE"):
               return False
           else:
               return dieselNeeded(myIterator, setupDir,powerComponents)
       except FileNotFoundError:
           return dieselNeeded(myIterator, setupDir)
   return dieselNeeded(myIterator, setupDir,powerComponents)

def attributeFromColumn(columnHeading):
    match = re.match(r"([a-z]+)([0-9]+)([A-Z]+)", columnHeading, re.I)
    if match:
        attribute = match.group(3)
        return attribute
    return

def componentNameFromColumn(columnHeading):
    match = re.match(r"([a-z]+)([0-9]+)", columnHeading, re.I)
    if match:
        name = match.group()
        return name 
    return

    # local functions - not used outside fixBadData

def checkMinMaxPower(component, df, descriptorxml, baddata):
    '''

    :param component: String name of the component tha is being checked
    :param dataFrameList: List of DataFrames, each containing data for the given component
    :param descriptorxml: String path to the descriptor xml file for the specified component
    :param baddata: Dictionary oraganized with reason for replacement as keys and indices (datetimes) of replaced values
    :return: Dictionary of baddata
    '''
    '''change out of bounds values to be within limits'''

    def getValue(xml, node, convertToFloat=True):
        '''
        Retrieves a specified value from a specified XML file
        :param xml: XML object
        :param node: String node to find
        :param convertToFloat: Boolean whether or not the value should be a float
        :return: The value retrieved from the xml file
        '''
        '''returns the value at a specified noede within an xml file'''
        if xml.find(node) is not None:
            value = xml.find(node).attrib.get('value')
            if convertToFloat is True:
                value = float(value)
        else:
            value = 0
        return value

    # look up possible min/max
    # if it is a sink, max power is the input, else it is the output
    if getValue(descriptorxml, "type", False) == "sink":
        maxPower = getValue(descriptorxml, "PInMaxPa")
        minPower = getValue(descriptorxml, "POutMaxPa")
    else:
        maxPower = getValue(descriptorxml, "POutMaxPa")
        minPower = getValue(descriptorxml, "PInMaxPa")
    if minMaxValid(minPower, maxPower):
        try:
            over = df[component.column_name] > maxPower

            under = df[component.column_name] < minPower
            df[component.column_name] = df[component.column_name].mask((over | under))
            if (len(df[component.column_name][pd.isnull(df[component.column_name])].index.tolist()) > 0):
                badDictAdd(component.column_name, baddata, '3.Exceeds Min/Max',
                           df.loc[pd.isnull(df[component.column_name])].index.tolist())
                df.loc[pd.isnull(df[component.column_name]), component.column_name + '_flag'] = 3

        except KeyError:
            print("%s was not found in the dataframe" % component.column_name)
    else:
        print("valid min/max values were not found for %s" % component.component_name)
    return df, baddata


