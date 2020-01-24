# Projet: MiGRIDS
# Created by: # Created on: 1/24/2020
import glob
import os
from PyQt5 import QtCore, QtWidgets, QtGui

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit, ComboDelegate
from MiGRIDS.UserInterface.ModelRunTable import RunTableModel


class BaseForm(QtWidgets.QWidget):

    """
    Description: 'Form superclass inherited by all forms'
    Attributes:
        
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = Controller()
        self.setResultForm()


    def initUI(self):
        pass

    def updateDependents(self, data=None):
        pass
    def setResultForm(self):
        pass
    def onControllerStateChange(self):
        pass

    def showAlert(self,title,msg):
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,title ,msg
                                    )
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def refreshDataPlot(self):
        resultDisplay = self.parent().findChild(self.resultForm)
        resultDisplay.setData(self.controller.inputData)
        resultDisplay.defaultPlot()

    def eventFilter(self, ob: 'QObject', ev: 'QEvent'):
        '''used to filter events during project switching, or any time the database is closed'''
        if ev.type() == QtCore.QEvent.MouseButtonPress:
            print("index changed")
            return True
        else:
            print("event")
            return False

    def clear(self):
        '''
        Clears the contents of a form and all its subforms
        :param listOfWidgets: List of Widgets
        :return: None
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
        :param widget: Any QT widget - may have children
        :return: None
        '''
        # input widgets get cleared out - text set to empty string
        inputs = self.findChildren((QtWidgets.QLineEdit, QtWidgets.QTextEdit,
                                      QtWidgets.QComboBox, ClickableLineEdit, ComboDelegate))

        for i in inputs:
            i.installEventFilter(self)
            if type(i) in [QtWidgets.QLineEdit, QtWidgets.QTextEdit, ClickableLineEdit]:
                i.setText("")
            elif type(i) in [QtWidgets.QComboBox]:
                i.setCurrentIndex(0)
            i.removeEventFilter(self)
        # SQL tables get re-selected, unless its a RunTableModle, then it gets cleared.

        #self.clearTables()

    def clearTables(self):
        tables = self.findChildren(QtWidgets.QTableView)
        for t in tables:
            m = t.model()
            m.select()
