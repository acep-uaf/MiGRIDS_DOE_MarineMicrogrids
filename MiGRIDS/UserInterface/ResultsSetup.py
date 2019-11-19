

from MiGRIDS.UserInterface.ResultsPlot import ResultsPlot
import pandas as pd

class ResultsSetup(ResultsPlot):

    #data object consisting of fixed and raw dataframes
    def defaultDisplay(self):

        displayData = {'raw': {'x':self.data['raw'].index, 'y':self.data['raw']['total_p']},
                       'fixed': {'x':self.data['fixed'].index, 'y':self.data['fixed'].total_p}
                       }
        return displayData

    def defaultPlot(self):
        if self.data is not None:
           # combo boxes need to be set with field options
            options = list(self.data['fixed'].columns.values)
            options.append('index')
            self.set_XCombo(options)
            self.set_YCombo(options)

            self.plotWidget.makePlot(self.getPlotData())

    def setData(self, data):
        '''sets the data attribute
        :param data [DataClass] is the data to be available for use in plots'''
        def mergedDF(lodf):
            df0 = lodf[0]
            for d in lodf[1:]:
                df0 = df0.append(d)
            return df0
        self.data = {'raw':data.raw,'fixed':mergedDF(data.fixed)}



    def getPlotData(self):
        xvalue = self.getSelectedX()
        yvalue = self.getSelectedY()
        def dropna():
            for k in list(data.keys()):
                if (all(pd.isnull(d) for d in data[k]['x'])) | (all(pd.isnull(d) for d in data[k]['y'])):
                    data.pop(k)

        if (xvalue == '') | (yvalue == '') | (self.data is None) :
            return {}
        if xvalue == 'index':
            data = {'raw': {'x': self.data['raw'].index, 'y': self.data['raw'][yvalue]},
                    'fixed': {'x': self.data['fixed'].index, 'y': self.data['fixed'][yvalue]}
                    }
        else:
            data = {'raw': {'x': self.data['raw'][xvalue], 'y': self.data['raw'][yvalue]},
                       'fixed': {'x': self.data['fixed'][xvalue], 'y': self.data['fixed'][yvalue]}
                       }
        dropna()
        return data

    def revalidate(self):
        return True