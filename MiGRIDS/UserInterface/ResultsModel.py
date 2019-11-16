from PyQt5 import QtSql


from MiGRIDS.Controller.RunHandler import RunHandler
from MiGRIDS.UserInterface.ModelRunTable import RunFields
from MiGRIDS.UserInterface.ResultsPlot import ResultsPlot
from MiGRIDS.UserInterface.getFilePaths import getFilePath


class ResultsModel(ResultsPlot):
    '''Class for plotting results of model simulation runs. Displayed within the 'model' containiner form
'''

    def defaultDisplay(self):
        return


    def defaultPlot(self):
        # combo boxes need to be set with field options
        # x can be any tag that was changed
        # y is any metadata value
        #optionsX = self.dbhandler.setComponentTag(1)  # TODO this needs to be the setID

        self.setPlotData(self.getData())
        if self.data is not None:
            self.displayData = self.defaultDisplay()
            self.plotWidget.makePlot(self.displayData)
        return

    def makePlotArea(self):
        optionsX = QtSql.QSqlQueryModel()
        strsql = "SELECT " \
                      "group_concat(set_name ||' ' || componentnamevalue ||'.' || tag) from run_attributes " \
                      "JOIN set_components ON set_components._id = run_attributes.set_component_id " \
                      "JOIN component on set_components.component_id = component._id "\
                      "JOIN set_ on set_components.set_id = set_._id"

        optionsX.setQuery(strsql)
        optionsX.query()
        r = optionsX.rowCount()

        optionsY = [name for name, member in RunFields.__members__.items()][6:]
        self.set_XCombo(optionsX)
        self.set_YCombo(optionsY)

    def setPlotData(self, data):
        '''sets the data attribute'''
        self.data = data
        return


    def getData(self):
        tag = self.getSelectedX()
        metric = self.getSelectedY()
        #x is values for tag changes
        data = self.getXYData(tag,metric)
        data = self.validate(data)
        return data

    def validate(self,dataDict):
        handler = RunHandler()

        def lookup(v, runfolder):
            if not handler.isTagReferenced(v):
                return v
            else:
                return handler.getReferencedValue(v,runfolder)[0]

        def fixReferenced(k):
            '''converts tag refenced values in x lists for each series in the data dictionary to actual numbers '''
            x = dataDict[k]['x']
            runFolder = self.getRunFolder(k)
            trueX = [lookup(i,runFolder) for i in x]
            dataDict[k]['x'] = trueX
        if dataDict is not None:
            [fixReferenced(d) for d in dataDict.keys()]
        return dataDict

    def getRunFolder(self,setRun):
        import re
        setName = setRun.split(' ')[0]

        runName = setRun.split(' ')[1]
        projectDir = self.dbhandler.getProjectPath()
        setDir = getFilePath(setName,projectFolder=projectDir)
        runDir = getFilePath(runName, set=setDir)
        return runDir
    def refreshPlot(self):
        super(ResultsModel, self).refreshPlot()
        self.makePlotArea()

    def getXYData(self,tag,metric):
        if (tag =='')|(metric==''):
            return
        else:
            return self.dbhandler.getRunXYValues(tag,metric) #[run1:40,run2:100,run3:20]


    def revalidate(self):
        return True