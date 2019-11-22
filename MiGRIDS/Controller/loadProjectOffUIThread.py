# Projet: MiGRIDS
# Created by: # Created on: 11/22/2019
# Purpose :  loadProjectOffUIThread
import os

from MiGRIDS.Analyzer.DataRetrievers.getAllRuns import getAllSets
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.Controller.SetupHandler import SetupHandler
from MiGRIDS.Controller.Validator import ValidatorTypes
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.replaceDefaultDatabase import replaceDefaultDatabase


def loadProjectOffUIThread(setupFile,controller):
    # TODO thread needs to be called from controller not calling controller
    # load project gets run on a seperate thread so it uses a newly initialized handlers
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
    controller.projectFolder = getFilePath('Project', setupFolder=os.path.dirname(setupFile))
    controller.project = os.path.basename(controller.projectFolder)
    controller.sender.update(1, 'Data loading')
    # Look for an existing project database and replace the default one with it
    if os.path.exists(os.path.join(controller.projectFolder, 'project_manager')):
        print('An existing project database was found.')

        replaceDefaultDatabase(os.path.join(controller.projectFolder, 'project_manager'))
        controller.projectDatabase = True


    else:
        print('An existing project database was not found.')
        # load setup information
        setupDictionary = setupHandler.readInSetupFile(setupFile)
        controller.validate(ValidatorTypes.SetupXML, setupFile)

        dbHandler.insertRecord('project', ['project_name', 'project_path', 'setupfile'],
                               [controller.project, controller.projectFolder, setupFile])
        dbHandler.updateSetupInfo(setupDictionary, setupFile)
        controller.sender.update(1, 'Loading Set Results')
        # load Sets - this loads attribute xmls, set setups, set descriptors, setmodel selectors and run result metadata
        controller.sets = getAllSets(getFilePath('OutputData', setupFolder=os.path.dirname(setupFile)))
        [runHandler.loadExistingProjectSet(os.path.dirname(s).split('\\')[-1]) for s in controller.sets]
    controller.sender.update(3, 'Validating Data')

    controller.projectFolder = dbHandler.getProjectPath()

    # get input data object
    controller.inputData = findDataObject()
    controller.validate(ValidatorTypes.DataObject, controller.inputData)
    controller.sender.update(3, 'Loading NetCDFs')
    # get model input netcdfs
    controller.netcdfs = listNetCDFs()
    controller.validate(ValidatorTypes.NetCDFList, controller.netcdfs)
    controller.sender.update(3, 'Project Loaded')
    del setupHandler
    del dbHandler
    del runHandler
    return
