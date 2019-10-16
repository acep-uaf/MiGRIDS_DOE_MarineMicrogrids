# Projet: MiGRIDS
# Created by: # Created on: 9/25/2019
from PyQt5 import QtWidgets


class DatesDialog(QtWidgets.QDialog):

    def __init__(self, minDate, maxDate):
        super().__init__()
        self.setWindowTitle("Dates to Analyze")
        grp = QtWidgets.QGroupBox()
        hz = QtWidgets.QVBoxLayout()
        prompt = QtWidgets.QLabel("Select Dates to Analyze")
        hz.addWidget(prompt)
        box = QtWidgets.QHBoxLayout()
        self.startDate = QtWidgets.QDateEdit()
        self.startDate.setObjectName('start')
        self.startDate.setDisplayFormat('yyyy-MM-dd')
        self.startDate.setDate(minDate)
        self.startDate.setCalendarPopup(True)
        self.endDate = QtWidgets.QDateEdit()
        self.endDate.setDate(maxDate)
        self.endDate.setObjectName('end')
        self.endDate.setDisplayFormat('yyyy-MM-dd')
        self.endDate.setCalendarPopup(True)
        box.addWidget(self.startDate)
        box.addWidget(self.endDate)
        grp.setLayout(box)
        hz.addWidget(grp)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok
                                     | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        hz.addWidget(buttonBox)

        self.setLayout(hz)

        def getValues(self):
            a, b = self.startDate.text(), self.endDate.text()
            return a, b