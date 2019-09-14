# Projet: MiGRIDS
# Created by: # Created on: 9/13/2019
# Purpose :  XMLEditor displays xml forms for a specific selected file
from PyQt5 import QtWidgets
import os
from MiGRIDS.UserInterface.GridFromXML import GridFromXML
from bs4 import BeautifulSoup

class XMLEditor(QtWidgets.QWidget):
    def __init__(self,xmllist,xmldefault):
        self.xmlOptions = xmllist
        self.default = xmldefault
        self.resourcetype = self.getResourceFromFileName()
        self.xmltype = self.getXMLTypeFromFileName()
        return

    def minimize(self):
        '''
        minimizes the widget so input cannot be seen
        :return:
        '''
        return

    def expand(self):
        '''
        expands the widget so inputs are visible
        :return:
        '''
    def getReourceFromFileName(self):
        return
    def getXMLTypeFromFileName(self):
        return
    def makeLayout(self):
        #title bar with min/expand button
        self.makeTitleBar()
        #xml form
        xmlFile = os.path.join(os.path.dirname(__file__), *['..','Model','Resources',self.default])
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        #TODO soup should come from controller
        soup = BeautifulSoup(contents_child, 'xml')

        myLayout = GridFromXML(self, soup)
        self.setLayout(myLayout)
