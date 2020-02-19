import unittest
from MiGRIDS.InputHandler.readWindData import readWindData
from MiGRIDS.InputHandler.readWindData import WindRecord

class ReadWindDataTest(unittest.TestCase):
    def setUp(self):
        self.inputDict = {'fileLocation':
                        'C:/Users/tmorga22/Documents/MiGRIDS/MiGRIDSProjects/MyProject/InputData/TimeSeriesData/RawData/RawWind',
                          'dateColumnFormat':'YYYY-MM-DD',
                          'timeColumnFormat': 'HH:MM:SS',
                          'fileType': 'MET', 'outputInterval': '30S', 'outputIntervalUnit': 'S',
                            'columnNames': ['CH3Avg'],
                          'dateColumnName': 'Date_&_Time_Stamp',
                          'timeColumnName': 'Date_&_Time_Stamp',
                          'useNames': ['wtg0WS'],
                          'timeZone': 'America/Anchorage',
                          'utcOffsetUnit': 'hr', 'dst': '0',
                          }

        return

    def test_WindRecord(self):
        myRecord = WindRecord(25, 250, 0, 20)
        self.assertEqual(myRecord.getDatetime(), None)
        self.assertEqual(myRecord.sigma,25)

    def test_readWindData(self):
        filedict, winddf = readWindData(self.inputDict)
        #9 is the value of the first record read, 8 is the column for wtg0WS
        self.assertEqual(winddf.iloc[0,8], 9)

if __name__ == '__main__':
    unittest.main()
