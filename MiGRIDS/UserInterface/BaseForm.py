# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 1/24/2020
import glob
import os
from PyQt5 import QtCore, QtWidgets, QtGui

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit, ComboDelegate
from MiGRIDS.UserInterface.ModelRunTable import RunTableModel


class BaseForm(QtWidgets.QWidget):

    """
    Description: 'Form superclass inherited by all forms'
    Attributes: controller
        
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = Controller()
        self.setResultForm()


    def initUI(self):
        pass

    def updateDependents(self, data=None):
        '''called to update components within a form that are dependent on one another'''
        pass
    def setResultForm(self):
        pass
    def onControllerStateChange(self):
        '''called when the data or attributes associated with a controller have changed and information needs to be passed throught the form'''
        pass
    def showChecking(self, title, msg):
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, title, msg                          )
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
        result = msg.exec()
        return result
    def showAlert(self,title,msg):
        '''standard notification dialog'''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,title ,msg
                                    )
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def refreshDataPlot(self):
        '''called to refresh the display on the data plot within the resultForm'''
        resultDisplay = self.parent().findChild(self.resultForm)
        if resultDisplay != None:
            resultDisplay.setData(self.controller.inputData)
            resultDisplay.defaultPlot()

    # def eventFilter(self, ob: 'QObject', ev: 'QEvent'):
    #     '''used to filter events during project switching, or any time the database is closed'''
    #     if ev.type() == QtCore.QEvent.MouseButtonPress:
    #         print("index changed")
    #         return True
    #     else:
    #         print("event")
    #         return False

    def clear(self):
        '''
        Clears the contents of a form and all its subforms
        '''
        # look for tabs and other children to clear
        # tabs get removed completely
        tabWidgets = self.findChildren(QtWidgets.QTabWidget)
        for tw in tabWidgets:
            for t in reversed(range(1,tw.count())):
                tw.removeTab(t)
        subForms = self.findChildren(BaseForm)

        if len(subForms) > 0:
            # clear a widget and all its children widgets then move to the next widget
            subForms[0].clearInput()
            subForms.pop(0)
        else:
            self.clearInput()

    def clearInput(self):
        '''
        Clear the contents of a widget depending on what type of widget it is

        '''
        # input widgets get cleared out - text set to empty string
        inputs = self.findChildren((QtWidgets.QLineEdit, QtWidgets.QTextEdit,
                                      QtWidgets.QComboBox, ClickableLineEdit, ComboDelegate))

        for i in inputs:
            i.installEventFilter(self)
            if type(i) in [QtWidgets.QLineEdit, QtWidgets.QTextEdit, ClickableLineEdit]:
                i.setText("")
            elif type(i) in [QtWidgets.QComboBox]:
                self.reconnect(i.currentIndexChanged, None, self.saveInput)
                i.setCurrentIndex(0)
            i.removeEventFilter(self)


    def clearTables(self):
        '''re-select table contents to reflect current filters'''
        tables = self.findChildren(QtWidgets.QTableView)
        for t in tables:
            m = t.model()
            m.select()
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    @staticmethod
    def reconnect(signal, newhandler=None, oldhandler=None):
        '''
        Connects a new slot to a widget signal and disconnects an old one
        :param signal: the signal to respond to
        :param newhandler: the new function to be called when the signal is triggered
        :param oldhandler: the old function that should be removed from the widgets slot
        :return:
        '''
        try:
            if oldhandler is not None:
                signal.disconnect(oldhandler)
        except TypeError:
            pass
        if newhandler is not None:
            signal.connect(newhandler)

    def newTab(self,i):
        pass

    def displayTabbedData(self,tab_count, start):
        """creates a tab for each input directory specified the SetupModelInformation model inputFileDir attribute.
        Each tab contains a FileBlock object to interact with the data input
        Each FileBlock is filled with data specific to the input directory"""
        #if directories have been entered then replace the first tab and create a tab for each directory
        # self.tabs.removeTab(0)
        if (tab_count > 0) :
            # self.tabs.removeTab(0)
            for i in range(tab_count):
                self.tabs.removeTab(i+start)
                self.newTab((i+start))
        else:
            self.newTab(0 + start)
        return
