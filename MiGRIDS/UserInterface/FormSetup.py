'''created by T.Morgan
The FormSetup widget has 3 purposes.
1. Creates or loads a setup.xml file for a specific project
2. It creates or loads descriptor xml files for each component that will be included in the model
3. It ties individual components to an input file containing timer series values for each component
wind turbine components can have either an associated power time series or a windspeed file that a power time series will be generated from
In the case of a windspeed file a windspeed netcdf file will be generated and power time series will be generated once the model is run based
on each wtg components descriptor file.'''
import os
from PyQt5 import QtCore, QtWidgets, QtGui
#from MiGRIDS.UserInterface.ModelSetupInformation import ModelSetupInformation

from MiGRIDS.Controller.UIToInputHandler import UIToHandler
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.ResultsSetup import  ResultsSetup
from MiGRIDS.UserInterface.FormModelRuns import SetsTableBlock
from MiGRIDS.UserInterface.Pages import Pages

from MiGRIDS.UserInterface.FileBlock import FileBlock
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

from MiGRIDS.UserInterface.switchProject import switchProject
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.replaceDefaultDatabase import replaceDefaultDatabase

class FormSetup(QtWidgets.QWidget):
    global model
    #model = ModelSetupInformation()
    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
    #initialize the form
    def initUI(self):
        self.dbHandler = ProjectSQLiteHandler()
        self.setObjectName("setupDialog")
        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()

        # the top block is buttons to load setup xml and data files
        self.createButtonBlock()
        windowLayout.addWidget(self.ButtonBlock)
        #each tab is for an individual input file.
        self.tabs = Pages(self, '1',FileBlock)
        self.tabs.setDisabled(True)

        # button to create a new file tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Input')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)
        windowLayout.addWidget(newTabButton)
        windowLayout.addWidget(self.tabs,3)

        #list of dictionaries containing information for wizard
        #this is the information that is not input file specific.
        dlist = [
            {'title': 'Dates to model', 'prompt': 'Enter the timespan you would like to include in the model.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'runTimesteps', 'folder': False, 'dates':True},
            {'title': 'System Components','prompt':'Indicate the number of each type of component to include.','sqltable': None,
             'sqlfield': None, 'reftable': None, 'name': 'componentNames'
            },
            {'title': 'Timestep', 'prompt': 'Enter desired timestep', 'sqltable': None, 'sqlfield': None,
              'reftable': 'ref_time_units', 'name': 'timeStep', 'folder': False},
            {'title': 'Project', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'project', 'folder': False}
        ]

        self.WizardTree = self.buildWizardTree(dlist)
        self.createBottomButtonBlock()
        windowLayout.addWidget(self.BottomButtons)
        #set the main layout as the layout for the window

        self.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Input Files')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #show the form
        self.showMaximized()

    def createButtonBlock(self):
        '''
        create the layout containing buttons to load or create a new project
        :return: QWidgets.QHBoxLayout
        '''
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        #layout object name
        hlayout.setObjectName('buttonLayout')
        #add the button to load a setup xml

        hlayout.addWidget(makeButtonBlock(self, self.functionForLoadButton,
                                 'Load Existing Project', None, 'Load a previously created project files.','loadProject'))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            makeButtonBlock(self,self.functionForCreateButton,
                                 'Create setup XML', None, 'Start the setup wizard to create a new setup file','createProject'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)

        self.ButtonBlock.setLayout(hlayout)

        self.ButtonBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        projectTitlewdg = QtWidgets.QLabel()
        projectTitlewdg.setObjectName('projectTitle')
        hlayout.addWidget(projectTitlewdg)
        hlayout.addStretch(1)
        return hlayout

    def createBottomButtonBlock(self):
        '''
        Creates the bottom buttons associated with the setup form
        :return: QWidgets.QHBoxLayout
        '''
        self.BottomButtons = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        # layout object name
        hlayout.setObjectName('buttonLayout')
        # add the button to load a setup xml
        button = QtWidgets.QPushButton('Create input files')
        button.setToolTip('Create input files to run models')
        button.clicked.connect(lambda: self.onClick(self.createInputFiles))
        button.setFixedWidth(200)
        # windowLayout.addWidget(makeButtonBlock(self,self.createInputFiles,'Create input files',None,'Create input files to run models'),3)
        hlayout.addWidget(button)
        dataLoaded = QtWidgets.QLineEdit()
        dataLoaded.setFrame(False)
        dataLoaded.setObjectName('dataloaded')
        dataLoaded.setText('No data loaded')
        dataLoaded.setFixedWidth(200)
        self.dataLoaded = dataLoaded
        hlayout.addWidget(self.dataLoaded)
        # generate netcd button
        netCDFButton = self.createSubmitButton()
        hlayout.addWidget(netCDFButton)
        button.setFixedWidth(200)
        self.netCDFsLoaded  = QtWidgets.QLineEdit()
        self.netCDFsLoaded.setFrame(False)
        self.netCDFsLoaded.setText("none")
        hlayout.addWidget(self.netCDFsLoaded)
        #hlayout.addStretch(1)
        self.BottomButtons.setLayout(hlayout)

        return hlayout

    @QtCore.pyqtSlot()
    def onClick(self,buttonFunction):
        '''
        calls the provided function during an onclick event
        :param buttonFunction: a function or routine to be called
        :return: None
        '''
        buttonFunction()
    def projectExists(self):
        return os.path.exists(self.setupFolder)
    def functionForCreateButton(self):
        '''
        Launches input wizard and creates setup.xml file based on information collected by the wizard
        :return: None
        '''
        #if a project is already started save it before starting a new one
        try:
            if (self.project != '') & (self.project is not None):
                switchProject(self)
        except AttributeError as e:
            print("Project not set yet")
        #calls the setup wizard to fill the database from wizard information
        self.fillSetup()
        self.projectDatabase = False
        #display collected data


        # if setup is valid enable tabs
        if self.hasSetup():
            #enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget,'pages')
            pages.enableTabs()
            self.tabs.setEnabled(True)
            self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.project)

    def hasSetup(self):
        return True

    def loadSetup(self, setupFile):
        handler = UIToHandler()
        handler.inputHandlerToUI(setupFile, self)

    def fillSetup(self):
        '''
        calls the setup wizard to fill setup information into the project_manager database and subsequently to setup.xml
        :return:
        '''
        s = self.WizardTree
        s.exec_()
        handler = UIToHandler()

        #If the project already exists wait to see if it should be overwritten
        #assign project has already been called at this point so the directory is created
        if self.setupExists():
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Project Aready Exists",
                                        "Do you want to overwrite existing setup files?.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            overwrite = msg.exec()
            if overwrite != QtWidgets.QMessageBox.Yes:
                self.fillSetup() # call up the wizard again so a new project name can be assigned
        handler.makeSetup() #this line won't get reached until an original project name is generated or overwrite is chose

    def setupExists(self):
        '''

        :return: Boolean True if a setup file is found in the specified setup folder
        '''

        if os.path.exists(os.path.join(self.setupFolder, self.project + 'Setup.xml')):
            return True
        else:
            return False

    #searches for and loads existing project data - database, setupxml,descriptors, DataClass pickle, Component pickle netcdf,previously run model results, previous optimization results
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''
        dbhandler = ProjectSQLiteHandler()

        #if we were already working on a project its state gets saved and  new project is loaded
        if (dbhandler.getProjectPath() != '') & (dbhandler.getProjectPath() is not None):
            switchProject(self)


        #launch file navigator to identify setup file
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", self.lastProjectPath, "*xml" )
        if (setupFile == ('','')) | (setupFile is None):
            return
        self.loadSetup(setupFile[0])

        # now that setup data is set display it in the form
        #self.displayModelData() this should be done with binding

        #Look for an existing project database and replace the default one with it
        if os.path.exists(os.path.join(self.model.projectFolder,'project_manager')):
            print('An existing project database was found for %s.' %self.model.project)

            replaceDefaultDatabase(os.path.join(self.model.projectFolder, 'project_manager'))
            self.projectDatabase = True
        else:
            self.projectDatabase = False
            print('An existing project database was not found for %s.' % self.model.project)

        # record the current project
        self.dbHandler.insertRecord('project', ['project_path'], [setupFile[0]])


        # look for an existing data pickle
        handler = UIToHandler()
        self.model.data= handler.loadInputData(
            os.path.join(self.model.setupFolder, self.model.project + 'Setup.xml'))

        if self.model.data is not None:
            self.updateModelPage(self.model.data)
            self.dataLoaded.setText('data loaded')
            #refresh the plot
            resultDisplay = self.parent().findChild(ResultsSetup)
            resultDisplay.defaultPlot()

        #look for an existing component pickle or create one from information in setup xml
        self.model.components = handler.loadComponents(os.path.join(self.model.setupFolder, self.model.project + 'Setup.xml'))
        if self.model.components is None:
             self.getComponentsFromSetup()

        #list netcdf files previously generated
        self.netCDFsLoaded.setText('Processed Files: ' + ', '.join(self.listNetCDFs()))
        #TODO this part of the code always sets setsRun to false, need to implement check for models run
        #boolean indicator of whether or not model sets have already been run
        setsRun = False
        #make the data blocks editable if there are no sets already created
        #if sets have been created then input data is not editable from the interface
        if setsRun:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Analysis in Progress",
                                        "Analysis results were detected. You cannot edit input data after analysis has begun.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
        else:
            self.tabs.setEnabled(True)
            print('Loaded %s:' % model.project)

        #set the project name on the GUI form
        self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.model.project)

        return
    #looks in the processed folder and lists nc files found
    #->ListOfStrings
    def listNetCDFs(self):
        '''
        produces a list of netcdf files located in the Processed folder of a project TimeSeries folder
        :return: List of Strings of names of netCDF files
        '''
        lof = [f for f in os.listdir(getFilePath(self.model.setupFolder,'Processed')) if f[-2:] =='nc']
        return lof


    def displayModelData(self):
        """creates a tab for each input directory specified the SetupModelInformation model inputFileDir attribute.
        Each tab contains a FileBlock object to interact with the data input
        Each FileBlock is filled with data specific to the input directory"""
        self.tabs.removeTab(0)
        #the number of directories listed in inputFileDir indicates how many tabs are required
        tab_count = len(self.model.inputFileDir.value)
        #if directories have been entered then replace the first tab and create a tab for each directory #TODO should remove all previous tabs
        if tab_count > 0:
            self.tabs.removeTab(0)
            for i in range(tab_count):
                self.newTab(i+1)
        else:
            self.newTab(1)
        return

    def buildWizardTree(self, dlist):
        '''
        Builds a QWizard based on a list of inputs
        :param dlist: a list of dictionaries, list item becomes a page in the wizard tree
        :return: a QWizard
        '''
        wiztree = QtWidgets.QWizard()
        wiztree.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        wiztree.setWindowTitle("Setup")
        wiztree.addPage(WizardPage(dlist[3]))  #project name
        wiztree.addPage(TextWithDropDown(dlist[2])) #timesteps
        wiztree.addPage(ComponentSelect(dlist[1]))      #components
        wiztree.addPage(TwoDatesDialog(dlist[0]))  #runtimesteps
        btn = wiztree.button(QtWidgets.QWizard.FinishButton)
        btn.clicked.connect(self.saveTreeInput)
        return wiztree

    def assignProjectPath(self, name):
            self.project = name
            self.setupFolder = os.path.join(os.path.dirname(__file__), *['..','..','MiGRIDSProjects', self.project, 'InputData','Setup'])
            self.componentFolder = getFilePath(self.setupFolder ,'Components')
            projectFolder = getFilePath(self.setupFolder, 'Project')
            #self.outputFolder = getFilePath(self.projectFolder, 'OutputData')

            #if there isn't a setup folder then its a new project
            if not os.path.exists(self.setupFolder):
                #make the project folder
                os.makedirs(self.setupFolder)
            if not os.path.exists(self.componentFolder):
                #make the component
                os.makedirs(self.componentFolder)
            return projectFolder
    def saveTreeInput(self):
        '''
        save the input in the wizard tree attribute to the database
        :return: None
        '''

        dbhandler = ProjectSQLiteHandler()
        dbhandler.insertRecord("project",['project_name','project_path'],[self.WizardTree.field('project'),self.assignProjectPath(self.WizardTree.field('project'))])
        dbhandler.insertRecord("setup",['set_name','timestepvalue','timestepunit','date_start','date_end'],['set0',self.WizardTree.field('timeInterval'),self.WizardTree.field('timeUnit'),self.WizardTree.field('sdate'),self.WizardTree.field('edate')])
        lot = dbhandler.getComponentTypes()
        for t in lot:
            cnt = self.WizardTree.field(t[0]+'count')
            for i in range(0,cnt):
                dbhandler.insertRecord('component',['componentnamevalue','componenttype'],[t[0] + str(i),t[0]])
        print(dbhandler.getAllRecords('component'))
        return

    # def sendSetupInputToModel(self): Not necessary if submitting to database
    #     '''
    #     Reads data from gui and sends to the ModelSetupInformation data model
    #     reads through all the file tabs to collect input from all tabs
    #     :return: None
    #     '''
    #
    #     #extract data from every tab
    #     tabWidget = self.findChild(QtWidgets.QTabWidget)
    #     for t in range(tabWidget.count()):
    #         page = tabWidget.widget(t)
    #         # cycle through the input children in the topblock
    #         for child in page.FileBlock.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox)):
    #
    #             if type(child) is QtWidgets.QLineEdit:
    #                 value = child.text()
    #             elif type(child) is ClickableLineEdit:
    #                 value = child.text()
    #             elif type(child) is QtWidgets.QComboBox:
    #                 value = child.itemText(child.currentIndex())
    #             #append to appropriate list
    #             attr = child.objectName()
    #             model.assign(attr,value,position=int(page.input)-1)
    #
    #         model.setComponents(page.saveTables())
    #
    #         return

    #TODO this should be done on a seperate thread
    def createInputFiles(self):
        '''
        Create a dataframe of input data based on importing files within each SetupModelInformation.inputFileDir
        '''
        self.addProgressBar()
        self.progress.setRange(0, 0)
        #self.sendSetupInputToModel()
        # check all the required fields are filled
        dbhandler = ProjectSQLiteHandler()
        if not dbhandler.dataComplete():
            #if required fields are not filled in return to setup page.
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Required Fields",
                                        "Please fill in all required fields before generating input files.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()
            dbhandler.closeDatabase()
            return

        dbhandler.closeDatabase()

        # start with the setupxml
        handler = UIToHandler()
        handler.makeSetup()

        # import datafiles
        handler = UIToHandler()
        cleaned_data, components = handler.loadFixData(
            os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.updateModelPage(cleaned_data)
        # pickled data to be used later if needed
        handler.storeData(cleaned_data, os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        handler.storeComponents(components,os.path.join(model.setupFolder, model.project + 'Setup.xml'))
        self.dataLoaded.setText('data loaded')
        self.progress.setRange(0, 1)
        # generate netcdf files
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Time Series loaded",
                                    "Do you want to generate netcdf files?.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        result = msg.exec()

        # if yes create netcdf files, Otherwise this can be done after the data is reviewed.
        if result == QtWidgets.QMessageBox.Ok:
            d = {}
            for c in components:
                d[c.column_name] = c.toDictionary()
            handler.createNetCDF(cleaned_data.fixed, d,
                                 os.path.join(model.setupFolder, model.project + 'Setup.xml'))

        return

    def updateModelPage(self, data):
        '''
        updates the default component list, time range and time step values in the setup table in the project database
        based on fields and timesteps found in data.fixed and passes these values to the ModelDialog
        :param data: DataClass with a pandas.DataFrame named fixed which contains a datetime index
        :return: None
        '''
        # start and end dates get set written to database as default date ranges
        import pandas as pd
        #each dataframe needs a datetime index
        for df in data.fixed:
            assert(type(df.index[0])==pd.datetime)

        def getDefaults(listDf,defaultStart=pd.to_datetime("1/1/1900").date(), defaultEnd = pd.datetime.today().date()):
            '''
            returns the earliest and latest date index found in a list of dataframes with date indices. Will return initial default
            start and end if no dates are found in dataframes.
            :param listDf: is a list of pandas.dataframes, all with a date index
            :param defaultStart: pandas date value that will be the default start date if none is found in the list of dataframes
            :param defaultEnd: pandas date value that will be the default end date if none is found in the list of dataframes
            :return: String start date, String end date
            '''

            if len(listDf) > 0:
                s = listDf[0].index[0].date()
                e = listDf[0].index[len(listDf[0])-1].date()

                if (s < defaultStart) & (e > defaultEnd):
                    return getDefaults(listDf[1:],s,e)
                elif s < defaultStart:
                    return getDefaults(listDf[1:],s,defaultEnd)
                elif e > defaultStart:
                    return getDefaults(listDf[1:], defaultStart, e)
            return str(defaultStart), str(defaultEnd)

        #default start is the first date there is record for
        values = {}
        values['date_start'], values['date_end'] = getDefaults(data.fixed)
        values['component_names'] = ','.join(self.model.componentNames.value)

        self.dbHandler.updateDefaultSetup(values)

        # Deliver appropriate info to the ModelForm
        modelForm = self.window().findChild(SetsTableBlock)
        # start and end are tuples at this point
        modelForm.makeSetInfo(start=values['date_start'], end=values['date_end'], components=values['component_names'])

        #deliver the data to the ResultsSetup form so it can be plotted
        resultsForm = self.window().findChild(ResultsSetup)
        resultsForm.setPlotData(data)

    # close event is triggered when the form is closed
    def closeEvent(self, event):
        #save xmls
        if 'projectFolder' in self.__dict__.keys():
            self.sendSetupInputToModel()
            # on close save the xml files
            self.writeNewXML()
            self.dbHandler.closeDatabase
        #close the fileblocks
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i)
            page.close()
    #TODO add progress bar for uploading raw data and generating fixed data pickle
    def addProgressBar(self):
        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setObjectName('uploadBar')
        self.progress.setGeometry(100,100,100,50)
        return self.progress

    # add a new file input tab
    def newTab(self,i=0):
        # get the set count
        tab_count = self.tabs.count() +1
        widg = FileBlock(self, tab_count)
        #widg.fillSetInfo()
        self.tabs.addTab(widg, 'Input' + str(tab_count))
        #if its not the default empty tab fill data into form slots
        if i>0:
            widg.fillData(self.model,i)

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()


    def createSubmitButton(self):
        button = QtWidgets.QPushButton()
        button.setText("Generate netCDF inputs")
        button.clicked.connect(self.generateNetcdf)
        return button


    #uses the current data object to generate input netcdfs
    def generateNetcdf(self):

        handler = UIToHandler()
        #df gets read in from TimeSeries processed data folder
        #component dictionary comes from setupXML's
        MainWindow = self.window()
        setupForm = MainWindow.findChild(QtWidgets.QWidget,'setupDialog')
        setupModel= setupForm.model
        if 'setupFolder' in setupModel.__dict__.keys():
            setupFile = os.path.join(setupModel.setupFolder, setupModel.project + 'Setup.xml')
            componentModel = setupForm.findChild(QtWidgets.QWidget,'components').model()
            #From the setup file read the location of the input pickle
            #by replacing the current pickle with the loaded one the user can manually edit the input and
            #  then return to working with the interface
            data = handler.loadInputData(setupFile)
            if data:
                df = data.fixed
                componentDict = {}
                if 'components' not in setupModel.__dict__.keys():
                    #generate components
                    setupForm.makeComponentList(componentModel)
                for c in setupModel.components:
                    componentDict[c.column_name] = c.toDictionary()
                #filesCreated is a list of netcdf files that were generated
                filesCreated = handler.createNetCDF(df, componentDict,setupModel.setupFolder)
                self.netCDFsLoaded.setText(', '.join(filesCreated))
            else:
                print("no data found")

    #generate a list of Component objects based on attributes specified ModelSetupInformation
    #
    def getComponentsFromSetup(self):
        for i,c in enumerate(self.model.componentName.value):
            self.model.makeNewComponent(c,self.model.headerName.value[i],
                                        self.model.componentAttribute.unit[i],
                                        self.model.componentAttribute.value[i],
                                        None)

#classes used for displaying wizard inputs
class WizardPage(QtWidgets.QWizardPage):
    def __init__(self, inputdict,**kwargs):
        super().__init__()
        self.first = kwargs.get('first')
        self.last = kwargs.get('last')
        self.initUI(inputdict)

    # initialize the form
    def initUI(self, inputdict):
        self.d = inputdict
        self.setTitle(inputdict['title'])
        self.input = self.setInput()

        self.input.setObjectName(inputdict['name'])
        self.label = QtWidgets.QLabel()
        self.label.setText(inputdict['prompt'])
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)
        n = inputdict['name']
        self.registerField(inputdict['name'],self.input)

        return

    def setInput(self):
        wid = QtWidgets.QLineEdit()
        return wid

    def getInput(self):
        return self.input.text()

