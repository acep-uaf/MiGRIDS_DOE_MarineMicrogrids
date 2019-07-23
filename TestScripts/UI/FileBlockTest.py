import unittest
import sys
import os
from PyQt5 import QtWidgets, QtTest, QtSql, QtGui, QtCore
from MiGRIDS.UserInterface.FileBlock import FileBlock

from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler


class FileBlockTest(unittest.TestCase):
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
        self.F = FileBlock(self.window, 1)
        self.window.show()

    def tearDown(self):
        self.window.close()


    def testCreateFileBlock(self):

        #the window main window exists
        self.assertTrue(isinstance(self.window,QtWidgets.QMainWindow))
        self.assertTrue(self.window.isVisible())

        #FileBlock is created and has a tab position of 1, and is unvalidated
        self.assertTrue(isinstance(self.F, QtWidgets.QWidget))
        self.assertEqual(self.F.tabPosition,1)
        self.assertFalse(self.F.validated)


        #comboboxes have correct options and defaults set
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget,'inputfiletypevalue'), QtWidgets.QComboBox))
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget, 'datechannelvalue'), QtWidgets.QComboBox))
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget, 'timechannelvalue'), QtWidgets.QComboBox))
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget, 'timechannelformat'), QtWidgets.QComboBox))
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget, 'datechannelformat'), QtWidgets.QComboBox))
        self.assertTrue(isinstance(self.F.findChild(QtWidgets.QWidget, 'timezonevalue'), QtWidgets.QComboBox))
        self.assertEqual(self.F.findChild(QtWidgets.QWidget, 'inputfiletypevalue').currentText(),'CSV')
        self.assertEqual(self.F.findChild(QtWidgets.QWidget, 'timezonevalue').currentText(), 'America/Anchorage')
        #component table is disabled
        self.assertFalse(self.F.ComponentButtonBox.isEnabled())

    def test_fillFileBlock(self):

        #file directory starts off empty
        self.assertEqual(self.F.findChild(QtWidgets.QWidget,'inputfiledirvalue').text(),'')
        dateFields = []
        self.assertListEqual(dateFields, self.modelItems(self.F.findChild(QtWidgets.QComboBox, 'datechannelvalue')))
        dataPath = os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects','SampleProject','InputData','TimeSeriesData','RawData','HighRes')
        self.F.findChild(QtWidgets.QWidget, 'inputfiledirvalue').setFocus(True)
        QtTest.QTest.keyClicks(self.F.findChild(QtWidgets.QWidget,'inputfiledirvalue'),dataPath)
        self.F.findChild(QtWidgets.QWidget, 'inputfiledirvalue').setFocus(False)
        self.assertEqual(self.F.findChild(QtWidgets.QWidget, 'inputfiledirvalue').text(), dataPath)


        self.F.findChild(QtWidgets.QWidget, 'timezonevalue').setFocus(True)
        self.assertTrue(self.F.findChild(QtWidgets.QWidget, 'timezonevalue').hasFocus())

        #filling the directory changes database record and model info
        handler = ProjectSQLiteHandler()

        # filling directory triggers preview which changed field dropdowns and sets default values
        self.assertTrue(handler.cursor.execute("SELECT inputfiledirvalue FROM input_files").fetchone()!= None)
        self.assertEqual((handler.cursor.execute("SELECT inputfiletypevalue FROM input_files").fetchone())[0], 'CSV')
        #the files in the high res sample project folder have the headings DATE and Villagekw
        dateFields = ['','index','DATE','Villagekw']
        self.assertListEqual(dateFields, self.modelItems(self.F.findChild(QtWidgets.QComboBox, 'datechannelvalue')))

        #if selected directory has valid data the component table becomes active

        self.assertTrue(self.F.ComponentButtonBox.isEnabled())
    def test_fillComponentBlock(self):
        dataPath = os.path.join(os.path.dirname(__file__), '..', '..', 'MiGRIDSProjects', 'SampleProject', 'InputData',
                                'TimeSeriesData', 'RawData', 'HighRes')
        self.F.findChild(QtWidgets.QWidget, 'inputfiledirvalue').setFocus(True)
        QtTest.QTest.keyClicks(self.F.findChild(QtWidgets.QWidget, 'inputfiledirvalue'), dataPath)
        self.F.findChild(QtWidgets.QWidget, 'inputfiledirvalue').setFocus(False)
        self.F.findChild(QtWidgets.QWidget, 'timezonevalue').setFocus(True)
        #self.assertTrue(self.F.ComponentButtonBox.isEnabled())

        self.F.ComponentButtonBox.setEnabled(True)
        #test adding a row
        QtTest.QTest.mouseClick(self.F.findChild(QtWidgets.QPushButton,'newComponent'),QtCore.Qt.LeftButton)
        self.assertEqual(self.F.ComponentTable.model().rowCount(),1)

    def modelItems(self,cmb):
        l = []
        for i in range(0,cmb.count()):
            l.append(cmb.itemData(i,QtCore.Qt.DisplayRole))
        return l

if __name__ == '__main__':

    unittest.main()

