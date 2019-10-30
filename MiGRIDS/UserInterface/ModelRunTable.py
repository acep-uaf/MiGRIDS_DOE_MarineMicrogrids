#subclass of QTableView for displaying component information
from enum import Enum
from PyQt5 import QtWidgets, QtSql, QtCore

class SetComponentFields(Enum):
    _id=0
    set_id =1
    run_num = 2
    started = 3
    finished = 4
    genptot = 5
    genpch = 6
    gensw = 7
    genloadingmean = 8
    gencapacitymean = 9
    genfuelcons = 10
    gentimeoff = 11
    gentimeruntot = 12
    genruntimeruntotkwh = 13
    genoverloadingtime = 14
    genoverLoadingkwh = 15
    wtgpimporttot = 16
    wtgpspilltot = 17
    wtgpchtot = 18
    eesspdistot = 19
    eesspchtot = 20
    eesssrctot = 21
    eessoverloadingtime = 22
    eessoverloadingkwh = 23
    tessptot =24

class RunTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        #TODO set delegates

class RunTableModel(QtSql.QSqlQueryModel):
    def __init__(self, parent,setId,header):

        QtSql.QSqlQueryModel.__init__(self, parent)
        self.setId = setId
        self.header = header
        runQuery = QtSql.QSqlQuery("""SELECT * FROM run LEFT JOIN (SELECT run_id, aggregate(component |'.' | tag | ' = ' | tag_value) from run_attributes JOIN set_components ON set_components.component_id = run_attributes.component_id ) as ra ON run._id = ra.run_id""")
        #self.setFilter('set_id = '  + self.setId)
        self.setQuery(runQuery)



    def headerData(self, section: int, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.header[section])
        return QtCore.QVariant()


