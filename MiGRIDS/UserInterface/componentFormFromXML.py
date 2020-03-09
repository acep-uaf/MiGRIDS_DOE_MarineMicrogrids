# Projet: MiGRIDS
# Created by: # Created on: 11/8/2019
#creates a dynamic form based on the information in xml files
from PyQt5 import QtWidgets, QtCore
from MiGRIDS.Controller.UIHandler import UIHandler

class componentFormFromXML(QtWidgets.QDialog):
    def __init__(self, component, componentSoup, write=True):
        super().__init__()

        self.soup = componentSoup
        self.componentDictionary = component
        self.write = write
        self.changes={}
        self.initUI()

    # initialize and display the form
    def initUI(self):
        #container widget
        widget = QtWidgets.QWidget()
        self.setWindowTitle(self.componentDictionary['componentnamevalue'])
        self.setObjectName("Component Dialog")
        #layout of container widget
        windowLayout = QtWidgets.QVBoxLayout()

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        #a grid layout object
        xmlLayout = self.displayXML(self.soup, windowLayout)
        widget.setLayout(xmlLayout)
        scrollArea.setWidget(widget)

        #adding scroll layer
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(scrollArea,6)

        self.setLayout(self.layout)

        self.show()
        self.exec()


    #create a layout from the xml that was turned into soup
    #BeautifulSoup QVBoxLayout -> QVBoxLayout
    def displayXML(self, soup, vlayout):
        from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
        from MiGRIDS.UserInterface.gridLayoutSetup import setupGrid
        g1 = {'headers': [1,2,3,4,5],
              'rowNames': [],
              'columnWidths': [2, 1, 1, 1, 1]}
        masterDict={}
        #this uses a generic units table
        dbHandler = ProjectSQLiteHandler('project_manager')
        units = dbHandler.cursor.execute("select code from ref_units").fetchall()
        dbHandler.closeDatabase()

        units = [u[0] for u in units]


        for tag in soup.find_all():
            if tag.name not in ['component','childOf','type']:
                row = 0
                hint = "".join(tag.findAll(text=True))
                #the tag name is the main label
                if tag.parent.name not in ['component', 'childOf', 'type']:
                    #tags with parents become subtags
                    parent = tag.parent.name
                    pt = '.'.join([parent, tag.name])

                else:
                    #if there isn't a parent then the tag is the parent
                    pt = tag.name
                inputRow = pt #the label won't be vizible because it ends in a number

                g1['rowNames'].append(inputRow)

                #every tag gets a grid for data input
                #there are 4 columns - 2 for labels, 2 for values
                #the default is 2 rows - 1 for tag name, 1 for data input
                #more rows are added if more than 2 input attributes exist

                #create the overall label
                g1[inputRow] = {1:{'widget':'lbl','name':tag.name}}
                column = 1

                for a in tag.attrs:
                    name = '.'.join([pt,str(a)]) #the name of the attribute becomes joined with the tag
                    inputValue = tag[a]
                    kids = tag.findAll()
                    myParent = tag.parent.name
                    b = myParent in masterDict.keys()

                    #columns aways starts populating at 2
                    if column <=4:
                       column+=1
                    else: #check for children here. If subtags, advnce row, otherwise leave at 0
                        column = 2 #entry fields start in column 2
                        # here is where we determine if the input will be displayed in the same row as the main tag label



                    widget = 'txt'
                    items = None
                    #if setting units attribute use a combo box
                    if a =='unit':
                        widget = 'combo'
                        items = units
                    #if the value is set to true false use a checkbox
                    if inputValue in ['TRUE','FALSE']:
                        widget = 'chk'


                    #first column is the label
                    if (widget == 'chk') & (a =='value'):
                        g1[inputRow][column] = {'widget': 'lbl', 'name': 'lbl' + a, 'default': 'yes?',
                                                               'hint': hint}
                    else:
                        g1[inputRow][column] = {'widget':'lbl','name':'lbl' + a, 'default':a, 'hint':hint}
                    column+=1

                    if items is None:
                        g1[inputRow][column] = {'widget': widget, 'name':name, 'default':inputValue, 'hint':hint}
                    else:
                        g1[inputRow][column] = {'widget': widget, 'name':name, 'default': inputValue, 'items':items, 'hint':hint}

        #make the grid layout from the dictionary
        grid = setupGrid(g1)
        #add the grid to the parent layout
        vlayout.addLayout(grid)

        return vlayout


    def update(self):
        '''
        For every tag in the soup find its current value in the form and update the value in the soup
        :return: None
        '''
        for tag in self.soup.find_all():
            if tag.parent.name not in ['component', 'childOf', 'type']:
                parent = tag.parent.name
                pt = '.'.join([parent,tag.name])
            else:
                pt = tag.name
            for a in tag.attrs:
                widget = self.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox,QtWidgets.QCheckBox), '.'.join([pt,str(a)]))

                if type(widget) == QtWidgets.QLineEdit:
                    if tag.attrs[a] != widget.text():
                        self.changes['.'.join([pt, str(a)])]=widget.text()
                        tag.attrs[a] = widget.text()

                elif type(widget) == QtWidgets.QComboBox:
                    if tag.attrs[a] != widget.currentText():
                        self.changes['.'.join([pt, str(a)])]=widget.currentText()
                        tag.attrs[a]= widget.currentText()

                elif type(widget) == QtWidgets.QCheckBox:
                    if (widget.isChecked()) & (tag.attrs[a] != 'TRUE'):
                        self.changes['.'.join([pt, str(a)])]= 'TRUE'
                        tag.attrs[a] = 'TRUE'
                    elif (not widget.isChecked()) & (tag.attrs[a] != 'FALSE'):
                        self.changes['.'.join([pt, str(a)])]= 'TRUE'
                        tag.attrs[a]= 'FALSE'


    def closeEvent(self,evnt):
        '''When the form is closed the information gets written to the xml file'''
        print('closing descriptor file')
        #update the soup to reflect changes
        self.update()
        #write the xml
        if self.write:
            handler = UIHandler()
            handler.writeComponentSoup(self.componentDictionary['componentnamevalue'], self.soup)
        else:
            #If write is false then a list of changes gets printed to the console
            print(self.changes)