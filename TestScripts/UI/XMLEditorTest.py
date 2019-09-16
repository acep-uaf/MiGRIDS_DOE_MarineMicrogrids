import unittest
from PyQt5 import QtWidgets, QtTest, QtSql, QtGui, QtCore
import sys

from MiGRIDS.UserInterface.XMLEditor import XMLEditor


class XMLEditorTest(unittest.TestCase):
    app = QtWidgets.QApplication(sys.argv)

    def setUp(self):
        self.window = QtWidgets.QMainWindow()
        self.F = XMLEditor(None,['ReDispatch0','ReDispatch1'],'ReDispatch0')
        self.window.show()
        return

    def test_create(self):
        self.assertFalse(self.F.titleBar.btn_hide.isVisible())
        self.assertFalse(self.F.form.isVisible())

    def test_showForm(self):
        self.F.showForm()
        self.assertTrue(self.F.titleBar.btn_hide.isVisible())
        self.assertTrue(self.F.form.isVisible())

if __name__ == '__main__':
    unittest.main()
