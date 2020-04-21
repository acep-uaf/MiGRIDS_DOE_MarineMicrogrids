# Projet: MiGRIDS
# Created by: T. Morgan# Created on: 11/8/2019
import os

#import MiGRIDS.UserInterface.ModelComponentTable as T
import MiGRIDS.UserInterface.ModelFileInfoTable as F
import pytz

from MiGRIDS.UserInterface.BaseEditorTab import BaseEditorTab
from MiGRIDS.UserInterface.BaseForm import BaseForm
from MiGRIDS.UserInterface.Delegates import ClickableLineEdit
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.gridLayoutSetup import setupGrid
from MiGRIDS.Controller.Exceptions.NoValidFilesError import NoValidFilesError
from MiGRIDS.UserInterface.makeButtonBlock import makeButtonBlock
from MiGRIDS.Controller.DirectoryPreview import DirectoryPreview
from PyQt5 import QtWidgets,QtCore,QtSql


class FileBlock(BaseEditorTab):
    '''FileBlock is the portion of a form that hold input information related to file import'''
    updateComponentDelegates = QtCore.pyqtSignal(DirectoryPreview)
    # creates a single form for entering individual file type information
    def init(self, tabPosition):
        self.tabName = "Input " + str(self.tabPosition)
        self.preview = None
        self.makeForm()


    def createFileTab(self):

        windowLayout = QtWidgets.QVBoxLayout()
        self.createTopBlock('Setup',self.assignFileBlock)
        l = self.FileBlock.findChild(QtWidgets.QWidget, F.InputFileFields.inputfiledirvalue.name)
        windowLayout.addWidget(self.FileBlock)

        #self.createTableBlock('Components', 'components', self.assignComponentBlock)

        #if a loaded file was valid the table block becomes active
        self.setValid(self.validate())
        l.clicked.connect(self.lineclicked)
        #windowLayout.addWidget(self.componentBlock)

        # the bottom block is disabled until a setup file is created or loaded
        return windowLayout

        # creates a horizontal layout containing gridlayouts for data input
    def typeChanged(self):
        '''method called if the input type is changed. Changes the possible preview based on input type changes'''
        if not self.BLOCKED:
            self.saveInput()
            #self.filterTables()

            try:
                self.createPreview(self.FileBlock.findChild(ClickableLineEdit,F.InputFileFields.inputfiledirvalue.name).text(),
                                   self.FileBlock.findChild(QtWidgets.QComboBox,
                                                            F.InputFileFields.inputfiletypevalue.name).currentText())
            except AttributeError as a:
                print(a)

    def folderChanged(self,selectedFolder = None):
        '''called when the selected directory changes. Preview changes based on files found in the newly designated directory'''
        if not self.BLOCKED:
            print("Input folder %s is %s" %(self.tabPosition,selectedFolder))
            self.saveInput()
            #self.filterTables()

            try:
                self.createPreview(
                    self.FileBlock.findChild(ClickableLineEdit, F.InputFileFields.inputfiledirvalue.name).text(),
                    self.FileBlock.findChild(QtWidgets.QComboBox,
                                             F.InputFileFields.inputfiletypevalue.name).currentText())
            except AttributeError as a:
                print(a)

    @QtCore.pyqtSlot()
    def lineclicked(self):
        '''opens a folder dialog and returns the string value of the pathway selected'''
        #if the directory has already been set then open the dialog to there otherwise default to current working directory
        curdir = self.findChild(QtWidgets.QWidget, F.InputFileFields.inputfiledirvalue.name).text()
        
        if curdir == '':
            curdir = self.controller.dbhandler.getProjectPath()
        selectedFolder = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a directory.',curdir)

        if (selectedFolder != ''):
            #once selected folderDialog gets set to the input box
            #if the mapper is at -1 we need to make a new record to map to
            if self.mapper.currentIndex() == -1:
                #before we set the text value we need to make the input fields part of a new record that the mapper can write to
                self.makeNewInputFileRecord()
            self.findChild(QtWidgets.QWidget, F.InputFileFields.inputfiledirvalue.name).setText(selectedFolder)
            self.fileBlockModel.setData(self.fileBlockModel.index(self.mapper.currentIndex(),F.InputFileFields.inputfiledirvalue.value),selectedFolder)
            self.folderChanged(selectedFolder)
            #folder changed gets called once the text changes
            return selectedFolder

    def makeNewInputFileRecord(self):
        self.fileBlockModel.insertRow(self.fileBlockModel.rowCount())
        self.mapper.toLast()
        return

    def createPreview(self,folder,fileType):
        '''
        Create a preview object for the files of a given file type in a selected folder. Assumes all files in a folder are set up the same
        :param folder: String path to a folder
        :param fileType: String file extension of files to preview
        :return: None
        '''
        try:
            preview = DirectoryPreview(inputfiledirvalue=folder,inputfiletypevalue=fileType)
            self.preview = self.checkPreview(preview)
            self.showPreview(self.preview) #saveInput gets called after preview shown

        except NoValidFilesError as e:
            print(e)

    def checkPreview(self,preview):
        '''
        Check the preview object against values in the database so that nothing gets overwritten without the user specifying
        :param preview: A Preview object
        :return: A Preview object with date channel, time channel and format default values reset to database values if they exist
        '''
        row = self.controller.dbhandler.getRecordDictionary('input_files',self.tabPosition)

        for k in list(row.keys()):
            if(row[k] == 'infer') | (row[k] == '') | (row[k] == None) :
                del row[k]
        preview.__dict__.update(**row)
        return preview

    def showPreview(self,preview):
        '''
        Update the GUI based on information in a preview object
        :param preview: Preview object
        :return: None
        '''
        def setBox(name):

            wid = self.FileBlock.findChild(QtWidgets.QComboBox, name)
            BaseForm.reconnect(wid.currentIndexChanged, None,self.saveInput) #disconnect the signal so validate isn't called here
            wid.addItems(["", "index"] + list(preview.header))

            wid.setCurrentText(preview.__dict__.get(name))
            BaseForm.reconnect(wid.currentIndexChanged, self.saveInput, None)

        # show fields in date and time field selectors and set current position to most likely candidate
        for name in [F.InputFileFields.datechannelvalue.name, F.InputFileFields.timechannelvalue.name,
                     F.InputFileFields.datechannelformat.name, F.InputFileFields.timechannelformat.name]:
            try:
                if preview!=None:
                    setBox(name)
            except AttributeError as e:
                print(name + " not set")
                pass
        self.updateComponentDelegates.emit(preview)
        self.updateDefaultDates()
        #the component table needs to be updated to reflect the file input and preview - update table filter
        # try:
        #     self.updateComponentDelegates(preview) #error if component table not created yet
        # except AttributeError as a:
        #     pass

        self.saveInput()

    def updateDefaultDates(self,preview):
        self.controller.dbhandler.updateDefaultDates(preview.startDate,preview.endDate)
    def createTopBlock(self,title, fn):
        '''The top block is where file information is set (format, date and time channels and file type)
        :param title: [String]
        :param fn: [method] used to assign the layout to a property'''

        # create a horizontal grouping to contain the top portion of the form
        gb = QtWidgets.QGroupBox(title)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setObjectName("setup")

        # set model
        fileBlockModel = QtSql.QSqlRelationalTableModel()
        fileBlockModel.setTable("input_files")

        parent = QtCore.QModelIndex()
        fileBlockModel.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)


        #fileBlockModel.select();
        file_id = self.controller.dbhandler.getIDByPosition('input_files',self.tabPosition-1)
        fileBlockModel.setFilter('input_files._id = ' + str(file_id))
        fileBlockModel.select()

        fileBlockModel.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.fileBlockModel = fileBlockModel

        reffiletype = QtSql.QSqlTableModel()
        reffiletype.setTable("ref_file_type")
        reffiletype.select()

        refdatetype = QtSql.QSqlTableModel()
        refdatetype.setTable("ref_date_format")
        refdatetype.select()

        reftimetype = QtSql.QSqlTableModel()
        reftimetype.setTable("ref_time_format")
        reftimetype.select()

        # add the setup grids
        g1 = {'headers': [1,2,3,4],
                  'rowNames': [1,2,3,4],
                  'columnWidths': [1, 1,1,3],
                  1:{1:{'widget':'lbl','name':'File Type:', 'default':'File Type'},
                     2:{'widget':'combo', 'name':'inputfiletypevalue','items':reffiletype,'default':'CSV' },
                     3: {'widget': 'lbl', 'name': 'File Directory', 'default': 'Directory'},
                     4: {'widget': 'lncl', 'name': 'inputfiledirvalue'}
                     },
                  2: {1: {'widget': 'lbl', 'name': 'Date Channel','default': 'Date Channel'},
                      2: {'widget': 'combo', 'name': 'datechannelvalue'},
                      3: {'widget': 'lbl', 'name': 'Date Format'},
                      4: {'widget': 'combo', 'items': refdatetype, 'name': 'datechannelformat','default':''}
                      },
                  3: {1: {'widget': 'lbl', 'name': 'Time Channel', 'default':'Time Channel'},
                      2: {'widget': 'combo', 'name': 'timechannelvalue'},
                      3: {'widget': 'lbl', 'name': 'Time Format'},
                      4: {'widget': 'combo', 'items': reftimetype, 'name': 'timechannelformat','default':''}
                      },
                  4:{1: {'widget': 'lbl', 'name': 'Time Zone', 'default':'Time Zone'},
                     2: {'widget': 'combo', 'items':pytz.all_timezones,'name': 'timezonevalue','default':'America/Anchorage'},
                     3: {'widget': 'lbl', 'name': 'Use DST', 'default': 'Use DST'},
                     4: {'widget': 'chk', 'name': 'usedstvalue', 'default':False}
                     }

                    }

        grid = setupGrid(g1)
        hlayout.addLayout(grid)
        hlayout.addStretch(1)
        gb.setLayout(hlayout)
        fn(gb)

        #map model to fields
        self.mapper = QtWidgets.QDataWidgetMapper()
        self.mapper.setModel(self.fileBlockModel)
        self.mapper.setItemDelegate(QtSql.QSqlRelationalDelegate())
        #map the widgets we created with our dictionary to fields in the sql table

        for i in range(0,fileBlockModel.columnCount(parent)):
            if gb.findChild(QtWidgets.QWidget,fileBlockModel.record().fieldName(i)) != None:

                wid = gb.findChild(QtWidgets.QWidget, fileBlockModel.record().fieldName(i))
                self.mapper.addMapping(wid,i)
                if isinstance(wid,QtWidgets.QComboBox):
                    default = self.findDefault(wid.objectName(),g1)
                    wid.setCurrentIndex(wid.findText(default))
                    if wid.objectName() == 'inputfiletypevalue': #if the file type changes trigger the function to create a new preview
                        BaseForm.reconnect(wid.currentIndexChanged,self.folderChanged)


        # submit data changes automatically on field changes -this doesn't work
        self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.AutoSubmit)
        self.mapper.toFirst()

        #if there is data already show it
        if (fileBlockModel.data(fileBlockModel.index(0,F.InputFileFields.inputfiledirvalue.value)) != None) & (fileBlockModel.data(fileBlockModel.index(0,F.InputFileFields.inputfiletypevalue.value)) != None):
            self.createPreview(fileBlockModel.data(fileBlockModel.index(0,F.InputFileFields.inputfiledirvalue.value)),fileBlockModel.data(fileBlockModel.index(0,F.InputFileFields.inputfiletypevalue.value)))
            self.setValid(self.validate())

    def findDefault(self,name, dict):
        for k in dict.keys():
            try:
                for key in dict[k].keys():
                    if dict[k][key]['name'] == name:
                        return dict[k][key]['default']
            except:
               pass
        return None



    def assignFileBlock(self,value):
        self.FileBlock = value
        #self.FileBlock.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.FileBlock.sizePolicy().retainSizeWhenHidden()
        self.FileBlock.setObjectName('fileInput')

    def getSetupInfoFromFileBlock(self):
        '''reads data from an file input top block and returns a list of fields and values'''
        fieldNames = ['_id']

        values=[self.tabPosition]
        for child in self.FileBlock.findChildren((QtWidgets.QLineEdit, QtWidgets.QComboBox)):

            if type(child) is QtWidgets.QLineEdit:
                fieldNames.append(child.objectName())
                values.append(child.text())
            elif type(child) is ClickableLineEdit:
                fieldNames.append(child.objectName())
                values.append(child.text())
            else:
                fieldNames.append(child.objectName())
                values.append(child.itemText(child.currentIndex()))

        return fieldNames,values

    def saveInput(self):
        '''save the form input to the form setup data model'''
        #update model info from fileblock
        row = self.mapper.currentIndex()
        j = self.mapper.submit() #boolean true if values submitted

        f = self.fileBlockModel.data(self.fileBlockModel.index(row, F.InputFileFields.inputfiledirvalue.value))
        self.mapper.setCurrentIndex(row) #this is where data becomes available in the model but still not in database
        self.checkPath(f) #make sure relative and absolute paths that point to the same location are seen as the same
        m = self.fileBlockModel.submitAll()
        self.setValid(self.validate())
        return

    def checkPath(self, filePath):
        '''converts the selected path to an existing path if it matches'''
        currentPaths = self.controller.dbhandler.getAllRecords('input_files')
        for cpath in currentPaths:
            if os.path.abspath(filePath) == os.path.abspath(cpath[4]):
                filePath = cpath
                return filePath
        return filePath
    def setValid(self,valid):
        '''
        Adjusts the FileBlock form to reflect whether or not the inputs are valid
        The component table becomes enabled and editable
        :param valid: Boolean whether or not the file block info is valid
        :return: None
        '''
        if (valid):
            #we can reach this point before a fileblock is done getting created
            try:

                 # enable the component buttons
                self.ComponentButtonBox.setEnabled(True)
                self.ComponentTable.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
                self.updateComponentDelegates.emit(self.preview)
            except AttributeError as a:
                pass
                #print('attempted to set component table items before component table was created')

    def makeForm(self):
        windowLayout = self.createFileTab()
        self.setLayout(windowLayout)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.validated = False

    def validate(self):
        '''
        Checks that all the required fields in for an input directory have been set and valid files have been found
        A file block must contain either a date or time field with a specified format, a file type and a input directory
        :return: boolean - True if required fields have been set, otherwise false.
        '''
        #validate the file input fields before allowing component information to be collected
        try:
            if self.preview != None:
                if (len(self.preview.header) <=0):
                    self.validated = False
                    return False

            if (self.fileBlockModel.data(
                    self.fileBlockModel.index(0, F.InputFileFields.inputfiledirvalue.value)) == '') :
                self.validated = False
                return False
            if ((self.fileBlockModel.data(self.fileBlockModel.index(0,F.InputFileFields.datechannelvalue.value)) == '') & (self.fileBlockModel.data(self.fileBlockModel.index(0,F.InputFileFields.timechannelvalue.value)) == '')):
                self.validated = False
                return False
            if ((self.fileBlockModel.data(
                    self.fileBlockModel.index(0, F.InputFileFields.datechannelvalue.value)) != '') & (
                    self.fileBlockModel.data(
                            self.fileBlockModel.index(0, F.InputFileFields.datechannelformat.value)) == '')):
                self.validated = False

                return False
            if  (self.fileBlockModel.data(self.fileBlockModel.index(0,F.InputFileFields.timechannelvalue.value)) != '') & (self.fileBlockModel.data(self.fileBlockModel.index(0,F.InputFileFields.timechannelformat.value)) == ''):
                self.validated = False
                return False
            else:
                self.validated = True

                return True
        except AttributeError as e:
            #if a key attribute has no yet been created then the input is not yet valid
            print(e)
            self.validated = False
            return False

    # def filterTables(self):
    #     '''filter tables to only show values associated with specific input directories'''
    #     tables = self.findChildren(QtWidgets.QTableView)
    #     filedir = self.FileBlock.findChild(QtWidgets.QWidget, F.InputFileFields.inputfiledirvalue.name).text()
    #     id = self.controller.dbhandler.getId("input_files",['inputfiledirvalue'],[filedir])
    #     #self.filter = filedir
    #     #for t in tables:
    #         #m = t.model()
    #         #m.setFilter("inputfile_id" + " = " + str(id) + "")

    # def saveTables(self):
    #     '''get data from component and environment tables and update the setupInformation model
    #     components within a single directory are seperated with commas
    #     component info comes from the database not the tableview
    #     component names, units, scale, offset, attribute, fieldname get saved'''
    #
    #     self.ComponentTable.model.submitAll()
    #     print(self.ComponentTable.model.lastError().text())
    #
    #     #loC = [makeNewComponent(df['component_name'],x['original_field_name'],
    #     #                             x['units'],x['attribute'],x['component_type']) for i,x in df.iterrows()]
    #     return #loC

    def close(self):
        if 'projectFolder' in self.__dict__.keys():
            #input to model
            self.saveInput()
            #input to database
            setupFields, setupValues = self.getSetupInfoFromFileBlock()

            # update database table
            if not self.controller.dbhandler.insertRecord('input_files', setupFields, setupValues):
                self.controller.dbhandler.updateRecord('input_files', ['_id'], [setupFields[0]],
                                       setupFields[1:],
                                       setupValues[1:])


