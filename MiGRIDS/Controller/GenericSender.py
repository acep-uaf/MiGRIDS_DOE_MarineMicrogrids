from PyQt5 import QtCore
class GenericSender(QtCore.QObject):
    notifyProgress = QtCore.pyqtSignal(int,str)
    msg = QtCore.pyqtSignal(str,str)
    statusChanged = QtCore.pyqtSignal() #str is the attribute name, bool is its state


    def update(self,value,task):
        self.notifyProgress.emit(value, task)

    def callStatusChanged(self):
        self.statusChanged.emit()

    def message(self,type,msgtext):
        self.msg.emit(type,msgtext)

    def updateAttribute(self,className,attr,value):
        self.signalUpdateAttribute(className,attr,value)