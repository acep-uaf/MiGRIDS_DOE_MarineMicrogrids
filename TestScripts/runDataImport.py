# Author: T. Morgan
# Date: January 19 2020


# The goal of runDataImport is to take data from the user, check it for bad or missing data, and save it in a standard
# netcdf format

# this is run after the project files have been initiated (initiateProject.py) and filled (fillProjectData.py)

# get input data to run the functions to import data into the project
# each step should be run individually to evaluate expected outcomes
import os
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.InputHandler.fixBadData import fixBadData, fillComponentTypeLists
from MiGRIDS.InputHandler.fixDataInterval import fixDataInterval
from MiGRIDS.InputHandler.dataframe2netcdf import dataframe2netcdf
from MiGRIDS.InputHandler.readData import readInputData_mp
from MiGRIDS.InputHandler.readSetupFile import readSetupFile
import pandas as pd

#specify the correct path to your project setup file here
fileName = os.path.join(os.getcwd(),*['..','MiGRIDSProjects','SampleProject','InputData','Setup','SampleProjectSetup.xml'])
setupFolder = os.path.join(os.getcwd(),*['..','MiGRIDSProjects','SampleProject','InputData','Setup'])
# get the setup Directory

inputDictionary = readSetupFile(fileName)


# read time series data, combine with wind data if files are seperate.
# updates are performed by the sender

df, listOfComponents = readInputData_mp(inputDictionary)

# check the timespan of the dataset. If its more than 1 year the dataset should have runTimesteps set
minDate = min(df.index)
maxDate = max(df.index)

# now fix the bad data
# fixBad Data takes a DataClass object as input so create one
# create DataClass object to store raw, fixed, and summery outputs
data = DataClass(df, inputDictionary['runTimeSteps.value'])
data.components = listOfComponents #list of component objects created during the import
# parse data columns by type
eColumns, loads, powerColumns = fillComponentTypeLists(listOfComponents) #assign the key data types in the dataset
data.powerComponents = powerColumns
data.ecolumns = eColumns
data.loads = loads

data = fixBadData(data, setupFolder,
                  inputDictionary['runTimeSteps.value'])
#setup intervals
data = fixDataInterval(data, pd.to_timedelta(inputDictionary['timestep.value'], unit=inputDictionary['timestep.unit']))
data.preserve(setupFolder)

# now convert to a netcdf
#components get passed as s dictionrary with their attributes
componentDict = {}
for c in listOfComponents:
    componentDict[c.column_name] = c.toDictionary()

dataframe2netcdf(data.fixed[0], componentDict,os.path.join(setupFolder,*['..','TimeSeriesData','ProcessedData'] ))

