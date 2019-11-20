from MiGRIDS.InputHandler import DataClass
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
        #The data class object can have lots of NA's in the raw data surrounded by actual values.
        #These NA's will not get plotted unless we use a fill method to create atleast 2 consecutive points.
        #Data flags create overlays
        xvalue = self.getSelectedX()
        yvalue = self.getSelectedY()
        FLAGCOLORS = {1:(0.1,0.2,0.5,0.8),
                      2:(0.1,0.3,0.5,0.8),
                      3:(0.2, 0.25, 0.40,0.7),
                      4:(0.1, 0.0, 0.60,0.7)}
        def makeFlagOverlays():
            overlays={}
            if 'dataflag' in self.data['fixed'].columns:
                for s in set(self.data['fixed']['dataflag']):
                    if(xvalue == 'index'):
                        overlays[DataClass.getFlagName(s)] = {
                            'x': self.data['fixed'].index[self.data['fixed']['dataflag'] == s],
                            'y': self.data['fixed'][yvalue][self.data['fixed']['dataflag'] == s],
                            'color': FLAGCOLORS[s]}
                    else:
                        overlays[DataClass.getFlagName(s)] = {'x':self.data['fixed'][xvalue][self.data['fixed']['dataflag'] == s],
                                                          'y':self.data['fixed'][yvalue][self.data['fixed']['dataflag']==s],
                                                              'color':FLAGCOLORS[s]}
            return overlays
        def dropna():
            for k in list(data.keys()):
                if (all(pd.isnull(d) for d in data[k]['x'])) | (all(pd.isnull(d) for d in data[k]['y'])):
                    data.pop(k)

        if (xvalue == '') | (yvalue == '') | (self.data is None) :
            return {}
        if xvalue == 'index':
            data = {'raw': {'x': self.data['raw'].index, 'y': self.data['raw'][yvalue].fillna(method ='pad',limit=1),'color':'red'},
                    'fixed': {'x': self.data['fixed'].index, 'y': self.data['fixed'][yvalue],'color':(0.0, 0.04, 0.96,0.9)}

                    }
        else:
            data = {'raw': {'x': self.data['raw'][xvalue], 'y': self.data['raw'][yvalue],'color':'red'},
                       'fixed': {'x': self.data['fixed'][xvalue], 'y': self.data['fixed'][yvalue],'color':(0.0, 0.04, 0.96,0.9)}
                       }
        data.update(makeFlagOverlays())
        #dropna()
        return data

    def revalidate(self):
        return True