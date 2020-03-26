# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 8/16/2019
from PyQt5  import QtWidgets, QtSql, QtCore
from enum import Enum

from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import splitAttribute
from MiGRIDS.Controller.Controller import Controller

from MiGRIDS.UserInterface.Delegates import TextDelegate, ComboDelegate, RelationDelegate
from MiGRIDS.UserInterface.ModelRunTable import customTableView
from MiGRIDS.UserInterface.getFilePaths import getFilePath


class SetComponentFields(Enum):
    _id=0
    set_id =1
    component_id = 2
    tag = 3
    value = 4

class SetFields(Enum):
    _id=0,
    project_id=1
    set_name=2
    date_start=3
    date_end=4
    timestepvalue=5
    timestepunit=6

#subclass of QTableView for displaying set information
class SetTableView(customTableView):
    def __init__(self, *args, **kwargs):
        super(SetTableView, self).__init__()
        self.tabPosition = kwargs.get('position')
        self.controller = Controller()
        self.header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        attributes = QtCore.QStringListModel([])
        self.setItemDelegateForColumn(1, TextDelegate(self))
        # needs to be called componentname for delegate signal
        cdel = RelationDelegate(self, 'componentname',filter="_id in (SELECT component_id from set_components WHERE set_id = " + str(self.tabPosition + 1) + ")") #"_id in ('1')", "_id in (SELECT component_id from set_components)"

        cdel.componentNameChanged.connect(self.updateTagList)
        #cdel.componentNameChanged.connect(QtWidgets.QApplication.aboutQt)
        self.setItemDelegateForColumn(SetComponentFields.component_id.value, cdel)

        #attributes (column 3)get updated when component Name gets selected (column 2)
        self.setItemDelegateForColumn(SetComponentFields.tag.value, ComboDelegate(self, attributes,'componentAttribute'))

    def updateTagList(self,compname):
        if compname != '':
            projectFolder = self.controller.dbhandler.getProjectPath()
            componentFolder = getFilePath('Components', projectFolder=projectFolder)
            myBox = [c for c in self.findChildren(ComboDelegate) if c.name == 'componentAttribute'][0]
            if compname.isnumeric():
                compname = self.controller.dbhandler.getFieldValue('component','componentnamevalue','_id',compname)

              # the current selected component, and the folder with component xmls are passed used to generate tag list
             #the combo box that contains possible tags to edit
            myBox.values = QtCore.QStringListModel(self.controller.setupHandler.getComponentAttributesAsList(compname, componentFolder))

class SetTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent,position):
        super(SetTableModel,self).__init__(parent)
        QtSql.QSqlTableModel.__init__(self, parent)
        self.hide_headers_mode = True
        self.header = ['ID','Set', 'Component', 'Tag', 'Value']
        self.setTable('set_components')
        self.controller = Controller()
        #the set table gets filtered to only show records for that set
        self.setFilter("set_id = " + str(position + 1) + " and tag != 'None' ORDER BY _id")
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)

        self.setRelation(SetComponentFields.component_id.value,
                        QtSql.QSqlRelation('component','_id', 'componentnamevalue'))
        '''Edit Strategy needs to be on row change because multi-field unique id. 
        Submission before unique constraint fields filled in result in relations showing id field not display field'''
        self.setEditStrategy(QtSql.QSqlTableModel.OnRowChange)
        self.select()


    def hideHeaders(self):
        self.hide_headers_mode = True

    def unhideHeaders(self):
        self.hide_headers_mode = False

    def headerData(self, section: int, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation != QtCore.Qt.Horizontal:
            return None
        if section < 0 or section >= len(self.header):
            return None
        if self.hide_headers_mode == True:
            return None
        else:
            return self.header[section]


    def submitTable(self):
        for r in range(self.rowCount()):
            if len(self.data(self.index(r,SetComponentFields.value.value)).split(',')) > 1:
                lov = self.data(self.index(r,SetComponentFields.value.value)).split(',')
            else:
                lov = [self.data(self.index(r,SetComponentFields.value.value))]
                t,a = splitAttribute(self.data(self.index(r,SetComponentFields.tag.value)))
            self.controller.dbhandler.insertTagRecord(
                (self.data(self.index(r,SetComponentFields.component_id.value)),
                 t,a,
                 lov),
                self.data(self.index(r,SetComponentFields.set_id.value)))