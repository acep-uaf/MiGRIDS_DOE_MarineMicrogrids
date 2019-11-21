#subclass of QTableView for displaying component information
from enum import Enum

from IPython.core.inputtransformer import tr
from PyQt5 import QtWidgets, QtSql, QtCore

from MiGRIDS.UserInterface.Delegates import QueryCheckBoxDelegate


class RunFields(Enum):
    _id=0
    set_id =1
    run_num = 2
    base_case = 3
    started = 4
    finished = 5
    genptot = 6
    genpch = 7
    gensw = 8
    genloadingmean = 9
    gencapacitymean = 10
    genfuelcons = 11
    gentimeoff = 12
    gentimeruntot = 13
    genruntimeruntotkwh = 14
    genoverloadingtime = 15
    genoverLoadingkwh = 16
    wtgpimporttot = 17
    wtgpspilltot = 18
    wtgpchtot = 19
    eesspdistot = 20
    eesspchtot = 21
    eesssrctot = 22
    eessoverloadingtime = 23
    eessoverloadingkwh = 24
    tessptot = 25

class RunTableView(QtWidgets.QTableView):
    updateRunBaseCase = QtCore.pyqtSignal(int, bool)
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        d = QueryCheckBoxDelegate(self,'base_case','run')
        d.updateQuery.connect(self.notifyUpdateRun)
        self.setItemDelegateForColumn(RunFields.base_case.value, d)


    def notifyUpdateRun(self,table,id,value,field):
        if (table == 'run') & (field =='base_case'):
            self.updateRunBaseCase.emit(id,value)

class RunTableModel(QtSql.QSqlQueryModel):
    def __init__(self, parent,setId):
        super(RunTableModel, self).__init__(parent)

        QtSql.QSqlQueryModel.__init__(self, parent)
        self.setId = setId
        self.header = [name for name, member in RunFields.__members__.items()]
        self.header.append("run_id")
        self.header.append("Component Tag Values")



        self.refresh()


    def refresh(self, setId = None):
        if setId is not None:
            self.setId = setId
        self.strsql = "SELECT * FROM run LEFT JOIN (SELECT run_id, " \
                      "group_concat(componentnamevalue ||'.' || tag || ' = ' || tag_value) from run_attributes " \
                      "JOIN set_components ON set_components._id = run_attributes.set_component_id " \
                      "JOIN component on set_components.component_id = component._id WHERE " \
                      "set_components.set_id = " + str(self.setId) + " GROUP BY run_attributes.run_id) as ra ON run._id = ra.run_id " \
                      "GROUP BY run_id"

        self.setQuery(self.strsql)
        self.query()


    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            try:
                v = self.header[section]
                return QtCore.QVariant(self.header[section])
            except IndexError:
                return QtCore.QVariant(self.header[0])

        return QtCore.QVariant()

