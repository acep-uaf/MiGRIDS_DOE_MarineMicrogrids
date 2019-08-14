from PyQt5  import QtWidgets, QtSql, QtCore
from enum import Enum
from MiGRIDS.UserInterface.Delegates import TextDelegate, ComboDelegate
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

class SetFields(Enum):
    _id=0
    set_id =1
    component_id = 2
    tag = 3
    value = 4

#subclass of QTableView for displaying set information
class SetTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        #column1 is the set column that gets autofilled when we set a text delegate for column 1 in the table
        self.column1 = kwargs.get('column1')
        QtWidgets.QTableView.__init__(self, *args)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        def makeComponentList():
            import pandas as pd
            dbhandler = ProjectSQLiteHandler('project_manager')
            components = pd.read_sql_query("select componentnamevalue from component", dbhandler.connection)
            components = list(components['componentnamevalue'])
            return components

        values = QtCore.QStringListModel(makeComponentList())
        attributes = QtCore.QStringListModel([])
        self.setItemDelegateForColumn(1, TextDelegate(self))
        self.setItemDelegateForColumn(2,ComboDelegate(self,values,'componentName'))

        #attributes (column 3)get updated when component Name gets selected (column 2)
        self.setItemDelegateForColumn(3, ComboDelegate(self, attributes,'componentAttribute'))

class SetTableModel(QtSql.QSqlTableModel):
    def __init__(self, parent,position):

        QtSql.QSqlTableModel.__init__(self, parent)
        handler = ProjectSQLiteHandler()
        self.header = ['ID','Set', 'Component', 'Tag', 'Value']
        self.setTable('set_components')
        self.tabPosition = position
        self.tabName = "Set " + str(self.tabPosition)
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #the set table gets filtered to only show records for that set
        self.setFilter('set_id = ' + str(handler.getId('setup','set_name',parent.set)))
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


