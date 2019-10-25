from PyQt5 import QtWidgets, QtCore
from bs4 import BeautifulSoup
import os
from MiGRIDS.UserInterface.GridFromXML import GridFromXML
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.UIToInputHandler import UIHandler

class FormOptimize(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.init()

    def init(self):
        self.setObjectName("modelDialog")
        self.dbhandler = ProjectSQLiteHandler()
        widget = QtWidgets.QWidget()
        #main layout is vertical
        vlayout = QtWidgets.QVBoxLayout(self)
        #button block
        buttonBlock = QtWidgets.QGroupBox('Start Optimization',self)
        buttonBlock.setLayout(self.fillButtonBlock())
        vlayout.addWidget(buttonBlock)
        # read the config xml
        xmlFile = os.path.join(os.path.dirname(__file__), '../Optimizer/Resources/optimizerConfig.xml' )
        infile_child = open(xmlFile, "r")  # open
        contents_child = infile_child.read()
        infile_child.close()
        soup = BeautifulSoup(contents_child, 'xml')

        myLayout = GridFromXML(self, soup)
        widget.setLayout(myLayout)
        widget.setObjectName('inputGrid')
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        scrollArea.setWidget(widget)
        vlayout.addWidget(scrollArea)
        self.setLayout(vlayout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.showMaximized()
        return

    def fillButtonBlock(self):
        buttonLayout = QtWidgets.QHBoxLayout()

        runButton = makeButtonBlock(self, self.startOptimize, text='START', icon=None, hint='Start optimization process')
        stopButton = makeButtonBlock(self, None, text='STOP', icon=None, hint='Stop optimization process')
        buttonLayout.addWidget(runButton)
        buttonLayout.addWidget(stopButton)
        return buttonLayout

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):

        buttonFunction()
        return
    #start running the optimize routine
    def startOptimize(self):
        #make sure values are up to date
        self.updateStoredValues()
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,'Not implemented','If I knew how to optimize I would do it now.')
        msg.show()
        return
    #stop running the optimize routine
    def stopOptimize(self):
        return
    #if we leave the optimize form the parameters that we changed are updated
    def leaveEvent(self, event):
        self.updateStoredValues()
        return

    def writeXML(self,soup):
        #calls the controller to write an xml file of the optimization config file into the project folder
        handler = UIHandler()
        myGrid = self.findChildren(GridFromXML)[0]
        outFile = 'optimizerConfig.xml'
        outFile = os.path.join(getFilePath('Optimize',projectFolder = self.dbhandler.getProjectFolder()),outFile)
        handler.writeSoup(myGrid.extractValues()[0],outFile)

    def updateStoredValues(self):
        #find the data input grid
        myGrid = self.findChildren(GridFromXML)[0]
        #get a soup of values that have changed
        newSoup, changes = myGrid.extractValues()


        #write changes to the database
        for k in changes.keys():
            #if we return false upldate the existing parameter
            if not self.dbHandler.insertRecord('optimize_input', ['parameter','parameter_value'], [k,changes[k]]):
                self.dbHandler.updateRecord('optimize_input',['parameter'],[k],['parameter_value'],[changes[k]])

        #write to project file
        self.writeXML(newSoup)
        return

    def revalidate(self):
        return True