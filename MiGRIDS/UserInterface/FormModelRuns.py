# Projet: MiGRIDS
# Created by: T. Morgan# Created on: 11/8/2019

from PyQt5 import QtWidgets, QtCore, QtSql
from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.UserInterface.BaseForm import BaseForm
from MiGRIDS.UserInterface.CustomProgressBar import CustomProgressBar
from MiGRIDS.UserInterface.ResultsModel import ResultsModel
from MiGRIDS.UserInterface.SetAttributeBlock import SetsAttributeEditorBlock
from MiGRIDS.UserInterface.XMLEditor import XMLEditor
from MiGRIDS.UserInterface.XMLEditorHolder import XMLEditorHolder
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.ModelSetTable import SetTableModel, SetTableView
from MiGRIDS.UserInterface.ModelRunTable import RunTableModel, RunTableView
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit
from MiGRIDS.UserInterface.Pages import Pages
from MiGRIDS.UserInterface.DialogComponentList import ComponentSetListForm
from MiGRIDS.UserInterface.qdateFromString import qdateFromString
from MiGRIDS.InputHandler.InputFields import *
import datetime
import os

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
        newTabButton.clicked.connect(self.newTab)
        self.layout.addWidget(newTabButton)

        #set table goes below the new tab button
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)
        self.showMaximized()
    #add a new set to the project, this adds a new tab for the new set information
    def newTab(self):
        # get the set count
        tab_count = self.tabs.count()
        widg = SetsAttributeEditorBlock(self, tab_count)
        #widg.fillSetInfo()
        self.tabs.addTab(widg, 'Set' + str(tab_count))

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

