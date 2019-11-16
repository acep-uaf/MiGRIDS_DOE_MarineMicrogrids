# Projet: MiGRIDS
# Created by: # Created on: 11/15/2019
import os
from MiGRIDS.Controller.GenericSender import GenericSender
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.Controller.SetupHandler import SetupHandler
from MiGRIDS.Controller.Validator import Validator,ValidatorTypes

from MiGRIDS.Analyzer.DataRetrievers.getAllRuns import getAllSets
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

    def loadProject(self,setupFile):

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
            return self.setupHandler.loadInputData(os.path.dirname(setupFile))

        # different load pathways depending on whether or not a project database is found
        projectFolder = getFilePath('Project', setupFolder=os.path.dirname(setupFile))
        # Look for an existing project database and replace the default one with it
        if os.path.exists(os.path.join(projectFolder, 'project_manager')):
            print('An existing project database was found.')

            replaceDefaultDatabase(os.path.join(projectFolder, 'project_manager'))
            self.projectDatabase = True

        else:
            print('An existing project database was not found.')
            # load setup information
            setupDictionary = self.setupHandler.readInSetupFile(setupFile)
            self.setupValid = self.validator.validate(ValidatorTypes.SetupXML, setupFile)
            self.dbhandler.updateSetupInfo(setupDictionary, setupFile)
            # load Sets - this loads attribute xmls, set setups, set descriptors, setmodel selectors and run result metadata
            self.sets = getAllSets(getFilePath('OutputData', setupFolder=os.path.dirname(setupFile)))
            [self.runHandler.loadExistingProjectSet(os.path.dirname(s).split('\\')[-1]) for s in self.sets]

        self.project = self.dbhandler.getProject()
        self.projectFolder = self.dbhandler.getProjectPath()

        # get input data object
        self.inputData = findDataObject()
        self.dataObjectValid = self.validator.validate(ValidatorTypes.DataObject, self.inputData)

        # get model input netcdfs
        self.netcdfs = listNetCDFs()
        self.netcdfsValid = self.validator.validate(ValidatorTypes.NetCDFList, self.netcdfs)

        return


        