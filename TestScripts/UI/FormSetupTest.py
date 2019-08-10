import unittest
import sys
import os
from pathlib import Path
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
        #project without a database saved
        setupFile = os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects','SampleProject','InputData','Setup','SampleProjectSetup.xml')
        self.F.loadSetup(setupFile)
        #the setup information sets form attributes
        self.assertEqual(self.F.project, 'SampleProject')
        self.assertEqual(os.path.normpath(os.path.join('Users','tmorga22','Documents','MiGRIDS','MiGRIDSProjects','SampleProject')),os.path.normpath(os.path.join('Users','tmorga22','Documents','MiGRIDS','MiGRIDS','..','MiGRIDSProjects','SampleProject')))


        self.assertEqual(os.path.normpath(self.F.projectFolder), os.path.normpath(os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects','SampleProject')))
        #data also goes into a database
        dbhandler = ProjectSQLiteHandler()
        self.assertEqual(os.path.normpath(dbhandler.getProjectPath()),os.path.normpath(os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects','SampleProject')))

        #There should be 2 components in the database
        self.assertEqual(2, len(dbhandler.getAllRecords('component')))
        self.assertEqual(3, len(dbhandler.getAllRecords('input_files')))
        self.assertEqual(3, len(dbhandler.getAllRecords('component_files')))

        #There should be 3 file tabs
        self.assertEqual(len(self.F.tabs),3)
        fileblock1= self.F.findChildren(QtWidgets.QTabWidget)[0] #The first one in the list corresponds to Input 1
        #self.assertEqual((fileblock1.findChild(QtWidgets.QLineEdit,'inputfiledirvalue')).text(), os.path.join('SampleProject','InputData','TimeSeriesData','RawData','HighRes'))

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

