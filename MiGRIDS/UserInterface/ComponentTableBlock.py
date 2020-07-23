# Projet: MiGRIDS_V2.0
# Created by: # Created on: 7/21/2020
from PyQt5 import QtWidgets, QtSql

import MiGRIDS
from MiGRIDS.UserInterface.TableBlock import TableBlock
import MiGRIDS.UserInterface.ModelComponentTable as T
from MiGRIDS.UserInterface.getComponentNameFromDescriptor import getComponentNameFromDescriptor
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeButton import makeButton


class ComponentTableBlock(TableBlock):
    """
    Description: 
    Attributes: 
        
        
    """

    def __init__(self, parent):
        self.table = 'component'
        super().__init__(parent)

    def makeTableView(self):

        self.tableView = T.ComponentTableView(self)
        self.tableView.setObjectName('components')
        self.tableView.reFormat()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        return
    def makeTableModel(self):
        self.tableModel = T.ComponentTableModel(self.parent)
        self.tableModel.beforeUpdate.connect(self.controller.validateInput)

    def makeTableButtons(self):
        '''
        creates buttons associated with table behavior
        :param table: String the name of the table buttons actions are for
        :return: QHBoxLayout
        '''
        self.buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()


        buttonRow.addWidget(makeButton(self.parent, lambda: self.functionForLoadDescriptor(),
                                           None, 'SP_DialogOpenButton',
                                                'Load a previously created component xml file.'))

        buttonRow.addWidget(makeButton(self.parent, lambda: self.functionForNewRecord(),
                                            '+', None,
                                            'Add a component', 'newComponent'))
        buttonRow.addWidget(makeButton(self.parent, lambda: self.functionForDeleteRecord(),
                                       None, 'SP_TrashIcon',
                                            'Delete a component', 'deleteComponent'))
        buttonRow.addStretch(3)
        #self.buttonBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.buttonBox.setLayout(buttonRow)
        # when created buttons are not enabled
        self.buttonBox.setEnabled(True)
        return
    def functionForNewRecord(self):
        # add an empty record to the table
        filedir = self.parent.tabs.currentWidget().findChild(QtWidgets.QWidget, 'inputfiledirvalue').text()
        self.parent.saveInput()
        id = self.controller.dbhandler.getId('input_files', ['inputfiledirvalue'], [filedir])
        self.controller.dbhandler.closeDatabase()
        self.tableHandler.functionForNewRecord(self.tableView, fields=[1], values=[id])
        self.controller.createDatabaseConnection()

        return

    def updateComponentDelegate(self, loi, tv, cmbName):
            '''
            Update the list of possible values for a combobox that uses a ComboDelegate
            :param loi: A list of items to submit as the new combo list
            :param tv: a table view that contains a combo delegate
            :param cmbName: the objectName of the combo delegate
            :return:
            '''
            from MiGRIDS.UserInterface.Delegates import ComboDelegate
            # find the appropriate drop down and replace the list of values
            cbs = [c for c in tv.findChildren(QtWidgets.QItemDelegate) if 'name' in c.__dict__.keys()]
            cbs = [c for c in cbs if c.name == cmbName]
            for c in cbs:

                lm = c.items
                if isinstance(lm, QtSql.QSqlQueryModel):
                    c.updateContent()
                elif isinstance(lm, MiGRIDS.UserInterface.Delegates.RefTableModel):
                    lm.updateModel(loi)
                else:

                    # cbs.addItems(["", "index"] + list(loi))
                    lm.setStringList([''] + list(loi))

    def functionForDeleteRecord(self):
        '''Deletes a selected record'''
        # get selected rows

        # selected is the indices of the selected rows
        selected = self.tableView.selectionModel().selection().indexes()
        if len(selected) == 0:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Select Rows',
                                        'Select rows before attempting to delete')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Confirm Delete',
                                        'Are you sure you want to delete the selected records?')
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            result = msg.exec()

            if result == QtWidgets.QMessageBox.Ok:

                removedRows = []
                for r in selected:
                    if r.row() not in removedRows:

                        self.runSupplementalBehaviors(r)
                        removedRows.append(r.row())
                        self.controller.dbhandler.closeDatabase()
                        self.tableModel.removeRows(r.row(), 1)
                        self.controller.createDatabaseConnection()
                # Delete the record from the database and refresh the tableview
                if not self.tableModel.submitAll():
                    print(self.tableModel.lastError().text())
                self.tableModel.select()
        return

    def runSupplementalBehaviors(self, r):
        '''

        :param r: index of a selected row withing tableModel
        :return:
        '''
        # remove the xml files too
        componentFolder = getFilePath('Components',
                                      projectFolder=self.controller.dbhandler.getProjectPath())
        self.controller.setupHandler.removeDescriptor(self.tableModel.data(self.tableModel.index(r.row(), 3)),
                                                      componentFolder)
        # remove from component table, will be removed from component_files by model
        self.controller.dbhandler.removeRecord('component',
                                               self.controller.dbhandler.getId("component", [
                                                   "componentnamevalue"], [self.tableModel.data(
                                                   self.tableModel.index(r.row(), 4))]))

    def functionForLoadDescriptor(self):
        '''load a descriptor file for a component and populate the project_manager database with its values
        '''

        # identify the xml
        descriptorFile = QtWidgets.QFileDialog.getOpenFileName(self, "Select a descriptor file", None, "*xml")
        if (descriptorFile == ('', '')) | (descriptorFile is None):
            return

        fieldName, ok = QtWidgets.QInputDialog.getText(self, 'Field Name',
                                                       'Enter the name of the channel that contains data for this component.')
        # if a field was entered add it to the table model and database
        if ok:

            filedir = self.parent.findChild(QtWidgets.QWidget, 'inputfiledirvalue').text()
            self.parent.saveInput()
            id = self.controller.dbhandler.getId('input_files', ['inputfiledirvalue'], [filedir])
            component_id = self.controller.dbhandler.getId('component',
                                            ['componentnamevalue'], [
                                                getComponentNameFromDescriptor(
                                                    descriptorFile[0])])
            #if a field name was provided
            if ((fieldName is not None) & (fieldName != '') & (component_id == -1)):
                #new component with a fieldname in the dataframe
                recordValues = [id,fieldName,self.controller.dbhandler.inferComponentType(
                                                          getComponentNameFromDescriptor(descriptorFile[0])),
                                                      component_id]

                self.tableHandler.functionForNewRecord(self.tableView, fields=[1,
                                                             T.ComponentFields.headernamevalue.value,
                                                             T.ComponentFields.componenttype.value,
                                                             T.ComponentFields.component_id.value],
                                              values=recordValues)
            elif (component_id == -1):
                #new component
                #indert into component table then add new record to table
                component_id = self.controller.dbhandler.insertRecord('component',['componentnamevalue'],[getComponentNameFromDescriptor(
                                                    descriptorFile[0])])
                recordValues = [id, fieldName, self.controller.dbhandler.inferComponentType(
                    getComponentNameFromDescriptor(descriptorFile[0])),
                                component_id]

                self.tableHandler.functionForNewRecord(self.tableView, fields=[1,
                                                                               T.ComponentFields.headernamevalue.value,
                                                                               T.ComponentFields.componenttype.value,
                                                                               T.ComponentFields.component_id.value],
                                                       values=recordValues)
            else:
                #existing component, just replacing the fieldname and descriptor file
                self.controller.dbhandler.updateRecord("component_files",["component_id"],[component_id], ["headernamevalue"],[fieldName])
            # copy the file
            self.controller.setupHandler.copyDescriptor(descriptorFile[0],
                                                        getFilePath('Components',
                                                                    projectFolder=self.controller.dbhandler.getProjectPath()))
            self.tableModel.select()
        return