# Projet: MiGRIDS
# Created by: # Created on: 11/15/2019

#classes used for displaying wizard inputs
from PyQt5 import QtWidgets,QtGui,QtCore

from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler


class WizardPage(QtWidgets.QWizardPage):
    def __init__(self, inputdict,parent,**kwargs):
        super().__init__(parent)
        self.first = kwargs.get('first')
        self.last = kwargs.get('last')
        self.initUI(inputdict)
        self.dbhandler = ProjectSQLiteHandler()

    # initialize the form
    def initUI(self, inputdict):
        self.d = inputdict
        self.setTitle(self.d['title'])
        self.input = self.setInput()
        self.input.setObjectName(self.d['name'])
        self.label = QtWidgets.QLabel()
        self.label.setText(self.d['prompt'])
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)


        return

    def setInput(self):
        wid = QtWidgets.QLineEdit()
        try:
            value = self.parent().__getattribute__(self.d['name'])

        except AttributeError as a:
            print(a)
            value = ''
        finally:
            if ( value == ''):
                self.registerField(self.d['name'] + "*", wid) #defualt input is required
            else:
                self.registerField(self.d['name'], wid)
            wid.setText(value)
            self.setField(self.d['name'],value)
        return wid

    def getInput(self):
        return self.input.text()


class ComponentSelect(WizardPage):
    def __init__(self,d,parent):
        super().__init__(d,parent)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        layout = QtWidgets.QGridLayout()

        handler = ProjectSQLiteHandler()
        lot = handler.getCurrentComponentTypeCount() #all possible component types, tuples with three values type code, description, count

        for i,t in enumerate(lot):
            label = QtWidgets.QLabel()
            label.setText(t[1])
            comp = QtWidgets.QSpinBox()
            comp.setObjectName(t[0] + 'count')
            comp.setValue(t[2])
            layout.addWidget(label,i,0,1,1)
            layout.addWidget(comp,i,1,1,1)
            self.registerField(comp.objectName(), comp)

        grp.setLayout(layout)
        return grp

class TwoDatesDialog(WizardPage):
    def __init__(self,d,parent):
        super().__init__(d,parent)
        self.d = d

    def setInput(self):
        handler = ProjectSQLiteHandler()
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.startDate = QtWidgets.QDateEdit()
        self.startDate.setObjectName('start')
        self.startDate.setDisplayFormat('yyyy-MM-dd')
        self.startDate.setCalendarPopup(True)
        self.endDate = QtWidgets.QDateEdit()
        self.endDate.setObjectName('end')
        self.endDate.setDisplayFormat('yyyy-MM-dd')
        self.endDate.setCalendarPopup(True)
        box.addWidget(self.startDate)
        box.addWidget(self.endDate)
        grp.setLayout(box)
        self.registerField('sdate', self.startDate,"text")
        self.registerField('edate',self.endDate,"text")
        try:
            #if the setup info has already been set dates will be in the database table set
            print(handler.getFieldValue('setup', 'date_start', '_id',1))
            self.startDate.setDate(QtCore.QDate.fromString(handler.getFieldValue('setup', 'date_start', '_id', 1),"yyyy-MM-dd"))
            self.endDate.setDate(QtCore.QDate.fromString(handler.getFieldValue('setup', 'date_end',  '_id', 1),"yyyy-MM-dd"))
        except AttributeError as a:
            print(a)
        except TypeError as a:
            print(a)
        except Exception as e:
            print(e)
        return grp

    def getInput(self):
        return " - ".join([self.startDate.text(),self.endDate.text()])

class DropDown(WizardPage):
    def __init__(self,d,parent):
        super().__init__(d,parent)

    def setInput(self):
        self.input = QtWidgets.QComboBox()
        self.input.setItems(self.getItems())
        return
    def getInput(self):
        return self.breakItems(self.input.itemText(self.input.currentIndex()))

    def getItems(self):

        items = self.dbhandler.getCodes(self.d['reftable'])
        return items
    def breakItems(self,str):
        item = str.split(' - ')[0]
        return item

class TextWithDropDown(WizardPage):
    def __init__(self, d,parent):
        super().__init__(d,parent)
        self.d = d

    def setInput(self):
        grp = QtWidgets.QGroupBox()
        box = QtWidgets.QHBoxLayout()
        self.combo = QtWidgets.QComboBox()
        handler = ProjectSQLiteHandler()
        self.combo.addItems(self.getItems())
        self.textInput = QtWidgets.QLineEdit()
        self.textInput.setValidator(QtGui.QIntValidator())
        box.addWidget(self.textInput)
        box.addWidget(self.combo)
        grp.setLayout(box)
        #self.registerField(self.d['name'],self.combo,"currentText",self.combo.currentIndexChanged)
        self.registerField('timestepvalue', self.textInput)
        self.registerField('timestepunit',self.combo,"currentText")
        try:
            #if the setup info has already been set dates will be in the database table set
            self.textInput.setText(handler.getFieldValue('setup', 'timestepvalue', '_id', 1))
            self.combo.setCurrentText(handler.getFieldValue('setup', 'timestepunit', '_id', 1))
        except AttributeError as a:
            print(a)
        return grp

    def getInput(self):
        input = self.textInput.text()
        item = self.breakItems(self.input.itemText(self.input.currentIndex()))
        strInput = ' '.join([input,item])
        return strInput
    def getItems(self):
        dbhandler = ProjectSQLiteHandler()
        items = dbhandler.getCodes(self.d['reftable'])
        dbhandler.closeDatabase()
        return items

    def breakItems(self, str):
        item = str.split(' - ')[0]
        return item