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

        self.setData(self.getPlotData())
        if self.data is not None:
            self.displayData = self.defaultDisplay()
            self.plotWidget.makePlot(self.displayData)
        return

    def makePlotArea(self):
        optionsX = QtSql.QSqlQueryModel()
        strsql = "SELECT " \
                      "set_name ||' ' || componentnamevalue ||'.' || tag from run_attributes " \
                      "JOIN set_components ON set_components._id = run_attributes.set_component_id " \
                      "JOIN component on set_components.component_id = component._id "\
                      "JOIN set_ on set_components.set_id = set_._id GROUP BY set_name, componentnamevalue, tag"

        optionsX.setQuery(strsql)
        optionsX.query()


        optionsY = [name for name, member in RunFields.__members__.items()][6:]
        self.set_XCombo(optionsX)
        self.set_YCombo(optionsY)
        return

    def setData(self, data):
        '''sets the data attribute'''
        self.data = data
        return


    def getPlotData(self):
        tag = self.getSelectedX()
        metric = self.getSelectedY()
        #x is values for tag changes
        data = self.getXYData(tag,metric)
        data =self.validate(data)

        return data

    def validate(self,dataDict):
        #TODO implement further tests
        starter = 0
        if dataDict is not None:
            for k in dataDict.keys():
                if 'color' not in dataDict[k].keys():
                    dataDict[k]['color'] = self.pickColor(starter)
                    starter += 1
                if 'x' not in dataDict[k].keys():
                    return {}
                if 'y' not in dataDict[k].keys():
                    return {}

        return dataDict

    def getRunFolder(self,setRun):

        setName = setRun.split(' ')[0]

        runName = setRun.split(' ')[1]
        projectDir = self.dbhandler.getProjectPath()
        setDir = getFilePath(setName,projectFolder=projectDir)
        runDir = getFilePath(runName, set=setDir)
        return runDir

    def refreshPlot(self):
        super(ResultsModel, self).refreshPlot()


    def getXYData(self,tag,metric):
        if (tag =='')|(metric==''):
            return
        else:
            return self.dbhandler.getRunXYValues(tag,metric) #[run1:40,run2:100,run3:20]



    def revalidate(self):
        return True