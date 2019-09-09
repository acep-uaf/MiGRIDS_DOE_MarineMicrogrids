# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

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

from MiGRIDS.InputHandler import EnvironmentAttributeTypes
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.InputHandler.isInline import isInline
from MiGRIDS.InputHandler.badDictAdd import badDictAdd



# constants
DATETIME = 'DATE'  # the name of the column containing sampling datetime as a numeric
DESCXML = 'Descriptor.xml'  # the suffix of the xml for each component that contains max/min values
TOTALP = 'total_p'  # the name of the column that contains the sum of power output for all components


# dataframe, string, list, list, List/None -> DataClass
# Dataframe is the combined dataframe consisting of all data input (multiple files may have been merged)
# SampleInterval is a list of sample intervals for each input file
# returns a DataClass object with raw and cleaned data and powercomponent information
def fixBadData(df, setupDir, ListOfComponents,runTimeSteps, **kwargs):
   '''returns cleaned dataframe'''
   sender = kwargs.get("sender")

   def broadCastProgress(progress):
       if sender:
           sender.notifyProgress.emit(progress, 'fixing bad values')
   # local functions - not used outside fixBadData
   def checkMinMaxPower(component, dataFrameList, descriptorxml, baddata):
       '''

       :param component: String name of the component tha is being checked
       :param dataFrameList: List of DataFrames, each containing data for the given component
       :param descriptorxml: String path to the descriptor xml file for the specified component
       :param baddata: Dictionary oraganized with reason for replacement as keys and indices (datetimes) of replaced values
       :return: Dictionary of baddata
       '''
       '''change out of bounds values to be within limits'''
       for i, df in enumerate(dataFrameList):
           
            # look up possible min/max
           # if it is a sink, max power is the input, else it is the output
           if getValue(descriptorxml, "type", False) == "sink":
               maxPower = getValue(descriptorxml, "PInMaxPa")
               minPower = getValue(descriptorxml, "POutMaxPa")
           else:
               maxPower = getValue(descriptorxml, "POutMaxPa")
               minPower = getValue(descriptorxml, "PInMaxPa")
           if (maxPower is not None) & (minPower is not None):
               try:
                   over = df[component] > maxPower
    
                   under = df[component] < minPower
                   df[component] = df[component].mask((over | under))
                   if(len(df[component][pd.isnull(df[component])].index.tolist()) > 0):
                       badDictAdd(component, baddata, '1.Exceeds Min/Max',
                               df[component][pd.isnull(df[component])].index.tolist())
                       dataFrameList[i] = df
               except KeyError:
                   print("%s was not found in the dataframe" % component)

       return dataFrameList, baddata

   def getValue(xml, node, convertToFloat = True):
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
   

   # create DataClass object to store raw, fixed, and summery outputs

   data = DataClass(df, runTimeSteps)

  # create a list of power columns
   
   powerColumns = []
   eColumns = []
   loads=[]
   broadCastProgress(1)
   # replace out of bounds component values before we use these data to replace missing data
   for c in ListOfComponents:
       componentName = componentNameFromColumn(c.column_name)
       attribute = attributeFromColumn(c.column_name)
       descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([componentName, DESCXML]))
       #if it has a p attribute it is either a powercomponent or a load and has a min/max value
       if attribute == 'P':
           try:
               descriptorxml = ET.parse(descriptorxmlpath)
               checkMinMaxPower(c.column_name, data.fixed, descriptorxml, data.badDataDict)
               #Power components have a P attribute, but does not include load components
               if componentName[0:4] != 'load':
                   powerColumns.append(c.column_name)
               else:
                   loads.append(c.column_name)
           except FileNotFoundError:
               print('Descriptor xml for %s not found' % c.column_name)
               
       elif attribute in [e.name for e in EnvironmentAttributeTypes.EnvironmentAttributeTypes]:
           eColumns.append(c.column_name)       

   # store the power column list in the DataClass
   data.powerComponents = powerColumns
   data.eColumns = eColumns
   data.loads = loads
   
   # recalculate total_p, data gaps will sum to 0.
   data.totalPower()
  
   #identify groups of missing data
   #totalp is for all power component columns
   #ecolumns and load columns are treated individually
   if len(data.powerComponents) > 0:
       columns = data.eColumns + data.loads + [TOTALP]
   else:
       columns = data.eColumns + data.loads
  
   groupings = data.df[columns].apply(lambda c: isInline(c), axis=0)
   broadCastProgress(4)
   data.setYearBreakdown()

   #replace offline data for total power sources
   if TOTALP in columns:
        
      columnsToReplace= [TOTALP] + data.powerComponents
      #create a dataframe subset of total p column, grouping column and powercomponent columns
      
      #s = data.df[columnsToReplace]
      #replace the column in the dataframe with cleaned up data
      reps = data.fixOfflineData(columnsToReplace,groupings[TOTALP])
      data.df = data.df.drop(reps.columns, axis=1)
      data.df= pd.concat([data.df,reps],axis=1)
   broadCastProgress(6)
   #now e and load columns performed individually
   #nas produced from mismatched file timestamps get ignored during grouping - thus not replaced during fixbaddata

   cnt = len(data.df[data.eColumns + data.loads].columns)
   currentcnt = 1
   for c in data.df[data.eColumns + data.loads].columns:

       reps= data.fixOfflineData([c], groupings[c])
       data.df = data.df.drop(reps.columns, axis=1)
       data.df= pd.concat([data.df,reps],axis=1)
       broadCastProgress(6 + round((currentcnt/cnt) * 4,0))
   broadCastProgress(10)
   #reads the component descriptor files and
   #returns True if none of the components have isFrequencyReference=1 and

   def dieselNeeded(myIterator, setupDir):
       def get_next(myiter):
           try:
               return next(myiter)
           except StopIteration:
               return None

       c = get_next(myIterator)
       if c is None:
           return True

       if c.column_name in data.powerComponents:
           
           descriptorxmlpath = os.path.join(setupDir, '..', 'Components', ''.join([componentNameFromColumn(c.column_name), DESCXML]))
           try:
               descriptorxml = ET.parse(descriptorxmlpath)

               if (descriptorxml.find('isVoltageSource').attrib.get('value') == "1") & \
                         (descriptorxml.find('isFrequencyReference').attrib.get('value') == "TRUE"):
                   return False
               else:
                   return dieselNeeded(myIterator, setupDir)
           except FileNotFoundError:
               return dieselNeeded(myIterator, setupDir)
       return dieselNeeded(myIterator, setupDir)

    # fill diesel columns with a value if the system needs diesel to operate
   componentIterator = iter(ListOfComponents)
   if dieselNeeded(componentIterator,setupDir):
       data.fixGen(powerColumns)
       data.totalPower()
      # scale data based on units and offset in the component xml file
   data.scaleData(ListOfComponents)      
   data.splitDataFrame()

   data.totalPower()
   data.truncateAllDates()
   data.preserve(setupDir)
   data.logBadData(setupDir)
   return data


# supporting functions for fixBadData

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



