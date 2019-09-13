# Projet: MiGRIDS
# Created by: # Created on: 9/13/2019
# Purpose :  PredictEditorHolder
import os
from PyQt5 import QtWidgets
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler


class PredictEditorHolder(QtWidgets.QWidget):

    def __init__(self,tab):
        self.tab = tab
        self.set = tab + 1
        #get a dictionary of predictor xml files
        #self.usedPredictors = self.getComponentPredictorList()
        self.setSelectedPredictorsFromSetup()
        self.dbhandler  = ProjectSQLiteHandler()


    def getPredictorFiles(self):
        '''
        Generates a dictionary of possible predictor files to edit based on tags in the mode setup file.
        Only those associated with components in the set will be used
        :return Dictionary of possible predictor xml files for each component'''

        #read all xmls from resource folder
        #resource folder is in the model package
        folder = os.path.join(os.path.dirname(__file__),*['..','Model','Resources','Setup'])
        prefix = 'projectPredict'
        suffix = 'Inputs.xml'
        fileList = [f for f in os.listdir(folder) if (f[-len(suffix):] == suffix) & (f[0:len(prefix)] == prefix)]

        def parseComponentTypeFromFileName(filename):
            componentType = ''.join([i for i in filename[len(prefix):len(suffix)] if not i.isdigit()])
            return componentType.lower()

        #parse into dictionary
        predictorXMLs = {}
        for file in fileList:
            filetype = parseComponentTypeFromFileName(file)
            if  filetype in predictorXMLs.keys():
                predictorXMLs[filetype].append(file)
            else:
                predictorXMLs[filetype] = [file]
        return predictorXMLs

    def setSelectedPredictorsFromSetup(self):
        '''
        Identifies the selected predictor xmls from the model setup file
        :return: modifies predictorXMLs dictionary
        '''

        self.predictorXMLs



