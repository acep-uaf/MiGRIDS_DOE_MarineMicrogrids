#Is called from the UserInterface package to initiate xml file generation through the InputHandler functions
#ModelSetupInformation ->

import os
import pickle
import pandas as pd
import shutil
import numpy as np
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets


from MiGRIDS.InputHandler.getSetupInformation import setupToDictionary

from MiGRIDS.Controller.GenericSender import GenericSender
from MiGRIDS.InputHandler.makeSoup import makeComponentSoup
from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.InputHandler.getSetupInformation import getSetupInformation


class UIHandler():
    def __init__(self):
        self.sender = GenericSender() #used to send signals to pyqt objects
        self.dbhandler = ProjectSQLiteHandler()



    def splitAttribute(self,tag):
        a = tag.split(".")[len(tag.split(".")) - 1]
        tag = tag.split(".")[len(tag.split(".")) - 2]
        return tag, a
    def writeSoup(self,soup,file):

        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))

        f = open(file, "w+")
        f.write(soup.prettify())
        f.close()

    def writeTag(self,file,tag,value):
        def splitAttribute(tag):
            a = tag.split(".")[len(tag.split(".")) -1]
            tag =  tag.split(".")[len(tag.split(".")) -2]
            return tag,a
        tag, a = splitAttribute(tag)

        writeXmlTag(file, tag, a, value)
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

        return
    def relayProgress(self,i):
        self.notifyProgress.emit(i)
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
    def readSetup(self,setupFile):
        '''reads in the project setup file and returns it as a soup'''
        setupSoup = getSetupInformation(setupFile)
        return setupSoup
    def makeSetSetup(self,setName):
        setupSoup = self.readSetup(
            self.dbhandler.getFieldValue('project', 'setupfile', '_id', '1'))  # from the base setup
        self.writeSetup(setupSoup, setName)  # written to the set folder
        self.updateSetup(setName)  # updated and written to reflect changes in the database

        return
    def updateSetup(self, setName):
        '''modifies and existing setup file with database values for a set'''
        projectPath = self.dbhandler.getProjectPath()
        setupFile = os.path.join(*[getFilePath('Setup',projectFolder=projectPath),
                                              self.dbhandler.getProject() + 'Setup.xml'])
        setupSoup = self.readSetup(setupFile)  # from the base setup

        setRecord = self.dbhandler.getSetInfo(setName) #dictionary of tags and values
        #setRecord component value needs to have commas removed
        setRecord['componentNames.value'] = " ".join(setRecord['componentNames.value'].split(","))
        for k in setRecord.keys():
            setupSoup = self.updateSoup(setupSoup,k,setRecord[k])

        self.writeSetup(setupSoup,setName)
    def updateSoup(self,soup,tag,value):

        def splitAttribute(mytag):
            a = mytag.split(".")[len(mytag.split(".")) -1]
            t =  mytag.split(".")[len(mytag.split(".")) -2]
            return t,a


        def findTag(soup,mytag):
            '''matches a tag in soup regardless of case'''
            a = soup.find(mytag)
            if a == None:
                a = soup.find(lambda tag:tag.name.lower() ==mytag.lower())
            return a

        tag, attr = splitAttribute(tag)

        # assign value
        if isinstance(tag,(list,tuple)): # if tag is a list or tuple, itereate down
            a = findTag(soup,tag[0])

            for i in range(1,len(tag)): # for each other level of tags, if there are any
                a = a.find(tag[i])
        else: # if it is just one string
            a = findTag(soup,tag)
        # convert value to strings if not already
        if isinstance(value, (list, tuple, np.ndarray)): # if a list or tuple, iterate
            value = [str(e) for e in value]
        else:
            value = str(value)
        if a is not None:
            a[attr] = value
        return soup
    def writeSetup(self, setupSoup, setName):
        '''writes a setupSoup specific for a set to a set folder'''
        projectPath= self.dbhandler.getProjectPath()
        self.writeSoup(setupSoup,os.path.join(*[getFilePath(setName,projectFolder=projectPath),'Setup',
                                              self.dbhandler.getProject() + setName.capitalize() + 'Setup.xml']))

    def readInSetupFile(self, setupFile):

        #setupInfo is a dictionary of setup tags and values to be inserted into the database

        setupInfo = setupToDictionary(getSetupInformation(setupFile),setupFile)

        return setupInfo
    def readXML(self, xmlFile):
        '''
        Creates a soup object from xml file
        :param xmlFile: String path to xml file
        :return: BeautifulSoup soup object
        '''
        # read the attributes xml
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

        return soup
    def makeComponentDescriptor(self, component,componentDir):
        '''
        calls makecomponentSoup to write a default desciptor xml file for a component.
        :param component: [String] the name of a component with the format [type][#][attribute]
        :param componentDir: [String] the directory the descriptor xml file will be saved to
        :return: [BeautifulSoup] of tags and values associated with a component type
        '''
         #returns a template soup
        componentSoup = makeComponentSoup(component, componentDir)
        return componentSoup
    def getComponentAttributesAsList(self,componentName, componentFolder):

        componentSoup = self.makeComponentDescriptor(componentName, componentFolder)
        attributeList = []
        for tag in componentSoup.find_all():
            if (tag.parent.name not in ['component', 'childOf', 'type']) & (tag.name not in ['component','childOf','type']):
                parent = tag.parent.name
                pt = '.'.join([parent,tag.name])
            else:
                pt = tag.name

            for a in tag.attrs:
                if a != 'unit':
                     attributeList.append('.'.join([pt,str(a)]))
        return attributeList