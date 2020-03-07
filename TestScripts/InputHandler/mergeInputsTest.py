import unittest
from MiGRIDS.InputHandler.mergeInputs import mergeInputs


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.inputDict = {'fileLocation': ['C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/HighRes', 'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/LowRes', 'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/RawWind'], 'timeZone': ['America/Anchorage', 'America/Anchorage', 'America/Anchorage'], 'fileType': ['CSV', 'CSV', 'MET'], 'outputInterval': ['30S'], 'outputIntervalUnit': ['S'], 'inputInterval': ['1min'], 'inputIntervalUnit': ['min'], 'runTimeSteps': ['2007-01-01', '2009-01-01'], 'dateColumnName': ['DATE', 'DATE', 'Date_&_Time_Stamp'], 'dateColumnFormat': ['YYYY-MM-DD', 'YYYY-MM-DD', 'YYYY-MM-DD'], 'timeColumnName': ['Date_&_Time_Stamp'], 'timeColumnFormat': ['HH:MM:SS', 'HH:MM:SS', 'HH:MM:SS'], 'utcOffsetValue': ['None', 'None', 'None'], 'utcOffsetUnit': ['hr'], 'dst': ['0', '0', '0'], 'flexibleYear': [False, False, False], 'columnNames': ['Villagekw', 'loadkw', 'CH3Avg'], 'componentUnits': ['kW', 'kW', 'm/s'], 'componentAttributes': ['P', 'P', 'WS'], 'componentNames': ['load0', 'load0', 'wtg0'], 'useNames': ['load0P', 'load0P', 'wtg0WS']}

    def test_mergeHigh_LowRes(self):
        df, listOfComponents = mergeInputs(self.inputDict)
        print(df.head())
        #default scaling for windspeed is m/s * 1000
        #so althought the input is 9 it gets scaled to 9000 m/s (not sure why 1000 was chosen)
        self.assertEqual(df.loc['2007-11-15 09:00:00']['wtg0WS'],9000)
        self.assertTrue(len(df)==21124)
        self.assertTrue(len(listOfComponents)==2)
        self.assertListEqual(['load0','wtg0'],[ c.component_name for c in listOfComponents])

if __name__ == '__main__':
    unittest.main()
