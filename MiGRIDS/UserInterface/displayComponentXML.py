# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 8/16/2019
# Purpose :  displayComponentXML
from PyQt5 import QtWidgets

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.Controller.UIHandler import UIHandler
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.componentFormFromXML import componentFormFromXML
from MiGRIDS.UserInterface.getFilePaths import getFilePath

def displayComponentXML(component_name):
    '''

    :param component_name:
    :return:
    '''
    controller = Controller()
    uihandler = UIHandler(controller.dbhandler)
    projectFolder = uihandler.dbHandler.getProjectPath()
    componentDir = getFilePath('Components', projectFolder=projectFolder)
    component_id = uihandler.dbHandler.getId("component",["componentnamevalue"],[component_name])
    component = uihandler.dbHandler.getRecordDictionary("component",component_id)

    try:
        # tell the input handler to create or read a component descriptor and combine it with attributes in component
        componentSoup = uihandler.makeComponentDescriptor(component['componentnamevalue'], componentDir)
        # data from the form gets saved to a soup, then written to xml
        f = componentFormFromXML(component, componentSoup)
    except AttributeError as a:
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Component Information",
                                    "Please complete the components entry before editing tags.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

