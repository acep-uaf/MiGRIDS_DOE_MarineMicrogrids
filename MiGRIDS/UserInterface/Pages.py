# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 8/16/2019
from PyQt5 import QtWidgets

#each page contains information for a single file
#calls the specific page type during initiation

class Pages(QtWidgets.QTabWidget):
    #QtWidget,String, Class ->
    def __init__(self, parent,position,pageclass):
        super().__init__(parent)
        self.position = position
        self.init(pageclass)

    def init(self,pageclass):
        widg = pageclass(self, self.position)
        self.name = "Input " + str(self.position)
        self.addTab(widg, widg.tabName)


