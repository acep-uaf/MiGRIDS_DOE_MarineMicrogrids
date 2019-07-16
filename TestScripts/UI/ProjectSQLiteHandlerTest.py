import unittest
import os
from PyQt5 import QtSql

from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler


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
        self.handler.insertRecord("setup", ['project', 'set_name', 'date_start', 'date_end', 'timestep', 'timeunit' ], [1,'set0','','',1,'s'])

        #three input directories
        self.handler.insertRecord("input_files", ['project_id', 'inputfiletypevalue', 'inputfiledirvalue', 'timestep','datechannelvalue' , 'datechannelformat','timechannelvalue, timechannelformat','timezonevalue','usedstvalue'],
                              [1, 'CSV', 'SampleProject,InputData,TimeSeriesData,RawData,HighRes', 1, 'DATE', 'YYYYMMDD','DATE','','America/Anchorage','T'])

        self.handler.insertRecord("input_files",
                              ['project_id', 'inputfiletypevalue', 'inputfiledirvalue', 'timestep', 'datechannelvalue',
                               'datechannelformat', 'timechannelvalue, timechannelformat', 'timezonevalue',
                               'usedstvalue'],
                              [1, 'CSV', 'SampleProject,InputData,TimeSeriesData,RawData,LowRes', 1, 'DATE',
                               'YYYYMMDD', 'DATE', '', 'America/Anchorage', 'T'])

        self.handler.insertRecord("input_files",
                              ['project_id', 'inputfiletypevalue', 'inputfiledirvalue', 'timestep', 'datechannelvalue',
                               'datechannelformat', 'timechannelvalue, timechannelformat', 'timezonevalue',
                               'usedstvalue'],
                              [1, 'MET', 'SampleProject,InputData,TimeSeriesData,RawData,RawWind', 1, 'Date_&amp;_Time_Stamp',
                               'infer', 'Date_&amp;_Time_Stamp', '', 'America/Anchorage', 'T'])


        self.handler.insertRecord('component',
                                  ['component_type', 'component_name', 'units',
                                   'scale', 'offset', 'attribute'],
                                  ['load', 'load0', 'kW', '1', '0', 'P'])
        self.handler.insertRecord('component',
                                  ['component_type', 'component_name', 'units',
                                   'scale', 'offset', 'attribute'],
                                  ['wtg', 'wtg0', 'm/s', '1', '0', 'WS'])

        self.handler.insertRecord('component_files',['component_id','inputfile','original_field_name'],
                                              [1,1,'Villagekw'])
        self.handler.insertRecord('component_files',
                                  ['component_id','inputfile', 'original_field_name'],
                                  [1,2, 'loadkw'])
        self.handler.insertRecord('component_files',
                                  ['component_id','inputfile', 'original_field_name'],
                                  [2,3, 'CH3Avg'])
        self.handler.insertRecord('setup',['project','set_name','timestep','timeunit'],
                                  [1,'set0',1,'s'])
        self.handler.insertRecord('set_components',['set_id','component_id'],[1,1])
        self.handler.insertRecord('set_components', ['set_id', 'component_id'], [1, 2])



    def clearDatabase(self):
        tablelist = ['setup','set_components','components','project','run']
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
        self.insertTestData()
        mydict = self.handler.getSetInfo('set0')
        print(mydict)
        self.assertEqual(mydict['inputFileType'],'CSV CSV MET')
        self.assertEqual(mydict['componentNames'], 'load0 wtg0')



if __name__ == '__main__':
    unittest.main()
