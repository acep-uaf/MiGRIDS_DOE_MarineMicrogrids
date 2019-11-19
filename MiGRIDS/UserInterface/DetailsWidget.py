# Projet: MiGRIDS
# Created by: T. Morgan# Created on: 11/18/2019
from PyQt5 import QtWidgets,QtCore


class DetailsWidget(QtWidgets.QDockWidget):
    """
    Description: Floating widget to view text
    Attributes: 
        
        
    """

    def __init__(self,title,details):
        super().__init__()
        self.initUI(title,details)

    def initUI(self, title,details):

        self.setWindowTitle(title)
        textWindow = QtWidgets.QLabel()
        textWindow.setWordWrap(True)
        textWindow.setText(str(details))
        textWindow.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse);
        app = QtCore.QCoreApplication.instance()
        size = app.desktop().screenGeometry()
        self.setMaximumSize(size.width(),size.height())
        vs = QtWidgets.QScrollArea()
        self.setWidget(vs)
        vs.setWidget(textWindow)
        self.show()


