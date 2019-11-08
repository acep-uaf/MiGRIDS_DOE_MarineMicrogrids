# Projet: MiGRIDS
# Created by: # Created on: 9/25/2019
import os
import pickle

import pandas as pd
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Controller.UIToInputHandler import UIHandler
from MiGRIDS.InputHandler.buildProjectSetup import buildProjectSetup
from MiGRIDS.InputHandler.fillProjectData import fillProjectData
from MiGRIDS.InputHandler.makeSoup import makeComponentSoup
from MiGRIDS.InputHandler.mergeInputs import mergeInputs
from MiGRIDS.UserInterface.getFilePaths import getFilePath


class SetupHandler(UIHandler):
    """
    Description: Provides methods for reading, writing, and passing main project setup information.
    Attributes: 
        
        
    """

    def __init__(self):
        super().__init__()
        return

    def makeSetup(self):
       # write the information to a setup xml
        # create a mostly blank xml setup file, componentNames is a SetupTag class so we need the value

        project = self.dbhandler.getProject()
        setupFolder = os.path.join(os.path.dirname(__file__), *['..','..','MiGRIDSProjects', project, 'InputData','Setup'])
        #components are all possible components
        components = self.dbhandler.getComponentNames()
        buildProjectSetup(project, setupFolder,components)
        #fill in project data into the setup xml and create descriptor xmls if they don't exist
        fillProjectData()
        return

    def writeComponentSoup(self, component, soup):
        from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor

        #soup is an optional argument, without it a template xml will be created.
        fileDir = getFilePath('Components',projectFolder=self.dbHandler.getProjectPath())
        createComponentDescriptor(component, fileDir, soup)
        return

    def removeDescriptor(self, componentName, componentDir):
        if os.path.exists(os.path.join(componentDir, componentName + 'Descriptor.xml')):
            os.remove(os.path.join(componentDir, componentName + 'Descriptor.xml'))
        return

    def createCleanedData(self, setupFile):

        from MiGRIDS.InputHandler.getUnits import getUnits
        from MiGRIDS.InputHandler.fixBadData import fixBadData
        from MiGRIDS.InputHandler.fixDataInterval import fixDataInterval

        inputDictionary = {}
        Village = readXmlTag(setupFile, 'project', 'name')[0]
        # input specification

        # input a list of subdirectories under the Projects directory
        fileLocation = readXmlTag(setupFile, 'inputFileDir', 'value')
        inputDictionary['fileLocation'] = fileLocation
        # file type
        fileType = readXmlTag(setupFile, 'inputFileType', 'value')
        outputInterval = readXmlTag(setupFile, 'timeStep', 'value') + \
                         readXmlTag(setupFile, 'timeStep', 'unit')
        inputInterval = readXmlTag(setupFile, 'inputTimeStep', 'value') + \
                        readXmlTag(setupFile, 'inputTimeStep', 'unit')
        inputDictionary['timeZone'] = readXmlTag(setupFile, 'timeZone', 'value')
        inputDictionary['fileType'] = readXmlTag(setupFile, 'inputFileType', 'value')
        inputDictionary['outputInterval'] = readXmlTag(setupFile, 'timeStep', 'value')
        inputDictionary['outputIntervalUnit'] = readXmlTag(setupFile, 'timeStep', 'unit')
        inputDictionary['inputInterval'] = readXmlTag(setupFile, 'inputTimeStep', 'value')
        inputDictionary['inputIntervalUnit'] = readXmlTag(setupFile, 'inputTimeStep', 'unit')
        inputDictionary['runTimeSteps'] = readXmlTag(setupFile, 'runTimeSteps', 'value')
        # get date and time values
        inputDictionary['dateColumnName'] = readXmlTag(setupFile, 'dateChannel', 'value')
        inputDictionary['dateColumnFormat'] = readXmlTag(setupFile, 'dateChannel', 'format')
        inputDictionary['timeColumnName'] = readXmlTag(setupFile, 'timeChannel', 'value')
        inputDictionary['timeColumnFormat'] = readXmlTag(setupFile, 'timeChannel', 'format')
        inputDictionary['utcOffsetValue'] = readXmlTag(setupFile, 'inputUTCOffset', 'value')
        inputDictionary['utcOffsetUnit'] = readXmlTag(setupFile, 'inputUTCOffset', 'unit')
        inputDictionary['dst'] = readXmlTag(setupFile, 'inputDST', 'value')
        flexibleYear = readXmlTag(setupFile, 'flexibleYear', 'value')
        inputDictionary['flexibleYear'] = [(x.lower() == 'true') | (x.lower() == 't') for x in flexibleYear]

        # combine values with their units as a string
        for idx in range(len(inputDictionary['outputInterval'])):  # there should only be one output interval specified
            if len(inputDictionary['outputInterval']) > 1:
                inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][idx]
            else:
                inputDictionary['outputInterval'][idx] += inputDictionary['outputIntervalUnit'][0]

        for idx in range(len(inputDictionary['inputInterval'])):  # for each group of input files
            if len(inputDictionary['inputIntervalUnit']) > 1:
                inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][idx]
            else:
                inputDictionary['inputInterval'][idx] += inputDictionary['inputIntervalUnit'][0]

        # get data units and header names
        inputDictionary['columnNames'], inputDictionary['componentUnits'], \
        inputDictionary['componentAttributes'], inputDictionary['componentNames'], inputDictionary[
            'useNames'] = getUnits(Village, os.path.dirname(setupFile))

        # read time series data, combine with wind data if files are seperate.
        # Pass our sendet to mergeInputs so it can send signals
        df, listOfComponents = mergeInputs(inputDictionary, sender=self.sender)

        # check the timespan of the dataset. If its more than 1 year ask for / look for limiting dates
        minDate = min(df.index)
        maxDate = max(df.index)
        limiters = inputDictionary['runTimeSteps']

        if ((maxDate - minDate) > pd.Timedelta(days=365)) & (limiters == ['all']):
            newdates = self.DatesDialog(minDate, maxDate)
            m = newdates.exec_()
            if m == 1:
                # inputDictionary['runTimeSteps'] = [newdates.startDate.text(),newdates.endDate.text()]
                inputDictionary['runTimeSteps'] = [pd.to_datetime(newdates.startDate.text()),
                                                   pd.to_datetime(newdates.endDate.text())]
                # TODO write to the setup file so can be archived
        self.sender.update(0, 'fixing bad values')
        # now fix the bad data
        df_fixed = fixBadData(df, os.path.dirname(setupFile), listOfComponents, inputDictionary['runTimeSteps'],
                              sender=self.sender)
        self.sender.update(0, 'fixing intervals')
        # fix the intervals
        print('fixing data timestamp intervals to %s' % inputDictionary['outputInterval'])
        df_fixed_interval = fixDataInterval(df_fixed, inputDictionary['outputInterval'], sender=self.sender)
        df_fixed_interval.preserve(os.path.dirname(setupFile))

        return df_fixed_interval, listOfComponents

    def createNetCDF(self, lodf, componentDict, setupFolder):
        '''
        Create netcdf file from a list of dataframes return a list of netcdf files created
        :param lodf: List of DataFrames with time indices and column names that match the componentDict
        :param componentDict: a dictionary of component attributes, including column names
        :param setupFolder: The folder path containing the projects setup.xml file
        :return: List of Strings naming the netcdf files created.
        '''
        from MiGRIDS.InputHandler.dataframe2netcdf import dataframe2netcdf
        outputDirectory = getFilePath('Processed', setupFolder=setupFolder)
        netCDFList = []
        # if there isn't an output directory make one
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        # only the largest dataframe is kept
        largest = 0
        for i, df in enumerate(lodf):
            if len(df) > largest:
                netCDFList = dataframe2netcdf(df, componentDict, outputDirectory)
                largest = len(df)
        return netCDFList

    def storeComponents(self, ListOfComponents, setupFile):
        outputDirectory = os.path.dirname(setupFile)

        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'components.pkl')
        file = open(outfile, 'wb')
        pickle.dump(ListOfComponents, file)
        file.close()
        return

    def storeData(self, df, setupFile):

        outputDirectory = getFilePath(os.path.dirname(setupFile), 'Processed')
        print("processed data saved to %s: " % outputDirectory)
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'processed_input_file.pkl')
        file = open(outfile, 'wb')
        pickle.dump(df, file)
        file.close()
        return
