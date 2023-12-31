# Projet: MiGRIDS
# Created by: T. Morgan# Created on: 11/8/2019
#
'''
The FormSetup widget has 3 purposes.
1. Creates or loads a setup.xml file for a specific project
2. It creates or loads descriptor xml files for each component that will be included in the model
3. It ties individual components to an input file containing timer series values for each component
wind turbine components can have either an associated power time series or a windspeed file that a power time series will be generated from
In the case of a windspeed file a windspeed netcdf file will be generated and power time series will be generated once the model is run based
on each wtg components descriptor file.'''
import os
import datetime
from glob import glob

from PyQt5 import QtWidgets, QtCore

from MiGRIDS.UserInterface.ComponentTableBlock import ComponentTableBlock
from MiGRIDS.UserInterface.FormModelRuns import FormModelRun
from MiGRIDS.UserInterface.BaseForm import BaseForm
from MiGRIDS.UserInterface.FileBlock import FileBlock
from MiGRIDS.UserInterface.Pages import Pages
from MiGRIDS.Controller.loadProjectOffUIThread import ThreadedProjectLoad
from MiGRIDS.UserInterface.CustomProgressBar import CustomProgressBar
from MiGRIDS.UserInterface.DetailsWidget import DetailsWidget
from MiGRIDS.UserInterface.TableHandler import TableHandler
from MiGRIDS.UserInterface.WizardPages import WizardPage, TextWithDropDown, ComponentSelect, TwoDatesDialog
from MiGRIDS.UserInterface.makeButton import makeButton
from MiGRIDS.UserInterface.ResultsSetup import  ResultsSetup
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.Resources.SetupWizardDictionary import *


BASESET ='Set0'


