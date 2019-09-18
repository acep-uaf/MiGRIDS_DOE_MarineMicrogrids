#Is called from the UserInterface package to initiate xml file generation through the InputHandler functions
#ModelSetupInformation ->

import os
import pickle
import pandas as pd
from PyQt5 import QtWidgets,QtCore
from bs4 import BeautifulSoup

from PyQt5 import QtWidgets

from MiGRIDS.InputHandler.getSetupInformation import setupToDictionary
from MiGRIDS.Model.Operational.generateRuns import generateRuns
from MiGRIDS.UserInterface.makeAttributeXML import makeAttributeXML, writeAttributeXML
from MiGRIDS.Model.Operational.runSimulation import runSimulation
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Controller.GenericSender import GenericSender
from MiGRIDS.InputHandler.buildProjectSetup import buildProjectSetup
from MiGRIDS.InputHandler.fillProjectData import fillProjectData
from MiGRIDS.InputHandler.makeSoup import makeComponentSoup
from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag
from MiGRIDS.InputHandler.mergeInputs import mergeInputs
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeAttributeXML import makeAttributeXML
from MiGRIDS.InputHandler.getSetupInformation import getSetupInformation


class UIToHandler():
    def __init__(self):
        self.sender = GenericSender() #used to send signals to pyqt objects
        self.dbhandler = ProjectSQLiteHandler()

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


    def makeComponentDescriptor(self, component,componentDir):
        '''
        calls makecomponentSoup to write a default desciptor xml file for a component.
        :param component: [String] the name of a component with the format [type][#][attribute]
        :param componentDir: [String] the directory the descriptor xml file will be saved to
        :return: [BeautifulSoup] of tags and values associated with a component type
        '''
         #returns either a template soup or filled soup
        componentSoup = makeComponentSoup(component, componentDir)
        return componentSoup


    def writeComponentSoup(self, component, soup):
        from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor
        dbHandler=ProjectSQLiteHandler()
        #soup is an optional argument, without it a template xml will be created.
        fileDir = getFilePath('Components',projectFolder=dbHandler.getProjectPath())
        createComponentDescriptor(component, fileDir, soup)
        return

    def writeSoup(self,soup,file):
        f = open(file, "w")
        f.write(soup.prettify())
        f.close()

    def writeTag(self,file,tag,value):
        def splitAttribute(tag):
            a = tag.split(".")[len(tag.split(".")) -1]
            tag =  tag.split(".")[len(tag.split(".")) -2]
            return tag,a
        tag, a = splitAttribute(tag)

        writeXmlTag(file, tag, a, value)

    #fill a single tag for an existing component descriptor file
    #dictionary, string -> None
    def updateComponentDiscriptor(self, componentDict, tag):

        value = componentDict[tag]
        self.writeTag(componentDict['component_name'] + 'Descriptor.xml', tag + ".value", value)
        return

    #delete a descriptor xml from the project component folder
    #String, String -> None
    def removeDescriptor(self,componentName, componentDir):
        if os.path.exists(os.path.join(componentDir,componentName + 'Descriptor.xml')):
             os.remove(os.path.join(componentDir,componentName + 'Descriptor.xml'))
        return

    #return a list of component descriptor files in a component directory
    #String -> List
    def findDescriptors(self,componentDir):
        directories = []
        for file in os.listdir(componentDir):
            if file.endswith('.xml'):

                directories.append(file)
        return directories


    def copyDescriptor(self,descriptorFile, componentDir, sqlRecord):
        '''
        Copy an existing xml template in the resource folder to the project directory and write contents to component table in projet_manager
         database
        :param descriptorFile: [String] the name of the descriptor xml file to write
        :param componentDir: [String] the file path to the project component directory
        :param sqlRecord: The table record to write values to
        :return: sqlRecord
        '''
        import shutil

        fileName =os.path.basename(descriptorFile)

        componentName = fileName[:-14]
        # copy the xml to the project folder
        try:
            shutil.copy2(descriptorFile, componentDir)
        except shutil.SameFileError:
            print('This descriptor file already exists in this project')

        #get the soup and write the xml
        soup = self.makeComponentDescriptor(componentName,componentDir)
        sqlRecord = self.updateDescriptor(soup, sqlRecord)
        return sqlRecord

    #updates the values in a sqlrecord with attributes in soup
    #Beautiful Soup, SQLRecord -> SQlRecord
    def updateDescriptor(self,soup,sqlRecord):#fill the record
        sqlRecord.setValue('component_type',soup.findChild('component')['name'][0:3])

        sqlRecord.setValue('component_name',soup.findChild('component')['name'])

        sqlRecord.setValue('pinmaxpa',soup.findChild('PInMaxPa')['value'])
        sqlRecord.setValue('qoutmaxpa',soup.findChild('QOutMaxPa')['value'])
        sqlRecord.setValue('qinmaxpa',soup.findChild('QInMaxPa')['value'])
        sqlRecord.setValue('isvoltagesource',soup.findChild('isVoltageSource')['value'])

        return sqlRecord

    #use the input handler to load raw timeseries data, fix data and return fixed data
    #String, String, String -> DataClass
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
        inputDictionary['timeZone'] = readXmlTag(setupFile,'timeZone','value')
        inputDictionary['fileType'] = readXmlTag(setupFile, 'inputFileType', 'value')
        inputDictionary['outputInterval'] = readXmlTag(setupFile, 'timeStep', 'value')
        inputDictionary['outputIntervalUnit'] = readXmlTag(setupFile, 'timeStep', 'unit')
        inputDictionary['inputInterval'] = readXmlTag(setupFile, 'inputTimeStep', 'value')
        inputDictionary['inputIntervalUnit'] = readXmlTag(setupFile, 'inputTimeStep', 'unit')
        inputDictionary['runTimeSteps'] = readXmlTag(setupFile,'runTimeSteps','value')
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

        #combine values with their units as a string
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
        inputDictionary['componentAttributes'], inputDictionary['componentNames'], inputDictionary['useNames'] = getUnits(Village, os.path.dirname(setupFile))

        # read time series data, combine with wind data if files are seperate.
        #Pass our sendet to mergeInputs so it can send signals
        df, listOfComponents = mergeInputs(inputDictionary,sender=self.sender)

        # check the timespan of the dataset. If its more than 1 year ask for / look for limiting dates
        minDate = min(df.index)
        maxDate = max(df.index)
        limiters = inputDictionary['runTimeSteps']

        if ((maxDate - minDate) > pd.Timedelta(days=365)) & (limiters ==['all']):
             newdates = self.DatesDialog(minDate, maxDate)
             m = newdates.exec_()
             if m == 1:
               
                #inputDictionary['runTimeSteps'] = [newdates.startDate.text(),newdates.endDate.text()]
                inputDictionary['runTimeSteps'] = [pd.to_datetime(newdates.startDate.text()), pd.to_datetime(newdates.endDate.text())]
                #TODO write to the setup file so can be archived
        self.sender.update(0,'fixing bad values')
        # now fix the bad data
        df_fixed = fixBadData(df,os.path.dirname(setupFile),listOfComponents,inputDictionary['runTimeSteps'],sender=self.sender)
        self.sender.update(0, 'fixing intervals')
        # fix the intervals
        print('fixing data timestamp intervals to %s' %inputDictionary['outputInterval'])
        df_fixed_interval = fixDataInterval(df_fixed, inputDictionary['outputInterval'],sender=self.sender)
        df_fixed_interval.preserve(os.path.dirname(setupFile))

        return df_fixed_interval, listOfComponents

    def relayProgress(self,i):
        self.notifyProgress.emit(i)
    class DatesDialog(QtWidgets.QDialog):

        def __init__(self,minDate,maxDate):
            super().__init__()
            self.setWindowTitle("Dates to Analyze")
            grp = QtWidgets.QGroupBox()
            hz = QtWidgets.QVBoxLayout()
            prompt = QtWidgets.QLabel("Select Dates to Analyze")
            hz.addWidget(prompt)
            box = QtWidgets.QHBoxLayout()
            self.startDate = QtWidgets.QDateEdit()
            self.startDate.setObjectName('start')
            self.startDate.setDisplayFormat('yyyy-MM-dd')
            self.startDate.setDate(minDate)
            self.startDate.setCalendarPopup(True)
            self.endDate = QtWidgets.QDateEdit()
            self.endDate.setDate(maxDate)
            self.endDate.setObjectName('end')
            self.endDate.setDisplayFormat('yyyy-MM-dd')
            self.endDate.setCalendarPopup(True)
            box.addWidget(self.startDate)
            box.addWidget(self.endDate)
            grp.setLayout(box)
            hz.addWidget(grp)

            buttonBox = QtWidgets.QDialogButtonBox()
            buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok
                             | QtWidgets.QDialogButtonBox.Cancel)
            buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
            buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
            hz.addWidget(buttonBox)

            self.setLayout(hz)

            def getValues(self):
                a,b = self.startDate.text(), self.endDate.text()
                return a,b
    #List Of dataframe of cleaned data
    #generate netcdf files for model running
    #dataframe, dictionary -> None
    def createNetCDF(self, lodf,componentDict,setupFolder):
        '''
        Create netcdf file from a list of dataframes return a list of netcdf files created
        :param lodf: List of DataFrames with time indices and column names that match the componentDict
        :param componentDict: a dictionary of component attributes, including column names
        :param setupFolder: The folder path containing the projects setup.xml file
        :return: List of Strings naming the netcdf files created.
        '''
        from MiGRIDS.InputHandler.dataframe2netcdf import dataframe2netcdf
        outputDirectory = getFilePath('Processed',setupFolder=setupFolder)
        netCDFList = []
        #if there isn't an output directory make one
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        #only the largest dataframe is kept
        largest = 0
        for i, df in enumerate(lodf):
            if len(df) > largest:
                netCDFList = dataframe2netcdf(df, componentDict, outputDirectory)
                largest = len(df)
        return netCDFList

    #save the components for a project
    #List of Components, String -> None
    def storeComponents(self, ListOfComponents,setupFile):
        outputDirectory = os.path.dirname(setupFile)

        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'components.pkl')
        file = open(outfile, 'wb')
        pickle.dump(ListOfComponents, file)
        file.close()
        return
    #save the DataClass object as a pickle in the processed data folder
    #DataClass, string -> None
    def storeData(self,df,setupFile):

        outputDirectory = getFilePath(os.path.dirname(setupFile), 'Processed')
        print("processed data saved to %s: " %outputDirectory)
        if not os.path.exists(outputDirectory):
            os.makedirs(outputDirectory)
        outfile = os.path.join(outputDirectory, 'processed_input_file.pkl')
        file = open(outfile,'wb')
        pickle.dump(df,file)
        file.close()
        return

    def loadInputData(self,setupFile):
        '''
        Read in a pickled data object if it exists. Pickled objects are created once data has begun the fixing process
        which can be time consuming and may need to be performed in stages.
        :param setupFile: the file path to a setup xml
        :return: a DataClass object which consists of raw and fixed data
        '''
        outputDirectory = os.path.join(os.path.dirname(setupFile), *['..','TimeSeriesData'])
        outfile = os.path.join(outputDirectory, 'fixed_data.pkl')

        if not os.path.exists(outfile):
            return None

        file = open(outfile, 'rb')
        data = pickle.load(file)
        file.close()
        return data

    def loadComponents(self, setupFile):
        '''
        Loads component pickle objects that were created during the data fixing process.
        :param setupFile: String path to seup xml file
        :return: List of Component Objects
        '''
        outputDirectory = os.path.dirname(setupFile)
        infile = os.path.join(outputDirectory, 'components.pkl')
        if not os.path.exists(infile):
            return

        file = open(infile, 'rb')
        loC = pickle.load(file)
        file.close()
        return loC
    def makeAttributeXML(self,currentSet):
        # TODO remove this legacy code - not needed when models are run from gui
        # THIS IS OBSOLETE
        # generate the setAttributes xml file
        soup = makeAttributeXML(currentSet)
        dbhandler = ProjectSQLiteHandler()
        fileName = dbhandler.getProject() + currentSet.capitalize() + 'Attributes.xml'
        setDir = getFilePath(currentSet, projectFolder=dbhandler.getProjectPath())
        writeAttributeXML(soup, setDir, fileName)

    def readSetup(self,setupFile):
        '''reads in the project setup file and returns it as a soup'''
        setupSoup = getSetupInformation(setupFile)
        return setupSoup

    def updateSetup(self, setName):
        '''modifies and existing setup soup with database values for a set'''
        projectPath = self.dbhandler.getProjectPath()
        setupFile = os.path.join(getFilePath(setName,projectFolder=projectPath),
                                              self.dbhandler.getProject() + setName.capitaliz() + 'Setup.xml')
        setRecord = self.dbhandler.getRecordDictionary('set_',self.dbhandler.getId('set_','set_name',setName))
        for k in setRecord.keys():
            attr = k.split(".")[len(k.split(".")-1)]
            tag = k.split(".")[len(k.split(".") - 2)]
            writeXmlTag(setupFile,tag,attr,setRecord[k])

    def writeSetup(self, setupSoup, setName):
        '''writes a setupSoup specific for a set to a set folder'''
        projectPath= self.dbhandler.getProjectPath()
        self.writeSoup(setupSoup,os.path.join(getFilePath(setName,projectFolder=projectPath),
                                              self.dbhandler.getProject() + setName.capitalize() + 'Setup.xml'))

    def runModels(self, currentSet):
        '''makes a call to the model package to run a model set.
        All required xmls are already in the set and run directories'''

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Starting Models",
                                    "You won't beable to edit data while models are running. Are you sure you want to continue?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()
        dbhandler = ProjectSQLiteHandler()
        setDir = getFilePath(currentSet,projectFolder=dbhandler.getProjectPath())

        #this is silly to have more than 1 database in a single program
        # Check if a set component attribute database already exists
        if os.path.exists(os.path.join(setDir, currentSet + 'ComponentAttributes.db')):
            #ask to delete it or generate a new set
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Overwrite files?",
                                        "Set up files were already generated for this model set. Do you want to overwrite them? ")
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            result = msg.exec()

            if result == QtWidgets.QMessageBox.Yes:
                os.remove(os.path.join(setDir, currentSet + 'ComponentAttributes.db'))
            else:
                #create a new set tab
                return

        # call to run models
        runSimulation(projectSetDir=setDir)

    """  
    def generateRuns(self,setNum):
       '''generate runs puts the necessary files into the set folder
       The necessary files include: setup, model xmls'''
        

        # load the file with the list of different component attributes
        compName = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compName'],
                              'value')
        compTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compTag'],
                             'value')
        compAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml', ['compAttributeValues', 'compAttr'],
                              'value')
        compValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                               ['compAttributeValues', 'compValue'], 'value')

        # check if wind turbine values were varied from base case. If so, will set the 'recalculateWtgPAvail' tag to 1
        # for each wind turbine
        # isWtg = any(['wtg' in x for x in compName])
        compValue = 
        valSplit = []  # list of lists of attribute values
        for val in compValue:  # iterate through all comonent attributes
            if not isinstance(val,
                              list):  # readXmlTag will return strings or lists, depending if there are commas. we need lists.
                val = [val]
            valSplit.append(val)  # split according along commas

        # get all possible combinations of the attribute values
        runValues = list(itertools.product(*valSplit))

        # get headings
        heading = [x + '.' + compTag[idx] + '.' + compAttr[idx] for idx, x in enumerate(compName)]

        # get the setup information for this set of simulations
        setupTag = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                              ['setupAttributeValues', 'setupTag'], 'value')
        setupAttr = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                               ['setupAttributeValues', 'setupAttr'], 'value')
        setupValue = readXmlTag(projectName + 'Set' + str(setNum) + 'Attributes.xml',
                                ['setupAttributeValues', 'setupValue'],
                                'value')

        # copy the setup xml file to this simulation set directory and make the specified changes
        # if Setup dir does not exist, create
        setupFile = os.path.join(projectSetDir, 'Setup', projectName + 'Set' + str(setNum) + 'Setup.xml')
        if os.path.exists(os.path.join(projectSetDir, 'Setup')):
            inpt = input("This simulation set already has runs generated, overwrite? y/n")
            if inpt.lower() == 'y':
                generateFiles = 1
            else:
                generateFiles = 0
        else:
            generateFiles = 1
        if generateFiles == 1:
            if os.path.exists(os.path.join(projectSetDir, 'Setup')):
                rmtree(os.path.join(projectSetDir, 'Setup'))
            os.mkdir(os.path.join(projectSetDir, 'Setup'))
            # copy setup file
            copyfile(os.path.join(projectDir, 'InputData', 'Setup', projectName + 'Setup.xml'), setupFile)
            # make the cbanges to it defined in projectSetAttributes
            for idx, val in enumerate(setupValue):  # iterate through all setup attribute values
                tag = setupTag[idx].split('.')
                attr = setupAttr[idx]
                value = val
                writeXmlTag(setupFile, tag, attr, value)

            # make changes to the predict Load input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'predictLoad')
            # make changes to the predict Wind input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'predictWind')
            # make changes to the reDispatch input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'reDispatch')
            # make changes to the getMinSrc input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'getMinSrc')
            # make changes to the gen dispatch
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'genDispatch')
            # make changes to the genSchedule input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'genSchedule')
            # make changes to the wtg dispatch input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'wtgDispatch')
            # make changes to the ees dispatch input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'eesDispatch')
            # make changes to the tes dispatch input file
            generateInputFile(projectDir, projectSetDir, projectName, setNum, setupFile, 'tesDispatch')

        # get the components to be run
        components = readXmlTag(setupFile, 'componentNames', 'value')

        # generate the run directories
        runValuesUpdated = runValues  # if any runValues are the names of another tag, then it will be updated here
        for run, val in enumerate(runValues):  # for each simulation run
            # check if there already is a directory for this run number.
            runDir = os.path.join(projectSetDir, 'Run' + str(run))
            compDir = os.path.join(runDir, 'Components')
            if not os.path.isdir(runDir):
                os.mkdir(runDir)  # make run directory

                os.mkdir(compDir)  # make component directory
            # copy component descriptors  and fillSetInfo
            for cpt in components:  # for each component
                # copy from main input data
                copyfile(os.path.join(projectDir, 'InputData', 'Components', cpt + 'Descriptor.xml'),
                         os.path.join(compDir, cpt + 'Set' + str(setNum) + 'Run' + str(run) + 'Descriptor.xml'))

            # make changes
            for idx, value in enumerate(val):
                compFile = os.path.join(compDir,
                                        compName[idx] + 'Set' + str(setNum) + 'Run' + str(run) + 'Descriptor.xml')
                tag = compTag[idx].split('.')
                attr = compAttr[idx]
                # check if value is a tag in the xml document
                tryTagAttr = value.split('.')  # split into tag and attribute
                if len(tryTagAttr) > 1:
                    # seperate into component, tags and attribute. There may be multiple tags
                    tryComp = tryTagAttr[0]
                    tryTag = tryTagAttr[1]
                    for i in tryTagAttr[2:-1]:  # if there are any other tag values
                        tryTag = tryTag + '.' + i
                    tryAttr = tryTagAttr[-1]  # the attribute
                    if tryComp in compName:
                        idxComp = [i for i, x in enumerate(compName) if x == tryComp]
                        idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                        idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                        idxVal = list(set(idxTag).intersection(idxAttr).intersection(idxComp))
                        value = val[idxVal[0]]  # choose the first match, if there are multiple
                        a = list(runValuesUpdated[run])  # change values from tuple
                        a[idx] = value
                        runValuesUpdated[run] = tuple(a)
                    else:
                        # check if it is referring to a tag in the same component
                        # seperate into tags and attribute. There may be multiple tags
                        tryTag = tryTagAttr[0]
                        for i in tryTagAttr[1:-1]:  # if there are any other tag values
                            tryTag = tryTag + '.' + i
                        if tryTag in compTag:
                            tryAttr = tryTagAttr[-1]  # the attribute
                            idxTag = [i for i, x in enumerate(compTag) if x == tryTag]
                            idxAttr = [i for i, x in enumerate(compAttr) if x == tryAttr]
                            idxVal = list(set(idxTag).intersection(idxAttr))
                            value = val[idxVal[0]]  # choose the first match, if there are multiple
                            a = list(runValuesUpdated[run])  # change values from tuple
                            a[idx] = value
                            runValuesUpdated[run] = tuple(a)
                writeXmlTag(compFile, tag, attr, value)

                # if this is a wind turbine, then its values are being altered and the wind power time series will need
                # to be recalculated
                if 'wtg' in compName[idx]:
                    if tag == 'powerCurveDataPoints' or tag == 'cutInWindSpeed' or tag == 'cutOutWindSpeedMax' or tag == 'cutOutWindSpeedMin' or tag == 'POutMaxPa':
                        writeXmlTag(compFile, 'recalculateWtgPAvail', 'value', 'True')

        # create dataframe and save as SQL
        df = pd.DataFrame(data=runValuesUpdated, columns=heading)
        # add columns to indicate whether the simulation run has started or finished. This is useful for when multiple processors are
        # running runs to avoid rerunning simulations. The columns are called 'started' and 'finished'. 0 indicate not
        # started (finished) and 1 indicates started (finished)
        df = df.assign(started=[0] * len(runValues))
        df = df.assign(finished=[0] * len(runValues))
        conn = sqlite3.connect('set' + str(setNum) + 'ComponentAttributes.db')  # create sql database

        try:
            df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        except sqlite3.Error as er:
            print(er)
            print(
                'You need to delete the existing set ComponentAttributes.db before creating a new components attribute table')

        conn.close()
        os.chdir(here)"""
    def readInSetupFile(self, setupFile):

        #setupInfo is a dictionary of setup tags and values to be inserted into the database
        setupInfo = setupToDictionary(getSetupInformation(setupFile))
        return setupInfo

    def getSetAttributeXML(self, xmlFile):
        '''
        Creates a soup object from xml file
        :param xmlFile: String path to xml file
        :return: BeautifulSoup soup object
        '''
        #read the attributes xml
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

        return soup

    def getComponentTypes(self):
        '''
        Gets a list of component types associated with a project
        :return: List of String standardized types from component table in project_manager database
        '''
        dbhandler = ProjectSQLiteHandler()
        loT = dbhandler.getComponentTypes()
        dbhandler.closeDatabase()
        return loT

