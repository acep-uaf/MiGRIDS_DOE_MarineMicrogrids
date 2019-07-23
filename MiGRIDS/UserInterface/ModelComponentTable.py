'''
Created by: T. Morgan
ComponentTableView is a default table view tied to the component table in project_manager database
'''
from MiGRIDS.UserInterface.Delegates import *
import MiGRIDS.UserInterface.ModelFileInfoTable as F
from enum import Enum

class ComponentFields(Enum):
    ID=0
    DIRECTORY =1
    ORIGINALFIELD = 2
    TYPE = 3
    NAME = 4
    UNITS = 5
    SCALE = 6
    OFFSET = 7
    ATTRIBUTE = 8
    CUSTOMIZE = 9

#QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        # column 1 gets autfilled with filedir
        self.column1 = kwargs.get('column1')
        QtWidgets.QTableView.__init__(self, *args)


        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        #combo columns
        self.setItemDelegateForColumn(ComponentFields.DIRECTORY.value, TextDelegate(self))
        self.setItemDelegateForColumn(ComponentFields.TYPE.value, RelationDelegate(self, 'componenttype'))
        self.setItemDelegateForColumn(ComponentFields.ATTRIBUTE.value, RelationDelegate(self, 'componentattributevalue'))
        self.setItemDelegateForColumn(ComponentFields.UNITS.value, RelationDelegate(self, 'componentattributeunit'))
        self.setItemDelegateForColumn(ComponentFields.CUSTOMIZE.value, ComponentFormOpenerDelegate(self, '+'))

#data model to fill component table
class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):

        QtSql.QSqlTableModel.__init__(self, parent)
        #values to use as headers for component table
        self.header = ['ID','Directory','Field', 'Type', 'Component Name', 'Unit', 'Scale',
                    'Offset','Attribute','Customize']
        self.setTable('components')
        #leftjoin so null values ok
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        #set the dropdowns

        self.setRelation(3,QtSql.QSqlRelation('ref_component_type','code','code'))
        self.setRelation(8, QtSql.QSqlRelation('ref_attributes','code','code'))
        self.setRelation(5, QtSql.QSqlRelation('ref_power_units', 'code', 'code'))
        #database gets updated when fields are changed
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #select the data to display filtered to the input directory selected

        dirm = parent.FileBlock.findChild(QtWidgets.QWidget,F.InputFileFields.inputfiledirvalue.name).text()

        #self.setFilter('fileinputdir = ' + dirm)
        #self.setQuery(runQuery)
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


