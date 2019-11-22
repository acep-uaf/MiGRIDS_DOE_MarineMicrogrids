#MainForm is the parent for for all sections of the User Interface
#it consists of a navigation tree and pages
from PyQt5 import QtWidgets, QtCore, QtGui,QtSql

from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface import FormContainer
from MiGRIDS.UserInterface.ConsoleDisplay import ConsoleDisplay

from MiGRIDS.UserInterface.FormSetup import FormSetup
from MiGRIDS.UserInterface.switchProject import saveProject

class MainForm(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self,**kwargs):
        super().__init__()

        self.initUI(**kwargs)

    def initUI(self,**kwargs):
        self.lastProjectPath = kwargs.get('lastProjectPath')
        self.setObjectName("mainForm")
        self.layoutWidget = QtWidgets.QWidget(self)

        docker = QtWidgets.QDockWidget()

        app = QtCore.QCoreApplication.instance()
        # find the biggest screen to show the window on
        size = app.desktop().screenGeometry()

        for c in range(0, app.desktop().screenCount()):
            self.screen = app.desktop().screenGeometry(app.desktop().screen(0))
            if app.desktop().availableGeometry(app.desktop().screen(c)).width() > size.width():
                self.screen = app.desktop().screenGeometry(app.desktop().screen(c))
                self.move(self.screen.x(),self.screen.y())
                self.resize((app.desktop().screen(c)).width(),(app.desktop().screen(c)).height())


        self.treeBlock = self.createNavTree()
        docker.setWidget(self.treeBlock)
        self.pageBlock = self.createPageBlock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea(1),docker,QtCore.Qt.Vertical)


        # add a console window
        self.addConsole()
        docker2 = QtWidgets.QDockWidget()
        docker2.setWidget(self.console)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(8),docker2,QtCore.Qt.Horizontal)
        self.console.showMessage("This is where messages will appear")

        self.setCentralWidget(self.pageBlock)



        # Main title
        self.setWindowTitle('MiGRIDS')
        #self.resized.connect(self.screenMoved)

            # show the form
        self.showMaximized()

    def resizeEvent(self, event):
        self.resized.emit()
        return super(MainForm, self).resizeEvent(event)

    def screenMoved(self):
        app = QtCore.QCoreApplication.instance()
        if self.screen.width() != self.window().geometry().width():

            self.screen = self.window().geometry()
            #self.pageBlock.makeSize(self.screen)
            print("screen moved")
            print(self.screen.width())
            #re-creating everything looses attributes
            self.pageBlock = self.relayPageBlocks()

    # add a console block to display messages
    def addConsole(self):
        c = ConsoleDisplay()
        self.console = c

    #NavTree is a navigation tree for switching between pages or sections within pages
    #-> QTreeView
    def createNavTree(self):

        self.data = [
            ('Setup', [
                ('Setup File',[]),
                ('Input Files',[]),
                ('Components',[])
            ]),
            ('Model Runs', [
                ('Sets',[]),
                ('Runs',[]),
                ('Results',[])

            ]),
            ('Optimize',[

            ])
        ]
        self.focusObjects = {'Setup File':FormSetup.prePopulateSetupWizard,
                             'Input Files':'fileInput',
                             'Components':'components',

                             'Sets':'modelSets',
                             'Runs':'runResults',
                             'Results':'modelResults'

        }

        tree = QtWidgets.QTreeView()
        tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        tree.clicked.connect(self.switchFocus)
        model = QtGui.QStandardItemModel()
        self.addItems(model,self.data)
        tree.setModel(model)
        model.setHorizontalHeaderLabels([self.tr("Navigation")])

        return tree
    #add navigation items to the navigation tree
    def addItems(self, parent, elements):
        for text, children in elements:
            item = QtGui.QStandardItem(text)
            item.setEditable(False)
            parent.appendRow(item)

            if children:
                self.addItems(item,children)
        return
    #change focus to the selected item in the navigation tree
    def switchFocus(self, position):
        '''
        switches the focus from the current widget to one associated with a position in the navication tree
        :param position: integer position in the navigation tree
        :return:
        '''
        #what item is selected
        indexes = self.treeBlock.selectedIndexes()
        level = 0
        #if a sub-tree branch was selected
        if len(indexes) > 0:
            #this is the leaf
            index = indexes[0]
            #index becomes the root node, level is the steps removed
            while index.parent().isValid():
                index = index.parent()
                level +=1

        #change the active tab depending on the selection
        self.pageBlock.setCurrentIndex(index.row())
        # change the focus depending on the selection
        if level == 1:
            name = list(self.treeBlock.model().itemData(position).values())[0]
            focusObject = self.focusObjects[name]

            if type(focusObject) is str:
                focusWidget = self.pageBlock.currentWidget().findChild(QtWidgets.QWidget,focusObject)
                focusWidget.setFocus(True)
            else:

                #find and launch the method
                tabs = self.pageBlock.findChildren(QtWidgets.QWidget)
                tabs = [w  for w in tabs if not isinstance(w,(QtWidgets.QLineEdit,QtWidgets.QTextEdit,QtWidgets.QComboBox,QtWidgets.QGroupBox,QtWidgets.QLayout)) ]
                self.findFunction(focusObject,tabs,0)


        return

    def findFunction(self, focusObject, listOftabBar,i):
        if len(listOftabBar) <=0:
            return
        elif self.hasFunction(listOftabBar[0],focusObject): #no more tab bars to check
            return
        else:
            listOftabBar.remove(listOftabBar[0])
            return self.findFunction(focusObject,listOftabBar, i + 1)


    def hasFunction(self, widg,focusObject):
        '''

        :param widg: a QWidget
        :param focusObject: The name of a function or attribute to call
        :return: boolean True if the function was found and called, otherwise false
        '''
        if focusObject.__name__ in dir(widg):
            focusObject(widg)
            return True
        return False


    def closeEvent(self,event):
        import os

        setupForm = self.findChild(QtWidgets.QWidget, 'setupDialog')
        setupForm.closeEvent(event)

        # copy the project database to the project folder and save xmls
        dbhandler = ProjectSQLiteHandler()
        if len(dbhandler.getAllRecords('project')) > 0 :
             dbhandler.closeDatabase()
             saveProject(setupForm.projectFolder)

        else:
            dbhandler.closeDatabase()
            del dbhandler
            # if a project was never set then just close and remove the default database
            os.remove('project_manager')

    #page block contains all the forms
    def createPageBlock(self):
        pageBlock = PageBlock(lastProjectPath = self.lastProjectPath,screen=self.screen)

        return pageBlock


    def relayPageBlocks(self):
        tabs = self.pageBlock.findChildren(FormContainer)
        for t in tabs:
            t.changeLayout(self.screen)

        return

