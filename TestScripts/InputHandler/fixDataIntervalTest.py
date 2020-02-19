import unittest
import pandas as pd
import os
from MiGRIDS.InputHandler.fixBadData import fixBadData
from MiGRIDS.InputHandler.mergeInputs import mergeInputs
from MiGRIDS.InputHandler.fixDataInterval import fixDataInterval

class fixDataInterval_test(unittest.TestCase):

    def setUp(self):
        self.setupFolder = os.path.join(os.path.realpath(__file__),*['..','MiGRIDSProjects','MyProject','InputData','Setup'])
        self.inputDict = {'fileLocation': ['C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/HighRes', 'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/LowRes', 'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/RawWind'], 'timeZone': ['America/Anchorage', 'America/Anchorage', 'America/Anchorage'], 'fileType': ['CSV', 'CSV', 'MET'], 'outputInterval': ['30S'], 'outputIntervalUnit': ['S'], 'inputInterval': ['1min'], 'inputIntervalUnit': ['min'], 'runTimeSteps': ['2007-01-01', '2009-01-01'], 'dateColumnName': ['DATE', 'DATE', 'Date_&_Time_Stamp'], 'dateColumnFormat': ['YYYY-MM-DD', 'YYYY-MM-DD', 'YYYY-MM-DD'], 'timeColumnName': ['Date_&_Time_Stamp'], 'timeColumnFormat': ['HH:MM:SS', 'HH:MM:SS', 'HH:MM:SS'], 'utcOffsetValue': ['None', 'None', 'None'], 'utcOffsetUnit': ['hr'], 'dst': ['0', '0', '0'], 'flexibleYear': [False, False, False], 'columnNames': ['Villagekw', 'loadkw', 'CH3Avg'], 'componentUnits': ['kW', 'kW', 'm/s'], 'componentAttributes': ['P', 'P', 'WS'], 'componentNames': ['load0', 'load0', 'wtg0'], 'useNames': ['load0P', 'load0P', 'wtg0WS']}
        df, listOfComponents = mergeInputs(self.inputDict)
        minDate = min(df.index)
        maxDate = max(df.index)
        limiters = self.inputDict['runTimeSteps']

        if ((maxDate - minDate) > pd.Timedelta(days=365)) & (limiters == ['all']):
            newdates = self.DatesDialog(minDate, maxDate)
            m = newdates.exec_()
            if m == 1:
                # inputDictionary['runTimeSteps'] = [newdates.startDate.text(),newdates.endDate.text()]
                self.inputDict['runTimeSteps'] = [pd.to_datetime(newdates.startDate.text()),
                                                   pd.to_datetime(newdates.endDate.text())]

        # now fix the bad data
        self.df_fixed = fixBadData(df, self.setupFolder, listOfComponents, self.inputDict['runTimeSteps'])
    def tearDown(self):
        # if we don't get rid of attributes the memory will fail
        del self.setupFolder
        del self.inputDict
        del self.df_fixed

    def test_mixedUpDownSample(self):
        # input is in various timesteps, output should be 30 seconds
        self.inputDict['outputInterval'] = '30s'
        df_fixed_interval = fixDataInterval(self.df_fixed, self.inputDict['outputInterval'])
        df1 = df_fixed_interval.fixed[0]
        timediff = pd.Series(pd.to_datetime(df1.index, unit='s'), index=df1.index)
        self.assertEqual(max(timediff), min(timediff))


    '''def test_UpSample(self):

        self.assertEqual(True, True)

    def test_DownSample(self):
        self.assertEqual(True, True)'''

if __name__ == '__main__':
    unittest.main()