class ComponentSelect(WizardPage):
    def __init__(self,d):
        super().__init__(d)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        layout = QtWidgets.QGridLayout()

        handler = ProjectSQLiteHandler()
        lot = handler.getComponentTypes() #all possible component types

        for i,t in enumerate(lot):
            print(t)
            label = QtWidgets.QLabel()
            label.setText(t[1])
            comp = QtWidgets.QSpinBox()
            comp.setObjectName(t[0] + 'count')

            layout.addWidget(label,i,0,1,1)
            layout.addWidget(comp,i,1,1,1)
            self.registerField(comp.objectName(), comp)

        grp.setLayout(layout)
        return grp


class TwoDatesDialog(WizardPage):
    def __init__(self,d):
        super().__init__(d)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.startDate = QtWidgets.QDateEdit()
        self.startDate.setObjectName('start')
        self.startDate.setDisplayFormat('yyyy-MM-dd')
        self.startDate.setCalendarPopup(True)
        self.endDate = QtWidgets.QDateEdit()
        self.endDate.setObjectName('end')
        self.endDate.setDisplayFormat('yyyy-MM-dd')
        self.endDate.setCalendarPopup(True)
        box.addWidget(self.startDate)
        box.addWidget(self.endDate)
        grp.setLayout(box)
        name = self.d['name']
        self.registerField('sdate', self.startDate,"text")
        self.registerField('edate',self.endDate,"text")
        return grp

    def getInput(self):
        return " - ".join([self.startDate.text(),self.endDate.text()])

