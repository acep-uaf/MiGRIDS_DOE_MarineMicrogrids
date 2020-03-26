# Projet: MiGRIDS
# Created by: T.Morgan# Created on: 9/25/2019
import glob
import os

import shutil
from PyQt5 import QtWidgets
from MiGRIDS.Analyzer.DataRetrievers.getAllRuns import getAllRuns
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag, splitAttribute, isTagReferenced, getReferencedValue
from MiGRIDS.Analyzer.PerformanceAnalyzers.getRunMetaData import fillRunMetaData
from MiGRIDS.Controller.UIHandler import UIHandler
from MiGRIDS.Model.Operational.runSimulation import Simulation
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeAttributeXML import makeAttributeXML, writeAttributeXML

METADATANAMES = {'Generator Import kWh':'genptot',
                'Generator Charging kWh':'genpch',
'Generator Switching':'gensw',
'Generator Loading':'genloadingmean',
'Generator Online Capacity':'gencapacitymean',
'Generator Fuel Consumption kg':'genfuelcons',
'Diesel-off time h':'gentimeoff',
'Generator Cumulative Run time h':'gentimeruntot',
'Generator Cumulative Capacity Run Time kWh':'genruntimeruntotkwh',
'Generator Overloading Time h':'genoverloadingtime',
'Generator Overloading kWh':'genoverLoadingkwh',
'Wind Power Import kWh':'wtgpimporttot',
'Wind Power Spill kWh':'wtgpspilltot',
'Wind Power Charging kWh':'wtgpchtot',
'Energy Storage Discharge kWh':'eesspdistot',
'Energy Storage Charge kWh':'eesspchtot',
 'Energy Storage SRC kWh':'eesssrctot',
'Energy Storage Overloading Time h':'eessoverloadingtime',
'Energy Storage Overloading kWh':'eessoverloadingkwh',
'Thermal Energy Storage Throughput kWh':'tessptot'}


