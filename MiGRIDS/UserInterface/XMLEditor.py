# Projet: MiGRIDS
# Created by: # Created on: 9/13/2019
# Purpose :  XMLEditor displays xml forms for a specific selected file
from PyQt5 import QtWidgets, QtCore
import os
import re

from MiGRIDS.Controller.UIToInputHandler import UIHandler
from MiGRIDS.UserInterface.GridFromXML import GridFromXML
from bs4 import BeautifulSoup

from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getFilePaths import getFilePath


class XMLEditor(QtWidgets.QWidget):
    SUFFIX = 'Inputs.xml'
    PREFIX = 'project'
    pattern = re.compile(r'([a-z]*)(predict|dispatch|minsrc|schedule)(\d)', re.IGNORECASE)

    def __init__(self,parent,xmllist,xmldefault):
        super(XMLEditor,self).__init__(parent)
        self.xmlOptions = xmllist
        self.default = xmldefault
        self.dbhandler = ProjectSQLiteHandler()
        self.resourcetype = self.getResourceFromFileName()
        self.xmltype = self.getXMLTypeFromFileName()
        self.setObjectName(self.resourcetype.lower() + self.xmltype.lower())
        self.setLayout(self.makeLayout())
        self.setContentsMargins(0,0,0,0)
        return

    def hideForm(self):
        '''
        minimizes the widget so input cannot be seen
        :return:
        '''
        self.xmlform.setVisible(False)
        self.titleBar.btn_show.setVisible(True)
        self.titleBar.btn_hide.setVisible(False)
        return
    def showForm(self):
        '''
        expands the widget so inputs are visible
        :return:
        '''
        self.xmlform.setVisible(True)
        self.titleBar.btn_show.setVisible(False)
        self.titleBar.btn_hide.setVisible(True)
        return
    def newXML(self,position):

        self.formStack.setCurrentIndex(position)
    def update(self,selected):
        '''remove existing xml forms and create new project specific ones if they are available'''
        cb = self.findChildren(FileSelector)[0]
        cb.setCurrentText(selected)

        for i in reversed(range(self.formStack.count())):
            self.formStack.itemAt(i).widget().setParent(None)

        for x in self.xmlOptions:
            self.formStack.addWidget(self.makeForm(x))

        #self.xmlform.setLayout(self.formStack)
        return
    def getResourceFromFileName(self):
        #resource comes after the prefix, but before the number xmltype
        resourceType =self.pattern.search(self.default).group(1)
        if resourceType == "get":
            resourceType =""
        return resourceType
    def getXMLTypeFromFileName(self):
        x = self.pattern.search(self.default).group(2)
        return x
    def makeTitleBar(self):
        T = TitleBar(self,self.xmlOptions,self.resourcetype,self.default)
        T.btn_hide.clicked.connect(self.hideForm)
        T.btn_show.clicked.connect(self.showForm)
        T.selector.changeFile.connect(self.newXML)
        return T
    def makeLayout(self):
        '''The layout contains a title heading with buttons to expand/reduce and a
        form area derived from the xml it is linked to'''

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(-1, 0, -1, 0)
        mainLayout.setSpacing(1)
        #add a title bar
        self.titleBar = self.makeTitleBar()
        mainLayout.addWidget(self.titleBar)
        #add the form space
        #the possible forms are stacked
        self.xmlform = self.makeStack()

        mainLayout.addWidget(self.xmlform)

        self.formStack.setCurrentWidget(self.formStack.findChild(XMLForm,self.default))
        self.xmlform.setVisible(False)
        return mainLayout
    def makeStack(self):
        '''
        Creates a widget with a a stacked layout containing a xml editing form from all possible xml files
        associated with that resource and xml type
        :return:
        '''
        form = QtWidgets.QWidget()
        self.formStack = self.makeFormStackLayout()
        form.setLayout(self.formStack)
        return form
    def makeFormStackLayout(self):
        '''returns a stacked layout of forms generated from all the xml options'''
        formStack = QtWidgets.QStackedLayout()
        for x in self.xmlOptions:
            formStack.addWidget(self.makeForm(x))
        return formStack
    def makeForm(self,selectedXML):
        ''' Makes an editable xml form based on a designated file'''
        F = XMLForm(selectedXML)
        F.setObjectName(selectedXML)
        F.setVisible(False)
        return F
    def writeXML(self, setName=None):
        #file to write is based on selected file and project
        path = self.dbhandler.getProjectPath()
        if path is not None:
            projectName = self.dbhandler.getProject()
            selected = self.titleBar.selector.currentText()

            fileName = projectName + setName + selected + self.SUFFIX
            if setName == None:
                folder = getFilePath('Setup', projectFolder=path)
            else:
                folder = os.path.join(getFilePath(setName,projectFolder=path),'Setup')
            xmlpath = os.path.join(folder,fileName)
            currentForm = self.findChild(XMLForm,selected)
            currentForm.writeXML(xmlpath)
            self.updateSetupFile(selected[0].lower() + selected[1:],self.objectName())

    def updateSetupFile(self,selectedFile, tag):
        setupFile = self.dbhandler.getFieldValue('project','setupfile','_id','1')
        handler = UIHandler()
        handler.writeTag(setupFile,tag + ".value",selectedFile)

