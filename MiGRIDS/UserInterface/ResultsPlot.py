
import os

from PyQt5 import QtWidgets, QtCore, QtSql

from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from MiGRIDS.UserInterface.PlotResult import PlotResult

class ResultsPlot(QtWidgets.QWidget):
    def __init__(self,parent,plotName):
        super().__init__(parent)

        self.init(plotName)
    #initialize the form
    def init(self,plotName):
        self.dbhandler = ProjectSQLiteHandler()
        self.layout = QtWidgets.QGridLayout()
        self.setObjectName(plotName)
        self.plotName = plotName
        self.refreshButton = self.createRefreshButton()
        #get the current data object
        #print(self.parent().parent().findChildren(QtWidgets.QWidget))

        self.data = None

        #self.displayData = {'fixed': {'x': None, 'y': None}, 'raw': {'x': None, 'y': None}}
        #TODO data will always be None here?

        self.xcombo = self.createCombo('xcombo')
        self.ycombo = self.createCombo('ycombo')

        self.plotWidget = self.createPlotArea()
        self.layout.addWidget(self.plotWidget, 1, 0, 5, 5)
        self.layout.addWidget(self.refreshButton, 0,0,1,2)
        self.layout.addWidget(self.navi_toolbar,1,2,1,2)
        self.layout.addWidget(self.xcombo,7,2,1,1)
        self.layout.addWidget(self.ycombo,3,6,1,1)

        self.setLayout(self.layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.defaultPlot()

    def createCombo(self,name):
        combo = QtWidgets.QComboBox(self)
        combo.setObjectName(name)
        combo.currentIndexChanged.connect(self.updatePlotData)
        return combo


    def updatePlotData(self):
        #data is the data object
        self.data = self.getData()

    def getSelectedX(self):
        return self.xcombo.currentText()
    def getSelectedY(self):
        return self.ycombo.currentText()

    def getdata(self, field, axis):
        pass

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
        #update the graph

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    def createPlotArea(self):

        plotWidget = PlotResult(self, self.data,self.plotName)
        self.navi_toolbar = NavigationToolbar(plotWidget, self)

        #self.toolbar.hide()
        return plotWidget

    #->QPushButton
    def createRefreshButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Refresh plot")
        button.clicked.connect(self.refreshPlot)
        return button

    #refresh the data plot with currently set data
    def refreshPlot(self):
        #update drop downs

        self.plotWidget.makePlot(self.data)

    #Navigation
    def home(self):
        self.toolbar.home()
    def zoom(self):
        self.toolbar.zoom()
    def pan(self):
        self.toolbar.pan()

    def defaultDisplay(self):
        pass


    def defaultPlot(self):
        pass

    def setPlotData(self,data):
        '''sets the data attribute'''
        self.data = data
        return

    def set_X(self, v):
        # each item in x is vector representing a series
        if isinstance(v, list):
            self.y = [i for i in v]
        else:
            self.y[0] = v
        return
    def set_Y(self, v):
        # each item in y is vector representing a series
        if isinstance(v, list):
            self.y = [i for i in v]
        else:
            self.y[0] = v
        return
    def set_XCombo(self, v):
        '''set the drop down options for the x axis'''
        if isinstance(v,QtSql.QSqlQueryModel):
            r = v.rowCount()
            self.xcombo.setModel(v)
            self.Xoptions = self.xcombo.currentData()
        else:
            self.Xoptions = v
            self.xcombo.clear()
            self.xcombo.addItems(self.Xoptions)

        return
    def showPlot(self):
        if self.data is not None:
            self.plotWidget.makePlot(self.data)

    def set_YCombo(self, v):
        '''set the drop down options for the y axix'''
        if isinstance(v, QtSql.QSqlQueryModel):
            self.ycombo.setModel(v)
            self.Yoptions = self.ycombo.currentData()
        else:
            self.Yoptions = v
            self.ycombo.clear()
            self.ycombo.addItems(self.Yoptions)

        return
    def revalidate(self):
        pass