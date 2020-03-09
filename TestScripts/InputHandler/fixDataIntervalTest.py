import unittest
import pickle
from MiGRIDS.InputHandler.DataClass import DataClass
from MiGRIDS.InputHandler.fixDataInterval import *


class fixDataInterval_test(unittest.TestCase):

    def setUp(self):
        tsIndex = pd.date_range('2019-01-01 00:00:00',periods=4, freq = 'H')
        self.c1 = [100,300,800,700]
        self.c2 = [100,200,300,400]
        self.e1 = [1000,550,1300,890]
        self.df = pd.DataFrame({'c1':self.c1,'c2':self.c2,'e1':self.e1},index=tsIndex)
        self.testSeries = pd.Series(self.c1,index=tsIndex)

    def test_getValues(self):
        start = self.testSeries
        sigma = self.testSeries.shift(-1)
        sigma = sigma.ffill()
        t,k = getValues(start,sigma)
        self.assertEqual(len(k),(len(start)* 60 *60 + len(start)))
        self.assertTrue(np.isnan(k[-10])) #final values are na
    def test_estimateDistribution(self):
        start = self.testSeries
        sigma = self.testSeries.shift(-1)
        sigma = sigma.ffill()
        t, k = estimateDistribution(start, sigma)
        self.assertEqual(len(k), (len(start) * 60 * 60 + len(start)))
        self.assertTrue(np.isnan(k[-10]))  # final values are na
        self.assertEqual(len(k),len(t))
    def test_upsample_test(self):
        start = self.testSeries
        sigma = self.testSeries.shift(-1)
        sigma = sigma.ffill()
        simulatedSeries = upsample(start,sigma)
        self.assertTrue(isinstance(simulatedSeries,pd.Series))
        self.assertEqual(len(simulatedSeries),(len(start) -1) * 60 * 60 + 1) #na's for final interval get dropped
    def test_fixSeriesInterval(self):
        start = self.testSeries
        interval = pd.to_timedelta('1 s') #1 second is standard timestep
        reSampled = start.resample(interval).mean()

        simulatedSeries = fixSeriesInterval(start,reSampled,interval)
        self.assertTrue(len(simulatedSeries),(len(start) * 60 * 60 + len(start)))
        self.assertTrue(len(pd.isnull(simulatedSeries)),0)

        interval = pd.to_timedelta('1 m') #test with larger timestep
        reSampled = start.resample(interval).mean()
        simulatedSeries = fixSeriesInterval(start, reSampled, interval)
        self.assertTrue(len(simulatedSeries), (len(start) * 60 * 1 + len(start)))
        self.assertTrue(len(pd.isnull(simulatedSeries)), 0)

        interval = pd.to_timedelta('2 h')  # downsample
        reSampled = start.resample(interval).mean()
        simulatedSeries = fixSeriesInterval(start, reSampled, interval)
        self.assertTrue(len(simulatedSeries), len(start)/2) #initial intervals are 1 hour so we are downsampling by 2
        self.assertTrue(len(pd.isnull(simulatedSeries)), 0)
    def test_spreadFixedSeries(self):
        df = self.df
        df['c3'] = df['c1'] + df['c2']
        df.loc['2019-01-01 01:00:00', 'c1'] = np.nan
        df.loc['2019-01-01 02:00:00', 'c2'] = np.nan
        newdf = spreadFixedSeries('c3',['c1','c2'],df)
        self.assertEqual(newdf.loc['2019-01-01 01:00:00','c1'],250)
        self.assertEqual(newdf.loc['2019-01-01 02:00:00', 'c2'], 440)
    def test_truncateDataFrame_test(self):
        df = self.df
        newdf = truncateDataFrame(df) #test with no nas
        self.assertTrue(newdf.first_valid_index() == pd.to_datetime('2019-01-01 00:00:00'))
        self.assertTrue(newdf.last_valid_index() == pd.to_datetime('2019-01-01 03:00:00'))

        df.loc['2019-01-01 01:00:00', 'c1'] = np.nan
        newdf = truncateDataFrame(df) #with na
        self.assertTrue(newdf.first_valid_index() == pd.to_datetime('2019-01-01 02:00:00'))
        self.assertTrue(newdf.last_valid_index() == pd.to_datetime('2019-01-01 03:00:00'))


        df.loc['2019-01-01 02:00:00', 'c2'] = np.nan
        newdf = truncateDataFrame(df)  # multiple na's resulting in multiple dataframes of same size
        self.assertTrue(newdf.first_valid_index() == pd.to_datetime('2019-01-01 03:00:00'))  #last df is returned
        self.assertTrue(newdf.last_valid_index() == pd.to_datetime('2019-01-01 03:00:00'))
    def test_fixDataFrameInterval(self):
        interval = pd.to_timedelta('1 s')
        df = self.df
        df['total_load'] = df['c1'] + df['c2']
        newdf = fixDataFrameInterval(df,interval,['e1','total_load'],['c1','c2'],[])
        self.assertTrue(len(newdf[pd.isnull(newdf).any(axis=1)])==0)
        self.assertEqual(len(newdf),(len(self.df) -1) * 60 * 60 + 1)

        interval = pd.to_timedelta('1 m')
        newdf = fixDataFrameInterval(df, interval, ['e1', 'total_load'], ['c1', 'c2'], [])
        self.assertTrue(len(newdf[pd.isnull(newdf).any(axis=1)]) == 0)
        self.assertEqual(len(newdf), (len(self.df) - 1) * 60  + 1)

        interval = pd.to_timedelta('2 h')
        newdf = fixDataFrameInterval(df, interval, ['e1', 'total_load'], ['c1', 'c2'], [])
        self.assertTrue(len(newdf[pd.isnull(newdf).any(axis=1)]) == 0)
        self.assertTrue(len(newdf) == (len(self.df) / 2))
    def test_fixDataInterval(self):
        #with 1 dataframe
        raw_df = self.df
        df = self.df
        df['total_load'] = df['c1'] + df['c2']
        dc = DataClass(raw_df)
        dc.fixed = [df]
        dc.loads = ['c1','c2']
        dc.powerColumns = []
        # upsample to 1 sec
        interval = pd.to_timedelta('1 s')
        newdc = fixDataInterval(dc,interval)

        self.assertTrue(len(newdc.fixed) == 1)
        self.assertTrue(len(newdc.fixed[0]) == (len(self.df) -1) * 60 * 60 + 1)

        #with 2 dataframe
        df2 = df.copy()
        df2.loc['2019-01-01 02:00:00', 'total_load'] = np.nan
        dc = DataClass(raw_df)
        dc.fixed = [df,df2]
        dc.loads = ['c1', 'c2']
        dc.power = []
        interval = pd.to_timedelta('1 s')
        newdc = fixDataInterval(dc, interval)

        self.assertTrue(len(newdc.fixed) == 2) #
        self.assertTrue(len(newdc.fixed[0]) == (len(self.df) - 1) * 60 * 60 + 1)
        self.assertTrue(len(newdc.fixed[1]) == (len(self.df) - 1) * 60 * 60 + 1)
        #upsample to 1 min
        interval = pd.to_timedelta('1 m')
        dc = DataClass(raw_df)
        dc.fixed = [df, df2]
        dc.loads = ['c1', 'c2']
        dc.power = []
        newdc = fixDataInterval(dc, interval)
        self.assertTrue(len(newdc.fixed) == 2)  #
        self.assertTrue(len(newdc.fixed[0]) == (len(self.df) - 1) * 60  + 1)
        self.assertTrue(len(newdc.fixed[1]) == (len(self.df) - 1) * 60 + 1)
        #downsample to 2 hour
        interval = pd.to_timedelta('2 h')
        dc = DataClass(raw_df)
        dc.fixed = [df, df2]
        dc.loads = ['c1', 'c2']
        dc.power = []
        newdc = fixDataInterval(dc, interval)
        self.assertTrue(len(newdc.fixed) == 2)  #
        self.assertTrue(len(newdc.fixed[0]) == (len(self.df) /2))
        self.assertTrue(len(newdc.fixed[1]) == (len(self.df) /2))

    def test_fixDataIntervalHighLow(self):
        #read in df
        file = open("..\\..\\fixed_data.pkl",'rb')
        data = pickle.load(file)
        file.close()

        newdc = fixDataInterval(data, pd.to_timedelta('1 s'))
        self.assertTrue(len(newdc.fixed[0][pd.isnull(newdc.fixed[0]).any(axis=1)]) == 0)
        self.assertEqual(newdc.fixed[0].index[1]-newdc.fixed[0].index[0],pd.to_timedelta('1 s'))

        #with a bigger gap to fill
        file = open("..\\..\\fixed_data.pkl", 'rb')
        data = pickle.load(file)
        file.close()

        data.fixed[0].iloc[100:103]['wtg0WS'] = np.nan
        newdc = fixDataInterval(data, pd.to_timedelta('1 s'))
        self.assertTrue(len(newdc.fixed[0][pd.isnull(newdc.fixed[0]).any(axis=1)]) == 0)
        self.assertEqual(newdc.fixed[0].index[1] - newdc.fixed[0].index[0], pd.to_timedelta('1 s'))
        file = open("..\\..\\fixed_data.pkl", 'rb')
        data = pickle.load(file)
        file.close()
        newdc = fixDataInterval(data, pd.to_timedelta('300 s'))
        self.assertTrue(len(data.fixed[0] > len(newdc.fixed[0])))
        self.assertTrue(len(newdc.fixed[0][pd.isnull(newdc.fixed[0]).any(axis=1)]) == 0)
        self.assertEqual(newdc.fixed[0].index[1] - newdc.fixed[0].index[0], pd.to_timedelta('300 s'))
        self.assertEqual(newdc.fixed[0].index[12] - newdc.fixed[0].index[11], pd.to_timedelta('300 s'))


if __name__ == '__main__':
    unittest.main()
