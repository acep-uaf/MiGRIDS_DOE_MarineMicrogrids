#creates a dynamic form based on the information in xml files
from PyQt5 import QtWidgets, QtCore, QtGui

class GridFromXML(QtWidgets.QVBoxLayout):
    def __init__(self, parent,soup, fields = [],write=False):
        super().__init__()
        self.fields = fields
        #soup is from the xml file that was read in
        self.soup = soup
        #write is whether or not to write the changed soup an xml file; default is False
        self.write = write
        self.changes={}
        gb = self.displayXML(self.soup)

        #self.addLayout(gb)



    #create a layout from the xml that was turned into soup
    #BeautifulSoup QVBoxLayout -> QVBoxLayout
    def displayXML(self, soup):

        from MiGRIDS.UserInterface.gridLayoutSetup import setupGrid
        g1 = {'headers': [1,2,3,4,5],
              'rowNames': [],
              'columnWidths': [2, 1, 1, 1, 1]}

        #this uses a generic units table

        for tag in soup.find_all():
            row = 0
            hint = "".join(tag.findAll(text=True))

            #the tag name is the main label
            if tag.parent.name not in ['component', 'childOf', 'type','[document]']:
                parent = tag.parent.name
                pt = '.'.join([parent, tag.name])
            else:
                pt = tag.name
            g1['rowNames'].append(pt)

            #create the overall label
            g1[pt] = {1:{'widget':'lbl','name':tag.name}}
            column = 1

            for a in tag.attrs:

                name = '.'.join([pt,str(a)])
                inputValue = tag[a]

                #columns aways starts populating at 2
                if a != 'choices':

                    if column <=4:
                       column+=1
                    else:
                        #start populating a new data input row
                       column = 2
                       row+=1

                    widget = 'txt'
                    items = None
                    #We don't want names to be editable so if its a name tag then it gets set as a label
                    if a == 'name':
                        widget ='lbl'
                    #if setting units attribute use a combo box
                    if 'choices' in tag.attrs:
                        widget = 'combo'
                        items = tag['choices'].split(' ')

                    #if the value is set to true false use a checkbox
                    if a == 'active':
                        widget = 'chk'
                    if a == 'mode':
                        widget = 'txt'
                        items = None
                #first column is the label
                    #don't show the labe if it is value
                    if a == 'value':
                        g1[pt][column] = {'widget': 'lbl', 'name': 'lbl' + a,
                                          'hint': hint}
                    else:
                        g1[pt][column] = {'widget': 'lbl', 'name': 'lbl' + a, 'default': a,
                                                           'hint': hint}

                    column+=1

                    if items is None:
                        g1[pt][column] = {'widget': widget, 'name': name, 'default': inputValue,
                                                               'hint': hint}
                    else:
                        g1[pt][column] = {'widget': widget, 'name': name, 'default': inputValue,
                                                               'items': items, 'hint': hint}

        #make the grid layout from the dictionary
        grid = setupGrid(g1)
        #add the grid to the parent layout
        self.addLayout(grid)

        return

    # updates the soup to reflect changes in the form
    # None->Soup, Dictionary
    def extractValues(self):

        # soup belongs to the layout object
        soup = self.soup
        changes = self.changes
        # for every tag in the soup fillSetInfo its value from the form
        for tag in soup.find_all():
            if tag.parent.name not in ['component', 'childOf', 'type', '[document]']:
                parent = tag.parent.name
                pt = '.'.join([parent, tag.name])
            else:
                pt = tag.name
            for a in tag.attrs:

                widget = self.findChild((QtWidgets.QLineEdit, QtWidgets.QComboBox, QtWidgets.QCheckBox),
                                        '.'.join([pt, str(a)]))

                if type(widget) == QtWidgets.QLineEdit:
                    if tag.attrs[a] != widget.text():
                        changes['.'.join([pt, str(a)])] = widget.text()
                        tag.attrs[a] = widget.text()

                elif type(widget) == QtWidgets.QComboBox:
                    if tag.attrs[a] != widget.currentText():
                        changes['.'.join([pt, str(a)])] = widget.currentText()
                        tag.attrs[a] = widget.currentText()

                elif type(widget) == QtWidgets.QCheckBox:

                    if (widget.isChecked()) & (tag.attrs[a] != 'TRUE'):
                        changes['.'.join([pt, str(a)])] = 'TRUE'
                        tag.attrs[a] = 'TRUE'
                    elif (not widget.isChecked()) & (tag.attrs[a] != 'FALSE'):
                        changes['.'.join([pt, str(a)])] = 'TRUE'
                        tag.attrs[a] = 'FALSE'

        return soup, changes

