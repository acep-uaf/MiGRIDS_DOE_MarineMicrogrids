# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 11/1/2019

from PyQt5 import QtWidgets
from qtpy import QtCore

import MiGRIDS
from MiGRIDS.Controller.UIHandler import UIHandler
class TableHandler():

    def __init__(self, parent):
        self.parent = parent
    #create a new empty record in the specified table
    #String -> None
    def functionForNewRecord(self, table, **kwargs):

        # add an empty record to the table

        # get the model
        tableView = self.parent.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        model.submitAll()
        debugvar = model.rowCount()
        # insert an empty row as the last record
        model.insertRows(model.rowCount(), 1)
        #model.setData(model.index(model.rowCount() -1,0), None) #id field nees to remain empty until data is inserted
        #this makes the first column editable (set, filedir, ect.)
        #tableView.openPersistentEditor(model.index(model.rowCount()-1, 1))
        #model.setData(model.index(model.rowCount() - 1, 1), 1)

        #insert values that were passed in through optional arguments
        #fields are integer column positions
        fields = kwargs.get('fields')
        if fields:
            values = kwargs.get('values')
            for i,n in enumerate(fields):
                tableView.model().setData(model.index(model.rowCount()-1, n), values[i],QtCore.Qt.EditRole)

        result = model.submitAll()
        if result == False:
            print(model.lastError().text())
    # update the component drop down in the set table to include the selected or default components
    def updateComponentDelegate(self, loi,tv,cmbName):
        '''
        Update the list of possible values for a combobox that uses a ComboDelegate
        :param loi: A list of items to submit as the new combo list
        :param tv: a table view that contains a combo delegate
        :param cmbName: the objectName of the combo delegate
        :return:
        '''
        from MiGRIDS.UserInterface.Delegates import ComboDelegate, ComponentFormOpenerDelegate
        # find the appropriate drop down and replace the list of values
        cbs = tv.findChildren(ComboDelegate)
        for c in cbs:
            if c.name == cmbName:
                lm = c.values

                if isinstance(lm,MiGRIDS.UserInterface.Delegates.RefTableModel):
                    lm.updateModel(loi)
                else:

                    #cbs.addItems(["", "index"] + list(loi))
                    lm.setStringList([''] + list(loi))

    #removes selected records from the table and its underlying sql table
    #String -> None
    def functionForDeleteRecord(self, table):
        # get selected rows
        tableView = self.parent.findChild((QtWidgets.QTableView), table)
        model = tableView.model()
        # selected is the indices of the selected rows
        selected = tableView.selectionModel().selection().indexes()
        if len(selected) == 0:
            #exit if no rows were selected
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Select Rows',
                                        'Select rows before attempting to delete')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

        else:
            #confirm delete
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Confirm Delete',
                                        'Are you sure you want to delete the selected records?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            result = msg.exec()

            if result == 1024:
                handler = UIHandler()
                for r in selected:
                    model.removeRows(r.row(), 1)

                # Delete the record from the database and refresh the tableview
                model.submitAll()
                print(model.lastError().text())
                model.select()

        return