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
from MiGRIDS.Controller.UIToInputHandler import UIToHandler
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.ResultsSetup import  ResultsSetup
from MiGRIDS.UserInterface.FormModelRuns import SetsTableBlock
from MiGRIDS.UserInterface.Pages import Pages
from MiGRIDS.UserInterface.FileBlock import FileBlock
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.switchProject import switchProject
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.replaceDefaultDatabase import replaceDefaultDatabase
from MiGRIDS.UserInterface.Resources.SetupWizardDictionary import *

BASESET ='Set0'
class FormSetup(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
    #initialize the form
    def initUI(self):
        self.dbhandler = ProjectSQLiteHandler()
        self.uihandler = UIToHandler()
        self.setObjectName("setupDialog")
        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()

        # the top block is buttons to load setup xml and data files
        self.createButtonBlock()
        windowLayout.addWidget(self.ButtonBlock)
        self.makeTabs(windowLayout)

        #list of dictionaries containing information for wizard
        #this is the information that is not input file specific.

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
        windowLayout.addWidget(self.tabs, 3)
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
        self.dataLoadedOutput = dataLoaded
        hlayout.addWidget(self.dataLoadedOutput)
        #TODO make progress bar invisible until we need it
        self.addProgressBar()
        hlayout.addWidget(self.progressBar)
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
        Launches the setup process for creating a new project
        :return: None
        '''
        #if a project is already started save it before starting a new one
        try:
            if (self.project != '') & (self.project is not None):
                if self.validateProjectSwitch() != True:
                    return

        except AttributeError as e:
            print("Project not set yet")
        self.createNewProject()
    def createNewProject(self):
        # calls the setup wizard to fill the database from wizard information
        self.fillSetup()
        self.projectDatabase = False
        # if setup is valid enable tabs
        if self.hasSetup():
            # enable the model and optimize pages too
            pages = self.window().findChild(QtWidgets.QTabWidget, 'pages')
            pages.enableTabs()
            self.tabs.setEnabled(True)
            #FileBlock mapper needs to be set to a new records so information can be saved
            self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.project)
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
            switchProject(self)
            return True
        else:
            return False
    def hasSetup(self):
        try:

            setupfolder = self.uihandler.findSetupFolder(self.project)
            if os.path.exists(os.path.join(setupfolder, self.project + 'Setup.xml')):
                return True
        except AttributeError as e:
            return False
        return False

    def loadSetup(self, setupFile):

        #setup is a dictionary read from the setupFile
        setup = self.uihandler.inputHandlerToUI(setupFile, BASESET)
        self.assignProjectPath(setup['project'])
        self.displayModelData(setup)
    def showSetup(self):
            #rebuild the wizard tree with values pre-set
            self.WizardTree = self.buildWizardTree(dlist)
            self.WizardTree.exec()
    def fillSetup(self):
        '''
        calls the setup wizard to fill setup information into the project_manager database and subsequently to setup.xml
        :return:
        '''
        s = self.WizardTree
        s.exec_()

    def procedeToSetup(self):
        '''Evaluates whether or not the setup input should be generated. If a setup file already exists then the user needs to
        indicate they are willing to overwrite that file
        :return Boolean True if the input should be written to a file. False if the input needs to be altered.'''

        # If the project already exists wait to see if it should be overwritten
        # assign project has already been called at this point so the directory is created
        if self.setupExists():
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
    def setupExists(self):
        '''

        :return: Boolean True if a setup file is found in the specified setup folder
        '''
        try:
            setupfolder = self.setupFolder
        except AttributeError as a:

            setupfolder = self.uihandler.findSetupFolder(self.project)
        finally:
            if os.path.exists(os.path.join(setupfolder, self.project + 'Setup.xml')):
                return True
            else:
                return False
    #searches for and loads existing project data - database, setupxml,descriptors, DataClass pickle, Component pickle netcdf,previously run model results, previous optimization results
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''

        #if we were already working on a project its state gets saved and  new project is loaded
        if (self.dbhandler.getProjectPath() != '') & (self.dbhandler.getProjectPath() is not None):
            switchProject(self)


        #launch file navigator to identify setup file
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects'), "*xml" )
        if (setupFile == ('','')) | (setupFile is None):
            return

        self.loadSetup(setupFile[0])

        # now that setup data is set display it in the form
        #self.displayModelData() this should be done with binding

        #Look for an existing project database and replace the default one with it
        if os.path.exists(os.path.join(self.projectFolder,'project_manager')):
            print('An existing project database was found for %s.' %self.project)

            replaceDefaultDatabase(os.path.join(self.projectFolder, 'project_manager'))
            self.projectDatabase = True
        else:
            self.projectDatabase = False
            print('An existing project database was not found for %s.' % self.project)
        # record the current project

        i = self.dbhandler.updateRecord('project', ['project_name'],[self.project],['project_path'],
                                        getFilePath('Project',setupFolder=os.path.dirname(setupFile[0])))

        # look for an existing data pickle
        self.inputData= self.uihandler.loadInputData(
            os.path.join(self.setupFolder, self.project + 'Setup.xml'))

        if self.inputData is not None:
            self.updateModelPage(self.inputData)
            self.dataLoadedOutput.setText('data loaded')
            #refresh the plot
            resultDisplay = self.parent().findChild(ResultsSetup)
            resultDisplay.defaultPlot()

        #look for an existing component pickle or create one from information in setup xml
        self.components = self.uihandler.loadComponents(os.path.join(self.setupFolder, self.project + 'Setup.xml'))
        if self.components is None:
            self.makeComponentList()

        #list netcdf files previously generated
        self.netCDFsLoaded.setText('Processed Files: ' + ', '.join(self.listNetCDFs()))
        #TODO this part of the code always sets setsRun to false, need to implement check for models run
        #boolean indicator of whether or not model sets have already been run
        setsRun = False
        #make the data blocks editable if there are no sets already created
        #if sets have been created then input data is not editable from the interface
        if setsRun:
            self.showAlert("Analysis in Progress","Analysis results were detected. You cannot edit input data after analysis has begun.")
        else:
            self.tabs.setEnabled(True)
            print('Loaded %s:' % self.project)

        #set the project name on the GUI form
        self.findChild(QtWidgets.QLabel, 'projectTitle').setText(self.project)
        return
    def makeComponentList(self):
        loc = self.dbhandler.makeComponents()
        return loc
    def showAlert(self,title,msg):
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,title ,msg
                                    )
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()
    def listNetCDFs(self):
        '''
        produces a list of netcdf files located in the Processed folder of a project TimeSeries folder
        :return: List of Strings of names of netCDF files
        '''
        try:
            lof = [f for f in os.listdir(getFilePath('Processed',setupFolder=self.setupFolder,)) if f[-2:] =='nc']
            return lof
        except FileNotFoundError as e:
            print('No netcdf model files found.')
            return
    def displayModelData(self,setupInfo):
        """creates a tab for each input directory specified the SetupModelInformation model inputFileDir attribute.
        Each tab contains a FileBlock object to interact with the data input
        Each FileBlock is filled with data specific to the input directory"""
        self.tabs.removeTab(0)
        #the number of directories listed in inputFileDir indicates how many tabs are required
        tab_count = len(setupInfo['inputFileDir.value'].split(' '))
        #if directories have been entered then replace the first tab and create a tab for each directory
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
        wiztree = QtWidgets.QWizard(self)
        wiztree.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        wiztree.setWindowTitle("Setup")
        wiztree.addPage(WizardPage(dlist[3],self))  #project name
        wiztree.addPage(TextWithDropDown(dlist[2],self)) #timesteps
        wiztree.addPage(ComponentSelect(dlist[1],self))  #components
        wiztree.addPage(TwoDatesDialog(dlist[0],self))  #runtimesteps
        btn = wiztree.button(QtWidgets.QWizard.FinishButton)
        btn.clicked.disconnect()
        #disconnect(btn,SIGNAL(clicked()),self, SLOT(accept()))
        btn.clicked.connect(self.saveTreeInput)
        return wiztree
    def assignProjectPath(self, name):
            self.project = name
            self.setupFolder = os.path.join(os.path.dirname(__file__), *['..','..','MiGRIDSProjects', self.project, 'InputData','Setup'])
            self.componentFolder = getFilePath('Components', setupFolder=self.setupFolder)
            projectFolder = getFilePath('Project', setupFolder=self.setupFolder)
            self.projectFolder = projectFolder

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
        projectPath = self.assignProjectPath(self.WizardTree.field('project'))
        if self.procedeToSetup():
            project_id = self.dbhandler.insertRecord("project",['project_name','project_path'],[self.WizardTree.field('project'),projectPath])
            _id = self.dbhandler.insertRecord("setup",['_id','project_id','timestepvalue','timestepunit','date_start','date_end'],[project_id,1,self.WizardTree.field('timestepvalue'),self.WizardTree.field('timestepunit'),self.WizardTree.field('sdate'),self.WizardTree.field('edate')])
            if _id == -1: #record was not inserted, try updating
                self.dbhandler.updateRecord("setup","_id",1,['project_id','timestepvalue','timestepunit','date_start','date_end','runtimestepvalue'],
                                       [project_id,  self.WizardTree.field('timestepvalue'),
                                        self.WizardTree.field('timestepunit'), self.WizardTree.field('sdate'),
                                        self.WizardTree.field('edate'), str.join(" ",[self.WizardTree.field('sdate'),
                                        self.WizardTree.field('edate')])])
                _id = self.dbhandler.getId('setup','_id',1)
            lot = self.dbhandler.getComponentTypes()
            for t in lot:
                cnt = self.WizardTree.field(t[0]+'count')
                for i in range(0,cnt):
                    comp_id = self.dbhandler.insertRecord('component',['componentnamevalue','componenttype'],[t[0] + str(i),t[0]])
                    #self.dbhandler.insertRecord('set_components',['component_id','set_id','tag'],[comp_id,_id,None])
                    #the delegate for componentname in the component table should also be updated
                    if comp_id != -1:
                        loFileBlock = self.findChildren(FileBlock)
                        for f in loFileBlock:
                           f.updateComponentNameList()

            self.uihandler.makeSetup()
            self.WizardTree.close()
        return

    def createInputFiles(self):
        '''
        Create a dataframe of input data based on importing files within each SetupModelInformation.inputFileDir
        '''


        #self.sendSetupInputToModel()
        # check all the required fields are filled

        # start with the setupxml

        self.uihandler.makeSetup()
        if not self.setupValid():
            #if required fields are not filled in return to setup page.
            self.showAlert("Missing Required Fields",
                                        "Please fill in all required fields before generating input files.")

            return
        if not self.dataValid():
            #when thread finishes self.inputData and self.components are set
            self.myThread = ThreadedDataCreate(self.setupFolder,self.project)

            self.myThread.notifyCreateProgress.connect(self.onProgress)
            self.myThread.catchComponents.connect(self.gotComponents)
            self.myThread.catchData.connect(self.gotData)
            self.myThread.finished.connect(self.dataLoaded)
            self.myThread.start()


        else:
            self.inputData = self.findDataObject()
            self.components = self.findComponents()
            self.dataLoaded()

        return

    def dataLoaded(self):
        # This has to happen after thread completes
        if self.inputData:
            self.updateModelPage(self.inputData)
            self.dataLoadedOutput.setText('data loaded')
            # refresh the plot
            resultDisplay = self.parent().findChild(ResultsSetup)
            resultDisplay.defaultPlot()
            self.progressBar.setRange(0, 1)
        # generate netcdf files
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Time Series loaded",
                                    "Do you want to generate netcdf files?.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
        result = msg.exec()
        # if yes create netcdf files, Otherwise this can be done after the data is reviewed.
        if result == QtWidgets.QMessageBox.Ok:
            self.makeNetcdfs()
        return

    def makeNetcdfs(self):
        d = {}
        for c in self.components:
            d[c.column_name] = c.toDictionary()
        self.ncs = self.uihandler.createNetCDF(self.inputData.fixed, d,
                                               os.path.join(self.setupFolder, self.project + 'Setup.xml'))

    def makeData(self):
        # import datafiles
        #TODO remove and call thread

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

            assert((type(df.index[0])==pd.Timestamp) | (type(df.index[0])==pd.datetime))

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
        values['date_start'] = [values['date_start']]
        values['date_end'] = [values['date_end']]
        values['set_name'] = ['set0']
        info = self.dbhandler.getSetUpInfo()
        values['timestepvalue']=[info['timeStep.value']]
        values['timestepunit']=[info['timeStep.unit']]
        values['project_id'] = [1] #always 1, only 1 project per database

        self.dbhandler.insertFirstSet(values)

        self.dbhandler.insertAllComponents('set0')

        # Deliver appropriate info to the ModelForm
        modelForm = self.window().findChild(SetsTableBlock)

        modelForm.updateForm()

        #deliver the data to the ResultsSetup form so it can be plotted
        resultsForm = self.window().findChild(ResultsSetup)
        resultsForm.setPlotData(data)
        resultsForm.defaultPlot()
    # close event is triggered when the form is closed

    def closeEvent(self, event):
        #save xmls
        if 'projectFolder' in self.__dict__.keys():
            #self.sendSetupInputToModel()
            # on close save the xml files

            self.uihandler.makeSetup() #The setup form always contains information for set0
            self.dbhandler.closeDatabase
        #close the fileblocks
        for i in range(self.tabs.count()):
            page = self.tabs.widget(i)
            page.close()

    def addProgressBar(self):
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setObjectName('progresBar')
        self.progressBar.setGeometry(100,100,100,50)


        self.progressBar.setAlignment(QtCore.Qt.AlignLeft);
        return

    def onProgress(self, i,task):
        self.progressBar.setValue(i)
        if i < 10:
            self.progressBar.setRange(0, 10)
            self.progressBar.setFormat(task + "...");
            self.progressBar.setTextVisible(True)
        else:
            self.progressBar.setTextVisible(False);
            self.progressBar.setRange(0,1)

    def newTab(self,i=0):
        # get the set count
        tab_count = self.tabs.count() +1
        widg = FileBlock(self, tab_count)
        self.tabs.addTab(widg, 'Input' + str(tab_count))
        #if its not the default empty tab fill data into form slots
        '''if i>0:
            widg.fillData(self.model,i)'''
    @QtCore.pyqtSlot()
    def onClick(self, buttonFunction):
        buttonFunction()
    def createSubmitButton(self):
        '''
        Create a button to initiate the creation of netcdf files for model input
        :return:
        '''
        button = QtWidgets.QPushButton()
        button.setText("Generate netCDF inputs")
        button.clicked.connect(self.generateModelInput)
        return button
    def setupValid(self):
        #TODO implement function to check if setup contains all the required input
        return True
    def generateModelInput(self):
        '''Checks if setup of file is valid, looks for existing model netcdf files, and dataclass objects
        if no netcdf files are found attempts to create them from dataclass object
        if no dataclass object is found attempts to create a dataclass object then create netcdfs
        :return boolean True if there is a netcdf file for each component'''
        if self.setupValid():
            if self.netcdfValid():
                #don't need to do anything because model inputs already generated
                if self.checkOverride("NetCDF Inputs Already Exist", "Do you want to re-write these files?") == False:
                    return True
            if self.dataValid():
                #make netcdf from dataclass object
                data = self.findDataObject()
                self.generateNetcdf(data)
                return self.netcdfValid()
            else:
                data = self.makeData()
                self.generateNetcdf(data)
                return self.netcdfValid()
        else:
            self.fixSetup()
            self.generateModelInput()
    def dataValid(self):
        if self.findDataObject() != None:
            return True
        else:
            return False
    def fixSetup(self):
        '''warns the user the setup file is not valid and re-opens the setup wizard so inputs can be corrected.'''
        self.showAlert("Setup file invalid","Please correct your setup input")
        self.showSetup()
    def netcdfValid(self):
        '''
        Checks to make sure there is a valid netcdf file for each component.
        :return: boolean True if all components have a valid netcdf file
        '''
        #TODO implement validity and file count check
        netList = self.listNetCDFs()
        if len(netList)>1:
            return True
        else:
            return False
    def findDataObject(self):
        '''looks for and returns dataclas object if found in InputData Folder
        :return DataClass object'''


        # df gets read in from TimeSeries processed data folder
        # component dictionary comes from setupXML's
        if 'setupFolder' in self.__dict__.keys():
            setupFile = os.path.join(self.setupFolder, self.project + 'Setup.xml')
            # From the setup file read the location of the input pickle
            # by replacing the current pickle with the loaded one the user can manually edit the input and
            #  then return to working with the interface
            return self.uihandler.loadInputData(setupFile)
        print('no data object found')
        return None
    def findComponents(self):
        '''Creates a list of components based on database input
        :return List of Components object'''
        return self.dbhandler.makeComponents()
    def generateNetcdf(self, data):
        '''uses a dataclass object to generate model input netcdf files
        netcdf files are written to the processed data folder'''
        #MainWindow = self.window()
       # setupForm = MainWindow.findChild(QtWidgets.QWidget, 'setupDialog')
        #componentModel = setupForm.findChild(QtWidgets.QWidget, 'components').model()
        handler = UIToHandler()
        if data:
            df = data.fixed
        componentDict = {}
        if 'components' not in self.__dict__.keys():
            #generate components
            self.components = self.makeComponentList()
        elif self.components == None:
            self.components = self.makeComponentList()
        for c in self.components:
            componentDict[c.column_name] = c.toDictionary()

        #filesCreated is a list of netcdf files that were generated
        self.ncs = handler.createNetCDF(df, componentDict,self.setupFolder)
        self.netCDFsLoaded.setText(', '.join(self.ncs))
    def getProjectFolder(self):
        return self.dbhandler.getProjectPath()
    def revalidate(self):
        # df gets read in from TimeSeries processed data folder
        # component dictionary comes from setupXML's
        if 'setupFolder' in self.__dict__.keys():
            setupFile = os.path.join(self.setupFolder, self.project + 'Setup.xml')

        self.loadSetup(setupFile)
        return True
    #pyqt slot
    def gotData(self,data):
        self.inputData = data
    #pyqt slot
    def gotComponents(self,loc):
        self.components = loc

#classes used for displaying wizard inputs
class WizardPage(QtWidgets.QWizardPage):
    def __init__(self, inputdict,parent,**kwargs):
        super().__init__(parent)
        self.first = kwargs.get('first')
        self.last = kwargs.get('last')
        self.initUI(inputdict)
        self.dbhandler = ProjectSQLiteHandler()

    # initialize the form
    def initUI(self, inputdict):
        self.d = inputdict
        self.setTitle(self.d['title'])
        self.input = self.setInput()
        self.input.setObjectName(self.d['name'])
        self.label = QtWidgets.QLabel()
        self.label.setText(self.d['prompt'])
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)


        return

    def setInput(self):
        wid = QtWidgets.QLineEdit()
        try:
            value = self.parent().__getattribute__(self.d['name'])

        except AttributeError as a:
            print(a)
            value = ''
        finally:
            if ( value == ''):
                self.registerField(self.d['name'] + "*", wid) #defualt input is required
            else:
                self.registerField(self.d['name'], wid)
            wid.setText(value)
            self.setField(self.d['name'],value)
        return wid

    def getInput(self):
        return self.input.text()

class ComponentSelect(WizardPage):
    def __init__(self,d,parent):
        super().__init__(d,parent)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        layout = QtWidgets.QGridLayout()

        handler = ProjectSQLiteHandler()
        lot = handler.getCurrentComponentTypeCount() #all possible component types, tuples with three values type code, description, count

        for i,t in enumerate(lot):
            label = QtWidgets.QLabel()
            label.setText(t[1])
            comp = QtWidgets.QSpinBox()
            comp.setObjectName(t[0] + 'count')
            comp.setValue(t[2])
            layout.addWidget(label,i,0,1,1)
            layout.addWidget(comp,i,1,1,1)
            self.registerField(comp.objectName(), comp)

        grp.setLayout(layout)
        return grp


class TwoDatesDialog(WizardPage):
    def __init__(self,d,parent):
        super().__init__(d,parent)
        self.d = d

    def setInput(self):
        handler = ProjectSQLiteHandler()
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
        self.registerField('sdate', self.startDate,"text")
        self.registerField('edate',self.endDate,"text")
        try:
            #if the setup info has already been set dates will be in the database table set
            print(handler.getFieldValue('setup', 'date_start', '_id',1))
            self.startDate.setDate(QtCore.QDate.fromString(handler.getFieldValue('setup', 'date_start', '_id', 1),"yyyy-MM-dd"))
            self.endDate.setDate(QtCore.QDate.fromString(handler.getFieldValue('setup', 'date_end',  '-id', 1),"yyyy-MM-dd"))
        except AttributeError as a:
            print(a)
        except TypeError as a:
            print(a)
        except Exception as e:
            print(e)
        return grp

    def getInput(self):
        return " - ".join([self.startDate.text(),self.endDate.text()])

class DropDown(WizardPage):
    def __init__(self,d,parent):
        super().__init__(d,parent)

    def setInput(self):
        self.input = QtWidgets.QComboBox()
        self.input.setItems(self.getItems())
        return
    def getInput(self):
        return self.breakItems(self.input.itemText(self.input.currentIndex()))

    def getItems(self):

        items = self.dbhandler.getCodes(self.d['reftable'])
        return items
    def breakItems(self,str):
        item = str.split(' - ')[0]
        return item


class TextWithDropDown(WizardPage):
    def __init__(self, d,parent):
        super().__init__(d,parent)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.combo = QtWidgets.QComboBox()
        handler = ProjectSQLiteHandler()
        self.combo.addItems(self.getItems())
        self.textInput = QtWidgets.QLineEdit()
        self.textInput.setValidator(QtGui.QIntValidator())
        box.addWidget(self.textInput)
        box.addWidget(self.combo)
        grp.setLayout(box)
        #self.registerField(self.d['name'],self.combo,"currentText",self.combo.currentIndexChanged)
        self.registerField('timestepvalue', self.textInput)
        self.registerField('timestepunit',self.combo,"currentText")
        try:
            #if the setup info has already been set dates will be in the database table set
            self.textInput.setText(handler.getFieldValue('setup', 'timestepvalue', '_id', 1))
            self.combo.setCurrentText(handler.getFieldValue('setup', 'timestepunit', '_id', 1))
        except AttributeError as a:
            print(a)
        return grp

    def getInput(self):
        input = self.textInput.text()
        item = self.breakItems(self.input.itemText(self.input.currentIndex()))
        strInput = ' '.join([input,item])
        return strInput
    def getItems(self):
        dbhandler = ProjectSQLiteHandler()
        items = dbhandler.getCodes(self.d['reftable'])
        dbhandler.closeDatabase()
        return items

    def breakItems(self, str):
        item = str.split(' - ')[0]
        return item

class ThreadedDataLoad(QtCore.QThread):
    notifyLoadProgress = QtCore.pyqtSignal(int)
    def run(self):
        for i in range(101):
            self.notifyLoadProgress.emit(i)

class ThreadedDataCreate(QtCore.QThread):
    notifyCreateProgress = QtCore.pyqtSignal(int,str)
    catchData = QtCore.pyqtSignal(DataClass)
    catchComponents = QtCore.pyqtSignal(list)

    def __init__(self,setupFolder, project):
        QtCore.QThread.__init__(self)
        self.setupFolder = setupFolder
        self.project = project

    def __del__(self):
        self.wait()

    def run(self):
        handler = UIToHandler()
        handler.sender.notifyProgress.connect(self.notify)
        cleaned_data, components = handler.createCleanedData(
            os.path.join(self.setupFolder, self.project + 'Setup.xml'))\
            #.connect(self, QtCore.SIGNAL('notifyProgress'), self.notify)
        self.catchData.emit(cleaned_data)
        self.catchComponents.emit(components)
        return

    def done(self):
        QtGui.QMessageBox.information(self, "Done!", "Done loading data!")

    def notify(self,i,task):
        self.notifyCreateProgress.emit(i,task)

class ThreadedNetcdfCreate(QtCore.QThread):
    notifyProgress = QtCore.pyqtSignal(int)
    def run(self):
        for i in range(101):
            self.notifyNetcdfProgress.emit(i)