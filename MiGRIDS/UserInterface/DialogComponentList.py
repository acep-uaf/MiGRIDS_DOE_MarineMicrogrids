# Projet: MiGRIDS
# Created by: T. Morgan# Created on: 11/8/2019


from PyQt5 import QtWidgets, QtCore

class ComponentSetListForm(QtWidgets.QDialog):
    '''Dialog widget with select list to choose components to include in model'''
    #initialize with a list of component names and list of boolean values for whether or not to include
    def __init__(self,setName):
        super().__init__()
       #checked is the list of components that are actually checked
        self.setName = setName
        self.init()
    def init(self):
        layout = QtWidgets.QVBoxLayout()
        #make the list widget
        self.listBlock = self.makeListWidget()
        layout.addWidget(self.listBlock)
        self.setLayout(layout)
        self.setWindowTitle('Select components to include')
        self.exec()

   #Make a list widget with checkboxes and a list of components
    def makeListWidget(self):
        import pandas as pd
        from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
        sqlhandler = ProjectSQLiteHandler('project_manager')
        self.components = pd.read_sql_query("select componentnamevalue from component",sqlhandler.connection)

        self.components = list(self.components['componentnamevalue'])

        #checked boxes will appear for all components listed in the set_components table
        checked = sqlhandler.getSetComponentNames(self.setName)
        sqlhandler.closeDatabase()
        listWidget = QtWidgets.QListWidget()
        for i in range(len(self.components)):
           item = QtWidgets.QListWidgetItem(self.components[i])
           item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
           if self.components[i] in checked:
               item.setCheckState(QtCore.Qt.Checked)
           else:
               item.setCheckState(QtCore.Qt.Unchecked)
           listWidget.addItem(item)

        listWidget.itemClicked.connect(self.on_listWidget_itemClicked)
        return listWidget
    #when an item is clicked check or uncheck it
    def on_listWidget_itemClicked(self, item):
        if item.listWidget().itemWidget(item) != None:
            if item.checkState() == QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Checked)

    #get the checked items
    def checkedItems(self):
        checked =[]
        for i in range(self.listBlock.count()):
            item = self.listBlock.item(i)
            if item.checkState() == QtCore.Qt.Checked:
               checked.append(item.text())

        return checked