class FormSetup(BaseForm):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()



    #initialize the form
    def initUI(self):

        self.controller.sender.statusChanged.connect(self.onControllerStateChange)

        self.setObjectName("setupDialog")

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()

        # the top block is buttons to load setup xml and data files
        self.createTopButtonBlock()
        windowLayout.addWidget(self.ButtonBlock)
        self.makeTabs(windowLayout)
        self.makeTableBlock()
        windowLayout.addWidget(self.tableBlock,stretch=6)
        #list of dictionaries containing information for wizard
        #this is the information that is not input file specific.
        self.WizardTree = self.buildWizardTree(dlist)
        self.createBottomButtonBlock()
        windowLayout.addWidget(self.BottomButtons)
        #set the main layout as the layout for the window

        self.setLayout(windowLayout)
        #title is setup
        self.setWindowTitle('Input Files')

        self.grantPermissions()
        #show the form
        self.showMaximized()
        return

    def makeTableBlock(self):
        self.tableBlock = ComponentTableBlock(self)
        try:
            self.updateComponentDelegate(self.preview, self.tableHandler)
        except AttributeError as a:
            pass

        return
    def tabChanged(self,index):
        if self.tabs.currentWidget() != None:
            preview = self.tabs.currentWidget().preview
            if preview != None:
                self.updateComponentHeaders(preview)
        return
    def makeTabs(self, windowLayout):
        # each tab is for an individual input file.
        self.tabs = Pages(self, 1, FileBlock)
        self.tabs.setDisabled(True)
        # button to create a new file tab
        newTabButton = QtWidgets.QPushButton()
        newTabButton.setText(' + Input')
        newTabButton.setFixedWidth(100)
        newTabButton.clicked.connect(self.newTab)

        windowLayout.addWidget(newTabButton)
        windowLayout.addWidget(self.tabs, stretch = 1)
        self.connectDelegateUpdateSignal()
        #tab switch signal
        self.tabs.currentChanged.connect(self.tabChanged)


    def connectDelegateUpdateSignal(self):
        loFileBlock = self.findChildren(FileBlock)
        for f in loFileBlock:
            f.updateComponentDelegates.connect(self.updateComponentDelegates)
    def clearInput(self):
        loFileBlock = self.findChildren(FileBlock)
        for f in loFileBlock:
            f.BLOCKED = True
        super().clearInput()

    def createTopButtonBlock(self):
        '''
        create the layout containing buttons to load or create a new project
        :return: QWidgets.QHBoxLayout
        '''
        self.ButtonBlock = QtWidgets.QGroupBox()
        hlayout = QtWidgets.QHBoxLayout()
        #layout object name
        hlayout.setObjectName('buttonLayout')
        #add the button to load a setup xml
        hlayout.addWidget(makeButton(self, self.functionForLoadButton,
                                 'Load Existing Project', None, 'Load a previously created project files.','loadProject'))

        #add button to launch the setup wizard for setting up the setup xml file
        hlayout.addWidget(
            makeButton(self, self.functionForCreateButton,
                                 'New Project', None, 'Start the setup wizard to create a new setup file','createProject'))
        #force the buttons to the left side of the layout
        hlayout.addStretch(1)

        self.ButtonBlock.setLayout(hlayout)

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
        self.createInputButton = QtWidgets.QPushButton('Create input files')
        self.createInputButton.setToolTip('Create input files to run models')
        self.createInputButton.clicked.connect(lambda: self.onClick(self.createInputFiles))
        self.createInputButton.setFixedWidth(200)
        # windowLayout.addWidget(makeButtonBlock(self,self.createInputFiles,'Create input files',None,'Create input files to run models'),3)
        hlayout.addWidget(self.createInputButton)
        #make the data log viewing button
        self.detailsBtn = QtWidgets.QPushButton('Details')
        self.detailsBtn.setToolTip('View data fixing log.')
        self.detailsBtn.clicked.connect(lambda: self.onClick(self.viewLogDetails))
        self.detailsBtn.setFixedWidth(200)
        self.detailsBtn.setEnabled(False)
        hlayout.addWidget(self.detailsBtn)

        self.dataLoadedOutput = QtWidgets.QLineEdit()
        self.dataLoadedOutput.setFrame(False)
        self.dataLoadedOutput.setFixedWidth(200)
        hlayout.addWidget(self.dataLoadedOutput)

        # generate netcd button
        self.netCDFButton = self.createSubmitButton()
        hlayout.addWidget(self.netCDFButton)

        self.loadNetCDFButton = self.createLoadNetcdfButton()
        hlayout.addWidget(self.loadNetCDFButton)

        self.switchGenerateNetcdf(False)

        self.netCDFButton.setFixedWidth(200)
        self.currentNetcdfs  = QtWidgets.QLineEdit()
        self.currentNetcdfs.setFrame(False)

        hlayout.addWidget(self.currentNetcdfs)
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

    def viewLogDetails(self):
        '''Opens a window for viewing data fixing metrics and log file'''
        try:
            self.details = DetailsWidget('Bad Data Log',self.controller.inputData.badDataDict)
        except AttributeError as e:
            print (e)
            print('no data transformation log found')
        return

    def functionForCreateButton(self):
        '''
        Launches the setup process for creating a new project
        :return: None
        '''
        #if a project is already started save it before starting a new one
        try:
            if (self.controller.project != '') & (self.controller.project is not None):
                if self.validateProjectSwitch() != True:
                    return

        except AttributeError as e:
            print("Project not set yet")
        self.createNewProject()

    def resetValidateStatus(self):
        self.controller.initializeState()

    def saveInput(self):
        pass
    def createNewProject(self):
        # calls the setup wizard to fill the database from wizard information
        self.controller.initializeState()
        self.fillSetup()

        # if setup is valid enable tabs
        if self.controller.setupValid:
            # enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget, 'pages')
            pages.enableTabs()
            self.tabs.setEnabled(True)
            #FileBlock mapper needs to be set to a new records so information can be saved
            self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.controller.project)
        self.tableBlock.tableModel.select()
        return
    def validateProjectSwitch(self):
        '''
        launches a dialog to make sure the user wants to switch projects
        :return: Boolean, True if user selects yes to dialog.
        '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Project has already been set.",
                                    "Do you want to switch to a new project?.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        newProject = msg.exec()
        if newProject == QtWidgets.QMessageBox.Yes:
            self.resetValidateStatus()
            pathTo = self.controller.dbhandler.getProjectPath()
            self.controller.switchProject(self,pathTo)
            return True
        else:
            return False

    def onControllerStateChange(self):
        self.grantPermissions()
        return
    def grantPermissions(self):
        self.tabs.setEnabled(self.controller.setupValid)
        self.createInputButton.setEnabled(self.controller.setupValid)
        if self.controller.dataObjectValid:
            self.dataLoadedOutput.setText('Data Loaded')
            self.updateFormProjectDataStatus()
        else:
            self.dataLoadedOutput.setText('')
        self.switchGenerateNetcdf(self.controller.dataObjectValid)
        self.detailsBtn.setEnabled(self.controller.dataObjectValid)
        self.currentNetcdfs.setText(",".join(self.controller.netcdfs))
        self.updateSetRunnable(self.controller.netcdfsValid)
        return
    def switchGenerateNetcdf(self, hasDataObject):
        self.netCDFButton.setEnabled(hasDataObject) #generate button becomes enabled or disabled
        self.netCDFButton.setVisible(hasDataObject)
        self.loadNetCDFButton.setEnabled(not hasDataObject) #load becomes enabled or disabled
        self.loadNetCDFButton.setVisible(not hasDataObject)
    def prePopulateSetupWizard(self):
            #rebuild the wizard tree with values pre-set
            self.WizardTree = self.buildWizardTree(dlist)
            self.fillSetup()

    def fillSetup(self):
        '''
        calls the setup wizard to fill setup information into the project_manager database and subsequently to setup.xml
        :return:
        '''
        self.WizardTree.exec_()

    def procedeToSetup(self,pathToCheck):
        '''Evaluates whether or not the setup input should be generated. If a setup file already exists then the user needs to
        indicate they are willing to overwrite that file
        :return Boolean True if the input should be written to a file. False if the input needs to be altered.'''

        # If the project already exists wait to see if it should be overwritten
        # assign project has already been called at this point so the directory is created
        if self.hasSetup(pathToCheck):
            overwrite = self.checkOverride("Project Aready Exists",
                                    "Do you want to overwrite existing setup files?.")
            if not overwrite:
                #self.fillSetup()  # call up the wizard again so a new project name can be assigned

                self.WizardTree.restart()
                return False
            else:

                return True # this line won't get reached until an original project name is generated or overwrite is chose
        else:
            return True

    def checkOverride(self,title,msg):
        '''message dialog ot check if files should be overwritten
           :return Boolean True if yes button was triggered     '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, title,msg)
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        overwrite = msg.exec()
        if overwrite != QtWidgets.QMessageBox.Yes:
            return False
        else:
            return True
    def hasSetup(self,pathToCheck):
        setupFolder = getFilePath('Setup',projectFolder=pathToCheck)

        if glob(os.path.join(setupFolder,'*etup.xml')):
            return True
        return False

    #searches for and loads existing project data - database, setupxml,descriptors, DataClass pickle, Component pickle netcdf,previously run model results, previous optimization results
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''

        #if we were already working on a project its state gets saved and  new project is loaded
        if (self.controller.dbhandler.getProjectPath() != '') & (self.controller.dbhandler.getProjectPath() is not None):
            pathTo = self.controller.dbhandler.getProjectPath()
            self.controller.switchProject(self,pathTo)
            self.controller.createDatabaseConnection()

        #launch file navigator to identify setup file
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects'), "*xml" ,options=QtWidgets.QFileDialog.DontUseNativeDialog)
        if (setupFile == ('','')) | (setupFile is None):
            return
        self.controller.setupFile = setupFile
        self.progressBar = CustomProgressBar('Loading Project')
        try:
            # when thread finishes self.controller.inputData and self.components are set
            self.myThread = ThreadedProjectLoad(setupFile[0])
            self.myThread.notifyCreateProgress.connect(self.progressBar.onProgress)
            self.myThread.signalUpdateAttribute.connect(self.controller.updateAttribute)
            self.myThread.finished.connect(self.onProjectLoaded)
            self.myThread.start()
        except Exception as e:
            print(e)

    def onProjectLoaded(self):
        try:
            setupFolder = getFilePath("Setup", projectFolder=self.controller.dbhandler.getProjectPath())
            setupXML = os.path.join(setupFolder, self.controller.project + 'Setup.xml')
            self.controller.validator.validateSetupXML(setupXML)
            self.controller.sender.callStatusChanged()
            # the number of directories listed in inputFileDir indicates how many tabs are required
            tab_count = len(self.controller.dbhandler.getAllRecords('input_files'))
            self.displayTabbedData(tab_count, 1) #update the form with loaded data
            #self.updateFormProjectDataStatus()
            self.updateComponentFiles()
            self.updateComponentNameList()

            #boolean indicator of whether or not model sets have already been run
            #make the data blocks editable if there are no sets already created
            #if sets have been created then input data is not editable from the interface
            if self.setsRun():
                self.showAlert("Analysis in Progress","Analysis results were detected. You cannot edit input data after analysis has begun.")
            else:
                self.tabs.setEnabled(True)
                print('Loaded %s:' % self.controller.project)

            #set the project name on the GUI form
            self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.controller.project)
        except Exception as e:
            print("project not loaded successfully")
        finally:
            self.progressBar.hide()
        return

    def setsRun(self):
        '''Checks the database for existing run data
        If data is found returns true, otherwsie false'''
        if self.controller.dbhandler.modelsRun():
            return True
        return False

    def makeComponentList(self):
        '''Gets a list of all components in the component table'''
        loc = self.controller.dbhandler.makeComponents()
        return loc

    def buildWizardTree(self, dlist):
        '''
        Builds a QWizard based on a list of inputs
        :param dlist: a list of dictionaries, list item becomes a page in the wizard tree
        :return: a QWizard
        '''
        wiztree = QtWidgets.QWizard(self)
        wiztree.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        wiztree.setWindowTitle("Setup")
        wiztree.addPage(WizardPage(dlist[3],self.controller.dbhandler,self))  #project name
        wiztree.addPage(TextWithDropDown(dlist[2],self.controller.dbhandler,self)) #timesteps
        wiztree.addPage(ComponentSelect(dlist[1],self.controller.dbhandler,self))  #components
        wiztree.addPage(TwoDatesDialog(dlist[0],self.controller.dbhandler,self))  #runtimesteps
        btn = wiztree.button(QtWidgets.QWizard.FinishButton)
        btn.clicked.disconnect()
        #disconnect(btn,SIGNAL(clicked()),self, SLOT(accept()))
        btn.clicked.connect(self.saveTreeInput)
        return wiztree

    def saveTreeInput(self):
        '''
        save the input in the wizard tree attribute to the database
        It is assumed that the database is empty (cleared on switchproject or never filled)
        :return: None
        '''
        projectDefaultPath = os.path.join(os.path.dirname(__file__),
                                                       *['..', '..', 'MiGRIDSProjects', self.WizardTree.field('project')])
        if self.procedeToSetup(projectDefaultPath): #this checks if we are overwriting an existing setup file
            project_id = self.controller.dbhandler.insertRecord("project",['project_name','project_path'],[self.WizardTree.field('project'),
                                                                                                           projectDefaultPath])

            _id = self.controller.dbhandler.insertRecord("setup",['_id','project_id','timestepvalue','timestepunit','date_start','date_end'],
                                                         [project_id,1,self.WizardTree.field('timestepvalue'),self.WizardTree.field('timestepunit'),self.WizardTree.field('sdate'),self.WizardTree.field('edate')])

            if _id == -1: #record was not inserted, try updating
                self.controller.dbhandler.updateRecord("setup",["_id"],[1],['project_id','timestepvalue','timestepunit','date_start','date_end','runtimestepvalue'],
                                       [project_id,  self.WizardTree.field('timestepvalue'),
                                        self.WizardTree.field('timestepunit'), self.WizardTree.field('sdate'),
                                        self.WizardTree.field('edate'), str.join(" ",[self.WizardTree.field('sdate'),
                                        self.WizardTree.field('edate')])])


            lot = self.controller.dbhandler.getComponentTypes()
            for t in lot:
                cnt = self.WizardTree.field(t[0]+'count')
                for i in range(0,cnt):
                    comp_id = self.controller.dbhandler.insertRecord('component',['componentnamevalue','componenttype'],[t[0] + str(i),t[0]])

                    #the delegate for componentname in the component table should also be updated and record should be inserted into inputfiles
                    if comp_id != -1:
                        file_id = self.controller.dbhandler.insertRecord('component_files',['component_id','componenttype'],[comp_id,t[0]])
                        loFileBlock = self.findChildren(FileBlock)
                        for f in loFileBlock:
                           self.updateComponentNameList()

            self.WizardTree.close()
            self.controller.newProject()
            #self.ComponentTable.model().createRelations()
        return
    def createInputFiles(self):
        '''
        Create a dataframe of input data based on importing files within each SetupModelInformation.inputFileDir
        '''
        if not self.controller.setupValid:
            #if required fields are not filled in return to setup page.
            self.showAlert("Missing Required Fields",
                                        "Please fill in all required fields before generating input files.")

            return
        result = self.tableBlock.tableModel.submit()
        if not result:
            print(self.tableBlock.tableModel.lastError().text())
        #make sure everything is in the setup file
        self.controller.setupHandler.makeSetup(self.controller.project, self.controller.setupFolder)

        self.progressBar = CustomProgressBar('Data fixing')
        self.controller.sender.notifyProgress.connect(self.progressBar.onProgress)
        try:
            #when thread finishes self.controller.inputData and self.components are set
            self.controller.createInputData() #this spins up a new thread

        except Exception as e:
            print(e)

        return
    def updateFormProjectDataStatus(self):
        '''updates the setup form to reflect project data (DataClass object, Component info, netcdfs)status
        '''
        #self.refreshTable()
        try:
           # update the Model tab with set information
            self.updateDependents(self.controller.inputData) #make sure there is data here
        except Exception as e:
            print(e)
    def setResultForm(self):
        self.resultObject = ResultsSetup
    def updateDependents(self, data = None):
        '''
        updates the default component list, time range and time step values in the setup table in the project database
        based on fields and timesteps found in data.fixed and passes these values to the ModelDialog
        :param data: DataClass with a pandas.DataFrame named fixed which contains a datetime index
        :return: None
        '''
        # start and end dates get set written to database as default date ranges

        values = self.updateInputDataDependents(data)
        self.updateModelInputDependents(values)
        return
    def updateSetRunnable(self,hasnetcdf):
        if hasnetcdf:
            self.updateDependents()
    def updateModelInputDependents(self, values):
        if len(self.controller.sets)<=0:
            self.controller.dbhandler.updateSetSetup('Set0',values)
            self.controller.dbhandler.insertAllComponents('Set0')
        modelForm = self.window().findChild(FormModelRun)
        modelForm.projectLoaded()
        return
    def updateInputDataDependents(self, data = None):
        ''':return dictionary of values relevant to a setup file'''

        def getDefaults(listDf, defaultStart=datetime.datetime.today().date(), defaultEnd=datetime.datetime.today().date()):
            '''
            returns the earliest and latest date index found in a list of dataframes with date indices. Will return initial default
            start and end if no dates are found in dataframes.
            :param listDf: is a list of pandas.dataframes, all with a date index
            :param defaultStart: pandas date value that will be the default start date if none is found in the list of dataframes
            :param defaultEnd: pandas date value that will be the default end date if none is found in the list of dataframes
            :return: String start date, String end date
            '''

            if len(listDf) > 0:
                s = datetime.datetime.strftime(listDf[0].index[0],'%Y-%m-%d %H:%M:%S')
                e = datetime.datetime.strftime(listDf[0].index[len(listDf[0]) - 1],'%Y-%m-%d %H:%M:%S')
                return str(s), str(e)
            return str(defaultStart), str(defaultEnd)

        # default start is the first date there is record for
        values = {}
        if data!= None:
            values['date_start'], values['date_end'] = getDefaults(data.fixed)
        else:
            values['date_start'], values['date_end'] = getDefaults([])
        values['runtimestepsvalue'] = ' '.join([values['date_start'],values['date_end']])
        self.controller.dbhandler.updateFromDictionaryRow('setup',values,['_id'],[1]) #update the setup to reflect the actual span of the dataframe
        values['date_start'] = [values['date_start']]
        values['date_end'] = [values['date_end']]
        values['set_name'] = ['Set0']
        info = self.controller.dbhandler.getSetUpInfo()
        if info is None:
            info = self.controller.dbhandler.getSetInfo()
        values['timestepvalue'] = [info['timeStep.value']]
        values['timestepunit'] = [info['timeStep.unit']]
        values['project_id'] = [1]  # always 1, only 1 project per database

        # deliver the data to the ResultsSetup form so it can be plotted
        if data != None:
            resultsForm = self.window().findChild(ResultsSetup)
            resultsForm.setData(self.controller.inputData)
            resultsForm.makePlotArea()
            resultsForm.defaultPlot()#getting called first time here

        return values

    def closeEvent(self, event):
        ''' closeEvent is triggered when the form is closed
        called by FormContainer
        :param: qt event'''
        if self.controller.projectFolder != None:
            # close the fileblocks
            #make sure database is up to date with fileblock data
            for i in range(self.tabs.count()):
                page = self.tabs.widget(i)
                page.close()
            #make sure database is up to date with component table data
            self.tableBlock.tableModel.submit()
            #Write the setup file - don't overwrite descriptors
            self.controller.setupHandler.makeSetup(self.controller.project, self.controller.setupFolder) #The setup form always contains information for set0



    def newTab(self,i=0):
        # get the set count
        tab_count = self.tabs.count() +1
        widg = FileBlock(self, tab_count)
        self.tabs.addTab(widg, 'Input' + str(tab_count))
        self.connectDelegateUpdateSignal()

    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()

    def createLoadNetcdfButton(self):
        '''
        Create a button to initiate the creation of netcdf files for model input
        :return: QtWidget.QPushButton
        '''
        button = QtWidgets.QPushButton()
        button.setText("Load netCDF inputs")
        button.clicked.connect(self.readNetcdf)
        return button
    def readNetcdf(self):
        self.controller.loadNetcdfs()
        return

    def createSubmitButton(self):
        '''
        Create a button to initiate the creation of netcdf files for model input
        :return:  QtWidget.QPushButton
        '''
        button = QtWidgets.QPushButton()
        button.setText("Generate netCDF inputs")
        button.clicked.connect(self.generateModelInput)
        return button
    def generateModelInput(self):
        '''Checks if setup of file is valid, looks for existing model netcdf files, and dataclass objects
        if no netcdf files are found attempts to create them from dataclass object
        if no dataclass object is found attempts to create a dataclass object then create netcdfs
        :return boolean True if there is a netcdf file for each component'''
        if self.controller.setupValid:
            if self.controller.netcdfsValid:
                #don't need to do anything because model inputs already generated
                if self.checkOverride("NetCDF Inputs Already Exist", "Do you want to re-write these files?") == False:
                    return

            if not self.controller.dataObjectValid:
                self.controller.inputData = self.makeData()
                #make netcdf from dataclass object
            self.controller.generateNetcdf(self.controller.inputData)
            return
        else:
            self.fixSetup()
            self.generateModelInput()
    def fixSetup(self):
        '''warns the user the setup file is not valid and re-opens the setup wizard so inputs can be corrected.'''
        self.showAlert("Setup file invalid","Please correct your setup input")
        self.prePopulateSetupWizard()



    def saveTables(self):
        '''get data from component and environment tables and update the setupInformation model
        components within a single directory are seperated with commas
        component info comes from the database not the tableview
        component names, units, scale, offset, attribute, fieldname get saved'''

        self.tableBlock.tableModel.submitAll()
        print(self.tableBlock.tableModel.lastError().text())

        #loC = [makeNewComponent(df['component_name'],x['original_field_name'],
        #                             x['units'],x['attribute'],x['component_type']) for i,x in df.iterrows()]
        return #loC

    def updateComponentDelegates(self, preview):

        self.updateComponentHeaders(preview)
        self.updateComponentFiles()
        self.updateComponentNameList()
        self.tableBlock.tableModel.makeModel()

    def updateComponentFiles(self):

        self.tableBlock.updateComponentDelegate(None, self.tableBlock.tableView, 'inputfiledirvalue')
        self.tableBlock.tableModel.makeModel()
        return
    def updateComponentHeaders(self, preview):
        self.tableBlock.updateComponentDelegate(preview.header, self.tableBlock.tableView, 'headernamevalue')

    def updateComponentNameList(self):

        # tableHandler.updateComponentDelegate(self.controller.dbhandler.getAsRefTable('component', '_id', 'componentnamevalue'),
        #                                      self.ComponentTable, 'componentnamevalue')
        self.tableBlock.updateComponentDelegate(None, self.tableBlock.tableView, 'componentnamevalue')
        self.tableBlock.displayData()
    def loadDescriptor(self):
        self.tableBlock.functionForLoadDescriptor()

    def getNextName(self,componentType):
        '''returns the id of the next component name to use for a specified component type
        Returns none if not component names are left
        :param componentType String type of component
        :return integer or none'''
        allNames = set(self.controller.dbhandler.getComponentByType(componentType)) #returns tuples of id and name
        usedNames = set(self.controller.dbhandler.getComponentFilesByType(componentType))#returns tuples of id and name
        unusedNames = allNames.difference(usedNames) #return list of unused componentNames
        if len(unusedNames)>0:
            return list(unusedNames)[0][1] #return the name of the first unused name

        return
    def getComponentNameCount(self, componentType):
        allNames = set(self.controller.dbhandler.getComponentByType(componentType))
        return len(allNames)
    def getComponentTypeCount(self, componentType):
        return self.controller.dbhandler.getTypeCount(componentType)
    def addName(self,componentType,currentCount):

        self.controller.dbhandler.insertRecord('component',['componenttype','componentnamevalue'],[componentType,componentType + str(currentCount)])
        self.updateComponentNameList()