# Projet: MiGRIDS
# Created by: T.Morgan # Created on: 3/12/2020
import datetime

import os
from PyQt5 import QtWidgets, QtSql, QtCore
import pandas as pd

from MiGRIDS.InputHandler.InputFields import COMPONENTNAMES

from MiGRIDS.UserInterface.BaseEditorTab import BaseEditorTab
from MiGRIDS.UserInterface.CustomProgressBar import CustomProgressBar
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit
from MiGRIDS.UserInterface.DialogComponentList import ComponentSetListForm
from MiGRIDS.UserInterface.ModelSetTable import SetTableView, SetTableModel
from MiGRIDS.UserInterface.ResultsModel import ResultsModel
from MiGRIDS.UserInterface.SetTableBlock import SetTableBlock
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.XMLEditor import XMLEditor
from MiGRIDS.UserInterface.XMLEditorHolder import XMLEditorHolder
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.makeButton import makeButton
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
        self.setId = self.controller.dbhandler.getIDByPosition('set_',tabPosition)
        if ((self.setId == None) | (self.setId == -1)) & (self.controller.dbhandler.getProject() != None):

            self.setId = self.controller.dbhandler.insertRecord('set_',['set_name','project_id','date_start','date_end','runtimestepsvalue'],
                                                                [self.setName,1,self.controller.dbhandler.getFieldValue('setup','date_start','_id',1),
                                                                 self.controller.dbhandler.getFieldValue('setup',
                                                                                                         'date_end',
                                                                                                         '_id', 1),
                                                                 self.controller.dbhandler.getFieldValue('setup',
                                                                                                         'runtimestepsvalue',
                                                                                                         '_id', 1)
                                                                 ])
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
        self.tableBlock = SetTableBlock(self, self.tabPosition)

        tableGroup.addWidget(self.tableBlock, 2, 0, 8, 4)

        self.updateComponentLineEdit(
        self.controller.dbhandler.getComponentNames())  # update the clickable line edit to show current components

        # xmlEditing block
        self.xmlEditor = XMLEditorHolder(self, self.tabPosition)
        tableGroup.addWidget(self.xmlEditor, 2, 4, 8, 6)
        self.setLayout(tableGroup)


    def updateForm(self):
        '''refreshes data displayed in form based on any changes made in database or xml model files'''
        self.refreshSetModel()
        self.setValidators() #update the validators tied to inputs
        self.mapper.toLast() #make sure the mapper is on the actual record (1 per tab)
        self.updateComponentLineEdit(self.controller.dbhandler.getComponentNames()) # update the clickable line edit to show current components
        self.tableBlock.tableModel.select()
        self.xmlEditor.updateWidget() #this relies on xml files, not the database
        self.rehide(self.findChild(QtWidgets.QTableView,'sets'), [0,1])
        return

    def refreshSetModel(self):
        self.setId = self.controller.dbhandler.getSetId(str(self.tabPosition))
        self.set_model.setFilter('set_._id = ' + str(self.setId))
        self.set_model.select()  # update the set data inputs
        return

    def rehide(self,tview,loc):
        for i in loc:
            tview.hideColumn(i)
    def submitData(self):
        result = self.tableBlock.tableModel.submitAll()
        if not result:
            print(self.tableBlock.tableModel.lastError().text())
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
            start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%m:%s')
            end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%m:%s')
        else:
            start = datetime.datetime.strptime(start[0], '%Y-%m-%d %H:%m:%s')
            end = datetime.datetime.strptime(end[0], '%Y-%m-%d %H:%m:%s')

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
        # self.runModel.query()
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
        #update the runtimesteps to match the setup file if they are outside the bounds
        self.updateRunTimeSteps()
        self.updateForm()
        return
    def updateRunTimeSteps(self):
        setInfo = self.controller.dbhandler.getSetInfo(self.setName)
        setupInfo = self.controller.dbhandler.getSetUpInfo()

        if not (pd.to_datetime(setInfo['date_start']) > (pd.to_datetime(setupInfo['date_start']))) & (
            pd.to_datetime(setInfo['date_start']) < (pd.to_datetime(setupInfo['date_end']))):
            setInfo['date_start'] = setupInfo['date_start']
        if not (pd.to_datetime(setInfo['date_end']) > (pd.to_datetime(setupInfo['date_start']))) & (
            pd.to_datetime(setInfo['date_end']) < (pd.to_datetime(setupInfo['date_end']))):
            setInfo['date_end'] = setupInfo['date_end']
        if 'project_name' in setInfo.keys():
            setInfo.pop('project_name')
        if 'componentNames.value' in setInfo.keys():
            setInfo.pop('componentNames.value')

        self.controller.dbhandler.updateFromDictionaryRow('set_',setInfo,['_id'],[self.controller.dbhandler.getSetId(self.setName)])
        return


    def setValidators(self):
        '''validator values used set when the form is updated'''
        #timesteps need to be equal to or greater than the setup timestep
        minSeconds = self.controller.dbhandler.getFieldValue('setup','timestepvalue','_id',1)
        units = self.controller.dbhandler.getFieldValue('setup','timestepunit','_id',1)
        if units.lower() != 's':
            minSeconds = self.controller.dbhandler.convertToSeconds(minSeconds,units)
        timestepWidget = self.infoBox.findChild(QtWidgets.QDoubleSpinBox,'timestepvalue')
        #timestepWidget.setValidator(QtGui.QIntValidator(int(minSeconds),86400))
        timestepWidget.setMinimum(int(minSeconds))
        def constrainDateRange(dateWidget,start,end):
            dateWidget.setMinimumDateTime(start)
            dateWidget.setMaximumDateTime(end)
        #start date needs to be equal to or greater than the setup start
        start, end = self.controller.dbhandler.getSetupDateRange()
        wids = self.infoBox.findChildren(QtWidgets.QDateEdit)
        list(map(lambda w: constrainDateRange(w,qdateFromString(start),qdateFromString(end)), wids))
        return
    def saveSet(self):
        dict = {}
        for i in range(3,6):
            wid = self.infoBox.findChild(QtWidgets.QWidget, self.set_model.record().fieldName(i))
            dict[wid.objectName()] = wid.text()

        if (self.setId == -1) | (self.setId == None) | (self.setId ==""):
             self.setId = self.controller.dbhandler.insertRecord('set_',['set_name','project_id','date_start','date_end','runtimestepsvalue'],
                                                            [self.setName,1,self.controller.dbhandler.getFieldValue('setup','date_start','_id',1),
                                                             self.controller.dbhandler.getFieldValue('setup',
                                                                                                     'date_end',
                                                                                                     '_id', 1),
                                                             self.controller.dbhandler.getFieldValue('setup',
                                                                                                     'runtimestepsvalue',
                                                                                                     '_id', 1)
                                                             ])
        else:
            self.controller.dbhandler.updateFromDictionaryRow('set_',dict, ['_id'],[self.setId])
        return
    def mapWidgets(self):
        '''
        create a widget mapper object to tie fields to data in database tables
        :return:
        '''
        # map model to fields
        self.mapper = QtWidgets.QDataWidgetMapper()
        self.mapper.setModel(self.set_model)
        #self.mapper.setItemDelegate(QtSql.QSqlRelationalDelegate())

        # map the widgets we created with our dictionary to fields in the sql table
        for i in range(0, self.set_model.columnCount()):
            if self.infoBox.findChild(QtWidgets.QWidget, self.set_model.record().fieldName(i)) != None:
                wid = self.infoBox.findChild(QtWidgets.QWidget, self.set_model.record().fieldName(i))
                self.mapper.setItemDelegate(QtWidgets.QItemDelegate())
                self.mapper.addMapping(wid, i)
                if isinstance(wid,QtWidgets.QDateEdit):
                    wid.setDateTime(qdateFromString(self.set_model.data(self.set_model.index(0, i))))

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
        '''makes the component selection widget
        :return: ClickableLineEdit widget'''
        #if components are not provided use the default list

        allcomponents = self.controller.dbhandler.getComponentNames()
        #setcomponents = self.controller.dbhandler.getSetComponentNames(self.setName)

        widg = ClickableLineEdit(','.join(allcomponents)) #all are selectable
        widg.setText(','.join(allcomponents))
        widg.setObjectName('componentNames')

        widg.clicked.connect(lambda: self.componentCellClicked())
        return widg
    def fillSetInfo(self,setName = '0'):
        '''
        fills the unmapped form fields with set information found in the database
        :param setName: String name or number of the set
        :return: None
        '''
        setid = self.controller.dbhandler.getSetId(setName)
        setInfo = self.controller.dbhandler.getSetInfo(self.controller.dbhandler.getFieldValue('_set','set_name','_id',setid))
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

        return
    @QtCore.pyqtSlot()
    def componentCellClicked(self):
        '''Display a list of displaying values from the clicked widget and update the database with the result'''
        # get the cell, and open a listbox of checked components for this project
        listDialog = ComponentSetListForm(self.setName)

        #get the selected Items
        components = listDialog.checkedItems()
        # format the list to be inserted into a text field in a datatable
        str1 = ','.join(components)
        widg = self.findChild(QtWidgets.QLineEdit,'componentNames')
        widg.setText(str1)
        self.controller.dbhandler.updateSetComponents(self.setName,components)

        self.tableBlock.tableModel.select()
        return

    #Boolean -> QDateEdit
    def makeDateSelector(self, start=True):
        widg = QtWidgets.QDateTimeEdit()
        if start:
            widg.setObjectName('date_start')
        else:
            widg.setObjectName('date_end')
        widg.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        widg.setCalendarPopup(True)
        return widg
    #QDateEdit, Boolean -> QDateEdit()
    def setDateSelectorProperties(self, widg, start = True):
        # default is entire dataset
        if start:
           widg.setDate(QtCore.QDate(self.startDate.year,self.startDate.month,self.startDate.day))
        else:
            widg.setDate(QtCore.QDate(self.endDate.year, self.endDate.month, self.endDate.day))
        widg.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        widg.setCalendarPopup(True)
        return widg

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

        result = self.tableBlock.tableModel.submitAll()
        if not result:
            print(self.tableBlock.tableModel.lastError().text())
        self.controller.dbhandler.getAllRecords('set_components')

        # calculate the run matrix
        runs = self.calculateRuns()
        # create a folder for each run
        if runs != None:
            [self.controller.runHandler.createRun(r,i,self.setName) for i,r in enumerate(runs)]
        return
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

    def runModels(self):
        #make sure data is up to date in the database
        self.saveSet()
        self.controller.dbhandler.getAllRecords(("set_components"))
        # self.tableBlock.tableModel.submitTable()
        result = self.tableBlock.tableModel.submitAll()

        if not result:
            print(self.tableBlock.tableModel.lastError().text())
        if len(self.controller.dbhandler.getSetComponents(self.setId))> 0: #won't run models unless tags have been set
            #cretae the required xml files and set directory
            self.setupSet()
            self.controller.runHandler.checkRunTimesteps()
            self.startModeling()
        else:
            pass
        return

    def startModeling(self):
        #post a progress dialog box
        pbox = CustomProgressBar("Running Simulations")
        self.controller.runHandler.sender.notifyProgress.connect(pbox.onProgress)
        try:#starts running models based on xml files that were genereted in a set directory
            self.controller.runHandler.runModels(self.setName)
            self.controller.updateAttribute('Controller','sets',self.controller.sets + [self.setName])
            self.controller.sender.callStatusChanged()#update the plot to show results
        except OSError as e:
            print(e)
            print("Could not complete model simulations")
        except Exception as e:
            print(e)
            print("Could not complete model simulations")
        finally:
           self.controller.runHandler.sender.update(10, "complete")

        return

    def closeForm(self):
         self.tableBlock.tableModel.submit()
         path = self.controller.dbhandler.getProjectPath()
         if path is not None:
             self.setupSet() #write all the xml files required to restart the project later


        