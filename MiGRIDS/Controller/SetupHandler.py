# Projet: MiGRIDS
# Created by: T.Morgan # Created on: 9/25/2019
import os
import pickle
import pandas as pd
from MiGRIDS.Controller.UIHandler import UIHandler
from MiGRIDS.InputHandler.buildProjectSetup import buildProjectSetup
from MiGRIDS.InputHandler.fillProjectData import fillProjectData
from MiGRIDS.InputHandler.readData import readInputData_mp
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
        setupXML = buildProjectSetup(project, setupFolder,components)
        #fill in project data into the setup xml and create descriptor xmls if they don't exist
        fillProjectData()
        return setupXML

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

    def createCleanedData(self):

        from MiGRIDS.InputHandler.getUnits import getUnits
        from MiGRIDS.InputHandler.fixBadData import fixBadData
        from MiGRIDS.InputHandler.fixDataInterval import fixDataInterval

        inputDictionary = self.dbhandler.getSetUpInfo()

        # read time series data, combine with wind data if files are seperate.
        # Pass sender to mergeInputs so it can send signals back to progress bar
        #sender can update upto 2
        df, listOfComponents = readInputData_mp(inputDictionary, sender = self.sender)


        # check the timespan of the dataset. If its more than 1 year ask for / look for limiting dates
        minDate = min(df.index)
        maxDate = max(df.index)
        limiters = inputDictionary['runTimeSteps.value']

        if ((maxDate - minDate) > pd.Timedelta(days=365)) & ((limiters == ['all']) | (limiters == 'None None')):
            newdates = self.DatesDialog(minDate, maxDate)
            m = newdates.exec_()
            if m == 1:

                inputDictionary['runTimeSteps.value'] = [pd.to_datetime(newdates.startDate.text()),
                                                   pd.to_datetime(newdates.endDate.text())]

        self.sender.update(2, 'fixing bad values') #second update
        # now fix the bad data
        df_fixed = fixBadData(df, getFilePath('Setup',projectFolder=self.dbhandler.getProjectPath()), listOfComponents, inputDictionary['runTimeSteps.value'],
                              sender=self.sender) #can update up to 2 counts on progress bar
        self.sender.update(2, 'fixing intervals')
        # fix the intervals
        print('fixing data timestamp intervals to %s' % inputDictionary['timeStep.value'])
        #can update upto 2 counts on progress bar
        df_fixed_interval = fixDataInterval(df_fixed, pd.to_timedelta(inputDictionary['timeStep.value'], unit = inputDictionary['timeStep.unit']), sender=self.sender)
        df_fixed_interval.preserve(getFilePath('Setup',projectFolder=self.dbhandler.getProjectPath))
        self.sender.update(10, 'done') #the process is complete
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
