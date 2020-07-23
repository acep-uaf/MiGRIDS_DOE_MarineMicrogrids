# Projet: MiGRIDS_V2.0
# Created by: # Created on: 7/21/2020
from PyQt5 import QtWidgets

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.UserInterface.TableHandler import TableHandler


class TableBlock(QtWidgets.QGroupBox):
    """
    Description: class to handle custom table views and their data models
    Attributes: tableView - QTableView
                tableModel - QModel
        
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.controller = Controller()
        self.parent = parent
        self.tableHandler = TableHandler(self)
        self.makeLayout()
        self.setLayout(self.layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def makeLayout(self):

        self.layout = QtWidgets.QVBoxLayout()
        self.makeTableButtons()
        self.layout.addWidget(self.buttonBox)
        self.makeTableView()
        self.makeTableModel()
        self.displayData()
        self.tableView.reFormat()
        self.layout.addWidget(self.tableView,1)

        return

    def makeTableView(self):
        pass
    def makeTableModel(self):
        pass
    def makeTableButtons(self):
        pass

    def displayData(self):
        self.tableView.setModel(self.tableModel)

    def runSupplementalBehaviors(self):
         pass