class RunHandler(UIHandler):
    """
    Description: Provides methods used for reading, writing and passing run data within the user interface and between the ui and model packages
    Attributes:
    """

    def __init__(self,dbhandler):
        super().__init__(dbhandler)
        return

    def makeAttributeXML(self,currentSet):

        # generate the setAttributes xml file
        compChanges = self.dbhandler.getSetChanges(self.dbhandler.getSetId(currentSet))
        setChanges = self.dbhandler.getNewSetInfo(currentSet)
        soup = makeAttributeXML(currentSet,compChanges,setChanges)

        fileName = self.dbhandler.getProject() + currentSet.capitalize() + 'Attributes.xml'
        setDir = getFilePath(currentSet, projectFolder=self.dbhandler.getProjectPath())
        writeAttributeXML(soup, setDir, fileName)

        #add model xml attributes
    def makeRunDescriptors(self,setCompId,runName,setName):
        allComponents = self.dbhandler.getSetComponents(self.dbhandler.getSetId(setName))
        for i in allComponents:
            runFolder = getFilePath(runName,projectFolder = self.dbhandler.getProjectPath(),Set=setName)
            descFile = os.path.join(*[runFolder,'Components',
                                    self.dbhandler.getFieldValue('component','componentnamevalue','_id',str(i[0])) + setName + runName + 'Descriptor.xml'])
            inFile = os.path.join(getFilePath('Components',projectFolder = self.dbhandler.getProjectPath()),
                                  self.dbhandler.getFieldValue('component','componentnamevalue','_id',str(i[0])) + 'Descriptor.xml')
            if not os.path.exists(os.path.dirname(descFile)):
                os.makedirs(os.path.dirname(descFile))
            shutil.copy2(inFile, descFile)
        holdRecord = []
        for sc in setCompId:

            setCompRecord = self.dbhandler.getRecordDictionary('set_components',sc)
            if isTagReferenced(setCompRecord['tag_value']):
                #keep the record for later
                holdRecord.append(setCompRecord)
                pass
            descFile=os.path.join(*[getFilePath(runName, projectFolder=self.dbhandler.getProjectPath(), Set=setName),'Components',
                         self.dbhandler.getFieldValue('component', 'componentnamevalue', '_id',
                                                      setCompRecord['component_id']) + setName + runName + 'Descriptor.xml'])
            self.writeTag(descFile,setCompRecord['tag'],setCompRecord['tag_value'])

        for r in holdRecord:
            descFile = os.path.join(*[getFilePath(runName, projectFolder=self.dbhandler.getProjectPath(), Set=setName),'Components',
                                    self.dbhandler.getFieldValue('component', 'componentnamevalue', '_id',
                                                                 r[
                                                                     'component_id']) + setName + runName + 'Descriptor.xml'])

            self.writeTag(descFile, r['tag'], getReferencedValue(r['tag_value'],runFolder))

        return


    def loadExistingProjectSet(self,setName,dbhandler):
        '''populates the project database with set information extracted from a set folder
        if the set does not already exist within the database
        :param setName: string name of the set and setfolder
        :param dbhandler a connection to the database
        New handler because this function is called from thread'''

        #get a setup dictionary - None if setup file not found
        setSetup = self.readInSetupFile(self.findSetupFile(setName))
        #if a set folder exists but set setup info is not in the database populate the datebase with the set xml files
        if (setSetup != None) & (dbhandler.getSetId(setName) == -1):
            #update the database based on info in the set setup file, this includes adding components to set_components if not already there
            dbhandler.updateSetSetup(setName, setSetup)
            #get the list of components associated with this project
            compList = setSetup['componentNames.value'].split(" ")
            #add components to the set_component table (base case, tag set to None)
            dbhandler.updateSetComponents(setName, compList)

            #look for existing runs and update the database
            #read attribute xml and put new tags in set_component table
            try:
                self.updateFromAttributeXML(setName)
            except FileNotFoundError as e:
                return
            self.loadExistingRuns(setName,dbhandler)
            return

    def loadExistingRuns(self,setName,dbhandler):
        '''fill in the project database with information found in the set folder.
        Assumes there is not information already in the database for each run'''
        projectDir = dbhandler.getProjectPath()
        projectSetDir = getFilePath(setName,projectFolder = projectDir)
        runs = getAllRuns(projectSetDir)

        setId = dbhandler.getSetId(setName)
          # fills in metadata results - TODO remove.
        [self.updateRunStartFinishMeta(projectSetDir,setId,r,dbhandler) for r in runs if self.dbhandler.getFieldValue('run','started','run_num',str(r)) is None]
        fillRunMetaData(projectSetDir, []) #fills in metadata for all runs
        return

    def updateRunStartFinishMeta(self,setDir,setId,runNum,dbhandler):
        #get the metadata for all existing runs
        runPath = getFilePath('Run' + str(runNum), set=setDir)
        if self.hasOutPutData(runPath):
            dbhandler.insertCompletedRun(setId, runNum) #puts minimal info in database
            runId = self.dbhandler.getId('run', ['run_num', 'set_id'], [runNum, setId])
            self.setRunComponentsFromFolder(setId,runPath,runId,dbhandler) #fill in the run_attribute table


    def hasOutPutData(self,runPath):
        '''checks if there are any netcdf files in the output folder
        If there is atleast 1 file returns true
        otherwise false'''
        searchpath = os.path.join(*[runPath,'OutputData','*.nc'])
        outdata = glob.glob(searchpath )
        if outdata:
            return True
        else:
            return False

    def setRunComponentsFromFolder(self,setId,runPath,runId,dbhandler):
        def setComponentName(d):
            d['component_name'] = self.dbhandler.getFieldValue('component','componentnamevalue','_id',d['component_id'])
            return d
        possibleComponentAttributesDict = dbhandler.getSetComponentTags(setId)
        possibleComponentAttributesDict =[setComponentName(p) for p in possibleComponentAttributesDict]
        [self.addToRunAttribute(t,runId,runPath,dbhandler) for t in possibleComponentAttributesDict]

    def addToRunAttribute(self,d,runId,runPath,dbhandler):
        import re
        def xmlMatched(xmlName,componentName):
            filename = os.path.basename(xmlName)
            if re.findall("[a-z]+[0-9]+", filename, re.IGNORECASE)[0] == componentName:
                return xmlName
        searchPath = os.path.join(*[runPath, 'Components', '*.xml'])
        xmls = glob.glob(searchPath)
        selectedXML = [xmlMatched(x,d['component_name']) for x in xmls][0]
        t, a = splitAttribute(d['tag'])
        xmlValue = readXmlTag(os.path.basename(selectedXML),t ,a, os.path.dirname(selectedXML))
        def actualValue(tagv):
            if isTagReferenced(tagv):
                t, a = splitAttribute(tagv)

                return readXmlTag(os.path.basename(selectedXML), t, a, os.path.dirname(selectedXML))
            else:
                return tagv

        if ((isinstance(xmlValue,list)) & (actualValue(d['tag_value']) in xmlValue)) | \
                ((not isinstance(xmlValue,list)) & (actualValue(d['tag_value']) == xmlValue)) | \
                ((isinstance(xmlValue, list)) & (actualValue(d['tag_value']) == xmlValue)):
           # put the record into the run_attribute table
            dbhandler.insertRunComponent(runId, d['_id'])
            return

    def updateFromAttributeXML(self,setName):
        #the attribute xml is set up different from other files.
        fileName = self.dbhandler.getProject() + setName.capitalize() + 'Attributes.xml'
        setDir = getFilePath(setName, projectFolder=self.dbhandler.getProjectPath())
        compName = readXmlTag(fileName, 'compName', 'value', setDir)
        compId = [self.dbhandler.getId('component',['componentnamevalue'],[c]) for c in compName]
        compTag = readXmlTag(fileName, 'compTag', 'value', setDir)

        compAttr = readXmlTag(fileName, 'compAttr', 'value', setDir)
        compValue = readXmlTag(fileName, 'compValue', 'value', setDir)#supports a comma seperated list
        compTuple = list(zip(compId,compTag,compAttr,compValue))
        self.dbhandler.insertSetComponentTags(setName,compTuple)
    def attributeToDictionary(self,fileName,setDir):
        '''creates a dictionary from the component portion of  attribute xml file '''
        lod = []
        d = {}


        return lod

    def findSetupFile(self, setName):
        return os.path.join(*[getFilePath(setName,projectFolder=self.dbhandler.getProjectPath()),'Setup',self.dbhandler.getProject() + setName +  'Setup.xml'])

    def runModels(self, currentSet):
        '''makes a call to the model package to run a model set.
        All required xmls are already in the set and run directories'''

        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Starting Models",
                                    "You won't beable to edit data while models are running. Are you sure you want to continue?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

        setDir = getFilePath(currentSet,projectFolder=self.dbhandler.getProjectPath())

        if self.hasOutPutData(setDir):
            #ask to delete it or generate a new set
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Overwrite files?",
                                        "Set up files were already generated for this model set. Do you want to overwrite them? ")
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)
            result = msg.exec()

            if result == QtWidgets.QMessageBox.Yes:
                os.remove(os.path.join(setDir, currentSet + '/'))
            else:
                #create a new set tab
                return

        # call to run models
        searchpath = os.path.join(*[setDir, 'Run*'])
        runCount = len(glob.glob(searchpath))
        Sim = Simulation(setDir,self.findSetupFile(currentSet))
        Sim.PrepareSimulationInput()
        while 1:
            # read the SQL table of runs in this set and look for the next run that has not been started yet.

            runNum = self.dbhandler.getNextRun(currentSet)
            if runNum == None:  # this is the only exit
                break
            else:
                self.sender.update(1/runCount,"Running simulation " + str(runNum))
                self.dbhandler.updateRunToStarted('Set' + str(currentSet), runNum)
                Sim.runIndividualSimulation(runNum)
                self.dbhandler.updateRunToFinished('Set' + str(self.setNum), runNum)
        self.sender.update(9,"Extracting run results")
        fillRunMetaData(setDir, []) #get metadata for all the runs
        self.sender.update(10, "complete")

    def createRun(self, setComponentIds, run,setName):
        # make the run directory
        os.makedirs(getFilePath("Run" + str(run), Set=setName, projectFolder=self.dbhandler.getProjectPath()),exist_ok=True)

        # move Descriptors with eddited attributes to the correct run folders
        self.makeRunDescriptors(setComponentIds, "Run" + str(run), setName)

        #insert the run into the run table
        run_id = self.dbhandler.insertRecord('run',['run_num','set_id'],[run,self.dbhandler.getSetId(setName)])
        #and the run_attributes table
        loi = list(setComponentIds)
        [self.dbhandler.insertRecord('run_attributes', ['run_id', 'set_component_id'],[run_id, x]) for x in loi]
    def getNextRun(self,setName):
        self.dbhandler.getNextRun(setName)

    def updateRunToStarted(self,setName,runNum):
        self.dbhandler.updateRunToStarted(setName,runNum)

    def updateRunToFinished(self,setName,runNum):
        self.dbhandler.updateRunToFinished(setName,runNum)