class XMLForm(QtWidgets.QWidget):
    SUFFIX = 'Inputs.xml'
    PREFIX = 'project'

    def __init__(self,selectedFile):
        super(XMLForm, self).__init__()
        contents_child = self.readXml(selectedFile)

        # TODO soup should come from controller
        soup = BeautifulSoup(contents_child, 'xml')

        myLayout = GridFromXML(self, soup)
        myLayout.setContentsMargins(-1,0,-1,0)
        self.setLayout(myLayout)
        self.setStyleSheet('font-size: 11pt; font-family: Courier;')

    def readXml(self, selectedFile):
        # xml form
        with open(self.getFile(selectedFile),"r") as infile_child:
             contents_child = infile_child.read()

        return contents_child

    def getFile(self, selectedFile):
        '''
        returns a project specific file path if there is one, otherwise returns the template
        :param selectedFile:
        :return:
        '''
        dbhandler = ProjectSQLiteHandler()
        projectPath = dbhandler.getProjectPath()
        projectName = dbhandler.getProject()
        xmlFile = ""

        try:
            setupFolder = getFilePath('Setup', projectFolder=projectPath)
            xmlFile = os.path.join(setupFolder, projectName + selectedFile + self.SUFFIX)

        except FileNotFoundError:
            pass
        except TypeError:
            pass
        finally:
            if not os.path.exists(xmlFile):
                 xmlFile = os.path.join(os.path.dirname(__file__),
                               *['..', 'Model', 'Resources', 'Setup', self.PREFIX + selectedFile + self.SUFFIX])
        return xmlFile

    def writeXML(self, file):
        # calls the controller to write an xml file of the optimization config file into the project folder
        handler = UIHandler()
        myGrid = self.findChildren(GridFromXML)[0]

        handler.writeSoup(myGrid.extractValues()[0], file)


class TitleBar(QtWidgets.QWidget):

    def __init__(self, parent, xmlOptions, resourcetype, xmlvalue):
        super(TitleBar, self).__init__()
        '''returns a custom title bar layout with buttons'''
        bar = QtWidgets.QHBoxLayout()
        bar.setContentsMargins(-1, 0, -1, 0)
        self.title = QtWidgets.QLabel(resourcetype)
        bar.addWidget(self.title)
        self.selector = FileSelector(bar,xmlOptions,xmlvalue)
        bar.addWidget(self.selector)
        btn_size = 20
        self.title.setFixedHeight(btn_size)
        self.title.setContentsMargins(0,0,0,0)
        self.title.setAlignment(QtCore.Qt.AlignTop)
        self.setMinimumHeight(btn_size)
        #self.setMaximumHeight(2*btn_size)

        self.btn_hide = QtWidgets.QPushButton("X")
        self.btn_hide.setFixedSize(btn_size, btn_size)
        self.btn_hide.setStyleSheet(" QPushButton { text-align: center; background-color: red;}")
        self.btn_hide.setVisible(False)
        self.btn_hide.setContentsMargins(0,0,0,0)

        self.btn_show = QtWidgets.QPushButton("+")
        self.btn_show.setFixedSize(btn_size, btn_size)
        self.btn_show.setStyleSheet(" QPushButton { text-align: center; background-color: green;}")
        self.btn_show.setVisible(True)

        bar.addWidget(self.btn_hide)
        bar.addWidget(self.btn_show)
        self.setMaximumHeight(btn_size)
        self.setLayout(bar)
        return

class FileSelector(QtWidgets.QComboBox):
    changeFile = QtCore.pyqtSignal(int)
    def __init__(self,parent,items,selected):
        super(FileSelector, self).__init__()
        self.addItems(items)
        self.setCurrentText(selected)
        self.currentIndexChanged.connect(self.selectionChange)


    def selectionChange(self):
        position = self.currentIndex()
        self.changeFile.emit(position)

