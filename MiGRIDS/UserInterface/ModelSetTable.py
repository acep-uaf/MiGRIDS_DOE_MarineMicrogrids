from PyQt5  import QtWidgets, QtSql, QtCore
from enum import Enum
from MiGRIDS.UserInterface.Delegates import TextDelegate, ComboDelegate, RelationDelegate
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.getComponentAttributesAsList import getComponentAttributesAsList
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
class SetTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        self.tabPosition = kwargs.get('position')
        QtWidgets.QTableView.__init__(self, *args)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        attributes = QtCore.QStringListModel([])
        self.setItemDelegateForColumn(1, TextDelegate(self))
        cdel = RelationDelegate(self, 'componentnamevalue',filter="_id in SELECT component_id from set_components where set_id = " + str(self.tabPosition +1))
        cdel.componentNameChanged.connect(self.updateTagList)
        #self.setItemDelegateForColumn(2,cdel)
        self.setItemDelegateForColumn(SetComponentFields.component_id.value, cdel)
        #attributes (column 3)get updated when component Name gets selected (column 2)
        self.setItemDelegateForColumn(3, ComboDelegate(self, attributes,'componentAttribute'))

    def updateTagList(self,compname):
        projectFolder = self.dbhandler.getProjectPath()
        componentFolder = getFilePath('Components', projectFolder=projectFolder)
        # the current selected component, and the folder with component xmls are passed used to generate tag list
        myBox = [c for c in self.findChildren(ComboDelegate) if c.name == 'componentAttribute'][0] #the combo box that contains possible tags to edit
        myBox.values = QtCore.QStringListModel(getComponentAttributesAsList(compname, componentFolder))

class SetTableModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent,position):
        QtSql.QSqlRelationalTableModel.__init__(self, parent)
        self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
        self.header = ['ID','Set', 'Component', 'Tag', 'Value']
        self.setTable('set_components')
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        #the set table gets filtered to only show records for that set
        self.setFilter('set_id = ' + str(position + 1)  )#+ ' and tag != None'
        self.setRelation(SetComponentFields.component_id.value,
                         QtSql.QSqlRelation('component', '_id', 'componentnamevalue'))
        self.select()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


