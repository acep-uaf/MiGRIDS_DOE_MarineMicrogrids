# Projet: MiGRIDS
# Created by: T.Morgan # Created on: 3/12/2020
import datetime

import os
from PyQt5 import QtWidgets, QtSql, QtCore

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.InputHandler.InputFields import COMPONENTNAMES
from MiGRIDS.UserInterface.BaseEditorTab import BaseEditorTab
from MiGRIDS.UserInterface.CustomProgressBar import CustomProgressBar
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit
from MiGRIDS.UserInterface.DialogComponentList import ComponentSetListForm
from MiGRIDS.UserInterface.ModelRunTable import RunTableView, RunTableModel
from MiGRIDS.UserInterface.ModelSetTable import SetTableView, SetTableModel
from MiGRIDS.UserInterface.ResultsModel import ResultsModel
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.XMLEditor import XMLEditor
from MiGRIDS.UserInterface.XMLEditorHolder import XMLEditorHolder
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.qdateFromString import qdateFromString


class SetsAttributeEditorBlock(BaseEditorTab):
    '''
    The setAttributeEditorBlock contains inputs to determin what runs will occurr within a set and displays run results
    '''
    def __init__(self, parent, tabPosition):
        super().__init__(parent,tabPosition)

    def init(self, tabPosition):

        self.defaultComponents = []
        self.setName = "Set" + str(tabPosition) #set name is a string with a prefix
        self.tabName = "Set " + str(tabPosition)
        self.setId = self.controller.dbhandler.getSetId(str(tabPosition))
        if (self.setId == -1) & (self.controller.dbhandler.getProject() != None):
            self.setId = self.controller.dbhandler.insertRecord('set_',['set_name','project_id'],[self.setName,1])
            #update components to the default list
            components = self.controller.dbhandler.getComponentNames()
            self.controller.dbhandler.updateSetComponents(self.setName, components)

        #main layouts
        self.makeForm()
    def makeForm(self):
        tableGroup = QtWidgets.QGridLayout()

        # setup info for a set
        self.setInfo = self.makeSetInfoCollector()  # edits on setup attributes
        tableGroup.addWidget(self.infoBox, 0, 0, 1, 10)

        # buttons for adding and deleting component attribute edits - edits to descriptor files
        tableGroup.addWidget(self.dataButtons('sets'), 1, 0, 1, 3)

        # table of descriptor file changes to be made
        # the table view filtered to the specific set for each tab
        tv = SetTableView(self, position=self.tabPosition)
        tv.setObjectName('sets')
        self.set_componentsModel = SetTableModel(self, self.tabPosition)
        self.set_componentsModel.setFilter('set_id = ' + str(self.tabPosition + 1) + " and tag != 'None'")
        tv.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.updateComponentLineEdit(
            self.controller.dbhandler.getComponentNames())  # update the clickable line edit to show current components

        self.set_componentsModel.select()

        tv.setModel(self.set_componentsModel)

        # hide the id column
        tv.hiddenColumns = [0, 1]
        tv.reFormat()

        tableGroup.addWidget(tv, 2, 0, 8, 4)

        # xmlEditing block
        self.xmlEditor = XMLEditorHolder(self, self.tabPosition)
        tableGroup.addWidget(self.xmlEditor, 2, 4, 8, 6)
        self.setLayout(tableGroup)

        # make the run result table
        tableGroup.addWidget(self.createRunTable(str(self.setId)), 11, 0, 10,
                             10)  # Set Id will be negative 1 at creation
        # self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.fillSetInfo(str(self.tabPosition))

    def updateForm(self):
        '''refreshes data displayed in form based on any changes made in database or xml model files'''
        self.setId = self.controller.dbhandler.getSetId(str(self.tabPosition))
        self.set_model.select() #update the set data inputs
        self.set_model.setFilter('set_._id = ' + str(self.setId))
        self.setValidators() #update the validators tied to inputs
        self.mapper.toLast() #make sure the mapper is on the actual record (1 per tab)
        #self.setModel.submit() #submit any data that was changed
        #print(self.setModel.lastError().text())
        self.updateComponentLineEdit(self.controller.dbhandler.getComponentNames()) # update the clickable line edit to show current components
        #self.updateComponentDelegate(self.controller.dbhandler.getComponentNames())

        self.set_componentsModel.select()

        self.xmlEditor.updateWidget() #this relies on xml files, not the database
        self.run_Model.refresh(self.setId)
        self.rehide(self.findChild(QtWidgets.QTableView,'runs'),[0,1,26])
        self.rehide(self.findChild(QtWidgets.QTableView,'sets'), [0,1])
        self.updateDependents()
    def rehide(self,tview,loc):
        for i in loc:
            tview.hideColumn(i)
    def submitData(self):
        #result = self.setModel.submitAll()
        #print(self.setModel.lastError().text())
        result = self.set_componentsModel.submitAll()
        print(self.set_componentsModel.lastError().text())
    def updateComponentLineEdit(self,listNames):
        '''component line edit is unbound so it gets called manually to update'''
        lineedit = self.infoBox.findChild(ClickableLineEdit,'componentNames')
        lineedit.setText(",".join(listNames))
        return
    def getDefaultDates(self):

        start,end = self.controller.dbhandler.getSetupDateRange()

       #format the tuples from database output to datetime objects
        if (start == None) | (start == (None,)) | (start == 'None'): #no date data in the database yet
            #end = datetime.datetime.today().strftime('%Y-%m-%d')
            end = datetime.datetime.today()
            start = datetime.datetime.today() - datetime.timedelta(days=365)
        elif type(start)== str:
            start = datetime.datetime.strptime(start, '%Y-%m-%d')
            end = datetime.datetime.strptime(end, '%Y-%m-%d')
        else:
            start = datetime.datetime.strptime(start[0], '%Y-%m-%d')
            end = datetime.datetime.strptime(end[0], '%Y-%m-%d')

        return start, end
    def setSetDates(self,setInfo):
        '''
        :param setName:
        :return:
        '''

        self.startDate = setInfo['date_end']
        self.endDate = setInfo['date_start']
        return
    def makeSetInfoCollector(self):
        '''
        Creates the input form for fields needed to create and run a model set
        :param kwargs: String set can be passed as a keyword argument which refers to the setname in the project_manager database tble setup
        :return: QtWidgets.QGroupbox input fields for a model set
        '''
        self.infoBox = self.makeSetLayout()
        self.set_model = self.makeSetModel()
        self.mapWidgets()

        return
    def updateModel(self):
        self.set_model.select()
        self.set_model.setFilter('set_._id = ' + str(self.setId))
        self.runModel.query()
    def makeSetLayout(self):
        infoBox = QtWidgets.QGroupBox()
        infoRow = QtWidgets.QHBoxLayout()
        # time range filters
        infoRow.addWidget(QtWidgets.QLabel('Filter Date Range: '))
        ds = self.makeDateSelector(True)
        infoRow.addWidget(ds)
        infoRow.addWidget(QtWidgets.QLabel(' to '))
        de = self.makeDateSelector(False)
        infoRow.addWidget(de)
        infoRow.addWidget(QtWidgets.QLabel('Timestep:'))
        #timestepWidget = QtWidgets.QLineEdit('1')
        timestepWidget = QtWidgets.QDoubleSpinBox()
        timestepWidget.setRange(1,86400)
        timestepWidget.setDecimals(0)
        timestepWidget.setObjectName(('timestepvalue'))
        #timestepWidget.setValidator(QtGui.QIntValidator(1,86400))
        infoRow.addWidget(timestepWidget)
        infoRow.addWidget(QtWidgets.QLabel('Seconds'), 1)
        infoRow.addWidget(QtWidgets.QLabel('Components'))
        infoRow.addWidget(self.componentSelector(), 2)
        infoBox.setLayout(infoRow)
        return infoBox

    def loadSetData(self):
        # load and update from set setup file
        # self.controller.runHandler.loadExistingProjectSet(self.setName)
        # load and update from attributeXML
        # load and update from xml resources
        self.updateForm()
        return
    def setValidators(self):
        #timesteps need to be equal to or greater than te setup timestep
        minSeconds = self.controller.dbhandler.getFieldValue('setup','timestepvalue','_id',1)
        units = self.controller.dbhandler.getFieldValue('setup','timestepunit','_id',1)
        if units.lower() != 's':
            minSeconds = self.controller.dbhandler.convertToSeconds(minSeconds,units)
        timestepWidget = self.infoBox.findChild(QtWidgets.QDoubleSpinBox,'timestepvalue')
        #timestepWidget.setValidator(QtGui.QIntValidator(int(minSeconds),86400))
        timestepWidget.setMinimum(int(minSeconds))
        def constrainDateRange(dateWidget,start,end):
            dateWidget.setMinimumDate(start)
            dateWidget.setMaximumDate(end)
        #start date needs to be equal to or greater than the setup start
        start, end = self.controller.dbhandler.getSetupDateRange()
        wids = self.infoBox.findChildren(QtWidgets.QDateEdit)


        list(map(lambda w: constrainDateRange(w,qdateFromString(start),qdateFromString(end)), wids))
    def mapWidgets(self):
        '''
        create a widget mapper object to tie fields to data in database tables
        :return:
        '''
        # map model to fields
        self.mapper = QtWidgets.QDataWidgetMapper()
        self.mapper.setModel(self.set_model)
        self.mapper.setItemDelegate(QtSql.QSqlRelationalDelegate())

        # map the widgets we created with our dictionary to fields in the sql table
        for i in range(0, self.set_model.columnCount()):
            if self.infoBox.findChild(QtWidgets.QWidget, self.set_model.record().fieldName(i)) != None:
                wid = self.infoBox.findChild(QtWidgets.QWidget, self.set_model.record().fieldName(i))
                self.mapper.addMapping(wid, i)
                if isinstance(wid,QtWidgets.QDateEdit):
                    wid.setDate(qdateFromString(self.set_model.data(self.set_model.index(0, i))))

        # submit data changes automatically on field changes -this doesn't work
        self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.AutoSubmit)
        self.mapper.toFirst()
        return
    def makeSetModel(self):
        # set model
        infoRowModel = QtSql.QSqlRelationalTableModel()
        infoRowModel.setTable("set_")

        infoRowModel.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        infoRowModel.select();
        infoRowModel.setFilter('set_._id = ' + str(self.setId))
        infoRowModel.select()
        infoRowModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        return infoRowModel
    def componentSelector(self):

        #if components are not provided use the default list

        allcomponents = self.controller.dbhandler.getComponentNames()
        #setcomponents = self.controller.dbhandler.getSetComponentNames(self.setName)

        widg = ClickableLineEdit(','.join(allcomponents)) #all are selectable
        widg.setText(','.join(allcomponents))
        widg.setObjectName('componentNames')

        widg.clicked.connect(lambda: self.componentCellClicked())
        return widg
    def fillSetInfo(self,setName = '0'):

        setInfo = self.controller.dbhandler.getSetInfo('set' + str(setName))
        if setInfo != None:
            if type(setInfo[COMPONENTNAMES]) == str:
                self.defaultComponents = setInfo[COMPONENTNAMES].split(',')
            else:
                self.defaultComponents = setInfo[COMPONENTNAMES]
            start,end = self.getDefaultDates() #this gets the range of possible dates based on original input
            self.setSetDates(setInfo)#this sets the attributes startdate, enddate which can be used in range
            #fillSetInfo the widget values

            self.findChild(QtWidgets.QDateEdit, 'startDate').setDateRange(start, end)
            self.findChild(QtWidgets.QDateEdit, 'endDate').setDateRange(start, end)
            self.setDateSelectorProperties(self.findChild(QtWidgets.QDateEdit, 'startDate'))
            self.setDateSelectorProperties(self.findChild(QtWidgets.QDateEdit, 'endDate'),False)
            self.findChild(QtWidgets.QLineEdit,'componentNames').setText(','.join(self.defaultComponents))
            #self.updateComponentDelegate(self.componentDefault)

        return
    @QtCore.pyqtSlot()
    def componentCellClicked(self):

        # get the cell, and open a listbox of checked components for this project
        listDialog = ComponentSetListForm(self.setName)

        #get the selected Items
        components = listDialog.checkedItems()
        # format the list to be inserted into a text field in a datatable
        str1 = ','.join(components)
        widg = self.findChild(QtWidgets.QLineEdit,'componentNames')
        widg.setText(str1)
        self.controller.dbhandler.updateSetComponents(self.setName,components)
        #self.updateComponentDelegate(components)
        self.set_componentsModel.select()
    #Boolean -> QDateEdit
    def makeDateSelector(self, start=True):
        widg = QtWidgets.QDateEdit()
        if start:
            widg.setObjectName('date_start')
        else:
            widg.setObjectName('date_end')
        widg.setDisplayFormat('yyyy-MM-dd')
        widg.setCalendarPopup(True)
        return widg
    #QDateEdit, Boolean -> QDateEdit()
    def setDateSelectorProperties(self, widg, start = True):
        # default is entire dataset
        if start:
           widg.setDate(QtCore.QDate(self.startDate.year,self.startDate.month,self.startDate.day))
        else:
            widg.setDate(QtCore.QDate(self.endDate.year, self.endDate.month, self.endDate.day))
        widg.setDisplayFormat('yyyy-MM-dd')
        widg.setCalendarPopup(True)
        return widg
    # string -> QGroupbox
    def dataButtons(self, table):
        handler = TableHandler(self)
        buttonBox = QtWidgets.QGroupBox()
        buttonRow = QtWidgets.QHBoxLayout()

        buttonRow.addWidget(makeButtonBlock(self, lambda: self.functionForNewRecord(table),
                                            '+', None,
                                            'Add a component change'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: handler.functionForDeleteRecord(table),
                                            None, 'SP_TrashIcon',
                                            'Delete a component change'))
        buttonRow.addWidget(makeButtonBlock(self, lambda: self.runModels(),
                                            'Run', None,
                                            'Run Set'))
        buttonRow.addStretch(3)

        buttonBox.setLayout(buttonRow)
        return buttonBox
    def makeSetFolder(self):
        path = self.controller.dbhandler.getProjectPath()
        setFolder = getFilePath(self.setName, projectFolder = path)
        if not os.path.exists(setFolder):
            os.makedirs(setFolder,exist_ok=True)
        if not os.path.exists(os.path.join(setFolder,'Setup')):
                os.mkdir(os.path.join(setFolder,'Setup'))
    def setupSet(self):
        '''
        Sets of the direcotory and xml files required for a run. Each set folder has a run folder for each run
        and a setup folder that contains model xml references and setup xml. Once the setup is complete. runSets can be called.
        :return:
        '''

        xmlHolder = self.findChild(XMLEditorHolder)
        xmls = xmlHolder.findChildren(XMLEditor)
        [x.writeXML(self.setName) for x in xmls]#write the model xml files

        #create a set folder
        #write the attributes xml to the set folder
        self.makeSetFolder()
        #the attributes xml gets written
        self.writeAttributeXML()

        # calculate the run combinations and setup directories
        self.setupRuns()

        #write the setup for the set
        self.writeSetup()
        #write the model xmls for the set
        self.writeModelXMLs()
    def writeSetup(self):
        '''copies the setup file from the project setup folder to the set folder
        and makes tag modifications where specified in the model run form'''
        self.controller.runHandler.makeSetSetup(self.setName)
        return
    def writeModelXMLs(self):
        '''calls each xml editor to write its file to the set folder'''
        holder = self.findChild(XMLEditorHolder)
        holder.writeToSetFolder(self.setName)
        return
    def writeAttributeXML(self):
        self.controller.runHandler.makeAttributeXML(self.setName)
    def setupRuns(self):
        '''Calculates the the run combinations and creates a folder for each run. Necessary xmls are transferred to the run folder'''
        #make sure all set attribute entries are entered
        result = self.set_model.submit()
        self.controller.dbhandler.getAllRecords('set_components')
        result = self.set_componentsModel.submitAll()
        self.controller.dbhandler.getAllRecords('set_components')
        print(self.set_componentsModel.lastError().text())
        #self.setModel.submitAll()
        # calculate the run matrix
        runs = self.calculateRuns()
        # create a folder for each run
        [self.controller.runHandler.createRun(r,i,self.setName) for i,r in enumerate(runs)]
    def calculateRuns(self):
        '''calculates a dictionary of run possibilities. Each key is the name of a run folder from Run0...Run#
        The number of runs is based on the number of possible combination for component tag changes
        :return dictionary of run combinations'''

        set_id = self.controller.dbhandler.getSetId(self.setName)

        #all possible combinations not allowing for repeated use of a component:tag:value combination
        runs = self.controller.dbhandler.getRuns(set_id)
        return runs
    def revalidate(self):
        return True
    def functionForNewRecord(self,table):
        self.controller.dbhandler.closeDatabase()
        handler = TableHandler(self)
        handler.functionForNewRecord(table, fields=[1], values=[self.tabPosition + 1])
        self.controller.createDatabaseConnection()
    def runModels(self):
        #make sure data is up to date in the database
        result = self.set_model.submitAll()
        if not result:
            print(self.set_model.lastError().text())
        self.controller.dbhandler.getAllRecords(("set_components"))
        result = self.set_componentsModel.submitAll()

        if not result:
            print(self.set_componentsModel.lastError().text())
        if len(self.controller.dbhandler.getSetComponents(self.setId))> 0:
            #cretae the required xml files and set directory
            self.setupSet()
            self.startModeling()
        else:
            pass
    def startModeling(self):
        #post a progress dialog box
        pbox = CustomProgressBar("Running Simulations")
        self.controller.runHandler.sender.notifyProgress.connect(pbox.onProgress)
        try:#starts running models based on xml files that were genereted in a set directory
            self.controller.runHandler.runModels(self.setName)
            self.updateDependents() #update the plot to show results
        except OSError as e:
            print(e)
            print("Could not complete model simulations")
        except Exception as e:
            print("Could not complete model simulations")
        finally:
            self.controller.runHandler.sender.update(10, "complete")
        return
    def updateDependents(self):
        self.refreshDataPlot()
    def createRunTable(self,setId):
        '''Show table of run information'''
        gb = QtWidgets.QGroupBox('Runs')

        tableGroup = QtWidgets.QVBoxLayout()

        tv = RunTableView(self)
        tv.setObjectName('runs')
        self.run_Model = RunTableModel(self,setId)

        # hide the id columns
        tv.hiddenColumns = [0,1,4,5,26]
        self.run_Model.query()
        tv.setModel(self.run_Model)
        tv.updateRunBaseCase.connect(self.receiveUpdateRunBaseCase)
        tv.reFormat()
        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        #gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #gb.setSizePolicy((QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed))

        return gb
    def refreshDataPlot(self):
        '''finds the plot object and calls its default method'''
        resultDisplay = self.window().findChild(ResultsModel)
        resultDisplay.makePlotArea()
        resultDisplay.showPlot()
    def receiveUpdateRunBaseCase(self,id, checked):
         self.controller.dbhandler.updateBaseCase(self.setId, id, checked)
         self.run_Model.refresh()
         self.refreshDataPlot()

    def closeForm(self):
         self.submitData()
         self.setupSet() #write all the xml files required to restart the project later


        