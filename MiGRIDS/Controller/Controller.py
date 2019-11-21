# Projet: MiGRIDS
# Created by: # Created on: 11/15/2019
import os
from PyQt5 import QtCore, QtGui

from MiGRIDS.Controller.GenericSender import GenericSender
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.Controller.SetupHandler import SetupHandler
from MiGRIDS.Controller.Validator import Validator,ValidatorTypes

from MiGRIDS.Analyzer.DataRetrievers.getAllRuns import getAllSets
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.replaceDefaultDatabase import replaceDefaultDatabase


class Controller:
    """
    Description: Controller is singleton with methods to manage project flow from creation to completion
    Attributes: 
        
        
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)

        return cls.instance

    def __init__(self):

        self.dbhandler = ProjectSQLiteHandler()
        self.runHandler = RunHandler()
        self.setupHandler = SetupHandler()
        self.validator = Validator()
        self.sender = GenericSender()
        self.initializeState()

    def initializeState(self):
        self.project = None
        self.inputData = None  # dataclass object that can be used to create netcdf files
        self.netcdfs = None  # list of netcdf files to feed into model
        self.setupValid = False  # does the setup xml contain all the required inputs with valid filepaths
        self.dataObjectValid = False  # is the dataclass object valid for producing netcdfs
        self.rawDataValid = False  # are the input files valid for producting the dataclass object
        self.netcdfsValid = False  # are all the netcdf files valid as model inputs
        self.projectDatabase = False #is there a project specific database
        self.projectFolder = None # Path to the project folder
        self.sets=[] # list of set folders

    def loadProject(self, setupFile):
        #load project gets run on a seperate thread so it uses a newly initialized handlers
        setupHandler = SetupHandler()
        dbHandler = ProjectSQLiteHandler()
        runHandler = RunHandler()

        # local assistants
        def listNetCDFs():
            '''
            produces a list of netcdf files located in the Processed folder of a project TimeSeries folder
            :return: List of Strings of names of netCDF files
            '''
            try:
                lof = [f for f in os.listdir(getFilePath('Processed', setupFolder=os.path.dirname(setupFile))) if
                       f[-2:] == 'nc']
                return lof
            except FileNotFoundError as e:
                print('No netcdf model files found.')
            return []

        def findDataObject():
            '''looks for and returns dataclas object if found in InputData Folder
            :return DataClass object'''

            # From the setup file read the location of the input pickle
            # by replacing the current pickle with the loaded one the user can manually edit the input and
            #  then return to working with the interface
            return setupHandler.loadInputData(os.path.dirname(setupFile))

        # different load pathways depending on whether or not a project database is found
        self.projectFolder = getFilePath('Project', setupFolder=os.path.dirname(setupFile))
        self.project = os.path.basename(self.projectFolder)
        # Look for an existing project database and replace the default one with it
        if os.path.exists(os.path.join(self.projectFolder, 'project_manager')):
            print('An existing project database was found.')

            replaceDefaultDatabase(os.path.join(self.projectFolder, 'project_manager'))
            self.projectDatabase = True
            self.sender.update(1,'Data loading')

        else:
            print('An existing project database was not found.')
            # load setup information
            setupDictionary = setupHandler.readInSetupFile(setupFile)
            self.setupValid = self.validator.validate(ValidatorTypes.SetupXML, setupFile)
            dbHandler.insertRecord('project', ['project_name', 'project_path', 'setupfile'], [self.project, self.projectFolder, setupFile])
            dbHandler.updateSetupInfo(setupDictionary, setupFile)
            self.sender.update(1, 'Project loading')
            # load Sets - this loads attribute xmls, set setups, set descriptors, setmodel selectors and run result metadata
            self.sets = getAllSets(getFilePath('OutputData', setupFolder=os.path.dirname(setupFile)))
            [runHandler.loadExistingProjectSet(os.path.dirname(s).split('\\')[-1]) for s in self.sets]
        self.sender.update(3, 'Project loading')

        self.projectFolder = dbHandler.getProjectPath()

        # get input data object
        self.inputData = findDataObject()
        self.dataObjectValid = self.validator.validate(ValidatorTypes.DataObject, self.inputData)
        self.sender.update(3, 'Project loading')
        # get model input netcdfs
        self.netcdfs = listNetCDFs()
        self.netcdfsValid = self.validator.validate(ValidatorTypes.NetCDFList, self.netcdfs)
        self.sender.update(3, 'Project loading')
        del setupHandler
        del dbHandler
        del runHandler
        return

    def newProject(self):
        '''Creates folders and writes new setup xml'''
        self.project = self.dbhandler.getProject()
        self.projectFolder = self.dbhandler.getProjectPath()
        self.setupFolder = os.path.join(
                                                   *[self.projectFolder,
                                                     'InputData', 'Setup'])
        self.componentFolder = getFilePath('Components', setupFolder=self.setupFolder)

    def makeNetcdfs(self):
        d = {}
        for c in self.components:
            d[c.column_name] = c.toDictionary()

        self.netcdfs = self.setupHandler.createNetCDF(d,self.inputData.fixed,
                                               os.path.join(self.setupFolder, self.project + 'Setup.xml'))

        # if there isn't a setup folder then its a new project
        if not os.path.exists(self.setupFolder):
            # make the project folder
            os.makedirs(self.setupFolder)
        if not os.path.exists(self.componentFolder):
            # make the component
            os.makedirs(self.componentFolder)
        self.setupHandler.makeSetup()  # make setup writes the setup file in the setup folder
        return

    def generateNetcdf(self, data):
        '''uses a dataclass object to generate model input netcdf files
        netcdf files are written to the processed data folder'''
        # MainWindow = self.window()
        # setupForm = MainWindow.findChild(QtWidgets.QWidget, 'setupDialog')
        # componentModel = setupForm.findChild(QtWidgets.QWidget, 'components').model()

        if data:
            df = data.fixed
        componentDict = {}
        if 'components' not in self.__dict__.keys():
            # generate components

            self.components = self.dbhandler.makeComponents()
        elif self.components == None:
            self.components = self.dbhandler.makeComponents()
        for c in self.components:
            componentDict[c.column_name] = c.toDictionary()

        # filesCreated is a list of netcdf files that were generated
        self.netcdfs = self.setupHandler.createNetCDF(df, componentDict, self.controller.setupFolder)
        self.netcdfsValid = self.validator.validateNetCDFList(self.netcdfs)

    def createInputData(self):
        self.myThread = ThreadedDataCreate()
        self.myThread.notifyCreateProgress.connect(self.sender.update)
        self.myThread.catchComponents.connect(self.gotComponents)
        self.myThread.catchData.connect(self.gotData)
        self.myThread.finished.connect(self.loadProject)
        self.myThread.start()

    @QtCore.pyqtSlot()
    def gotData(self,data):
        self.inputData = data

    @QtCore.pyqtSlot()
    def gotComponents(self,loc):
        self.components = loc

class ThreadedDataCreate(QtCore.QThread):
    notifyCreateProgress = QtCore.pyqtSignal(int,str)
    catchData = QtCore.pyqtSignal(DataClass)
    catchComponents = QtCore.pyqtSignal(list)

    def __init__(self,setupFile):
        QtCore.QThread.__init__(self)
        self.setupFile = setupFile

    def __del__(self):
        self.wait()

    def run(self):
        setupHandler = SetupHandler()
        cleaned_data, components = setupHandler.createCleanedData(self.setupFile)

        self.catchData.emit(cleaned_data)
        self.catchComponents.emit(components)
        return

    def done(self):
        QtGui.QMessageBox.information(self, "Done!", "Done loading data!")

    def notify(self,i,task):
        self.notifyCreateProgress.emit(i,task)

class ThreadedNetcdfCreate(QtCore.QThread):
    notifyProgress = QtCore.pyqtSignal(int)
    def run(self):
        for i in range(101):
            self.notifyNetcdfProgress.emit(i)