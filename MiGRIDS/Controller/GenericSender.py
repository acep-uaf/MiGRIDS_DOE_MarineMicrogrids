from PyQt5 import QtCore
class GenericSender(QtCore.QObject):
    notifyProgress = QtCore.pyqtSignal(int,str)

    def update(self,value,task):
        if value == 0:
            self.last = 0
        if self.last:
            self.notifyProgress.emit(self.last + value,task)
            self.last = self.last + value
        else:
            self.notifyProgress.emit(value, task)
            self.last = value