# Projet: MiGRIDS
# Created by: T.Morgan # Created on: 9/25/2019
import os
import pandas as pd
from MiGRIDS.Controller.UIHandler import UIHandler
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.InputHandler.InputFields import *
from MiGRIDS.InputHandler.buildProjectSetup import buildProjectSetup
from MiGRIDS.InputHandler.fillProjectData import fillProjectData
from MiGRIDS.InputHandler.fixBadData import fillComponentTypeLists
from MiGRIDS.InputHandler.readData import readInputData_mp
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor

class SetupHandler(UIHandler):
    """
    Description: Provides methods for reading, writing, and passing main project setup information.
    Attributes: dbhandler (passed during init)
    """

    def __init__(self,dbhandler):
        super().__init__(dbhandler)
        return

    def makeSetup(self, project, setupFolder):
        '''
        write databae infomration to a setup xml
        create a mostly blank xml setup file, componentNames is a SetupTag class so we need the value
        :return: path to the setup xml file that was written
        '''

        #components are all possible components
        components = self.dbhandler.getComponentNames()
        setupXML = buildProjectSetup(project, setupFolder,components)
        #fill in project data into the setup xml and create descriptor xmls if they don't exist
        fillProjectData()
        return setupXML

    def writeComponentSoup(self, component, soup):
        '''
        Create a component xml file based on the provided component soup object
        :param component: String name of the component
        :param soup: Beautiful soup object of tags and values to wriete
        :return: None
        '''

        #soup is an optional argument, without it a template xml will be created.
        fileDir = getFilePath('Components',projectFolder=self.dbhandler.getProjectPath())
        createComponentDescriptor(component, fileDir, soup)
        return

    def removeDescriptor(self, componentName, componentDir):
        '''Remove a descriptor xml file from a specified directory
        @:param: componentName is string name of the component
        @:param: componentDir is string path containing component xml file.'''
        if os.path.exists(os.path.join(componentDir, componentName + 'Descriptor.xml')):
            os.remove(os.path.join(componentDir, componentName + 'Descriptor.xml'))
        return

    def createCleanedData(self):
        ''' calls input handler functions to create a clean dataset that can be used to produce input files for modeling.
        Input information is pulled from the project_manager database'''
        from MiGRIDS.InputHandler.fixBadData import fixBadData
        from MiGRIDS.InputHandler.fixDataInterval import fixDataInterval

        inputDictionary = self.dbhandler.getSetUpInfo()

        # read time series data, combine with wind data if files are seperate.
        #updates are performed by the sender
        self.sender.update(1, 'Reading data')  # second update
        df, listOfComponents = readInputData_mp(inputDictionary, sender = self.sender)

        # check the timespan of the dataset. If its more than 1 year look for limiting dates
        minDate = min(df.index)
        maxDate = max(df.index)
        limiters = inputDictionary[RUNTIMESTEPS]

        if ((maxDate - minDate) > pd.Timedelta(days=365)) & ((limiters == ['all']) | (limiters == 'None None')):
            newdates = self.DatesDialog(minDate, maxDate)
            m = newdates.exec_()
            if m == 1:

                inputDictionary[RUNTIMESTEPS] = [pd.to_datetime(newdates.startDate.text()),
                                                   pd.to_datetime(newdates.endDate.text())]

        self.sender.update(3, 'Fixing bad values')
        # now fix the bad data
        #fixBad Data takes a DataClass object as input so create one
        # create DataClass object to store raw, fixed, and summery outputs
        data = DataClass(df, inputDictionary[RUNTIMESTEPS])

        # parse data columns by type
        eColumns, loads, powerColumns = fillComponentTypeLists(listOfComponents)
        data.powerComponents = powerColumns
        data.ecolumns = eColumns
        data.loads = loads
        data= fixBadData(data, getFilePath('Setup',projectFolder=self.dbhandler.getProjectPath()),inputDictionary['runTimeSteps.value'],
                              sender=self.sender) #can update up to 2 counts on progress bar
        self.sender.update(3, 'Fixing intervals')
        # fix the intervals
        print('fixing data timestamp intervals to %s %s' % (inputDictionary[TIMESTEP],inputDictionary[TIMESTEPUNIT]))
        #can update upto 2 counts on progress bar
        data = fixDataInterval(data, pd.to_timedelta(inputDictionary[TIMESTEP], unit = inputDictionary[TIMESTEPUNIT]), sender=self.sender)
        data.preserve(getFilePath('Setup',projectFolder=self.dbhandler.getProjectPath()))
        self.sender.update(10, 'done') #the process is complete
        return data, listOfComponents

    def createNetCDF(self, lodf, componentDict, setupFolder):
        '''
        Create netcdf file from a list of dataframes return a list of netcdf files created.
        Netcdfs for components in the largest of the listed dataframes is are returned. No netcdfs for smaller dataframes are retained.
        :param lodf: List of DataFrames with time indices and column names that match the componentDict keys
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

