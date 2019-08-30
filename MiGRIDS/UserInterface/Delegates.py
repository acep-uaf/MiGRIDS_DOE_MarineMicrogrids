from PyQt5 import QtCore, QtWidgets, QtSql

#class for combo boxes that are not derived from database relationships
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.displayComponentXML import displayComponentXML


class ComboDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent,values, name=None):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.values = values
        self.name = name

    def createEditor(self,parent, option, index):
        combo = QtWidgets.QComboBox(parent)
        combo.setObjectName(self.name)
        combo.setModel(self.values)
        #combo.currentIndexChanged.connect(self.currentIndexChanged)
        combo.activated.connect(self.currentIndexChanged)
        return combo


    def setEditorData(self, editor, index):
        editor.blockSignals(True)

        #set the combo to the selected index
        if isinstance(index.model().data(index),str):
            editor.setCurrentText(index.model().data(index))
        else:
            editor.setCurrentIndex(index.model().data(index))
        editor.blockSignals(False)

    #write model data
    def setModelData(self,editor, model, index):
         irow = index.row()
         crow = editor.currentIndex()
         txt = editor.itemText(editor.currentIndex())
         '''if isinstance(self.values,RefTableModel):
             model.setData(index, editor.currentIndex())'''
         #model is the table storing the combo
         model.setData(index, editor.itemText(editor.currentIndex()))

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        from MiGRIDS.UserInterface.getComponentAttributesAsList import getComponentAttributesAsList
        self.commitData.emit(self.sender())
        #if its the sets table then the attribute list needs to be updated
        if self.name == 'componentName':
            tv = self.parent()
            cbs = tv.findChildren(ComboDelegate)
            for cb in cbs:
                if cb.name == 'componentAttribute':
                    lm = cb.values
                    #populate the combo box with the possible attributes that can be changed

                    # project folder is from
                    projectFolder = tv.window().findChild(QtWidgets.QWidget, "setupDialog").getprojectFolder()
                    componentFolder = getFilePath('components',projectFolder = projectFolder)
                    #the current selected component, and the folder with component xmls are passed used to generate tag list
                    lm.setStringList(getComponentAttributesAsList(self.sender().currentText(),componentFolder))

#LineEdit textbox connected to the table
class TextDelegate(QtWidgets.QItemDelegate):
    def __init__(self,parent):
        QtWidgets.QItemDelegate.__init__(self,parent)
        if 'column1' in parent.__dict__.keys():
            self.autotext1 = parent.column1


    def createEditor(self,parent, option, index):
        txt = QtWidgets.QLineEdit(parent)
        txt.inputMethodHints()
        txt.textChanged.connect(self.currentIndexChanged)
        return txt

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        if ('autotext1' in self.__dict__.keys()) & (index.column == 1):
            editor.setText(self.autotext1)

        else:
            editor.setText(str(index.model().data(index)))

        editor.blockSignals(False)

    def setModelData(self, editor, model, index):

        model.setData(index, editor.text())

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())

#combo boxes for tables with foreign keys
class RelationDelegate(QtSql.QSqlRelationalDelegate):
    def __init__(self, parent,name):
        QtSql.QSqlRelationalDelegate.__init__(self,parent)
        self.parent = parent
        self.name=name

    def createEditor(self, parent, option, index):
        #make a combo box if there is a valid relation
        if index.model().relation(index.column()).isValid:
            editor = QtWidgets.QComboBox(parent)
            #editor.setCurrentIndex(0)
            editor.activated.connect(self.currentIndexChanged)
            return editor
        else:
            return QtWidgets.QStyledItemDelegate(parent).createEditor(parent,option,index)

    def setEditorData(self, editor, index):
        m = index.model()
        relation = m.relation(index.column())
        #TODO filter possible components
        if relation.isValid():
            pmodel = QtSql.QSqlTableModel()
            pmodel.setTable(relation.tableName())
            pmodel.select()
            editor.setModel(pmodel)
            editor.setModelColumn(pmodel.fieldIndex(relation.displayColumn()))
            editor.setCurrentIndex(editor.findText(str(m.data(index))))

    def setModelData(self,editor, model, index):
         model.setData(index, editor.itemText(editor.currentIndex()))



    @QtCore.pyqtSlot()
    def currentIndexChanged(self):

        self.commitData.emit(self.sender())
        return

#QLineEdit that when clicked performs an action
class ClickableLineEdit(QtWidgets.QLineEdit):
    clicked = QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        else:
            super().mousePressEvent(event)

class ComponentFormOpenerDelegate(QtWidgets.QItemDelegate):

    def __init__(self,parent,text):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.text = text
    def paint(self, painter, option, index):

        if not self.parent().indexWidget(index):
            self.parent().setIndexWidget(
                index, QtWidgets.QPushButton(self.text,self.parent(), clicked=lambda:self.cellButtonClicked(index))
            )
    @QtCore.pyqtSlot()
    def cellButtonClicked(self, index):
        from MiGRIDS.UserInterface.ModelComponentTable import  ComponentTableModel
        from MiGRIDS.UserInterface.ModelComponentTable import  ComponentFields

        model = self.parent().model()
        #if its a component table bring up the component editing form
        if type(model) is ComponentTableModel:

            displayComponentXML(model.data(model.index(index.row(), ComponentFields.component_id.value)))

class RefTableModel(QtCore.QAbstractTableModel):
    def __init__(self, dataIn, parent=None, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = dataIn

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        if(len(self.arraydata)>0):
            return len(self.arraydata[0])
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        #elif role == QtCore.Qt.DisplayRole:
        #  return QtCore.QVariant(self.arraydata[index.row()][1]) #column 1 is display data
        else:
            return QtCore.QVariant(self.arraydata[index.row()][0]) #this fills the data field with the value in column 0

    def updateModel(self, newArray):
        self.arraydata = newArray