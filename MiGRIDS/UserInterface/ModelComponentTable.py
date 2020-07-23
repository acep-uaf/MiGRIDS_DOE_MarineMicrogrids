# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 8/16/2019
'''
Created by: T. Morgan
ComponentTableView is a default table view tied to the component table in project_manager database
'''
import typing

from MiGRIDS.UserInterface.Delegates import *
from MiGRIDS.UserInterface.Delegates import ComboDelegate

from enum import Enum

from MiGRIDS.UserInterface.CustomAlternateTableView import CustomAlternateTableView


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
class ComponentTableView(CustomAlternateTableView):
    def __init__(self, *args, **kwargs):
        super(ComponentTableView, self).__init__()
        self.hiddenColumns = [0]
        fields = []

        #combo columns
        self.setItemDelegateForColumn(ComponentFields.inputfile_id.value,ComboRelationDelegate(self,'input_files','_id','inputfiledirvalue','inputfiledirvalue'))
        self.setItemDelegateForColumn(ComponentFields.headernamevalue.value,ComboDelegate(self,QtCore.QStringListModel(fields),'headernamevalue'))
        self.setItemDelegateForColumn(ComponentFields.component_id.value, ComboRelationDelegate(self, 'component','_id','componentnamevalue','componentnamevalue'))
        cdel = RelationDelegate(self, 'componenttype')
        cdel.itemChanged.connect(self.typeChanged)
        self.setItemDelegateForColumn(ComponentFields.componenttype.value, cdel)
        self.setItemDelegateForColumn(ComponentFields.componentattributevalue.value, RelationDelegate(self, 'componentattributevalue'))
        self.setItemDelegateForColumn(ComponentFields.componentattributeunit.value, RelationDelegate(self, 'componentattributeunit'))
        self.setItemDelegateForColumn(ComponentFields.customize.value, ComponentFormOpenerDelegate(self, '+'))


    def typeChanged(self,field,value):
        if field == 'componenttype':
            currentRow = self.currentIndex().row()
            self.model().componentTypeSelected(currentRow, value)

        return
#data model to fill component table
class ComponentTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent):
        super(ComponentTableModel, self).__init__(parent)
        QtSql.QSqlTableModel.__init__(self, parent)
        #values to use as headers for component table
        self.header = ['ID','Directory','Field', 'Type', 'Component Name', 'Unit', 'Attribute','Scale',
                    'Offset','Customize','dummyfield','andanother']

        self.makeModel()

        return

    def hideHeaders(self):
        self.hide_headers_mode = True

    def unhideHeaders(self):
        self.hide_headers_mode = False

    def makeModel(self):
        self.removeComboRelations()
        self.setTable('component_files')
        # set the dropdowns
        self.createRelations()
        # database gets updated when fields are changed
        #self.setEditStrategy(QtSql.QSqlTableModel.OnRowChange)
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    def createRelations(self):
        # leftjoin so null values ok
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.setRelation(ComponentFields.component_id.value,
                        QtSql.QSqlRelation('component', '_id', 'componentnamevalue'))
        self.setRelation(ComponentFields.inputfile_id.value,
                         QtSql.QSqlRelation('input_files', '_id', 'inputfiledirvalue'))
        self.setRelation(ComponentFields.componenttype.value, QtSql.QSqlRelation('ref_component_type', 'code', 'code'))
        self.setRelation(ComponentFields.componentattributevalue.value,
                         QtSql.QSqlRelation('ref_attributes', 'code', 'code'))
        self.setRelation(ComponentFields.componentattributeunit.value, QtSql.QSqlRelation('ref_units', 'code', 'code'))

        return
    def removeComboRelations(self):
        self.setRelation(ComponentFields.inputfile_id.value,QtSql.QSqlRelation())
        self.setRelation(ComponentFields.component_id.value, QtSql.QSqlRelation())

    def columnCount(self, parent=QtCore.QModelIndex()):
        """override the columnCount method to add an extra column"""
        return super(ComponentTableModel, self).columnCount() + 1

    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()

    def setData(self, index,value,role):

        if (index.column() == ComponentFields.inputfile_id.value) | (index.column() == ComponentFields.component_id.value) :
            self.removeComboRelations()
        success = super(ComponentTableModel, self).setData(index, value, role)
        self.createRelations()

        return success

    def componentTypeSelected(self, row, value):
       # make sure there is a name to match the type in the name dropdowns
       #parent is FormSetup
       if value != '':
           componentnamecount = self.parent().getComponentNameCount(value)
           typecount = 0 #typecount comes from the displayed data not the database
           for r in range(self.rowCount()):
               if self.data(self.index(r, ComponentFields.componenttype.value), QtCore.Qt.DisplayRole) == value:
                   typecount += 1

           if typecount > componentnamecount:
              self.parent().addName(value,componentnamecount)

       return

