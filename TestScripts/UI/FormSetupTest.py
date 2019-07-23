import unittest
import sys
import os
from PyQt5 import QtWidgets, QtTest, QtSql, QtGui, QtCore
from MiGRIDS.UserInterface.FormSetup import FormSetup

from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler


class FormSetupTest(unittest.TestCase):
    app = QtWidgets.QApplication(sys.argv)

    @classmethod
    def setUpClass(cls):
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('project_manager')

        handler = ProjectSQLiteHandler()
        # get the name of the last project worked on
        lastProjectPath = handler.getProjectPath()
        handler.makeDatabase()
    '''@classmethod
    def tearDownClass(cls):
        os.remove(os.path.join(os.path.dirname(__file__), 'project_manager'))'''

    def setUp(self):
        self.window = QtWidgets.QMainWindow()
        self.F = FormSetup(self.window)
        self.window.show()

    def tearDown(self):
        self.window.close()


    def testCreateSetup(self):

        #the window main window exists
        self.assertTrue(isinstance(self.window,QtWidgets.QMainWindow))
        self.assertTrue(self.window.isVisible())

        #FormSetup is created
        self.assertTrue(isinstance(self.F, QtWidgets.QWidget))

        #comboboxes have correct options and defaults set
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget,'inputfiletypevalue'), QtWidgets.QComboBox))


    def test_LoadSetup(self):
        #information is read in from an existing setup file
        return

    def test_createInputFiles(self):
        #create input files based on input collected in FormSetup and stored in project_manager database
        return

    def modelItems(self,cmb):
        l = []
        for i in range(0,cmb.count()):
            l.append(cmb.itemData(i,QtCore.Qt.DisplayRole))
        return l

if __name__ == '__main__':

    unittest.main()