class PageBlock(QtWidgets.QTabWidget):
    def __init__(self,**kwargs):
        super().__init__()
        self.setObjectName('pages')
        self.lastProjectPath = kwargs.get('lastProjectPath')
        self.screen = kwargs.get("screen")

        self.initUI()


    def initUI(self):
        from MiGRIDS.UserInterface.FormSetup import FormSetup
        from MiGRIDS.UserInterface.ResultsSetup import ResultsSetup
        from MiGRIDS.UserInterface.FormModelRuns import FormModelRun
        from MiGRIDS.UserInterface.FormOptimize import FormOptimize
        from MiGRIDS.UserInterface.ResultsModel import ResultsModel
        from MiGRIDS.UserInterface.ResultsOptimize import ResultsOptimize
        from MiGRIDS.UserInterface.FormContainer import FormContainer

        self.addTab(FormContainer(self,[FormSetup(self), ResultsSetup(self,'setupResult')],'Setup',screen=self.screen), 'Setup')
        self.addTab(FormContainer(self, [FormModelRun(self), ResultsModel(self,'modelResult')],'Model',screen=self.screen), 'Model')
        self.addTab(FormContainer(self, [FormOptimize(self), ResultsOptimize(self,'optimizeResult')],'Optimize',screen=self.screen), 'Optimize')

        self.findChild(FormContainer,'Model').hide()
        self.findChild(FormContainer, 'Optimize').hide()

    def makeSize(self,myGeom):
        '''

        :param myGeom: A geometry to be used as the screen dimensions
        :return:
        '''
        for i in range(0,self.count()):
            #get the container and re-arrange the objects to fit the screen dimensions

            self.widget(i).changeLayout(myGeom)

    #Creates model and optimize tabs
    #this is called after a project name is set
    def enableTabs(self):
        from MiGRIDS.UserInterface.FormModelRuns import FormModelRun
        from MiGRIDS.UserInterface.FormOptimize import FormOptimize

        self.findChild(FormModelRun).show()

        self.findChild(FormOptimize).show()

        return

    #if the tab block is closed make sure all the data is written to xml files
    def closeEvent(self):
        import os
        import shutil
        setupForm = self.findChild(QtWidgets.QWidget,'setupDialog')
        # move the default database to the project folder and save xmls
        if 'projectFolder' in setupForm.model.__dict__.keys():
            path = os.path.dirname(__file__)
            print('Database was saved to %s' % self.model.projectFolder)

            shutil.move(os.path.join(path, 'project_manager'),
                       os.path.join(self.model.projectFolder, 'project_manager'))
        else:
            # if a project was never set then just close and remove the default database
            os.remove('project_manager')