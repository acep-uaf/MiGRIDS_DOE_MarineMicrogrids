
import os

from PyQt5 import QtWidgets, QtCore
from MiGRIDS.Controller.UIToInputHandler import UIHandler
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class ResultsPlot(QtWidgets.QWidget):
    def __init__(self,parent,plotName):
        super().__init__(parent)

        self.init(plotName)
    #initialize the form
    def init(self,plotName):
        self.layout = QtWidgets.QGridLayout()
        self.setObjectName(plotName)

        self.refreshButton = self.createRefreshButton()
        #get the current data object
        #print(self.parent().parent().findChildren(QtWidgets.QWidget))

        self.data = None

        #self.displayData = {'fixed': {'x': None, 'y': None}, 'raw': {'x': None, 'y': None}}
        #TODO data will always be None here?

        self.xcombo = self.createCombo([], True)
        self.ycombo = self.createCombo([], False)

        self.plotWidget = self.createPlotArea(self.data)
        self.layout.addWidget(self.plotWidget, 1, 0, 5, 5)
        self.layout.addWidget(self.refreshButton, 0,0,1,2)
        self.layout.addWidget(self.navi_toolbar,1,2,1,2)
        self.layout.addWidget(self.xcombo,7,2,1,1)
        self.layout.addWidget(self.ycombo,3,6,1,1)

        self.setLayout(self.layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    #List, Boolean -> QComboBox
    def createCombo(self,list,x):
        combo = QtWidgets.QComboBox(self)
        combo.addItems(list),
        if x:
            combo.setObjectName('xcombo')
        else:
            combo.setObjectName('ycombo')
        combo.currentIndexChanged.connect(lambda: self.updatePlotData(combo.currentText(),combo.objectName()))
        return combo

    def updatePlotData(self, field, axis):
        #data is the data object
        if self.data is not None:
            if 'displayData' in self.__dict__.keys():
                for s in self.displayData.keys():
                   if axis == 'xcombo':
                       if field != 'index':
                           newx = self.data[s][field]
                           self.displayData[s]['x'] = newx.values
                       else:
                           self.displayData[s]['x'] = self.data[s].index
                   else:
                       if field != 'index':
                            self.displayData[s]['y'] = self.data[s][field].values
                       else:
                           self.displayData[s]['y'] = self.data[s].index


    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
        #update the graph

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    #->plotWidget
    def createPlotArea(self,data):
        from MiGRIDS.UserInterface.PlotResult import PlotResult
        plotWidget = PlotResult(self, data)
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

        if self.data is not None:
            #set the default data to display after fill options
            if 'displayData' not in self.__dict__.keys():
                self.displayData = self.defaultDisplay(self.data)
        else:
            self.displayData = None
        self.plotWidget.makePlot(self.displayData)

    #Navigation
    def home(self):
        self.toolbar.home()
    def zoom(self):
        self.toolbar.zoom()
    def pan(self):
        self.toolbar.pan()

    def defaultDisplay(self):
        return

    def defaultPlot(self):
        return

    def setPlotData(self,data):
        '''sets the data attribute'''
        return


    def revalidate(self):
        return True