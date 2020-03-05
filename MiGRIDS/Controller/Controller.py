# Projet: MiGRIDS
# Created by: T.Morgan # Created on: 11/15/2019
import os
from PyQt5 import QtCore, QtGui

from MiGRIDS.Controller.GenericSender import GenericSender
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.Controller.SetupHandler import SetupHandler
from MiGRIDS.Controller.Validator import Validator,ValidatorTypes

from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.UserInterface.getFilePaths import getFilePath

from MiGRIDS.UserInterface.switchProject import saveProject, clearAppForms, clearProjectDatabase


class Controller:
    """
    Description: Controller is singleton with methods to manage project flow from creation to completion
    Attributes: 
        
        
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Controller, cls).__new__(cls)
            cls.instance.init()
        return cls.instance

    def __init__(self):

        return

    def init(self):
        self.dbhandler = ProjectSQLiteHandler()
        self.runHandler = RunHandler(self.dbhandler)
        self.setupHandler = SetupHandler(self.dbhandler)
        self.validator = Validator()
        self.sender = GenericSender()
        self.initializeState()
        #self.sender.statusChanged.connect(self.updateAttribute)

    def createDatabaseConnection(self):
        self.dbhandler = ProjectSQLiteHandler()
        self.runHandler = RunHandler(self.dbhandler)
        self.setupHandler = SetupHandler(self.dbhandler)

    def initializeState(self):
        self.project = None
        self.inputData = None  # dataclass object that can be used to create netcdf files
        self.netcdfs = []  # list of netcdf files to feed into model
        self.setupValid = False  # does the setup xml contain all the required inputs with valid filepaths
        self.dataObjectValid = False  # is the dataclass object valid for producing netcdfs
        self.inputDataValid = False  # are the input files valid for producing the dataclass object
        self.netcdfsValid = False  # are all the netcdf files valid as model inputs
        self.projectDatabase = False #is there a project specific database
        self.projectFolder = None # Path to the project folder
        self.sets=[] # list of set folders


    def validate(self,validatorType,input=None):
        if validatorType == ValidatorTypes.SetupXML:
           self.setupValid = self.validator.validate(validatorType, input)
        elif validatorType == ValidatorTypes.NetCDFList:
           self.netcdfsValid =self.validator.validate(ValidatorTypes.NetCDFList, input)
        elif validatorType == ValidatorTypes.DataObject:
            self.inputData = self.validator.validate(ValidatorTypes.DataObject, input)
        self.sender.callStatusChanged() #this notifies the other forms after control attributes have been set

    def newProject(self):
        '''Creates folders and writes new setup xml'''
        self.project = self.dbhandler.getProject()
        self.projectFolder = self.dbhandler.getProjectPath()
        self.setupFolder = os.path.join(
                                                   *[self.projectFolder,
                                                     'InputData', 'Setup'])
        self.componentFolder = getFilePath('Components', setupFolder=self.setupFolder)
        #create the setup xml and validate it
        setupXML = self.setupHandler.makeSetup(self.project, self.setupFolder)
        self.validate(ValidatorTypes.SetupXML,input=setupXML)

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
        self.netcdfs = self.setupHandler.createNetCDF(df, componentDict, self.setupFolder)
        self.validate(ValidatorTypes.NetCDFList,input=self.netcdfs)
    def switchProject(self,caller,saveTo):
        saveProject(saveTo)
        clearAppForms(caller)
        self.dbhandler.closeDatabase()
        clearProjectDatabase(caller)
        self.createDatabaseConnection()

    def setAttribute(self, attr, value):
        try:
            setattr(self, attr, value)
        except Exception as e:
            print(e)
    def importData(self):
        return
    def loadedProject(self):
        self.createDatabaseConnection()
        if not self.validator.validate(ValidatorTypes.DataObject,self.inputData): #this will set dataobjectvalid to its current state
            self.showAlert("Could not create a valid data object.")

    def createInputData(self):
        self.dbhandler.closeDatabase()
        self.myThread = ThreadedDataCreate()
        self.myThread.notifyCreateProgress.connect(self.sender.update)
        self.myThread.signalAttributeUpdate.connect(self.updateAttribute)
        self.myThread.catchComponents.connect(self.gotComponents)
        self.myThread.catchData.connect(self.gotData)
        #TODO update the gui to reflect input data was created
        self.myThread.finished.connect(self.loadedProject)
        self.myThread.start()

    @QtCore.pyqtSlot()
    def updateAttribute(self,className,attr,value):
        if className == 'Controller':
           self.setAttribute(attr, value)


    @QtCore.pyqtSlot()
    def gotData(self,data):
        self.inputData = data

    @QtCore.pyqtSlot()
    def gotComponents(self,loc):
        self.components = loc

class ThreadedDataCreate(QtCore.QThread):
    notifyCreateProgress = QtCore.pyqtSignal(int,str)
    signalAttributeUpdate = QtCore.pyqtSignal(str,str,object)
    catchData = QtCore.pyqtSignal(DataClass)
    catchComponents = QtCore.pyqtSignal(list)

    def __init__(self):
        QtCore.QThread.__init__(self)


    def __del__(self):
        self.wait()

    def run(self):
        dbhandler = ProjectSQLiteHandler()
        setupHandler = SetupHandler(dbhandler)
        #connect the setupHandlers sender to the controllers sender to relay messages
        setupHandler.sender.notifyProgress.connect(self.notify)
        cleaned_data, components = setupHandler.createCleanedData()
        print('done cleaning')
        self.notify(10,'done') #this should not have an effect because the progress bar reaches 10 during update from fixbaddata
        self.catchData.emit(cleaned_data)
        self.catchComponents.emit(components)
        dbhandler.closeDatabase()
        return

    def done(self):
        QtGui.QMessageBox.information(self, "Done!", "Done loading data!")

    def notify(self,i,task):
        self.notifyCreateProgress.emit(i,task)

class ThreadedNetcdfCreate(QtCore.QThread):
    notifyProgress = QtCore.pyqtSignal(int)
    def __init__(self,setupFile):
        QtCore.QThread.__init__(self)
        self.setupFile = setupFile

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(101):
            self.notifyNetcdfProgress.emit(i)