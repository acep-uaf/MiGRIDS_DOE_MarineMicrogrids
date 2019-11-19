# Projet: MiGRIDS
# Created by: # Created on: 11/8/2019
from PyQt5 import QtWidgets, QtCore, QtSql

class CustomProgressBar(QtWidgets.QProgressDialog):
    """
    Description: A custom progress dialog
    Attributes: 
        
        
    """

    def __init__(self,title):
        super().__init__()
        self.initUI(title)

    def initUI(self,title):
        self.setWindowTitle(title)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setObjectName('progresBar')

        self.setAutoReset(True)
        self.setAutoClose(True)

        self.setMinimum(0)
        self.setMaximum(10)

        self.resize(500,100)
        self.show()
        self.setValue(0)
        self.lastValue = 0

    def onProgress(self, i, task):
        self.lastValue += i
        self.setValue(self.lastValue)


    def handleCancel(self):
        #emit cancel signal to all non-ui threads
        #close progressbar
        self.hide()
