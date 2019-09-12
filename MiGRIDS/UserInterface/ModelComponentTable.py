'''
Created by: T. Morgan
ComponentTableView is a default table view tied to the component table in project_manager database
'''
from MiGRIDS.UserInterface.Delegates import *
from MiGRIDS.UserInterface.Delegates import ComboDelegate
import MiGRIDS.UserInterface.ModelFileInfoTable as F
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from enum import Enum

class ComponentFields(Enum):
    _id=0
    inputfile_id =1
    headernamevalue = 2
    componenttype = 3
    component_id = 4
    componentattributeunit = 5
    componentattributevalue = 6
    componentscale = 7
    componentoffset = 8
    customize = 9

#QTableView for displaying component information
class ComponentTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        # column 1 gets autfilled with filedir
        self.column1 = kwargs.get('column1')
        QtWidgets.QTableView.__init__(self, *args)
        fields = kwargs.get('fields')

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()

        handler = ProjectSQLiteHandler()

        comps= handler.getAsRefTable('component', '_id', 'componentnamevalue')

        fields = []
        #combo columns
        self.setItemDelegateForColumn(ComponentFields.headernamevalue.value,ComboDelegate(self,QtCore.QStringListModel(fields),'headernamevalue'))
        #self.setItemDelegateForColumn(ComponentFields.component_id.value,ComboDelegate(self, RefTableModel(comps),'componentnamevalue'))
        self.setItemDelegateForColumn(ComponentFields.component_id.value, RelationDelegate(self, 'componentnamevalue'))
        self.setItemDelegateForColumn(ComponentFields.componenttype.value, RelationDelegate(self, 'componenttype'))
        self.setItemDelegateForColumn(ComponentFields.componentattributevalue.value, RelationDelegate(self, 'componentattributevalue'))
        self.setItemDelegateForColumn(ComponentFields.componentattributeunit.value, RelationDelegate(self, 'componentattributeunit'))
        self.setItemDelegateForColumn(ComponentFields.customize.value, ComponentFormOpenerDelegate(self, '+'))

#data model to fill component table
class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):
        super(ComponentTableModel, self).__init__(parent)
        QtSql.QSqlTableModel.__init__(self, parent)
        #values to use as headers for component table
        self.header = ['ID','Directory','Field', 'Type', 'Component Name', 'Unit', 'Attribute','Scale',
                    'Offset','Customize','dummyfield','andanother']
        self.setTable('component_files')

        #leftjoin so null values ok
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        #set the dropdowns

        self.setRelation(ComponentFields.component_id.value,QtSql.QSqlRelation('component','_id','componentnamevalue'))
        #self.setRelation(ComponentFields.inputfile_id.value, QtSql.QSqlRelation('input_file','_id','inputfiledirvalue'))
        self.setRelation(ComponentFields.componenttype.value,QtSql.QSqlRelation('ref_component_type','code','code'))
        self.setRelation(ComponentFields.componentattributevalue.value, QtSql.QSqlRelation('ref_attributes','code','code'))
        self.setRelation(ComponentFields.componentattributeunit.value, QtSql.QSqlRelation('ref_units', 'code', 'code'))
        #database gets updated when fields are changed
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)

        #select the data to display filtered to the input directory selected
        '''dirm = parent.FileBlock.findChild(QtWidgets.QWidget,F.InputFileFields.inputfiledirvalue.name).text()
        handler = ProjectSQLiteHandler()

        self.setFilter('inputfile_id = ' + str(handler.getId('input_files','inputfiledirvalue',dirm)))'''

        self.select()

    def columnCount(self, parent=QtCore.QModelIndex()):
        """override the columnCount method to add an extra column"""
        return super(ComponentTableModel, self).columnCount() + 1

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


