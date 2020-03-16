# Projet: MiGRIDS
# Created by: # Created on: 3/12/2020
from PyQt5 import QtWidgets, QtCore

from MiGRIDS.Controller.Controller import Controller


class BaseEditorTab(QtWidgets.QGroupBox):
    """
    Description: methods and attributes of a base tab class
    Attributes: 
        
        
    """

    def __init__(self, parent, tabPosition):
        super().__init__(parent)
        self.BLOCKED = False
        #integer -> FileBlock
        self.controller = Controller()
        self.tabPosition = tabPosition
        self.init(tabPosition)
    def init(self):
        pass
    def createFileTab(self):
        pass
    def saveInput(self):
        pass
    def closeForm(self):
        pass
    def showData(self):
        #suspend signals to update database
        #update all mapped models
        #update all tables
        ##reactivate signals and save data to database
        pass
    def makeForm(self):
        #make all the input fields and tables and buttons
        pass
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        '''calls the specified function connected to a button onClick event'''
        buttonFunction()
