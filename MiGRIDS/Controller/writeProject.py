# Projet: MiGRIDS
# Created by: # Created on: 11/13/2019
# Purpose :  writeProject()
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.Controller.SetupHandler import SetupHandler


def writeProject():
    runHandler = RunHandler()
    setupHandler = SetupHandler()
    dbhandler = ProjectSQLiteHandler()

    #write setup
    #write sets
