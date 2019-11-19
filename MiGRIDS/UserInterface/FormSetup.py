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

from MiGRIDS.Controller.Controller import Controller
from MiGRIDS.Controller.Validator import ValidatorTypes
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.UserInterface.CustomProgressBar import CustomProgressBar
from MiGRIDS.UserInterface.DetailsWidget import DetailsWidget
from MiGRIDS.UserInterface.WizardPages import WizardPage, TextWithDropDown, ComponentSelect, TwoDatesDialog
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.UserInterface.ResultsSetup import  ResultsSetup
from MiGRIDS.UserInterface.FormModelRuns import SetsAttributeEditorBlock
from MiGRIDS.UserInterface.Pages import Pages
from MiGRIDS.UserInterface.FileBlock import FileBlock
from MiGRIDS.UserInterface.switchProject import switchProject
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.Resources.SetupWizardDictionary import *
import pandas as pd

BASESET ='Set0'


class FormSetup(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()
    #initialize the form
    def initUI(self):
        self.controller = Controller()
        self.setObjectName("setupDialog")

        #the main layout is oriented vertically
        windowLayout = QtWidgets.QVBoxLayout()

        # the top block is buttons to load setup xml and data files
        self.createTopButtonBlock()
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
        #make the data log viewing button
        self.detailsBtn = QtWidgets.QPushButton('Details')
        self.detailsBtn.setToolTip('View data fixing log.')
        self.detailsBtn.clicked.connect(lambda: self.onClick(self.viewLogDetails))
        self.detailsBtn.setFixedWidth(200)
        self.detailsBtn.setEnabled(False)
        hlayout.addWidget(self.detailsBtn)

        dataLoaded = QtWidgets.QLineEdit()
        dataLoaded.setFrame(False)
        dataLoaded.setObjectName('dataloaded')
        dataLoaded.setText('No data loaded')
        dataLoaded.setFixedWidth(200)
        self.dataLoadedOutput = dataLoaded
        hlayout.addWidget(self.dataLoadedOutput)

        # generate netcd button
        netCDFButton = self.createSubmitButton()
        hlayout.addWidget(netCDFButton)
        button.setFixedWidth(200)
        self.currentNetcdfs  = QtWidgets.QLineEdit()
        self.currentNetcdfs.setFrame(False)
        self.currentNetcdfs.setText("none")
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
            if (self.project != '') & (self.project is not None):
                if self.validateProjectSwitch() != True:
                    return

        except AttributeError as e:
            print("Project not set yet")
        self.createNewProject()

    def resetValidateStatus(self):
        self.controller.initializeState()


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
            self.resetValidateStatus()
            switchProject(self)
            return True
        else:
            return False

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

    def procedeToSetup(self):
        '''Evaluates whether or not the setup input should be generated. If a setup file already exists then the user needs to
        indicate they are willing to overwrite that file
        :return Boolean True if the input should be written to a file. False if the input needs to be altered.'''

        # If the project already exists wait to see if it should be overwritten
        # assign project has already been called at this point so the directory is created
        if self.controller.setupValid:
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


    #searches for and loads existing project data - database, setupxml,descriptors, DataClass pickle, Component pickle netcdf,previously run model results, previous optimization results
    def functionForLoadButton(self):
        '''The load function reads the designated setup xml, looks for descriptor xmls,
        looks for an existing project database and a pickled data object.'''

        #if we were already working on a project its state gets saved and  new project is loaded
        if (self.controller.dbhandler.getProjectPath() != '') & (self.controller.dbhandler.getProjectPath() is not None):
            switchProject(self)


        #launch file navigator to identify setup file
        setupFile = QtWidgets.QFileDialog.getOpenFileName(self,"Select your setup file", os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects'), "*xml" )
        if (setupFile == ('','')) | (setupFile is None):
            return

        self.controller.loadProject(setupFile[0])

        self.displayModelData() #update the form with loaded data
        self.updateFormProjectDataStatus()

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

    def showAlert(self,title,msg):
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,title ,msg
                                    )
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec()

    def displayModelData(self):
        """creates a tab for each input directory specified the SetupModelInformation model inputFileDir attribute.
        Each tab contains a FileBlock object to interact with the data input
        Each FileBlock is filled with data specific to the input directory"""
        self.tabs.removeTab(0)
        #the number of directories listed in inputFileDir indicates how many tabs are required
        tab_count = len(self.controller.dbhandler.getAllRecords('input_files'))
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

    def saveTreeInput(self):
        '''
        save the input in the wizard tree attribute to the database
        It is assumed that the database is empty (cleared on switchproject or never filled)
        :return: None
        '''
        projectDefaultPath = os.path.join(os.path.dirname(__file__),
                                                       *['..', '..', 'MiGRIDSProjects', self.WizardTree.field('project')])
        if self.procedeToSetup(): #this checks if we are overwriting an existing setup file
            project_id = self.controller.dbhandler.insertRecord("project",['project_name','project_path'],[self.WizardTree.field('project'),
                                                                                                           projectDefaultPath])

            _id = self.controller.dbhandler.insertRecord("setup",['_id','project_id','timestepvalue','timestepunit','date_start','date_end'],
                                                         [project_id,1,self.WizardTree.field('timestepvalue'),self.WizardTree.field('timestepunit'),self.WizardTree.field('sdate'),self.WizardTree.field('edate')])

            if _id == -1: #record was not inserted, try updating
                self.controller.dbhandler.updateRecord("setup","_id",1,['project_id','timestepvalue','timestepunit','date_start','date_end','runtimestepvalue'],
                                       [project_id,  self.WizardTree.field('timestepvalue'),
                                        self.WizardTree.field('timestepunit'), self.WizardTree.field('sdate'),
                                        self.WizardTree.field('edate'), str.join(" ",[self.WizardTree.field('sdate'),
                                        self.WizardTree.field('edate')])])
                _id = self.controller.dbhandler.getId('setup','_id',1)[0]

            lot = self.controller.dbhandler.getComponentTypes()
            for t in lot:
                cnt = self.WizardTree.field(t[0]+'count')
                for i in range(0,cnt):
                    comp_id = self.controller.dbhandler.insertRecord('component',['componentnamevalue','componenttype'],[t[0] + str(i),t[0]])

                    #the delegate for componentname in the component table should also be updated
                    if comp_id != -1:
                        loFileBlock = self.findChildren(FileBlock)
                        for f in loFileBlock:
                           f.updateComponentNameList()



            self.WizardTree.close()
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

        progressBar = CustomProgressBar('Data fixing')
        try:
            #when thread finishes self.controller.inputData and self.components are set
            self.myThread = ThreadedDataCreate(self.controller)

            self.myThread.notifyCreateProgress.connect(progressBar.onProgress)
            self.myThread.catchComponents.connect(self.gotComponents)
            self.myThread.catchData.connect(self.gotData)
            self.myThread.finished.connect(self.loadProjectData)
            self.myThread.start()
        except Exception as e:
            print(e)
        finally:
            progressBar.hide()
            del progressBar

        if not self.validator.validate(ValidatorTypes.DataObject,self.controller.inputData): #this will set dataobjectvalid to its current state
            self.showAlert("Could not create a valid data object.")
        return

    # def loadProjectData(self):
    #     progressBar = CustomProgressBar("Data loading")
    #
    #     self.uihandler.sender.notifyProgress.connect(progressBar.onProgress)
    #     try:
    #         # look for an existing component pickle or create one from information in setup xml
    #         self.components = self.uihandler.loadComponents(os.path.join(self.setupFolder, self.project + 'Setup.xml'))
    #         if self.components is None:
    #             self.components = self.makeComponentList()
    #         self.uihandler.sender.notifyProgress(2,'loading')
    #         if self.controller.inputData:
    #             self.updateFormProjectDataStatus()
    #             self.uihandler.sender.notifyProgress(3,'loading')
    #         else:
    #             self.netCdfsLoaded()
    #             self.uihandler.sender.notifyProgress(5,'loading')
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         progressBar.hide()
    #         return

    def netCdfsLoaded(self):
        '''list netcdf files previously generated
        :returns True if necdfs are found
        '''
        self.currentNetcdfs.setText('Processed Files: ' + ', '.join(self.controller.netcdfs))
        self.updateDependents()
        return

    def updateFormProjectDataStatus(self):
        '''updates the setup form to reflect project data (DataClass object, Component info, netcdfs)status
        '''
        progressBar = CustomProgressBar('loading project')
        progressBar.onProgress(2,'notask')
        try:
            # indicate that the data has loaded
            if self.controller.dataObjectValid:
                self.dataLoadedOutput.setText('data loaded')
                self.detailsBtn.setEnabled(True)
            progressBar.onProgress(2,'loading project')
            # update the Model tab with set information
            self.updateDependents(self.controller.inputData) #make sure there is data here
            progressBar.onProgress(4, 'loading project')
            # refresh the plot or processed data
            self.refreshDataPlot()
            progressBar.onProgress(2, 'loading project')
            #self.progressBar.setRange(0, 1)

            if not self.controller.netcdfsValid:
                # generate netcdf files if requested
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Time Series loaded",
                                        "Do you want to generate netcdf files?.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.No)
                result = msg.exec()
                # if yes create netcdf files, Otherwise this can be done after the data is reviewed.
                if result == QtWidgets.QMessageBox.Ok:
                    self.makeNetcdfs()
            else:
                self.netCdfsLoaded()

            progressBar.onProgress(2, 'loading project')
        except Exception as e:
            print(e)
        finally:
            progressBar.hide()
    def refreshDataPlot(self):
        resultDisplay = self.parent().findChild(ResultsSetup)
        resultDisplay.setData(self.controller.inputData)
        resultDisplay.defaultPlot()

    def makeNetcdfs(self):
        d = {}
        for c in self.components:
            d[c.column_name] = c.toDictionary()
        self.ncs = self.uihandler.createNetCDF(self.controller.inputData.fixed, d,
                                               os.path.join(self.setupFolder, self.project + 'Setup.xml'))

    def makeData(self):
        # import datafiles
        #TODO remove and call thread

        return

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

    def updateModelInputDependents(self, values):
        if len(self.controller.sets)<=0:
            self.controller.dbhandler.insertFirstSet(values)
            self.controller.dbhandler.insertAllComponents('Set0')
        # Deliver appropriate info to the ModelForm
        modelForms = self.window().findChildren(SetsAttributeEditorBlock)
        [m.loadSetData() for m in modelForms] #load data individually for each set

    def updateInputDataDependents(self, data = None):
        ''':return dictionary of values relevant to a setup file'''

        def getDefaults(listDf, defaultStart=pd.datetime.today().date(), defaultEnd=pd.datetime.today().date()):
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
                e = listDf[0].index[len(listDf[0]) - 1].date()

                if (s < defaultStart) & (e > defaultEnd):
                    return getDefaults(listDf[1:], s, e)
                elif s < defaultStart:
                    return getDefaults(listDf[1:], s, defaultEnd)
                elif e > defaultStart:
                    return getDefaults(listDf[1:], defaultStart, e)
            return str(defaultStart), str(defaultEnd)

        # default start is the first date there is record for
        values = {}
        if data!= None:
            values['date_start'], values['date_end'] = getDefaults(data.fixed)
        else:
            values['date_start'], values['date_end'] = getDefaults([])
        values['date_start'] = [values['date_start']]
        values['date_end'] = [values['date_end']]
        values['set_name'] = ['Set0']
        info = self.controller.dbhandler.getSetUpInfo()
        values['timestepvalue'] = [info['timeStep.value']]
        values['timestepunit'] = [info['timeStep.unit']]
        values['project_id'] = [1]  # always 1, only 1 project per database

        # deliver the data to the ResultsSetup form so it can be plotted
        if data != None:
            resultsForm = self.window().findChild(ResultsSetup)
            resultsForm.setData(self.controller.inputData)

            resultsForm.defaultPlot()

        return values
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
            self.generateNetcdf(self.controller.inputData)
            return
        else:
            self.fixSetup()
            self.generateModelInput()

    def fixSetup(self):
        '''warns the user the setup file is not valid and re-opens the setup wizard so inputs can be corrected.'''
        self.showAlert("Setup file invalid","Please correct your setup input")
        self.prePopulateSetupWizard()

    def generateNetcdf(self, data):
        '''uses a dataclass object to generate model input netcdf files
        netcdf files are written to the processed data folder'''
        #MainWindow = self.window()
       # setupForm = MainWindow.findChild(QtWidgets.QWidget, 'setupDialog')
        #componentModel = setupForm.findChild(QtWidgets.QWidget, 'components').model()

        if data:
            df = data.fixed
        componentDict = {}
        if 'components' not in self.__dict__.keys():
            #generate components
            self.controller.components = self.makeComponentList()
        elif self.controller.components == None:
            self.controller.components = self.makeComponentList()
        for c in self.components:
            componentDict[c.column_name] = c.toDictionary()

        #filesCreated is a list of netcdf files that were generated
        self.ncs = self.controller.setupHandler.createNetCDF(df, componentDict,self.controller.setupFolder)
        self.netCdfsLoaded()

    @QtCore.pyqtSlot()
    def gotData(self,data):
        self.controller.inputData = data

    @QtCore.pyqtSlot()
    def gotComponents(self,loc):
        self.controller.components = loc



class ThreadedDataCreate(QtCore.QThread):
    notifyCreateProgress = QtCore.pyqtSignal(int,str)
    catchData = QtCore.pyqtSignal(DataClass)
    catchComponents = QtCore.pyqtSignal(list)

    def __init__(self,controller):
        QtCore.QThread.__init__(self)
        self.controller = controller

    def __del__(self):
        self.wait()

    def run(self):

        self.controller.sender.notifyProgress.connect(self.notify)
        cleaned_data, components = self.controller.createCleanedData(
            os.path.join(self.controller.setupFolder, self.controller.project + 'Setup.xml'))\
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