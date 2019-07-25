from PyQt5 import QtCore, QtWidgets, QtSql
from MiGRIDS.InputHandler.Component import Component
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

import os
#class for combo boxes that are not derived from database relationships
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

    '''def makeList(self,box, values):

        self.values = values
        for i in range(box.count()):
            box.removeItem(i)
        box.addItems(self.values)'''

    def setEditorData(self, editor, index):
        editor.blockSignals(True)

        #set the combo to the selected index
        editor.setCurrentText(index.model().data(index))
        editor.blockSignals(False)

    #write model data
    def setModelData(self,editor, model, index):
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

                    # project folder is from FormSetup model
                    projectFolder = tv.window().findChild(QtWidgets.QWidget, "setupDialog").model.projectFolder
                    componentFolder = os.path.join(projectFolder, 'InputData', 'Components')
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
        from MiGRIDS.UserInterface.formFromXML import formFromXML
        from MiGRIDS.Controller.UIToInputHandler import UIToHandler
        from MiGRIDS.UserInterface.ModelComponentTable import  ComponentTableModel
        from MiGRIDS.UserInterface.ModelComponentTable import  ComponentFields

        import os

        handler = UIToHandler()

        model = self.parent().model()
        #if its a component table bring up the component editing form
        if type(model) is ComponentTableModel:
            #if its from the component table do this:
            #there needs to be a component descriptor file written before this form can open
            #column 0 is id, 3 is name, 2 is type

            #make a component object from these model data
            component =Component(component_name=model.data(model.index(index.row(), ComponentFields.NAME.value)),
                                 original_field_name=model.data(model.index(index.row(), ComponentFields.ORIGINALFIELD.value)),
                                 units=model.data(model.index(index.row(), ComponentFields.UNITS.value)),
                                 offset=model.data(model.index(index.row(), ComponentFields.OFFSET.value)),
                                 type=model.data(model.index(index.row(), ComponentFields.TYPE.value)),
                                 attribute=model.data(model.index(index.row(), ComponentFields.ATTRIBUTE.value)),
                                 scale=model.data(model.index(index.row(), ComponentFields.SCALE.value)),

                                 )
             #the project filepath is stored in the model data for the setup portion

            setupform = self.parent().window().findChild(QtWidgets.QWidget,"setupDialog" )
            setupInfo = setupform.model
            setupInfo.setupFolder
            componentDir = os.path.join(setupInfo.setupFolder, '../Components')

            if component.type !="":
                #tell the input handler to create or read a component descriptor and combine it with attributes in component
                componentSoup = handler.makeComponentDescriptor(component.column_name, componentDir)
                #data from the form gets saved to a soup, then written to xml
                #modify the soup to reflect data in the data model
                component.component_directory = componentDir
                f = formFromXML(component, componentSoup)
            else:
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Component Type",
                                            "You need to select a component type before editing attributes.")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec()

        else:
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, "Missing Component Name",
                                            "You need to select a component before editing attributes.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec()

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
        elif role == QtCore.Qt.UserRole:
            return QtCore.QVariant(self.arraydata[index.row()][0]) #column 0 is id
        else:
            return QtCore.QVariant()

    def updateModel(self, newArray):
        self.arraydata = newArray