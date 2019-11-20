from PyQt5 import QtCore
class GenericSender(QtCore.QObject):
    notifyProgress = QtCore.pyqtSignal(int,str)
    msg = QtCore.pyqtSignal(str,str)

    def update(self,value,task):
        self.notifyProgress.emit(value, task)


    def message(self,type,msgtext):
        self.msg.emit(type,msgtext)