class DropDown(WizardPage):
    def __init__(self,d):
        super().__init__(d)

    def setInput(self):
        self.input = QtWidgets.QComboBox()
        self.input.setItems(self.getItems())
        return
    def getInput(self):
        return self.breakItems(self.input.itemText(self.input.currentIndex()))

    def getItems(self):

        items = self.dbHandler.getCodes(self.d['reftable'])
        return items
    def breakItems(self,str):
        item = str.split(' - ')[0]
        return item


class TextWithDropDown(WizardPage):
    def __init__(self, d):
        super().__init__(d)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.combo = QtWidgets.QComboBox()

        self.combo.addItems(self.getItems())
        self.text = QtWidgets.QLineEdit()
        self.text.setValidator(QtGui.QIntValidator())
        box.addWidget(self.text)
        box.addWidget(self.combo)
        grp.setLayout(box)
        #self.registerField(self.d['name'],self.combo,"currentText",self.combo.currentIndexChanged)
        self.registerField('timeInterval',self.text)
        self.registerField('timeUnit',self.combo,"currentText")
        return grp

    def getInput(self):
        input = self.text.text()
        item = self.breakItems(self.input.itemText(self.input.currentIndex()))
        strInput = ' '.join([input,item])
        return strInput
    def getItems(self):
        dbHandler = ProjectSQLiteHandler()
        items = dbHandler.getCodes(self.d['reftable'])
        dbHandler.closeDatabase()
        return items

    def breakItems(self, str):
        item = str.split(' - ')[0]
        return item