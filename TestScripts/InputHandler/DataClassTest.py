import unittest

import shutil

from MiGRIDS.InputHandler.Component import Component
from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor
from MiGRIDS.InputHandler.fixBadData import *
from MiGRIDS.InputHandler.isInline import *
from MiGRIDS.InputHandler.makeSoup import makeComponentSoup
from MiGRIDS.InputHandler.DataClass import DataClass

class DataClass_test(unittest.TestCase):

    def setUp(self):
        self.comps = [Component(column_name=n, component_name=n[0:4], attribute='P') for n in ['wtg0P', 'gen0P']] + [Component(column_name='load0P',component_name='load0',attribute='P'),
                      Component(column_name='wtg1WS',component_name='wtg1',attribute='WS')
                      ]
        self.setupProject(self.comps)
        self.df = self.createComponentDataframe(self.comps)

        return
    def setupProject(self, comps):
        if os.path.isdir("testProject"):
            shutil.rmtree("testProject")
        os.mkdir("testProject")
        os.mkdir("testProject//InputData")
        os.mkdir("testProject//InputData//Setup")
        os.mkdir("testProject//InputData//Components")
        self.setupFolder = "testProject//InputData//Setup"

        self.compFolder = "testProject//InputData//Components"
        for c in comps:
            s = makeComponentSoup(c.component_name, self.compFolder)
            createComponentDescriptor(c.component_name, self.compFolder, s)

    def createComponentDataframe(self,comps):
        #self.setupProject(comps)
        tsIndex = pd.date_range('2019-01-01 00:00:00', periods=10, freq='H')
        df = pd.DataFrame(index=tsIndex)
        for c in comps:
            descriptorxmlpath = os.path.join(self.setupFolder, '..', 'Components', ''.join([c.component_name, "Descriptor.xml"]))
            descriptorxml = ET.parse(descriptorxmlpath)
            sink = descriptorxml.find('type').attrib.get('value')
            if sink == 'sink':
                high = descriptorxml.find("PInMaxPa").attrib.get('value')
                low = descriptorxml.find("POutMaxPa").attrib.get('value')

            else:
                high = descriptorxml.find("POutMaxPa").attrib.get('value')
                low = descriptorxml.find("PInMaxPa").attrib.get('value')
            if low >= high:
                high = int(high) + 100
            cs = pd.Series(np.random.randint(int(low),int(high),len(df.index)), index = tsIndex)
            cs.name = c.column_name
            df = pd.concat([df,cs],axis=1)
        return df
    def createMultiYearComponentDataframe(self,comps):
        #self.setupProject(comps)
        #two year dataframe
        tsIndex = pd.date_range('2019-01-01 00:00:00', '2021-01-01 00:00:00', freq='H')
        df = pd.DataFrame(index=tsIndex)

        for c in comps:
            descriptorxmlpath = os.path.join(self.setupFolder, '..', 'Components', ''.join([c.component_name, "Descriptor.xml"]))
            descriptorxml = ET.parse(descriptorxmlpath)
            sink = descriptorxml.find('type').attrib.get('value')
            if sink == 'sink':
                high = descriptorxml.find("PInMaxPa").attrib.get('value')
                low = descriptorxml.find("POutMaxPa").attrib.get('value')

            else:
                high = descriptorxml.find("POutMaxPa").attrib.get('value')
                low = descriptorxml.find("PInMaxPa").attrib.get('value')
            if low >= high:
                high = int(high) + 100
            low = int(low)+1
            cs = pd.Series(np.random.randint(int(low),int(high),len(df)), index = df.index)
            cs.name = c.column_name
            df = pd.concat([df,cs],axis=1)
            df.loc['2019-03-01 00:00:00':'2019-05-01 00:00:00', 0:] = np.nan  # Get rid of march and april 2019
            df.loc['2020-12-01 00:00:00':'2020-12-31 00:00:00', 0:] = np.nan  # get rid fo december 2020
            df = df[pd.notnull(df).all(axis=1)]
        return df
    def tearDown(self):
        if os.path.isdir("testProject"):
            shutil.rmtree("testProject")
        return

    def test_init(self):
        df = self.df.copy()
        D = DataClass(df)
        self.assertEqual(len(D.df),len(df))
        self.assertEqual(D.badDataDict,{})
        self.assertEqual(D.fixed,[])
        self.assertEqual(len(D.df[pd.isnull(D.df[TOTALL])]), len(df))
        self.assertEqual(len(D.df[pd.isnull(D.df[TOTALP])]), len(df))
        self.assertTrue(isinstance(D.df.index, pd.DatetimeIndex))
    def test_splitDataFrame(self):
        df = self.df.copy()
        df.iloc[3:5, 0:] = np.nan
        D = DataClass(df)
        D.splitDataFrame()
        self.assertTrue(len(D.fixed),2)
    def test_fixGen(self):
        clist = [c.component_name for c in self.comps]
        #fixGen()
        self.assertTrue(False)
        return
    def test_totalPower(self):
        df = self.df.copy()
        D = DataClass(df)
        D.powerComponents = ['wtg0P']
        D.totalPower()
        self.assertTrue(len(D.df[pd.isnull(D.df[TOTALP])])== 0)

        df['gen1P'] = df['wtg0P'] #add a P column with some na
        df.loc[3:5,'gen1P'] = np.nan
        D = DataClass(df)
        D.powerComponents = ['wtg0P','gen1P']
        D.totalPower() #even though gen has some na, total p will sum to wtgp for those rows
        self.assertTrue(len(D.df[pd.isnull(D.df[TOTALP])])== 0)
        self.assertEqual(D.df.iloc[3,][TOTALP], D.df.iloc[3,]['wtg0P'])

        df.iloc[3:5, 0:] = np.nan
        D = DataClass(df)
        D.powerComponents = ['wtg0P', 'gen1P']
        D.totalPower()
        self.assertTrue(len(D.df[pd.isnull(D.df[TOTALP])])==2)
    def test_totalLoad(self):
        df = self.df.copy()
        D = DataClass(df)

        D.loads = ['load0P']
        D.totalLoad()
        self.assertTrue(len(D.df[pd.isnull(D.df[TOTALL])]) == 0)

        df['load2P'] = df['load0P']  # add a P column with some na
        df.loc[3:5, 'load2P'] = np.nan
        D = DataClass(df)
        D.loads = ['load0P','load2P']
        D.totalLoad()  # even though gen has some na, total p will sum to wtgp for those rows
        self.assertTrue(len(D.df[pd.isnull(D.df[TOTALL])]) == 0)
        self.assertEqual(D.df.iloc[3,][TOTALL], D.df.iloc[3,]['load0P'])

        df.iloc[3:5, 0:] = np.nan
        D = DataClass(df)
        D.loads = ['load0P', 'load2P']
        D.totalLoad()
        self.assertTrue(len(D.df[pd.isnull(D.df[TOTALL])]) == 2)
    def test_yearlyBreakdown(self):
        df = self.createMultiYearComponentDataframe(self.comps)
        D = DataClass(df)
        D.setYearBreakdown()
        self.assertEqual(D.yearBreakdown.iloc[0,:]['last'],pd.Timestamp('2019-12-31 23:00:00'))
        self.assertEqual(D.yearBreakdown.iloc[1,:]['last'],pd.Timestamp('2020-12-31 23:00:00'))
    def test_fixOfflineData(self):
        df = self.createMultiYearComponentDataframe(self.comps)
        df.loc['2020-09-01 00:00:00':'2020-09-02 00:00:00', 0:] = np.nan  # target 1 day of missing data
        D = DataClass(df)
        D.powerComponents = ['wtg0P','gen0P']
        D.loads = ['load0P']
        D.totalPower()
        D.totalLoad()
        D.setYearBreakdown()
        columns = D.ecolumns + [TOTALL] + [TOTALP]
        groupings = D.df[columns].apply(lambda c: isInline(c), axis=0)
        #missing day from september needs to be replaced
        reps = D.fixOfflineData('total_power',D.powerComponents + ['total_power'],groupings[TOTALP])
        self.assertTrue(len(reps['2020-09-01 00:00:00':'2020-09-02 00:00:00'][pd.isnull(reps['total_power'])]) <=0)
        self.assertTrue(len(reps['2020-09-01 00:00:00':'2020-09-02 00:00:00'][pd.isnull(reps['wtg0P'])]) <= 0)

    #test for inline methods
    def test_checkDataGaps(self):
        s = self.df['wtg0P']
        s.loc[2:5] = np.nan
        s = s[pd.notnull(s)]
        newS = checkDataGaps(s)
        self.assertTrue(len(self.df['wtg0P'])==len(newS))
        self.assertTrue(len(s) < len(newS))
        self.assertTrue(len(newS[pd.isnull(newS)])==3)

        #fill in with additinal closer spaced values
        newI = newS.index.copy()
        newI = newI + pd.to_timedelta('4 s')
        secondS = pd.Series(self.df['wtg0P'].copy())
        secondS.index = newI
        s = pd.concat([self.df['wtg0P'].copy(),secondS],axis=0)
        s = s.sort_index(0, ascending=True)
        s.loc[2:7] = np.nan
        s=s[pd.notnull(s)]
        newS = checkDataGaps(s)
        self.assertTrue(len(s)<len(newS))
    def test_isInline(self):
        s = self.df['wtg0P'].copy()
        s.loc[2:5] = np.nan
        s.loc[7:9] = 0

        inline = isInline(s)
        self.assertEqual(inline.iloc[0],inline.iloc[1],inline.iloc[2])
        self.assertEqual(inline.iloc[3],inline.iloc[4])
        self.assertEqual(len(inline), 5)
        #multiyear
        df = self.createMultiYearComponentDataframe(self.comps)
        df = df['2019-04-01 00:00:00':'2020-05-15 22:00:00']
        df['2020-05-01 00:00:00':'2020-05-01 22:00:00']['wtg0P'] = np.nan  # 1 day
        df['2020-08-01 00:00:00':'2020-08-01 00:10:00']['wtg0P'] = np.nan  # 1 hour
        df['2019-05-01 00:00:00':'2019-05-04 00:00:00']['wtg0P'] = np.nan  # 4 days missing values #these won't get filled because they are at beginning of dataset
        c = df['wtg0P'].copy()
        inline =  isInline(c)
        self.assertEqual(inline['2020-05-01 00:00:00':'2020-05-01 22:00:00'].tolist()[0],inline['2020-05-01 00:00:00':'2020-05-01 22:00:00'].tolist()[-1])
        self.assertTrue(len(inline['2019-05-01 00:00:00':'2019-05-04 00:00:00'])==0)

        # multiyear
        df = self.createMultiYearComponentDataframe(self.comps)
        df = df['2019-04-01 00:00:00':'2020-05-15 22:00:00']
        df['2020-05-01 00:00:00':'2020-05-01 22:00:00']['wtg0P'] = np.nan  # 1 day
        df['2020-08-01 00:00:00':'2020-08-01 00:10:00']['wtg0P'] = np.nan  # 1 hour
        df['2019-05-01 00:00:00':'2019-05-04 00:00:00'][
            'wtg0P'] = np.nan  # 4 days missing values #these won't get filled because they are at beginning of dataset
        #artificially give starting value a value so missing na's will be filled
        df.loc['2019-05-01 00:00:00':'2019-05-01 01:00:00']['wtg0P'] = 50.0
        c = df['wtg0P'].copy()
        inline = isInline(c)
        self.assertEqual(inline['2019-05-01 00:02:00':'2019-05-01 22:00:00'].tolist()[0],
                         inline['2019-05-01 00:02:00':'2019-05-01 22:00:00'].tolist()[-1])
        self.assertTrue(len(inline['2019-05-01 00:00:00':'2019-05-04 00:00:00']) > 0)
    def test_removeChunk(self):
        df = self.df.copy()
        i1 = pd.to_datetime('2019-01-01 03:00:00')
        i2 = pd.to_datetime('2019-01-01 05:00:00')
        lod = removeChunk(df,i1,i2)

        self.assertTrue(len(lod)==2)
        self.assertEqual(pd.to_datetime(lod[0].index[0]),pd.to_datetime('2019-01-01 00:00:00'))
        self.assertEqual(pd.to_datetime(lod[0].index[-1]), pd.to_datetime('2019-01-01 02:00:00'))

        self.assertEqual(pd.to_datetime(lod[1].index[0]), pd.to_datetime('2019-01-01 06:00:00'))
        self.assertEqual(pd.to_datetime(lod[1].index[-1]), pd.to_datetime('2019-01-01 09:00:00'))

        self.assertEqual(lod[1].iloc[0]['wtg0P'], df['2019-01-01 06:00:00':]['wtg0P'][0])
        self.assertEqual(lod[0].iloc[0]['wtg0P'], df['2019-01-01 00:00:00':]['wtg0P'][0])
    def test_identifyCuts(self):
        df = self.df.copy()
        df.loc[2:3, 'wtg0P'] = np.nan
        lod = [df]

        cuts = identifyCuts(lod, 'wtg0P', pd.to_timedelta('1.5 h'), pd.Series())
        self.assertEqual(cuts.index[0],pd.to_datetime(lod[0].index[1]))
    def test_findValid(self):
        df = self.createMultiYearComponentDataframe(self.comps)
        df['2019-05-01 00:00:00':'2019-05-04 00:00:00']['wtg0P'] = np.nan #4 days missing values
        initialTs = pd.to_datetime('2019-05-01 00:00:00')
        d = pd.to_datetime('2019-05-04 00:00:00') - pd.to_datetime('2019-05-01 00:00:00')
        possibles = df['wtg0P']
        s =df['wtg0P']
        value = findValid(initialTs, d, possibles, s)
        self.assertTrue(value == pd.to_datetime('2019-01-01 00:00:00'))
        possibles2 = df['2019-02-27 00:00:00':]['wtg0P'] #first possible index is shortly before gap in data
        value = findValid(initialTs,d, possibles2, s)
        self.assertTrue(value == pd.to_datetime('2019-05-04 01:00:00')) #first possible with enough data to replace gap is after the month long data gap
    def test_listToDataframe(self):
        df = self.df.copy()
        lor = pd.DataFrame()
        lor['first']=pd.to_datetime(df.index[1])
        lor['last'] = pd.to_datetime(df.index[4])
        lor['replacementsStarts'] = pd.to_datetime(df.index[8])
        replacementSeries = df['wtg0P']

    def test_filteredTimes(self):
       '''filtered times compares t1 with a list of times to make sure they are the correct day'''
       t1 = pd.to_datetime('2019-04-01 00:00:00')
       testRange = pd.Series(pd.date_range(start = '2019-04-01 00:00:00',end = '2019-04-28 00:00:00',freq='h'))
       testRange.index = testRange
       filteredValues = filteredTimes(testRange,t1)
       self.assertTrue(len(testRange)>len(filteredValues))
    def test_calculateStarts(self):
        possibles = []
        smallBlock = True
        searchPoint = pd.to_datetime('2020-04-01 00:00:00')
        missingIndex = [pd.to_datetime('2019-04-01 00:00:00'),pd.to_datetime('2019-04-02 00:00:00')]
        searchIndex = pd.Series(pd.date_range(start = '2019-03-01 00:00:00',end = '2020-04-28 00:00:00',freq='h'))
        searchIndex.index = searchIndex
        filteredlist = calculateStarts(possibles, smallBlock, searchPoint, missingIndex, searchIndex)
        #filteredlist is a list of lists
        self.assertTrue(len(filteredlist) > 0)
        self.assertTrue(filteredlist[0][0] == searchPoint - pd.to_timedelta('3 h'))
    def test_getPossibleStarts(self):
        missingIndex = [pd.to_datetime('2019-04-01 00:00:00'), pd.to_datetime('2019-04-02 00:00:00')]
        searchIndex = pd.Series(pd.date_range(start='2019-03-01 00:00:00', end='2020-04-28 00:00:00', freq='h'))
        searchIndex.index = searchIndex

        possibleStarts = getPossibleStarts(missingIndex[0],missingIndex[1], searchIndex)
        self.assertTrue(len(possibleStarts[0]) < len(searchIndex))
        self.assertTrue(possibleStarts[0][0] == pd.to_datetime('2020-03-30 00:00:00'))
        self.assertTrue(possibleStarts[0][-1] == pd.to_datetime('2020-04-01 00:00:00'))
    def test_fixBadData(self):
         self.setupProject(self.comps)
         df = self.createMultiYearComponentDataframe(self.comps)
         df.loc['2020-05-01 00:0:00':'2020-05-02 22:00:00', :] = np.nan #over a full day missing
         df.loc['2020-08-01 00:00:00':'2020-08-01 10:00:00']['wtg0P'] = np.nan  # 10 hour - this won't get fixed because there is data in another power column
         data = DataClass(df)
         data.loads = ['load0P']
         data.powerComponents = ['wtg0P', 'gen0P']

         newData = fixBadData(data, self.setupFolder,
                              pd.to_timedelta('1 m'))

         self.assertTrue(len(newData.fixed) > 0)
         self.assertTrue(len(newData.badDataDict.keys()) >0) # = ['total_power', 'wtg0P', 'gen0P', 'total_load', 'load0P']
         self.assertTrue(pd.to_datetime('2020-05-01 00:0:00') in newData.badDataDict['total_power']['2.Offline'])
         self.assertTrue(len(newData.fixed[0]['2020-08-01 00:00:00':'2020-08-01 10:00:00'][pd.isnull(newData.fixed[0]['wtg0P'])]) > 0)
         self.assertTrue(len(newData.fixed[0]['2020-05-01 00:02:00':'2020-05-02 22:00:00'][pd.isnull(newData.fixed[0]['load0P'])]) <= 0)
    def test_quickReplace(self):
        df_to_fix = self.df.copy()
        replacementdf = df_to_fix.copy()
        offset = pd.to_timedelta('2 h')
        grouping = pd.Series([0,0,1,1,0,0,0,2,2,2])
        grouping.index = df_to_fix.index
        grouping.loc[grouping == 0] = np.nan
        newdf,badGroups = quickReplace(replacementdf,df_to_fix,offset,grouping)
        self.assertTrue(len(newdf)==len(df_to_fix))
        self.assertTrue(len(badGroups)==0)
        self.assertTrue(newdf.iloc[2,0] == df_to_fix.iloc[0,0])
    def test_doReplaceData(self):
        df = self.createMultiYearComponentDataframe(self.comps)
        df = df['2019-04-01 00:00:00':'2020-05-15 22:00:00']
        df['2020-05-01 00:0:00':'2020-05-01 22:00:00']['wtg0P'] = np.nan  # 1 day
        df['2020-08-01 00:00:00':'2020-08-01 00:10:00']['wtg0P'] = np.nan  # 1 hour
        df['2019-05-01 00:00:00':'2019-05-04 00:00:00']['wtg0P'] = np.nan  # 4 days missing values
        df.loc['2019-05-01 00:00:00':'2019-05-01 01:00:00']['wtg0P'] = 50.0
        inline = df.apply(lambda c: isInline(c), axis=0)
        self.assertEqual(inline['2019-05-01 02:00:00':'2019-05-04 00:00:00']['wtg0P'].tolist()[0],
                         inline['2019-05-01 02:00:00':'2019-05-04 00:00:00']['wtg0P'].tolist()[-1])

        groupDf = pd.concat([df, inline.add_prefix('grouping_')], join="outer", axis=1)
        groups = pd.Series(pd.to_datetime(groupDf.index), index=df.index).groupby(
            groupDf['grouping_wtg0P']).agg(['first', 'last'])
        groups['size'] = groups['last'] - groups['first']

        cuts = groups['size'].quantile([0.25, 0.5, 0.75, 1])
        cuts = list(set(cuts.tolist()))
        cuts.sort()
        '''
            replace bad data in a dataframe starting with small missing blocks of data and moving to big blocks of missing data
            :param groups: pandas.DataFrame with columns size, first and last, first is the first indixe in a block to replace, last is the last index to replace
            :param df_to_fix: DataFrame the dataframe to fix
            :param cuts: [listOf TimeDeltas] the duration of each block of missing data will fall into a cut timedelta
            :param possibleReplacementValues: DataFrame where replacement values are drawn from. Can be larger than df_to_fix
            :return: [DataFrame] with bad values replaced
            '''
        newdf = doReplaceData(groups, df['wtg0P'], cuts, df.loc[pd.notnull(df['wtg0P'])]['wtg0P'])
        self.assertTrue(len(newdf) > 0)
        self.assertTrue(len(newdf['2020-05-01 00:02:00':'2020-05-01 22:00:00'][pd.isnull(newdf)]) <= 0)
        self.assertEqual(len(newdf[newdf.index.duplicated()]),0)
        # same process but with dataframe
        df.loc['2020-05-01 00:0:00':'2020-05-01 22:00:00', :] = np.nan
        newdf = doReplaceData(groups, df.loc[:, ['wtg0P', 'load0P']], cuts,
                              df.loc[pd.notnull(df).any(axis=1), ['wtg0P', 'load0P']])
        self.assertTrue(len(newdf) > 0)
        self.assertEqual(len(newdf[newdf.index.duplicated()]), 0)
        self.assertTrue(len(newdf['2020-05-01 00:02:00':'2020-05-01 22:00:00'][pd.isnull(newdf['wtg0P'])]) <= 0)
        self.assertTrue(len(newdf['2020-05-01 00:02:00':'2020-05-01 22:00:00'][pd.isnull(newdf['load0P'])]) <= 0)


if __name__ == '__main__':
    unittest.main()
