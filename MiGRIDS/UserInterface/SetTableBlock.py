# Projet: MiGRIDS_V2.0
# Created by: # Created on: 7/22/2020
from PyQt5 import QtWidgets

from MiGRIDS.UserInterface.ModelSetTable import SetTableView, SetTableModel
from MiGRIDS.UserInterface.TableBlock import TableBlock
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.makeButton import makeButton


class SetTableBlock(TableBlock):
    """
    Description:
    Attributes:


    """

    def __init__(self, parent,tabPosition):
        self.table = 'sets'
        self.tabPosition = tabPosition
        super().__init__(parent)

    def makeTableView(self):

        self.tableView = SetTableView(self, position=self.tabPosition)
        self.tableView.setObjectName('sets')
        self.tableView.hiddenColumns = [0,1]
        self.tableView.reFormat()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        return
    def makeTableModel(self):
        self.tableModel = SetTableModel(self, self.tabPosition)
        self.tableModel.setFilter('set_id = ' + str(self.tabPosition + 1) + " and tag != 'None'")

    def makeTableButtons(self):
        self.buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()

        buttonRow.addWidget(makeButton(self.parent, lambda: self.functionForNewRecord(),
                                       '+', None,
                                       'Add a component change'))
        buttonRow.addWidget(makeButton(self.parent, lambda: self.functionForDeleteRecord(),
                                       None, 'SP_TrashIcon',
                                       'Delete a component change'))
        buttonRow.addWidget(makeButton(self.parent, lambda: self.functionForRunModels(),
                                       'Run', None,
                                       'Run Set'))
        buttonRow.addStretch(3)

        self.buttonBox.setLayout(buttonRow)
        return

    def functionForDeleteRecord(self):
        self.tableModel.submit()
        self.controller.dbhandler.closeDatabase()
        handler = TableHandler(self)
        handler.functionForDeleteRecord(self.tableView)
        self.controller.createDatabaseConnection()

    def functionForNewRecord(self):
        self.tableModel.submit()
        self.controller.dbhandler.closeDatabase()
        handler = TableHandler(self)
        handler.functionForNewRecord(self.tableView, fields=[1], values=[self.tabPosition + 1])
        self.controller.createDatabaseConnection()

    def functionForRunModels(self):
        self.tableModel.submit()
        self.parent.runModels()
        return
