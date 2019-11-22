#subclass of QTableView for displaying component information
from enum import Enum

from IPython.core.inputtransformer import tr
from PyQt5 import QtWidgets, QtSql, QtCore, QtGui
from PyQt5.QtCore import QAbstractTableModel

from MiGRIDS.Controller.RunHandler import METADATANAMES
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

class customTableView(QtWidgets.QTableView):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(self, *args, **kwargs)
        #self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.resizeColumnsToContents()
        self.hiddenColumns = [0]
        self.columns = []

    def reFormat(self):
        self.setHorizontalHeader(HeaderViewWithWordWrap())
        self.horizontalHeader().setFixedHeight(50)
        self.unhideColumns()
        self.hideColumns()
        self.setColumnSizes()


    def setColumnSizes(self):
        self.resizeColumnsToContents()

    def unhideColumns(self):
        for i,c in enumerate(self.columns):
            self.setColumnHidden(c,False)

    def hideColumns(self):
        for c in self.hiddenColumns:
            self.hideColumn(c)

class RunTableView(customTableView):
    updateRunBaseCase = QtCore.pyqtSignal(int, bool)
    def __init__(self, *args, **kwargs):
        super(RunTableView, self).__init__(*args, **kwargs)

        d = QueryCheckBoxDelegate(self,'base_case','run')
        d.updateQuery.connect(self.notifyUpdateRun)
        self.setItemDelegateForColumn(RunFields.base_case.value, d)
    def reFormat(self):
        super().reFormat()
        self.horizontalHeader().setFixedHeight(100)

    def notifyUpdateRun(self,table,id,value,field):
        if (table == 'run') & (field =='base_case'):
            self.updateRunBaseCase.emit(id,value)

class RunTableModel(QtSql.QSqlQueryModel):
    def __init__(self, parent,setId):
        super(RunTableModel, self).__init__(parent)

        def getFancyName(n):
            nkey = [key for key, value in METADATANAMES.items() if value == n]
            if nkey:
                return nkey[0]
            return n

        #QtSql.QSqlQueryModel.__init__(self, parent)
        self.setId = setId
        self.header = [getFancyName(name) for name, member in RunFields.__members__.items()]
        self.header.append("run_id")
        self.header.append("Component Tag Values")
        self.hide_headers_mode = True
        self.refresh()

    def data(self, item: QtCore.QModelIndex, role: int = ...):

        if (role == QtCore.Qt.ToolTipRole):
             v = item.model().data(self.index(item.row(), 27), QtCore.Qt.DisplayRole)
             return v
        return super().data(item, role)

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

class HeaderViewWithWordWrap(QtWidgets.QHeaderView):
    def __init__(self):
        QtWidgets.QHeaderView.__init__(self, QtCore.Qt.Horizontal)
        self.setStyleState()

        self.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


    def sectionSizeFromContents(self, logicalIndex):
        if self.model():
            headerText = self.model().headerData(logicalIndex,
                                                 self.orientation(),
                                                 QtCore.Qt.DisplayRole)
            options = self.viewOptions()
            metrics = QtGui.QFontMetrics(options.font)
            maxWidth = self.sectionSize(logicalIndex)

            rect = metrics.boundingRect(QtCore.QRect(0, 0, maxWidth, 50000),
                                        QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap | QtCore.Qt.TextExpandTabs,
                                        headerText, 4)

            return rect.size()
        else:
            return QtWidgets.QHeaderView.sectionSizeFromContents(self, logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        if self.model():
            painter.save()
            self.model().hideHeaders()
            QtWidgets.QHeaderView.paintSection(self, painter, rect, logicalIndex)
            self.model().unhideHeaders()
            painter.restore()
            headerText = self.model().headerData(logicalIndex,
                                                 self.orientation(),
                                                 QtCore.Qt.DisplayRole)
            painter.drawText(QtCore.QRectF(rect), QtCore.Qt.AlignCenter|QtCore.Qt.TextWordWrap, headerText)
        else:
            QtWidgets.QHeaderView.paintSection(self, painter, rect, logicalIndex)

    def setStyleState(self):
        if self.model() is None:
            stylesheet = "::section{Background-color:rgb(171,181,184)}"
        elif self.model().rowCount() > 0:
            stylesheet = "::section{Background-color:rgb(171,181,184)}"
        else:
            stylesheet = "::section{Background-color:rgb(139, 140, 140)}"

        self.setStyleSheet(stylesheet)