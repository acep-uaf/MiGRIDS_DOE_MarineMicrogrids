# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 11/1/2019

import shutil
import os
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler



def saveProject(pathTo):
    '''saves the current project database to the specified path'''
    path = os.path.dirname(__file__)
    # shutil.copy(os.path.join(path, '../project_manager'),
    #              os.path.join(pathTo, 'project_manager'))
    #
    # print('Database was saved to %s' % os.path.realpath(pathTo))

    return

def clearProjectDatabase(caller=None):

    dbhandler = ProjectSQLiteHandler()

    pathTo = dbhandler.getProjectPath()
    # get the name of the last project worked on
    dbhandler.makeDatabase()
    #also closes the connection
    dbhandler.closeDatabase()
    return pathTo

def clearAppForms(caller):
    '''clears forms associated with the caller'''
    #param: caller [QtWidget] any form that is a child of the main window. All forms will be cleared
    win = caller.window()
    pageTabs = win.pageBlock
    for i in range(pageTabs.count()):
        form = pageTabs.widget(i)
        #clear the data input forms
        form.clear()
        #clearForms(form.findChildren(QtWidgets.QWidget))
    return


#
# def clearForms(listOfWidgets):
#     '''
#     Clears the contents from a list of widgets
#     :param listOfWidgets: List of Widgets
#     :return: None
#     '''
#     if len(listOfWidgets) > 0:
#         #clear a widget and all its children widgets then move to the next widget
#         listOfWidgets[0].clearInput())
#         childs = listOfWidgets[0].findChildren(QtWidgets.QWidget)
#         for c in childs:
#             if c in listOfWidgets:
#                 listOfWidgets.remove(c)
#         return clearForms(listOfWidgets[1:])
#     else:
#         return

# def clearInput(widget):
#     '''
#     Clear the contents of a widget depending on what type of widget it is
#     :param widget: Any QT widget - may have children
#     :return: None
#     '''
#     #look for tabs and other children to clear
#
#     #tabs get removed completely
#     tabWidgets = widget.findChildren(QtWidgets.QTabWidget)
#     for tw in tabWidgets:
#         for t in range(1,tw.count()):
#             tw.removeTab(t)
#     #input widgets get cleared out - text set to empty string
#     inputs = widget.findChildren((QtWidgets.QLineEdit,QtWidgets.QTextEdit,
#                                 QtWidgets.QComboBox,ClickableLineEdit,ComboDelegate))
#
#
#     for i in inputs:
#         i.installEventFilter(widget)
#         if type(i) in [QtWidgets.QLineEdit,QtWidgets.QTextEdit,ClickableLineEdit]:
#             i.setText("")
#         elif type(i) in [QtWidgets.QComboBox]:
#             i.setCurrentIndex(0)
#         i.removeEventFilter(widget)
#     #SQL tables get re-selected, unless its a RunTableModle, then it gets cleared.
#     tables = widget.findChildren(QtWidgets.QTableView)
#     for t in tables:
#         m=t.model()
#         if type(m) is RunTableModel:
#             m.clear()
#         else:
#             m.select()

