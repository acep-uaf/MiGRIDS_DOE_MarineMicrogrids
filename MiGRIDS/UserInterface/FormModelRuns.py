#Form for display model run parameters
from PyQt5 import QtWidgets, QtCore, QtGui, QtSql

from MiGRIDS.UserInterface.XMLEditor import XMLEditor
from MiGRIDS.UserInterface.XMLEditorHolder import XMLEditorHolder
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.ModelSetTable import SetTableModel, SetTableView
from MiGRIDS.UserInterface.ModelRunTable import RunTableModel, RunTableView
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.UIToInputHandler import UIToHandler
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit
from MiGRIDS.UserInterface.Pages import Pages
from MiGRIDS.UserInterface.DialogComponentList import ComponentSetListForm
import datetime
import os
import pandas as pd

#main form containing setup and run information for a project
from MiGRIDS.UserInterface.qdateFromString import qdateFromString

class FormModelRun(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.dbhandler = ProjectSQLiteHandler()
        self.setObjectName("modelDialog")
        #the first page is for set0
        #self.tabs = SetsPages(self, 'Set0')
        self.tabs = Pages(self, 0, SetsAttributeEditorBlock)
        self.tabs.setObjectName('modelPages')
        #self.setsTable = self.tabs

        #create the run table #TODO should this move to SetsTableBlock?
        self.runTable = self.createRunTable()

        self.layout = QtWidgets.QVBoxLayout()

        #button to create a new set tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Set')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)
        self.layout.addWidget(newTabButton)

        #set table goes below the new tab button
        self.layout.addWidget(self.tabs)
        #runs are at the bottom
        self.layout.addWidget(self.runTable)
        self.setLayout(self.layout)
        self.showMaximized()


    #the run table shows ??
    def createRunTable(self):
        gb = QtWidgets.QGroupBox('Runs')

        tableGroup = QtWidgets.QVBoxLayout()

        tv = RunTableView(self)
        tv.setObjectName('runs')
        m = RunTableModel(self)
        tv.setModel(m)

        # hide the id column
        tv.hideColumn(0)

        tableGroup.addWidget(tv, 1)
        gb.setLayout(tableGroup)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        return gb

    #add a new set to the project, this adds a new tab for the new set information
    def newTab(self):
        # get the set count
        tab_count = self.tabs.count()
        widg = SetsAttributeEditorBlock(self, tab_count)
        #widg.fillSetInfo()
        self.tabs.addTab(widg, 'Set' + str(tab_count))
        #TODO make sure this is done when we go to write to the set folder.
        #create a folder to hold the relevent set data
        '''#project folder is from FormSetup model
        projectFolder = self.dbhandler.getProjectPath()
        newFolder = os.path.join(projectFolder,'OutputData', 'Set' + str(tab_count))
        if not os.path.exists(newFolder):
            os.makedirs(newFolder)'''

    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()


#the set table shows components to include in the set and attributes to change for runs
#This widget is the main windget for each set tab on the model tab.
class SetsAttributeEditorBlock(QtWidgets.QGroupBox):
    def __init__(self, parent, set):
        super().__init__(parent)
        self.init(set)

    def init(self, set):
        self.componentDefault = []
        self.dbhandler = ProjectSQLiteHandler()
        self.set = set #set is an integer
        self.setName = "Set" + str(self.set) #set name is a string with a prefix
        self.tabName = "Set " + str(self.set)

        #main layouts
        tableGroup = QtWidgets.QVBoxLayout()

        #setup info for a set
        self.setInfo = self.makeSetInfo() #edits on setup attributes
        tableGroup.addWidget(self.infoBox)

        #buttons for adding and deleting component attribute edits - edits to descriptor files
        tableGroup.addWidget(self.dataButtons('sets'))

        #table of descriptor file changes to be made
        #the table view filtered to the specific set for each tab
        tv = SetTableView(self,position=self.set)
        tv.setObjectName('sets')
        self.set_componentsModel = SetTableModel(self,self.set)
        self.set_componentsModel.setFilter('set_id = ' + str(self.set + 1) + " and tag != 'None'")
        self.set_componentsModel.select()

        tv.setModel(self.set_componentsModel)
        '''for r in range(m.rowCount()):
            item = m.index(r,1)
            item.flags(~QtCore.Qt.ItemIsEditable)
            m.setItemData(QtCore.QModelIndex(r,1),item)'''

        #hide the id column
        tv.hideColumn(0)
        #tv.hideColumn(1)
        tableGroup.addWidget(tv, 1)

        #xmlEditing block
        self.xmlEditor = XMLEditorHolder(self, self.set)
        tableGroup.addWidget(self.xmlEditor)
        self.setLayout(tableGroup)
        if set is not None:
            self.fillSetInfo(set)
        else:
            self.fillSetInfo()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def updateForm(self):

        self.setModel.select() #update the set data inputs
        self.setValidators() #update the validators tied to inputs
        self.mapper.toLast() #make sure the mapper is on the actual record (1 per tab)
        self.setModel.submit() #submit any data that was changed
        self.updateComponentLineEdit(self.dbhandler.getComponentNames()) # update the clickable line edit to show current components
        #self.updateComponentDelegate(self.dbhandler.getComponentNames())
        self.set_componentsModel.select()
        self.xmlEditor.updateWidget()

    def updateComponentLineEdit(self,listNames):
        lineedit = self.infoBox.findChild(ClickableLineEdit,'componentNames')
        lineedit.setText(",".join(listNames))
        return

    #sets the start and end date range based on available dataset.
    #if no values are provided the values are drawn from the database
    #tuple(s) -> None
    def getDefaultDates(self):

        start,end = self.dbhandler.getSetupDateRange()

       #format the tuples from database output to datetime objects
        if (start == None) | (start == (None,)): #no date data in the database yet
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

    def getSetDates(self,setName):
        '''

        :param setName:
        :return:
        '''

        start, end = self.dbhandler.getSetupDateRange(setName)
        self.startDate = start
        self.endDate = end
        return
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    def makeSetInfo(self):
        '''
        Creates the input form for fields needed to create and run a model set
        :param kwargs: String set can be passed as a keyword argument which refers to the setname in the project_manager database tble setup
        :return: QtWidgets.QGroupbox input fields for a model set
        '''
        self.infoBox = self.makeSetLayout()
        self.setModel = self.makeSetModel()
        self.mapWidgets()

        return
    def updateModel(self):
        self.setModel.select()
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
    def setValidators(self):
        #timesteps need to be equal to or greater than te setup timestep
        minSeconds = self.dbhandler.getFieldValue('setup','timestepvalue','_id',1)
        units = self.dbhandler.getFieldValue('setup','timestepunit','_id',1)
        if units.lower() != 's':
            minSeconds = self.dbhandler.convertToSeconds(minSeconds,units)
        timestepWidget = self.infoBox.findChild(QtWidgets.QDoubleSpinBox,'timestepvalue')
        #timestepWidget.setValidator(QtGui.QIntValidator(int(minSeconds),86400))
        timestepWidget.setMinimum(int(minSeconds))
        def constrainDateRange(dateWidget,start,end):
            dateWidget.setMinimumDate(start)
            dateWidget.setMaximumDate(end)
        #start date needs to be equal to or greater than the setup start
        start, end = self.dbhandler.getSetupDateRange()
        wids = self.infoBox.findChildren(QtWidgets.QDateEdit)
        p = len(wids)

        list(map(lambda w: constrainDateRange(w,qdateFromString(start),qdateFromString(end)), wids))

    def mapWidgets(self):
        '''
        create a widget mapper object to tie fields to data in database tables
        :return:
        '''
        # map model to fields
        self.mapper = QtWidgets.QDataWidgetMapper()
        self.mapper.setModel(self.setModel)
        self.mapper.setItemDelegate(QtSql.QSqlRelationalDelegate())

        # map the widgets we created with our dictionary to fields in the sql table
        for i in range(0, self.setModel.columnCount()):
            if self.infoBox.findChild(QtWidgets.QWidget, self.setModel.record().fieldName(i)) != None:
                wid = self.infoBox.findChild(QtWidgets.QWidget, self.setModel.record().fieldName(i))
                self.mapper.addMapping(wid, i)
                if isinstance(wid,QtWidgets.QDateEdit):
                    wid.setDate(qdateFromString(self.setModel.data(self.setModel.index(0,i))))

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
        infoRowModel.setFilter('set_._id = ' + str(self.set +1))
        infoRowModel.select()
        infoRowModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        return infoRowModel

    #->QtWidgets.QLineEdit
    def componentSelector(self):

        #if components are not provided use the default list

        allcomponents = self.dbhandler.getComponentNames()
        #setcomponents = self.dbhandler.getSetComponentNames(self.setName)

        widg = ClickableLineEdit(','.join(allcomponents)) #all are selectable
        widg.setText(','.join(allcomponents))
        widg.setObjectName('componentNames')

        widg.clicked.connect(lambda: self.componentCellClicked())
        return widg
    #fills the setup portion of a set tab with either default values or current database values
    #String -> None
    def fillSetInfo(self,setName = '0'):


        # dictionary of set info
        setInfo = self.dbhandler.getSetInfo('set' + str(setName))
        if setInfo != None:
            if type(setInfo['componentNames.value']) == str:
                self.componentDefault = setInfo['componentNames.value'].split(',')
            else:
                self.componentDefault = setInfo['componentNames.value']
            start,end = self.getDefaultDates() #this gets the range of possible dates based on original input
            self.getSetDates(self.setName)#this sets the attributes startdate, enddate which can be used in range
            #fillSetInfo the widget values


            self.findChild(QtWidgets.QDateEdit, 'startDate').setDateRange(start, end)
            self.findChild(QtWidgets.QDateEdit, 'endDate').setDateRange(start, end)
            self.setDateSelectorProperties(self.findChild(QtWidgets.QDateEdit, 'startDate'))
            self.setDateSelectorProperties(self.findChild(QtWidgets.QDateEdit, 'endDate'),False)
            self.findChild(QtWidgets.QLineEdit,'componentNames').setText(','.join(self.componentDefault))
            #self.updateComponentDelegate(self.componentDefault)

        return

    '''def updateComponentDelegate(self,components):

        # find the component drop down delegate and reset its list to the selected components
        tv = self.findChild(QtWidgets.QWidget, 'sets')
        tableHandler = TableHandler(self)
        tableHandler.updateComponentDelegate(components,tv,'componentName')'''

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
        self.dbhandler.updateSetComponents(self.setName,components)
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
        buttonRow.addWidget(makeButtonBlock(self, lambda: self.runSet(),
                                            'Run', None,
                                            'Run Set'))
        buttonRow.addStretch(3)

        buttonBox.setLayout(buttonRow)
        return buttonBox

    def runSet(self):
        # currentSet
        currentSet = self.set
        xmlHolder = self.findChild(XMLEditorHolder)


        xmls = xmlHolder.findChildren(XMLEditor)
        written = [x.writeXML() for x in xmls]#write the model xml files

        uihandler = UIToHandler()
        # component table is the table associated with the button
        componentTable = self.findChild(SetTableView).model()
        if componentTable.rowCount() > 0:
            uihandler.runModels(currentSet, componentTable,self.window().findChild(QtWidgets.QWidget,'setupDialog').model)

    def revalidate(self):
        return True
    def functionForNewRecord(self,table):

        handler = TableHandler(self)
        handler.functionForNewRecord(table, fields=[1], values=[self.set + 1])
