# Projet: MiGRIDS
# Created by: # Created on: 9/25/2019

import os

import shutil
from PyQt5 import QtWidgets

from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Controller.UIToInputHandler import UIHandler
from MiGRIDS.Model.Operational.runSimulation import runSimulation
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeAttributeXML import makeAttributeXML, writeAttributeXML



class RunHandler(UIHandler):
    """
    Description: Provides methods used for reading, writing and passing run data within the user interface and between the ui and model packages
    Attributes: 
        
        
    """

    def __init__(self):
        super().__init__()
        return


    def makeAttributeXML(self,currentSet):

        # generate the setAttributes xml file
        soup = makeAttributeXML(currentSet)

        fileName = self.dbhandler.getProject() + currentSet.capitalize() + 'Attributes.xml'
        setDir = getFilePath(currentSet, projectFolder=self.dbhandler.getProjectPath())
        writeAttributeXML(soup, setDir, fileName)

        #add model xml attributes

    def makeRunDescriptors(self,setCompId,runName,setName):
        allComponents = self.dbhandler.getSetComponents(self.dbhandler.getId('set_','set_name',setName))
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
            if self.isTagReferenced(setCompRecord['tag_value']):
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

            self.writeTag(descFile, r['tag'], self.getReferencedValue(r['tag_value'],runFolder))

        return
    def getReferencedValue(self, tag, runFolder):
        '''looks for a file and tag within a specified folder. Returns the value of the tag if found
        tag uses the format [component].[tag].[attribute]'''
        sourceFile = [os.path.join(*[runFolder,'Components', xml]) for xml in os.listdir(os.path.join(runFolder,'Components')) if tag.split(".")[0] in xml]
        if len(sourceFile) >= 1:
            sourceFile = sourceFile[0]
            t, a = self.splitAttribute(tag)
            return readXmlTag(os.path.basename(sourceFile), t, a, os.path.dirname(sourceFile))
        else:
            return None
    def isTagReferenced(self,tag):
        pieces = tag.split(".")
        return len([p for p in pieces if not p.isnumeric()]) > 0
    def loadExistingProjectSet(self,setName):
       #get a setup dictionary - None if setup file not found
       setSetup = self.readInSetupFile(self.findSetupFile(setName))
       if setSetup != None:
           #update the database based on info in the set setup file, this includes adding components to set_components if not already there
           self.dbhandler.updateSetSetup(setName, setSetup)
           #get the list of components associated with this project
           compList = setSetup['componentNames.value'].split(" ")
           #add components to the set_component table (base case, tag set to None)
           self.dbhandler.updateSetComponents(setName, compList)
       #read attribute xml and put new tags in set_component table
       self.updateFromAttributeXML(setName)

       return

    def updateFromAttributeXML(self,setName):
        fileName = self.dbhandler.getProject() + setName.capitalize() + 'Attributes.xml'
        setDir = getFilePath(setName, projectFolder=self.dbhandler.getProjectPath())
        compName = readXmlTag(fileName, 'compName', 'value', setDir)
        compId = [self.dbhandler.getId('component','componentnamevalue',c) for c in compName]
        compTag = readXmlTag(fileName, 'compTag', 'value', setDir)

        compAttr = readXmlTag(fileName, 'compAttr', 'value', setDir)
        compValue = readXmlTag(fileName, 'compValue', 'value', setDir)
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

    def createRun(self, setComponentIds, run,setName):
        # make the run directory
        os.makedirs(getFilePath("Run" + str(run), Set=setName, projectFolder=self.dbhandler.getProjectPath()),exist_ok=True)

        # move Descriptors with eddited attributes to the correct run folders
        self.makeRunDescriptors(setComponentIds, "Run" + str(run), setName)

        #insert the run into the run table
        run_id = self.dbhandler.insertRecord('run',['run_num','set_id'],[run,self.dbhandler.getId('set_','set_name',setName)])
        #and the run_attributes table
        loi = list(setComponentIds)
        [self.dbhandler.insertRecord('run_attributes', ['run_id', 'set_component_id'],[run_id, x]) for x in loi]