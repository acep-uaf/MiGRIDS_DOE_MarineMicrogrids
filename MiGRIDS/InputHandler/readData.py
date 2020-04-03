# Projet: MiGRIDS
# Created by: # Created on: 12/19/2019
# Purpose :  readData
import shlex

import pandas as pd
import os
import importlib.util

from MiGRIDS.InputHandler.readCsv import readCsv
from MiGRIDS.InputHandler.InputFields import *
from MiGRIDS.InputHandler.readWindData import readIndividualWindFile
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.InputHandler.Component import Component

def dir2data(dirDict):
    # instantiate multiprocess

    file_list = getFileList(dirDict)
    dictList = []
    for file in file_list:

        dirDict[FILENAME] = file
        dictList.append(dirDict.copy())

    if dirDict[FILETYPE].lower() == 'csv':
        result = [readCsv(d) for d in dictList]

    elif dirDict[FILETYPE].lower() == 'met':
        result = [readIndividualWindFile(d) for d in dictList]

    print(len(result), "files")
    df = pd.concat(result, axis=0)
    return df

def readInputData_mp(inputDict, **kwargs):
    '''
    cycle through the directories in inputDict[inputfiledir.value], loading the data in each directory into a compbined dataframe
    :param inputDict: A import dictionary as produced from ProjectSqlite.getSetUpInfo
    :return: a single dataframe, and list of component objects
    '''

    completeDFList = []
    completeComponentList = []
    v = shlex.shlex(inputDict[FILEDIR])
    v.whitespace_split = True

    for position, directory in enumerate(list(v)): #lists are space delimited
        print("Reading files from: ",directory)
        dirDict = singleLocation(inputDict, position) #all values are as lists

        df = dir2data(dirDict)

        dirDF, dirComponents = standardize(dirDict,df)
        completeDFList.append(dirDF)
        #add only new components
        completeComponentList.extend([c for c in dirComponents if c.component_name not in [h.component_name for h in completeComponentList]])

    #combine the dataframes from all the directories into 1 dataframe
    completeDF = pd.DataFrame()
    for d in completeDFList:
        if len(set(completeDF.columns).intersection(set(d.columns))): #if the intersect then we are appending to an existing column
            completeDF = pd.concat([completeDF,d],axis=0)
        else: #if there are no common columns then we are adding columns
            completeDF = completeDF.join(d,how="outer")
    completeDF = completeDF.sort_index()
    return completeDF, completeComponentList

def standardize(dirDict, df):
    listOfComponents = []

    if dirDict['componentChannels.' + COMPONENTATTRIBUTE] != None:
        for i in range(len(dirDict[
                               'componentChannels.' + COMPONENTATTRIBUTEUNIT])):  # for each channel make a component object

            # cd to unit conventions file
            dir_path = os.path.dirname(os.path.realpath(__file__))
            unitConventionDir = os.path.join(dir_path, *['..', 'Analyzer', 'UnitConverters'])
            # get the default unit for the data type
            units = readXmlTag('internalUnitDefault.xml',
                               ['unitDefaults', dirDict['componentChannels.' + COMPONENTATTRIBUTE][i]],
                               'units', unitConventionDir)[0]
            # if the units don't match, convert
            if units.lower() != dirDict['componentChannels.' + COMPONENTATTRIBUTEUNIT][i].lower():
                unitConvertDir = os.path.join(dir_path, *['..', 'Analyzer', 'UnitConverters', 'unitConverters.py'])
                funcName = dirDict['componentChannels.' + COMPONENTATTRIBUTEUNIT][i].lower() + '2' + units.lower()
                # load the conversion
                spec = importlib.util.spec_from_file_location(funcName, unitConvertDir)
                uc = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(uc)
                x = getattr(uc, funcName)
                # update data
                df[dirDict['componentChannels.' + COMPONENTNAME][i]] = x(
                    df[dirDict['componentChannels.' + COMPONENTNAME][i]])
            # get the scale and offset
            scale = readXmlTag('internalUnitDefault.xml',
                               ['unitDefaults', dirDict['componentChannels.' + COMPONENTATTRIBUTE][i]],
                               'scale',
                               unitConventionDir)[0]
            offset = readXmlTag('internalUnitDefault.xml',
                                ['unitDefaults', dirDict['componentChannels.' + COMPONENTATTRIBUTE][i]],
                                'offset',
                                unitConventionDir)[0]

            df[(dirDict['componentChannels.' + COMPONENTNAME][i] +
               dirDict['componentChannels.' + COMPONENTATTRIBUTE][i])] = df[(dirDict['componentChannels.' + COMPONENTNAME][i] +
               dirDict['componentChannels.' + COMPONENTATTRIBUTE][i])] * int(scale) + int(offset)
            # get the desired data type and convert
            datatype = readXmlTag('internalUnitDefault.xml',
                                  ['unitDefaults', dirDict['componentChannels.' + COMPONENTATTRIBUTE][i]],
                                  'datatype',
                                  unitConventionDir)[0]
            df[(dirDict['componentChannels.' + COMPONENTNAME][i] +
                dirDict['componentChannels.' + COMPONENTATTRIBUTE][i])] = df[(
                        dirDict['componentChannels.' + COMPONENTNAME][i] +
                        dirDict['componentChannels.' + COMPONENTATTRIBUTE][i])].astype(datatype)
            listOfComponents.append(Component(
                component_name=dirDict['componentChannels.' + COMPONENTNAME][i],
                column_name=dirDict['componentChannels.' + COMPONENTNAME][i] + dirDict['componentChannels.' + COMPONENTATTRIBUTE][i],
                units=units, scale=scale,
                offset=offset, datatype=datatype,
                attribute=dirDict['componentChannels.' + COMPONENTATTRIBUTE][i]))

    return df, listOfComponents

def getFileList(dirDict):
    # get just the filenames ending with fileType. check for both upper and lower case
    # met files are text.
     fileType = dirDict[FILETYPE].replace('MET','txt')
     dir = dirDict[FILEDIR]
     files = [f for f in os.listdir(dir) if
                                            os.path.isfile(os.path.join(dir, f)) & (
                                                        f.endswith(fileType.lower()) or f.endswith(fileType))]
     return files

def singleLocation(dict, position):
    '''returns a dictionary that is a subset of the input dictionary with all the keys but only values at a specified position'''
    singleValueDict={}

    for key, val in dict.items():
        if isinstance(val,list):
            singleValueDict[key] = val
        else:
            v = shlex.shlex(str(val))
            v.whitespace_split = True
            val = list(v)
            if 'componentChannels' in key: #only component attributes can have a list of values
                try:
                    singleValueDict[key]=[val[position]]
                except IndexError:
                    singleValueDict[key] =[val[0]]
            else:
                try:
                    singleValueDict[key] = val[position]
                except IndexError:
                    singleValueDict[key] = val[0] #not a list


    return singleValueDict