# Projet: MiGRIDS
# Created by: # Created on: 11/22/2019
# Purpose :  loadProjectOffUIThread
import os
from PyQt5 import QtGui, QtCore

from MiGRIDS.Analyzer.DataRetrievers.getAllRuns import getAllSets


from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.Controller.SetupHandler import SetupHandler
from MiGRIDS.Controller.Validator import ValidatorTypes,Validator
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.replaceDefaultDatabase import replaceDefaultDatabase


class ThreadedProjectLoad(QtCore.QThread):
    notifyCreateProgress = QtCore.pyqtSignal(int, str)
    signalUpdateAttribute = QtCore.pyqtSignal(str, str, object)

    def __init__(self, setupFile):
        QtCore.QThread.__init__(self)
        self.setupFile = setupFile


    def __del__(self):
        self.wait()

    def run(self):
        self.dbHandler = ProjectSQLiteHandler()  # use a seperate dbhandler instance
        self.runHandler = RunHandler(self.dbHandler)
        self.setupHandler = SetupHandler(self.dbHandler)
        self.validator = Validator()
        self.loadProjectOffUIThread(self.setupFile)

        return

    def done(self):
        QtGui.QMessageBox.information(self, "Done!", "Done loading data!")

    def updateProgress(self, i, task):
        self.notifyCreateProgress.emit(i, task)

    def updateAttribute(self,className,attr,value):
        self.signalUpdateAttribute.emit(className,attr,value)

    def loadProjectOffUIThread(self,setupFile):
        # load project gets run on a seperate thread so it uses a newly initialized handlers

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
        self.updateAttribute('Controller','projectFolder',getFilePath('Project', setupFolder=os.path.dirname(setupFile)))
        project = os.path.basename(projectFolder)
        self.updateAttribute('Controller', 'project',project)
            #self.controller.project = os.path.basename(controller.projectFolder)
        self.updateProgress(1, 'Data loading')
        # Look for an existing project database and replace the default one with it

        if os.path.exists(os.path.join(projectFolder, 'project_manager')):
            print('An existing project database was found.')

            replaceDefaultDatabase(os.path.join(projectFolder, 'project_manager'))
            self.updateAttribute('Controller','projectDatabase',True)
            #TODO verify validator called for controller attributes

        else:
            print('An existing project database was not found.')
            # load setup information
            setupDictionary = self.setupHandler.readInSetupFile(setupFile)
            if self.validator.validate(ValidatorTypes.SetupXML,setupDictionary):
                self.updateAttribute('Controller','setupValid',True)
                self.dbHandler.insertRecord('project', ['project_name', 'project_path', 'setupfile'],
                                   [project, projectFolder, setupFile])
                self.dbHandler.updateSetupInfo(setupDictionary, setupFile)

            self.updateProgress(1, 'Loading Set Results')
            # load Sets - this loads attribute xmls, set setups, set descriptors, setmodel selectors and run result metadata
            sets = getAllSets(getFilePath('OutputData', setupFolder=os.path.dirname(setupFile)))
            self.updateAttribute('Controller','sets',sets)
            [self.runHandler.loadExistingProjectSet(os.path.dirname(s).split('\\')[-1]) for s in sets]
        self.updateProgress(3, 'Validating Data')

       # get input data object
        data= findDataObject()
        if self.validator.validate(ValidatorTypes.InputData):
            self.updateAttribute('Controller', 'inputDataValid', True)
        if self.validator.validate(ValidatorTypes.DataObject, data):
            self.updateAttribute('Controller', 'inputDataValid', True) #TODO this should be validated seperately
            self.updateAttribute('Controller','dataObjectValid',True)
            self.updateAttribute('Controller', 'inputData', data)  # send the object to the controller
        self.updateProgress(3, 'Loading NetCDFs')
        # get model input netcdfs
        netcdfs = listNetCDFs()
        if self.validator.validate(ValidatorTypes.NetCDFList, netcdfs):
            self.updateAttribute('Controller','netcdfsValid',True)
            self.updateAttribute('Controller', 'netcdfs', netcdfs)  # send the object to the controller
        self.updateProgress(10,'Complete')
        del self.dbHandler
        del self.runHandler
        return
