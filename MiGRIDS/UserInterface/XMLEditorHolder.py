# Projet: MiGRIDS
# Created by: # Created on: 9/13/2019
# Purpose :  PredictEditorHolder is a Form widget that holds modeleditor subwidgets
import os
from PyQt5 import QtWidgets

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.UIHandler import UIHandler
from MiGRIDS.UserInterface.XMLEditor import XMLEditor


class XMLEditorHolder(QtWidgets.QWidget):
    PREFIX = 'project'
    SUFFIX = 'Inputs.xml'

    def __init__(self,parent,tab):
        super(XMLEditorHolder,self).__init__(parent)
        self.tab = tab
        self.set = tab + 1
        self.xmls = {} #the list of possible xml files for each resource type and xml type combination (read from resource folder)
        self.xmlDefaults = {} #the value combo boxes for file selectors are originally set to
        self.controller = Controller()
        self.makeWidget()

    def updateWidget(self):
        '''Update the selected xml files and their values'''
        #new defaults
        self.xmlDefaults = self.getSelectedModelsFromSetup(self.designateSetupFile())
        for k in self.xmls.keys():
            for r in self.xmls[k].keys():
                editor = self.findChild(XMLEditor,k+r)
                if editor is not None:
                    editor.update(self.xmlDefaults[k][r])
        return


    def makeWidget(self):
        self.setAllXMLFiles()
        self.xmlDefaults = self.getSelectedModelsFromSetup(self.designateSetupFile())
        self.setLayout(self.createLayout())

    def createLayout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(1)
        layout.setContentsMargins(0,1,0,1)
        #each file editor gets its own widget

        def addEditor(xkey,rkey):
            return XMLEditor(self, self.xmls[xkey][rkey], self.xmlDefaults[xkey][rkey])

        for k in self.xmls.keys():
            layout.addWidget(self.makeDivider(k))
            wids = list(map(lambda x: addEditor(k,x),self.xmls[k].keys()))
            list(map(layout.addWidget,wids))

        return layout

    def makeDivider(self,blockTitle):
        '''creates a dividing bar widget to be placed between xmleditor widget sections '''
        bar = QtWidgets.QWidget()
        bar.setContentsMargins(-1,0,-1,0)
        title = QtWidgets.QLabel()
        title.setText(blockTitle)
        title.setStyleSheet("background-color: grey;")
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(title)
        bar.setLayout(layout)
        return bar

    def setAllXMLFiles(self):
        self.predictorXMLs = self.getPredictorFiles()
        self.dispatchXMLs = self.getDispatchFiles()
        self.minSRCXMLs = self.getMinSrcFiles()
        self.scheduleXMLs = self.getScheduleFiles()
        self.xmls = self.combineAllXmls()

    def getDispatchFiles(self):
        '''
        Generates a dictionary of possible predictor files to edit based on tags in the mode setup file.
        Only those associated with components in the set will be used
        :return Dictionary of possible predictor xml files for each component'''

        XMLs = self.getXMLFileNames('Dispatch')
        return XMLs
    def getMinSrcFiles(self):
        return self.getXMLFileNames('MinSrc')
    def getPredictorFiles(self):
        '''
        Generates a dictionary of possible predictor files to edit based on tags in the mode setup file.
        Only those associated with components in the set will be used
        :return Dictionary of possible predictor xml files for each component'''

        predictorXMLs = self.getXMLFileNames('Predict')
        return predictorXMLs
    def getScheduleFiles(self):
        return self.getXMLFileNames('Schedule')

    def getXMLFileNames(self,xmltype):
        import re
        #all xml files start with the same prefix and end with the same suffix
        #naming convention is project[resourcetype][xmltype][#]Inputs.xml

        # read all xmls from resource folder
        # resource folder is in the model package
        folder = os.path.join(os.path.dirname(__file__), *['..', 'Model', 'Resources', 'Setup'])
        pattern = re.compile(re.escape(self.PREFIX) + r'([a-z]*)' + re.escape(xmltype) + '(\d)' + re.escape(self.SUFFIX),re.IGNORECASE)
        fileList = [f for f in os.listdir(folder) if pattern.search(f) != None]

        # parse into dictionary
        XMLs = {}

        def addTo(file):
            resourceType = pattern.search(file).group(1)  # group 1 is the part of the file name indicated in the pattern by ([a-z]*)
            if xmltype.lower() in XMLs.keys():
                if resourceType.lower()in XMLs[xmltype.lower()].keys():
                    XMLs[xmltype.lower()][resourceType.lower()].append(file[len(self.PREFIX):len(self.PREFIX) +1].lower() + file[len(self.PREFIX) +1:len(file)-len(self.SUFFIX)])
                else:
                    XMLs[xmltype.lower()][resourceType.lower()] = [file[len(self.PREFIX):len(self.PREFIX) +1].lower() + file[len(self.PREFIX) +1:len(file)-len(self.SUFFIX)]]
            else:
                XMLs[xmltype.lower()] = {resourceType.lower():[file[len(self.PREFIX):len(self.PREFIX) +1].lower() + file[len(self.PREFIX) +1:len(file)-len(self.SUFFIX)]]}
        list(map(addTo,fileList))

        return XMLs

    def combineAllXmls(self):
        xmls = {}
        xmls.update(self.predictorXMLs)
        xmls.update(self.dispatchXMLs)
        xmls.update(self.scheduleXMLs)
        xmls.update(self.minSRCXMLs)
        return xmls

    def getSelectedModelsFromSetup(self,setup):
        '''
        Identifies the selected predictor xmls from the model setup file
        :param setup: dictionary produces from reading setup.xml
        :return: dictionary of default values for each xmlfile key
        '''
        #make setup keys lower to match xml keys
        setup = dict(zip(map(str.lower, setup.keys()), setup.values()))
        defaults = {}
        for k in self.xmls.keys():
            for r in self.xmls[k].keys():
                #each key should have a default in the setup file
                try:
                    if k in defaults.keys():
                        defaults[k][r] = setup[r + k +'.value']
                    else:
                        defaults[k] = {r:setup[r + k +'.value']}
                except AttributeError as e:
                    print(e)
        return defaults

    def designateSetupFile(self):
        '''looks for a project setup file and returns the dictionary from reading the file'''

        setupFile = self.controller.dbhandler.getFieldValue('project','setupfile','_id',1)
        if setupFile is None:
            setupFile = os.path.join(os.path.dirname(__file__), *['..', 'Model', 'Resources', 'Setup', 'projectSetup.xml'])
        # read setup (using resource default if necessary)
        setup = self.controller.setupHandler.readInSetupFile(setupFile)
        return setup

    def writeToSetFolder(self,setName):
        for k in self.xmls.keys():
            for r in self.xmls[k].keys():
                editor = self.findChild(XMLEditor,k+r)
                if editor is not None:
                    editor.writeXML(self.xmlDefaults[k][r],setName)