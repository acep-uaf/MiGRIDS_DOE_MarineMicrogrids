from PyQt5 import QtWidgets, QtCore, QtGui


class FormContainer(QtWidgets.QWidget):
    #if the screen is big enough show input and results
    #if its not very big show input and results on seperate tabs
    def __init__(self, parent, widgetList,name,**kwargs):
        super().__init__(parent)
        self.widgetList = widgetList
        self.screen = kwargs.get("screen")
        if self.screen == None:
            self.screen = self.window().geometry()
        self.initUI(name)

    def initUI(self,name):
        self.setObjectName(name)
        #layout changes dependent on screen width
        self.correctLayout(self.screen)

    def correctLayout(self,myGeom):
        self.screen = myGeom
        layout = QtWidgets.QHBoxLayout(self)
        if self.screen.width() > 2000:
            self.setLayout(self.untabLayout(layout))
        else:
            if not self.isTabbed():
                l = self.tabifyLayout(layout)

                self.setLayout(l)

        return

    def isTabbed(self):
         '''
         Identifies whether or not the current layout is tabbed
         :return: Boolean, true if the layout has seperate tabs for input and results
         '''
         tabs = self.findChildren(QtWidgets.QTabWidget)

         return (len(tabs) > 0) & (self.widgetList[0] in tabs)

    def untabLayout(self,layout):
        '''
        Creates a un-tabbed layout for input and result widgets
        :return un-tabbed layout with input and result widgets side by side
        '''
        for l in self.widgetList:
            widgAttr = l.__dict__
            layout.addWidget(l)
            l.__dict__.update(**widgAttr)

        return layout

    def tabifyLayout(self,layout):
        '''
        Creates a tabbed layout for input and result widgets
        :return: tabbed layout
        '''
        tabArea = QtWidgets.QTabWidget(self)
        for l in self.widgetList:
            widgAttr = l.__dict__
            tabArea.addTab(l, l.objectName())
            l.__dict__.update(**widgAttr)
        layout.addWidget(tabArea)

        return layout

    def changeLayout(self,newGeom):
        if self.screen.width() != newGeom.width():
            self.screen = newGeom
            #each page has 2 main widgets that need to be either tabbed or sidebyside
            layout = self.layout()
            for c in self.widgetList:
                layout.removeWidget(c)
            del layout
            self.correctLayout(self.screen)



