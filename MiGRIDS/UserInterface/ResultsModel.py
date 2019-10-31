from PyQt5 import QtWidgets,QtSql

from MiGRIDS.UserInterface.ModelRunTable import RunFields
from MiGRIDS.UserInterface.ResultsPlot import ResultsPlot


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
        optionsX = QtSql.QSqlQueryModel()
        strsql = "SELECT " \
                      "group_concat(set_name ||' ' || componentnamevalue ||'.' || tag) from run_attributes " \
                      "JOIN set_components ON set_components._id = run_attributes.set_component_id " \
                      "JOIN component on set_components.component_id = component._id "\
                      "JOIN set_ on set_components.set_id = set_._id"

        optionsX.setQuery(strsql)
        optionsX.query()

        optionsY = [name for name, member in RunFields.__members__.items()][6:]
        self.set_XCombo(optionsX)
        self.set_YCombo(optionsY)

        if self.data is not None:

            self.displayData = self.defaultDisplay()
            self.plotWidget.makePlot(self.displayData)
        return


    def setPlotData(self, data):
        '''sets the data attribute'''
        return





    def revalidate(self):
        return True