from PyQt5 import QtCore, QtWidgets, QtSql

#class for combo boxes that are not derived from database relationships

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
        elif isinstance(index.model().data(index),int):
             editor.setCurrentIndex(index.model().data(index))
        editor.blockSignals(False)

    #write model data
    def setModelData(self,editor, model, index):

         if isinstance(self.values,RefTableModel):
             model.setData(index, editor.currentIndex(),QtCore.Qt.EditRole)
         #model is the table storing the combo
         model.setData(index, editor.itemText(editor.currentIndex()),QtCore.Qt.EditRole)

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        #self.commitData.emit(self.sender())
        #if its the sets table then the attribute list needs to be updated
        return

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
    componentNameChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent,name,**kwargs):
        QtSql.QSqlRelationalDelegate.__init__(self,parent)
        self.parent = parent
        self.name=name
        self.filter = kwargs.get("filter")

    def createEditor(self, parent, option, index):
        #make a combo box if there is a valid relation
        if index.model().relation(index.column()).isValid:
            editor = QtWidgets.QComboBox(parent)
            editor.currentIndexChanged.connect(self.currentIndexChanged)
            #editor.activated.connect(self.currentIndexChanged)
            return editor
        else:
            return QtWidgets.QStyledItemDelegate(parent).createEditor(parent,option,index)

    def setEditorData(self, editor, index):
        m = index.model()
        relation = m.relation(index.column())

        if relation.isValid():
            pmodel = QtSql.QSqlTableModel()

            pmodel.setTable(relation.tableName())

            pmodel.select()
            editor.setModel(pmodel)

            editor.setModelColumn(pmodel.fieldIndex(relation.displayColumn()))
            editor.setCurrentIndex(editor.findText(str(m.data(index))))
        return
    def setModelData(self,editor, model, index):

         return super(RelationDelegate, self).setModelData(editor,model,index)

    @QtCore.pyqtSlot()
    def currentIndexChanged(self):
        #i = index
        #self.commitData.emit(self.sender())
        if self.name == 'componentname':
            currentSelected = self.sender().currentText()

            self.componentNameChanged.emit(currentSelected)
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
        elif role == QtCore.Qt.DisplayRole:
          return QtCore.QVariant(self.arraydata[index.row()][1]) #column 1 is display data
        else:
            return QtCore.QVariant(self.arraydata[index.row()][0]) #this fills the data field with the value in column 0

    def updateModel(self, newArray):
        self.arraydata = newArray
class QueryCheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    updateQuery= QtCore.pyqtSignal(str,int,bool,str)
    def __init__(self,parent,columnToUpdate,table):
        QtWidgets.QItemDelegate.__init__(self,parent)
        self.columnToUpdate = columnToUpdate
        self.table = table

    def createEditor(self, parent, option, index):
        """ Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled


    def paint(self, painter, option, index):
        modelValue = index.model().data(index, QtCore.Qt.DisplayRole)
        checked = bool(index.model().data(index, QtCore.Qt.DisplayRole))
        opt = QtWidgets.QStyleOptionButton()

        opt.state |= QtWidgets.QStyle.State_Active

        if checked:
            opt.state |= QtWidgets.QStyle.State_On
        else:
            opt.state |= QtWidgets.QStyle.State_Off
        opt.rect = self.getCheckBoxRect(option)

        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, opt, painter)


    def editorEvent(self, event: QtCore.QEvent, model: QtCore.QAbstractItemModel, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        flags = model.flags(index)

        #if not (index.flags() & QtCore.Qt.ItemIsEditable):
            #return False
        if event.button() == QtCore.Qt.LeftButton:
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if self.getCheckBoxRect(option).contains(event.pos()):
                    self.setModelData(None, model, index)
                    return True
            elif event.type() == QtCore.QEvent.MouseButtonDblClick:
                if self.getCheckBoxRect(option).contains(event.pos()):
                    return True
        return False

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex):

        checked = not bool(index.model().data(index, QtCore.Qt.DisplayRole))

        id = index.model().data(model.index(index.row(),0),QtCore.Qt.DisplayRole)
        model.setData(index, checked, QtCore.Qt.EditRole)

        self.updateQuery.emit(self.table,id,checked,self.columnToUpdate)

    def getCheckBoxRect(self, option):
        """ Get rect for checkbox centered in option.rect.
        """
        # Get size of a standard checkbox.

        opts = QtWidgets.QStyleOptionButton()
        checkBoxRect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, opts, None)
        # Center checkbox in option.rect.
        x = option.rect.x()
        y = option.rect.y()
        w = option.rect.width()
        h = option.rect.height()

        checkBoxTopLeftCorner = QtCore.QPoint(x + w / 2 - checkBoxRect.width() / 2, y + h / 2 - checkBoxRect.height() / 2)
        return QtCore.QRect(checkBoxTopLeftCorner, checkBoxRect.size())

