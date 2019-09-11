#Form for display model run parameters
from PyQt5 import QtWidgets, QtCore, QtGui, QtSql
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.ModelSetTable import SetTableModel, SetTableView
from MiGRIDS.UserInterface.ModelRunTable import RunTableModel, RunTableView
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.Controller.UIToInputHandler import UIToHandler
from MiGRIDS.UserInterface.Pages import Pages
import datetime
import os

#main form containing setup and run information for a project
from MiGRIDS.UserInterface.qdateFromString import qdateFromString


class FormModelRun(QtWidgets.QWidget):
    handler = ProjectSQLiteHandler()
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setObjectName("modelDialog")
        #the first page is for set0
        #self.tabs = SetsPages(self, 'Set0')
        self.tabs = Pages(self,0,SetsTableBlock)
        self.tabs.setObjectName('modelPages')
        #self.setsTable = self.tabs
        #create the run table
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
        widg = SetsTableBlock(self, 'set' + str(tab_count))
        widg.fillSetInfo()
        self.tabs.addTab(widg, 'Set' + str(tab_count))

        #create a folder to hold the relevent set data
        #project folder is from FormSetup model
        projectFolder = self.window().findChild(QtWidgets.QWidget, "setupDialog").model.projectFolder
        newFolder = os.path.join(projectFolder,'OutputData', 'Set' + str(tab_count))
        if not os.path.exists(newFolder):
            os.makedirs(newFolder)

    # calls the specified function connected to a button onClick event
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()



#the set table shows components to include in the set and attributes to change for runs
#This widget is the main windget for each set tab on the model tab.
class SetsTableBlock(QtWidgets.QGroupBox):
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

        self.setInfo = self.makeSetInfo()
        tableGroup.addWidget(self.infoBox)

        #buttons for adding and deleting set records
        tableGroup.addWidget(self.dataButtons('sets'))
        #the table view filtered to the specific set for each tab
        tv = SetTableView(self,column1=self.set)
        tv.setObjectName('sets')
        m = SetTableModel(self,set)
        m.setFilter("set_name = " + self.setName)
        tv.setModel(m)
        for r in range(m.rowCount()):
            item = m.index(r,1)
            item.flags(~QtCore.Qt.ItemIsEditable)
            m.setItemData(QtCore.QModelIndex(r,1),item)

        #hide the id column
        tv.hideColumn(0)
        tableGroup.addWidget(tv, 1)

        self.setLayout(tableGroup)
        if set is not None:
            self.fillSetInfo(set)
        else:
            self.fillSetInfo()
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    #fill form with existing data
    def fillData(self,set):
       return

    def updateForm(self):
        record = self.mapper.currentIndex()
        self.setModel.select()
        rcount = self.setModel.rowCount()
        self.mapper.toLast()
        myRecords = self.dbhandler.getAllRecords('set_')
        self.setModel.submit()
        record = self.mapper.currentIndex()
        print(myRecords)

    #sets the start and end date range based on available dataset.
    #if no values are provided the values are drawn from the database
    #tuple(s) -> None
    def getDefaultDates(self):
        #TODO this should come from a preview

        handler = ProjectSQLiteHandler()
        start = handler.cursor.execute("select date_start from setup where set_name = 'Set0'").fetchone()
        end = handler.cursor.execute("select date_end from setup where set_name = 'Set0'").fetchone()
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
        handler = ProjectSQLiteHandler()
        start, end = handler.getSetupDateRange(setName)
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
        timestepWidget = QtWidgets.QLineEdit('1')
        timestepWidget.setObjectName(('timestepvalue'))
        timestepWidget.setValidator(QtGui.QIntValidator())
        infoRow.addWidget(timestepWidget)
        infoRow.addWidget(QtWidgets.QLabel('Seconds'), 1)
        infoRow.addWidget(QtWidgets.QLabel('Components'))
        infoRow.addWidget(self.componentSelector(), 2)
        infoBox.setLayout(infoRow)
        return infoBox

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
        parent = QtCore.QModelIndex()
        infoRowModel.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        infoRowModel.select();
        infoRowModel.setFilter('set_._id = ' + str(self.set +1))
        infoRowModel.select()
        infoRowModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        return infoRowModel

    #->QtWidgets.QLineEdit
    def componentSelector(self,**kwargs):
        from MiGRIDS.UserInterface.Delegates import ClickableLineEdit
        #if components are not provided use the default list
        if kwargs.get("components"):
            components = kwargs.get("components")
        else:
            components = self.componentDefault


        widg = ClickableLineEdit(','.join(components))
        widg.setObjectName('componentNames')

        widg.clicked.connect(lambda: self.componentCellClicked())
        return widg
    #fills the setup portion of a set tab with either default values or current database values
    #String -> None
    def fillSetInfo(self,setName = '0'):

        databaseHandler = ProjectSQLiteHandler()
        # dictionary of set info
        setInfo = databaseHandler.getSetInfo('set' + str(setName))
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
            self.updateComponentDelegate(self.componentDefault)

        return


    def updateComponentDelegate(self,components):
        from MiGRIDS.UserInterface.Delegates import ComboDelegate, ComponentFormOpenerDelegate
        # find the component drop down delegate and reset its list to the selected components
        tv = self.findChild(QtWidgets.QWidget, 'sets')
        tableHandler = TableHandler(self)
        tableHandler.updateComponentDelegate(components,tv,'componentName')


    @QtCore.pyqtSlot()
    def componentCellClicked(self):
        from MiGRIDS.UserInterface.DialogComponentList import ComponentSetListForm
        from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

        import pandas as pd
        handler = ProjectSQLiteHandler('project_manager')

        # get the cell, and open a listbox of possible components for this project
        checked = pd.read_sql_query("select componentnamevalue from component", handler.connection)

        checked = list(checked['componentnamevalue'])
        handler.closeDatabase()
        # checked is a comma seperated string but we need a list
        #checked = checked.split(',')
        listDialog = ComponentSetListForm(checked)
        components = listDialog.checkedItems()
        # format the list to be inserted into a text field in a datatable
        str1 = ','.join(components)
        widg = self.findChild(QtWidgets.QLineEdit,'componentNames')
        widg.setText(str1)
        self.updateComponentDelegate(components)

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

        buttonRow.addWidget(makeButtonBlock(self, lambda: handler.functionForNewRecord(table),
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
        #set info needs to be updated in the database

        values = [currentSet,self.findChild(QtWidgets.QDateEdit,'startDate').text(),
            self.findChild(QtWidgets.QDateEdit, 'endDate').text(),
            self.findChild(QtWidgets.QLineEdit,'timestepvalue').text(),
            self.findChild(QtWidgets.QComboBox, 'timestepunit').Currenttext()]

        dbhandler = ProjectSQLiteHandler()
        try:
            dbhandler.insertRecord('set_',['set_name', 'date_start', 'date_end', 'timestepvalue','timestepunit'],values)
        except:
            dbhandler.updateRecord('set_',['set_name'],currentSet,['date_start', 'date_end', 'timestepvalue','timestepunit'], values[1:])
        dbhandler.addComponentsToSet(self.findChild(QtWidgets.QLineEdit,'componentNames').text().split(","))

        uihandler = UIToHandler()

        # component table is the table associated with the button
        componentTable = self.findChild(SetTableView).model()
        if componentTable.rowCount() > 0:
            uihandler.runModels(currentSet, componentTable,self.window().findChild(QtWidgets.QWidget,'setupDialog').model)
        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Add components",
                                        "You need to select component attributes to alter before running sets.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
    def revalidate(self):
        return True