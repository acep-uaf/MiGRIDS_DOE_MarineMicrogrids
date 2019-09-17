# Projet: MiGRIDS
# Created by: # Created on: 9/13/2019
# Purpose :  XMLEditor displays xml forms for a specific selected file
from PyQt5 import QtWidgets, QtCore
import os
import re
from MiGRIDS.UserInterface.GridFromXML import GridFromXML
from bs4 import BeautifulSoup

class XMLEditor(QtWidgets.QWidget):
    SUFFIX = 'Inputs.xml'
    PREFIX = 'project'
    pattern = re.compile(r'([a-z]*)(predict|dispatch|minsrc|schedule)(\d)', re.IGNORECASE)

    def __init__(self,parent,xmllist,xmldefault):
        super().__init__(parent)
        self.xmlOptions = xmllist
        self.default = xmldefault
        self.resourcetype = self.getResourceFromFileName()
        self.xmltype = self.getXMLTypeFromFileName()
        self.setLayout(self.makeLayout())
        self.setContentsMargins(0,0,0,0)
        return

    def hideForm(self):
        '''
        minimizes the widget so input cannot be seen
        :return:
        '''
        self.form.setVisible(False)
        self.titleBar.btn_show.setVisible(True)
        self.titleBar.btn_hide.setVisible(False)
        return

    def showForm(self):
        '''
        expands the widget so inputs are visible
        :return:
        '''
        self.form.setVisible(True)
        self.titleBar.btn_show.setVisible(False)
        self.titleBar.btn_hide.setVisible(True)
        return
    def newXML(self,position):

        self.formStack.setCurrentIndex(position)

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
        self.form = self.makeStack()

        mainLayout.addWidget(self.form)

        self.formStack.setCurrentWidget(self.formStack.findChild(XMLForm,self.default))
        self.form.setVisible(False)
        return mainLayout

    def makeStack(self):
        form = QtWidgets.QWidget()
        self.formStack = QtWidgets.QStackedLayout()
        for x in self.xmlOptions:
            self.formStack.addWidget(self.makeForm(x))
        form.setLayout(self.formStack)
        return form
    def makeForm(self,selectedXML):
        F = XMLForm(selectedXML)
        F.setObjectName(selectedXML)
        F.setVisible(False)
        return F

class XMLForm(QtWidgets.QWidget):
    SUFFIX = 'Inputs.xml'
    PREFIX = 'project'

    def __init__(self,selectedFile):
        super(XMLForm, self).__init__()
        # xml form
        xmlFile = os.path.join(os.path.dirname(__file__),
                               *['..', 'Model', 'Resources', 'Setup', self.PREFIX + selectedFile + self.SUFFIX])
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()

        # TODO soup should come from controller
        soup = BeautifulSoup(contents_child, 'xml')

        myLayout = GridFromXML(self, soup)
        myLayout.setContentsMargins(-1,0,-1,0)
        self.setLayout(myLayout)
        self.setStyleSheet('font-size: 11pt; font-family: Courier;')

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

