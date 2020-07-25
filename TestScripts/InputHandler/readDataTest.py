import unittest

from MiGRIDS.InputHandler.readData import readInputData


class readDataTest(unittest.TestCase):
    def setUp(self):
        self.inputDict = {'inputFileDir.value': ['C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/HighRes', 'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/LowRes', 'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/RawWind'], 'timeZone.value': ['America/Anchorage', 'America/Anchorage', 'America/Anchorage'], 'inputFileType.value': ['CSV', 'CSV', 'MET'], 'timeStep.value': ['30S'], 'timeStep.unit': ['S'], 'runTimeSteps.value': ['2007-01-01', '2009-01-01'], 'dateChannel.value': ['DATE', 'DATE', 'Date_&_Time_Stamp'], 'dateChannel.Format': ['YYYY-MM-DD', 'YYYY-MM-DD', 'YYYY-MM-DD'], 'timeChannel.value': ['Date_&_Time_Stamp'], 'timeChannel.Format': ['HH:MM:SS', 'HH:MM:SS', 'HH:MM:SS'], 'utcOffset.value': ['None', 'None', 'None'], 'utcOffset.unit': ['hr'], 'inputDST.value': ['0', '0', '0'], 'flexibleYear.value': [False, False, False], 'componentChannels.headerName.value': ['Villagekw', 'loadkw', 'CH3Avg'], 'componentChannels.componentAttribute.unit': ['kW', 'kW', 'm/s'], 'componentChannels.componentAttribute.value': ['P', 'P', 'WS'], 'componentChannels.componentName.value': ['load0', 'load0', 'wtg0']}

    def test_mergeHigh_LowRes(self):
        df, listOfComponents = readInputData(self.inputDict)

        #default scaling for windspeed is m/s * 1000
        #so althought the input is 9 it gets scaled to 9000 m/s to ensure it is an integer value (1000 = 1 m/s)
        self.assertEqual(df.loc['2007-11-15 09:00:00']['wtg0WS'],9000)
        self.assertTrue(len(df)==21124)
        self.assertTrue(len(listOfComponents)==2)
        self.assertListEqual(['load0','wtg0'],[ c.component_name for c in listOfComponents])


if __name__ == '__main__':
    unittest.main()
