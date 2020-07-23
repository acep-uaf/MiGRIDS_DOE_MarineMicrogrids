# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 8/16/2019
from MiGRIDS.UserInterface.Delegates import *
from enum import Enum

class InputFileFields(Enum):
    _id=0
    project_id = 1
    inputfiletypevalue=2
    datatype=3
    inputfiledirvalue=4
    inputtimestepvalue=5
    inputtimestepunit=6
    datechannelvalue=7
    datechannelformat=8
    timechannelvalue=9
    timechannelformat=10
    includechannels=11
    timezonevalue=12
    usedstvalue=13
    flexibleyearvalue=14
    inpututcoffsetvalue=15

# #subclass of QTableView for displaying inputFile information
# class FileInfoTableView(QtWidgets.QTableView):
#     def __init__(self, *args, **kwargs):
#         QtWidgets.QTableView.__init__(self)
#         self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
#         self.resizeColumnsToContents()
#         #set text boxes
#         t_boxes =[3,4,5,7]
#         for i in t_boxes:
#             self.setItemDelegateForColumn(i, TextDelegate(self))
#         self.setColumnHidden(0, True)
#         #set combo boxes
#         combos = [1,2,6,8]
#         for c in combos:
#             self.setItemDelegateForColumn(c,RelationDelegate(self,None))
#
# #Tabel model to be displayed in InputFile tableview
# class FileInfoTableModel(QtSql.QSqlRelationalTableModel):
#     def __init__(self,parent):
#         QtSql.QSqlRelationalTableModel.__init__(self, parent)
#         self.header = ['ID','File Type','Data Type','Directory','Time Sample Interval',
#                    'Date Channel','Date Format','Time Channel','Time Format','Channels']
#
#
#         self.setTable('inputFiles')
#         self.setJoinMode(QtSql.QSqlRelationalTableModel.LeftJoin)
#         self.setRelation(1, QtSql.QSqlRelation('ref_file_type', 'code', 'code'))
#         self.setRelation(2, QtSql.QSqlRelation('ref_data_format', 'code', 'code'))
#         self.setRelation(6, QtSql.QSqlRelation('ref_date_format', 'code', 'code'))
#         self.setRelation(8, QtSql.QSqlRelation('ref_time_format', 'code', 'code'))
#         self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
#         self.select()
#
#     def headerData(self, section: int, orientation, role):
#         if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
#             return QtCore.QVariant(self.header[section])
#         return QtCore.QVariant()
#
