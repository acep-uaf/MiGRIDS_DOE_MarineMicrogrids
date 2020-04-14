# Projet: MiGRIDS
# Created by: T. Morgan# Created on: 11/8/2019

from PyQt5 import QtWidgets, QtCore
from MiGRIDS.UserInterface.BaseForm import BaseForm
from MiGRIDS.UserInterface.SetAttributeBlock import SetsAttributeEditorBlock
from MiGRIDS.UserInterface.ModelRunTable import RunTableModel, RunTableView
from MiGRIDS.UserInterface.Pages import Pages

class FormModelRun(BaseForm):
    #model run information and result metadata
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):

        self.setObjectName("modelDialog")
        #the first page is for set0

        self.tabs = Pages(self, 0, SetsAttributeEditorBlock)
        self.tabs.setObjectName('modelPages')

        self.layout = QtWidgets.QVBoxLayout()

        #button to create a new set tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Set')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(lambda:self.newTab(self.getTabCount()))
        self.layout.addWidget(newTabButton)

        #set table goes below the new tab button
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.createRunTable())#, 11, 0, 10, 10)  # Set Id will be negative 1 at creation

        self.setLayout(self.layout)
        self.showMaximized()
        self.controller.sender.statusChanged.connect(self.updateForm)
    def getTabCount(self):
        return len(self.tabs)
    #add a new set to the project, this adds a new tab for the new set information
    def newTab(self,position):
        # get the set count

        widg = SetsAttributeEditorBlock(self, position)
        #widg.fillSetInfo()
        self.tabs.addTab(widg, 'Set' + str(position))

    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    def clearTables(self):
        '''overrides BaseForm clear Tables to call table clear insted of select for run table'''
        tables = self.findChildren(QtWidgets.QTableView)
        for t in tables:
            m = t.model()
            if type(m) is RunTableModel:
                m.clear()
            else:
                 m.select()
    def closeForm(self):
        tables = self.findChildren(QtWidgets.QTableView)
        for t in tables:
            m = t.model()
            if not isinstance(m,RunTableModel): #runtable model doesn't have a submitall method
                m.submitAll()
                print(m.lastError().text())

    def projectLoaded(self):
        tab_count = len(self.controller.dbhandler.getAllRecords('set_'))
        self.displayTabbedData(tab_count,0)  #0 based tabs
        modelForms = self.window().findChildren(SetsAttributeEditorBlock)
        [m.loadSetData() for m in modelForms]  # load data individually for each set
        self.updateForm()

    def createRunTable(self):
        '''Show table of run information'''
        gb = QtWidgets.QGroupBox('Runs')

        tableGroup = QtWidgets.QVBoxLayout()

        tv = RunTableView(self)
        tv.setObjectName('runs')
        self.run_Model = RunTableModel(self)

        # hide the id columns
        #tv.hiddenColumns = [0,1,4,5,26]
        self.run_Model.query()
        tv.setModel(self.run_Model)
        tv.updateRunBaseCase.connect(self.receiveUpdateRunBaseCase)
        tv.reFormat()
        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        #gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #gb.setSizePolicy((QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed))

        return gb
    def updateForm(self):#called on signal from controller.sender
        self.run_Model.refresh()
        return
    def receiveUpdateRunBaseCase(self, id, checked):
        self.controller.dbhandler.updateBaseCase(self.setId, id, checked)
        self.run_Model.refresh()
        self.refreshDataPlot()
