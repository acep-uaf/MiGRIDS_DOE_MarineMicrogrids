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
from MiGRIDS.InputHandler.getSetupInformation import setupToDictionary, getSetupInformation
from MiGRIDS.InputHandler.readData import readInputData
from MiGRIDS.InputHandler.readSetupFile import readSetupFile
import pandas as pd


def modifyForManualInput(inputDictionary):
    def keys_swap(orig_key, new_key, d):
        d[new_key] = d.pop(orig_key)
        return d

    d = keys_swap('headerName.value', 'componentChannels.headerName.value', inputDictionary)
    d = keys_swap('componentName.value', 'componentChannels.componentName.value', d)
    d = keys_swap('componentAttribute.value', 'componentChannels.componentAttribute.value', d)
    d = keys_swap('componentAttribute.unit', 'componentChannels.componentAttribute.unit', d)
    return d


if __name__ == '__main__':
    #specify the correct path to your project setup file here
    fileName = os.path.join(os.getcwd(),*['..','MiGRIDSProjects','Cordova','InputData','Setup','CordovaSetup.xml'])
    setupFolder = os.path.join(os.getcwd(),*['..','MiGRIDSProjects','Cordova','InputData','Setup'])
    # get the setup Directory

    soup = getSetupInformation(fileName)
    inputDictionary = setupToDictionary(soup,fileName)
    inputDictionary = modifyForManualInput(inputDictionary)
    # read time series data, combine with wind data if files are seperate.
    # updates are performed by the sender

    df, listOfComponents = readInputData(inputDictionary)

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

    data = fixBadData(data, setupFolder)
    #setup intervals
    data = fixDataInterval(data, pd.to_timedelta(int(inputDictionary['timeStep.value']), unit=inputDictionary['timeStep.unit']))
    data.preserve(setupFolder)

    # now convert to a netcdf
    #components get passed as s dictionrary with their attributes
    componentDict = {}
    for c in listOfComponents:
        componentDict[c.column_name] = c.toDictionary()

    dataframe2netcdf(data.fixed[0], componentDict,os.path.join(setupFolder,*['..','TimeSeriesData','ProcessedData'] ))
