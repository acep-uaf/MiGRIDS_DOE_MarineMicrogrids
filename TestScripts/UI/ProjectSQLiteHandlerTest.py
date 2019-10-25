import unittest
import os
from PyQt5 import QtSql

from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.InputHandler.getSetupInformation import getSetupInformation


class ProjectSQLiteHandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ''' tests work off a default database'''
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('project_manager')

        handler = ProjectSQLiteHandler()
        handler.makeDatabase()


    @classmethod
    def tearDownClass(cls):
        handler = ProjectSQLiteHandler()
        handler.closeDatabase
        #os.remove(os.path.join(os.path.dirname(__file__), 'project_manager'))

    def setUp(self):
        self.handler = ProjectSQLiteHandler()


    def tearDown(self):
        #do something
        self.clearDatabase()
        self.handler = None

    def insertTestData(self):
        self.handler.insertRecord("project",['project_name','project_path'],['SampleProject1',os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects','SampleProject1')])
        self.handler.insertRecord("setup", ['project', 'set_name', 'date_start', 'date_end', 'timestepvalue', 'timestepunit' ], [1,'Set0','','',1,'s'])

        #three input directories
        self.handler.insertRecord("input_files", ['project_id', 'inputfiletypevalue', 'inputfiledirvalue', 'inputtimestepvalue','inputtimestepunit','datechannelvalue' , 'datechannelformat','timechannelvalue, timechannelformat','timezonevalue','usedstvalue'],
                              [1, 'CSV', 'SampleProject,InputData,TimeSeriesData,RawData,HighRes', 1, 's','DATE', 'YYYYMMDD','DATE','','America/Anchorage','T'])

        self.handler.insertRecord("input_files",
                              ['project_id', 'inputfiletypevalue', 'inputfiledirvalue', 'inputtimestepvalue', 'inputtimestepunit','datechannelvalue',
                               'datechannelformat', 'timechannelvalue, timechannelformat', 'timezonevalue',
                               'usedstvalue'],
                              [1, 'CSV', 'SampleProject,InputData,TimeSeriesData,RawData,LowRes', 1,'s', 'DATE',
                               'YYYYMMDD', 'DATE', '', 'America/Anchorage', 'T'])

        self.handler.insertRecord("input_files",
                              ['project_id', 'inputfiletypevalue', 'inputfiledirvalue', 'inputtimestepvalue', 'inputtimestepunit','datechannelvalue',
                               'datechannelformat', 'timechannelvalue, timechannelformat', 'timezonevalue',
                               'usedstvalue'],
                              [1, 'MET', 'SampleProject,InputData,TimeSeriesData,RawData,RawWind', 1, 's','Date_&amp;_Time_Stamp',
                               'infer', 'Date_&amp;_Time_Stamp', '', 'America/Anchorage', 'T'])


        self.handler.insertRecord('component',
                                  ['componenttype', 'componentnamevalue'],
                                  ['load', 'load0'])
        self.handler.insertRecord('component',
                                  ['componenttype', 'componentnamevalue'],
                                  ['wtg', 'wtg0'])

        self.handler.insertRecord('component_files',['component_id','inputfile_id','headernamevalue', 'componentattributeunit',
                                   'componentattributevalue'],
                                              [1,1,'Villagekw','kW','P'])
        self.handler.insertRecord('component_files',
                                  ['component_id','inputfile_id', 'headernamevalue', 'componentattributeunit',
                                   'componentattributevalue'],
                                  [1,2, 'loadkw','kW','P'])
        self.handler.insertRecord('component_files',
                                  ['component_id','inputfile_id', 'headernamevalue', 'componentattributeunit',
                                   'componentattributevalue'],
                                  [2,3, 'CH3Avg','m/s','WS'])
        self.handler.insertRecord('setup',['project','set_name','timestepvalue','timestepunit'],
                                  [1,'Set0',1,'s'])
        self.handler.insertRecord('set_components',['set_id','component_id'],[1,1])
        self.handler.insertRecord('set_components', ['set_id', 'component_id'], [1, 2])

    def clearDatabase(self):
        tablelist = ['setup','set_components','component','component_files','project','run','input_files']
        for t in tablelist:
            self.handler.clearTable(t)

    def test_insertRecord(self):
        self.handler.insertRecord("project", ['project_name', 'project_path'], ['test1', 'C:'])
        self.assertEqual(len(self.handler.getAllRecords('project')),1)
        self.handler.clearTable('project')
        self.assertEqual(len(self.handler.getAllRecords('project')), 0)

    def test_createDefault(self):

        self.handler.makeDatabase()
        #add to the test list
        self.assertEqual(self.handler.getProjectPath(),None)
        self.assertEqual(len(self.handler.getAllRecords("setup")),1)
        self.assertEqual(len(self.handler.getAllRecords("ref_time_format")), 5)

    def test_getSetInfo(self):
        #test on empty database
        mydict = self.handler.getSetUpInfo()
        self.assertEqual(mydict, None)
        self.insertTestData()
        mydict = self.handler.getSetUpInfo('Set0')
        print(mydict)
        self.assertEqual(mydict['inputFileType'],'CSV CSV MET')
        self.assertEqual(mydict['componentNames'], 'load0 wtg0')

    def test_getProjectPath(self):
        self.insertTestData()
        self.assertEqual(self.handler.getProjectPath(),os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects','SampleProject1'))

    def test_updateRecord(self):
        self.insertTestData()
        self.handler.updateRecord('setup',['set_name'],['Set0'],['date_start','date_end'],['3','5'])
        self.assertEqual(self.handler.getSetUpInfo()['date_start'], '3')
        self.assertEqual(self.handler.getSetUpInfo()['date_end'], '5')

    def test_getComponentType(self):
        self.assertEqual(self.handler.getTypeCount('ees'),0)
        self.insertTestData()
        self.assertEqual(self.handler.getTypeCount('ees'),0)
        self.assertEqual(self.handler.getTypeCount('wtg'),1)

    def test_updateComponent(self):
        self.insertTestData()
        #update component that doesnt exist
        self.handler.updateComponent({'componentnamevalue': 'wtg1', 'componentattributevalue': 'P'})
        self.assertEqual(self.handler.getSetUpInfo()['componentChannels.componentAttribute.value'], 'P P WS')
        #update component that does exist
        self.handler.updateComponent({'componentnamevalue': 'wtg0', 'componentattributevalue': 'P'})
        self.assertEqual(self.handler.getSetUpInfo()['componentChannels.componentAttribute.value'], 'P P P')

    def test_insertDictionaryRow(self):
        #insert 1 row of data and id should be 1
        d = {'componentnamevalue':['wtg8']}
        self.assertListEqual(self.handler.insertDictionaryRow("component",d),[1])
        #insert 2 more rows
        d = {'componentnamevalue': ['wtg9','load0']}
        self.assertListEqual(self.handler.insertDictionaryRow('component',d),[2,3])
        self.assertEqual(len(self.handler.getAllRecords('component')), 3)

        #insert dictionary with mismatched column names
        d = {'componentnamevalue': ['wtg8']}
        '''with self.assertRaises(Exception):
            self.handler.insertDictionaryRow("component", d)'''

    def test_parseInputHandlerAttributes(self):
        #dictionary with to input directories for load0
        d = {'project': 'SampleProject', 'childOf': 'childOf', 'inputFileDir': 'inputFileDir',
             'inputFileDir.value': 'SampleProject,InputData,TimeSeriesData,RawData,HighRes SampleProject,InputData,TimeSeriesData,RawData,LowRes  SampleProject,InputData,TimeSeriesData,RawData,RawWind', 'inputFileType': 'inputFileType', 'inputFileType.value': 'CSV CSV MET', 'inputFileFormat': 'inputFileFormat',
             'inputFileFormat.value': 'AVEC', 'componentNames': 'componentNames', 'componentNames.value': 'load0 wtg1',
             'componentChannels': 'componentChannels', 'headerName': 'headerName',
             'headerName.value': 'Villagekw loadkw CH3Avg ', 'componentName': 'componentName',
             'componentName.value': 'load0 load0 wtg0', 'componentAttribute': 'componentAttribute',
             'componentAttribute.unit': 'kW kW m/s', 'componentAttribute.value': 'P P WS', 'dateChannel': 'dateChannel',
             'dateChannel.format': 'infer infer infer', 'dateChannel.value': 'DATE DATE  Date_&_Time_Stamp',
             'timeChannel': 'timeChannel', 'timeChannel.format': 'infer infer infer ', 'timeChannel.value': 'DATE DATE Date_&_Time_Stamp',
             'timeZone': 'timeZone', 'timeZone.name': 'timeZone', 'timeZone.value': 'America/Anchorage America/Anchorage America/Anchorage',
             'inputUTCOffset': 'inputUTCOffset', 'inputUTCOffset.unit': 'hr', 'inputUTCOffset.value': '-9 -9 -9',
             'inputDST': 'inputDST', 'inputDST.unit': 'bool', 'inputDST.value': 'TRUE TRUE TRUE', 'realLoadChannel': 'realLoadChannel',
             'realLoadChannel.unit': 'kW', 'realLoadChannel.value': '', 'flexibleYear': 'flexibleYear', 'flexibleYear.value': 'True True True True',
             'flexibleYear.unit': 'bool', 'minRealLoad': 'minRealLoad', 'minRealLoad.unit': '', 'minRealLoad.value': '', 'maxRealLoad': 'maxRealLoad', 'maxRealLoad.unit': '', 'maxRealLoad.value': '', 'imaginaryLoadChannel': 'imaginaryLoadChannel', 'imaginaryLoadChannel.unit': '', 'imaginaryLoadChannel.value': '', 'inputTimeStep': 'inputTimeStep', 'inputTimeStep.unit': 's', 'inputTimeStep.value': '2 900 600', 'timeStep': 'timeStep', 'timeStep.unit': 's', 'timeStep.value': '1', 'runTimeSteps': 'runTimeSteps', 'runTimeSteps.value': 'all', 'loadProfileFile': 'loadProfileFile', 'loadProfileFile.value': 'load2P.nc', 'predictLoad': 'predictLoad', 'predictLoad.value': 'predictLoad0', 'predictWind': 'predictWind', 'predictWind.value': 'predictWind0', 'eesDispatch': 'eesDispatch', 'eesDispatch.value': 'eesDispatch0', 'tesDispatch': 'tesDispatch', 'tesDispatch.value': 'tesDispatch0', 'genDispatch': 'genDispatch', 'genDispatch.value': 'genDispatch0', 'genSchedule': 'genSchedule', 'genSchedule.value': 'genSchedule0', 'wtgDispatch': 'wtgDispatch', 'wtgDispatch.value': 'wtgDispatch0', 'reDispatch': 'reDispatch', 'reDispatch.value': 'reDispatch0', 'getMinSrc': 'getMinSrc', 'getMinSrc.value': 'getMinSrc0'}
        self.handler.parseInputHandlerAttributes(d,1)
        self.assertEqual(len(self.handler.getAllRecords('component')),2)
        self.assertListEqual(self.handler.cursor.execute("SELECT componentnamevalue from component").fetchall(),
                             [('load0',),('wtg0',)])
        self.assertListEqual(self.handler.cursor.execute("SELECT set_id from set_components").fetchall(),
                             [(1,), (1,)])

    def test_updateSetupInfo(self):
        setupxml = os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects','SampleProject','InputData','Setup','SampleProjectSetup.xml')
        myDict = getSetupInformation(setupxml)
        self.handler.updateSetupInfo(myDict,setupxml)
        self.assertEqual(self.handler.getProject(),'SampleProject')
        self.assertEqual(self.handler.getSetUpInfo()['componentChannels.componentAttribute.value'], 'P P WS')
        self.assertEqual(self.handler.getSetUpInfo()['componentNames'], 'load0 wtg0')

    def test_addComponentsToSet(self):
        self.insertTestData()
        self.handler.insertRecord('setup', ['project', 'set_name', 'timestepvalue', 'timestepunit'],
                                  [1, 'Set1', 1, 's'])
        complist = ['wtg0','load0']
        self.handler.addComponentsToSet(2,complist)
        self.assertTrue(len(self.handler.getAllRecords('set_components')),4)
        #insert a component that is already there
        complist = ['load0']
        self.handler.addComponentsToSet(2, complist)
        self.assertTrue(len(self.handler.getAllRecords('set_components')), 4)
        #insert for a set_id that does not exist
        self.handler.addComponentsToSet(3, complist)
        self.assertTrue(len(self.handler.getAllRecords('set_components')), 4)
        #insert a component that does not exist
        complist = ['load1']
        self.handler.addComponentsToSet(2, complist)
        self.assertTrue(len(self.handler.getAllRecords('set_components')), 4)

if __name__ == '__main__':
    unittest.main()
