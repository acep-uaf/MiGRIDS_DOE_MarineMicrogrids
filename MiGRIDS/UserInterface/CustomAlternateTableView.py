# Projet: MiGRIDS_V2.0
# Created by: # Created on: 7/21/2020
# Purpose :  CustomAlternateTableView
from PyQt5 import QtWidgets

from MiGRIDS.UserInterface.ModelRunTable import HeaderViewWithoutWordWrap


class CustomAlternateTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.hiddenColumns = [1,3,4,7,8]
        self.columns = []
        self.header = HeaderViewWithoutWordWrap()


    def reFormat(self):
        self.setHorizontalHeader(self.header)

        self.horizontalHeader().setFixedHeight(50)
        self.unhideColumns()
        self.hideColumns()

    def unhideColumns(self):
        for i,c in enumerate(self.columns):
            self.setColumnHidden(c,False)

    def hideColumns(self):
        for c in self.hiddenColumns:
            self.hideColumn(c)