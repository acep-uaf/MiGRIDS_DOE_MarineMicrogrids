import unittest
import os
from bs4 import BeautifulSoup
from PyQt5 import QtSql
from MiGRIDS.Controller.UIToInputHandler import UIHandler
from MiGRIDS.InputHandler.readSetupFile import readSetupFile
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

class UIToHandlerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('project_manager')

        handler = ProjectSQLiteHandler()
        # get the name of the last project worked on
        handler.makeDatabase()

    def setUp(self):
        self.handler = ProjectSQLiteHandler()
        self.u = UIHandler()
        self.insertTestData()

    def tearDown(self):
       self.clearDatabase()

    def test_makeSetup(self):

        self.u.makeSetup('Set0')
        #there should now be a file named ''
        path = os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects','SampleProject1','InputData','Setup')
        self.assertEqual(os.path.exists(os.path.join(path, 'SampleProject1Setup.xml')), True)
        dict = readSetupFile(os.path.join(path, 'SampleProject1Setup.xml'))
        self.assertEqual(dict['inputdst.value'], 'T T T')
        self.assertEqual(dict['componentnames.value'],'load0 wtg0')
        self.assertEqual(dict['componentname.value'], 'load0 load0 wtg0')
    def test_makeComponentDescriptor(self):
        #component descriptor is made with default values so we just check the file is created
        compDir = os.path.dirname(__file__)
        self.u.makeComponentDescriptor('wtg0WS',compDir)
        self.assertEqual(os.path.exists('wtg0WSDescriptor.xml'), True)
        return
    def test_writeComponentSoup(self):
        #write component soup writes specific component tags found in a BeautifulSoup object to a components descriptor file
        compDir = os.path.dirname(__file__)
        self.u.makeComponentDescriptor('wtg0WS', compDir)
        #read in the default
        componentSoup = self.u.makeComponentDescriptor('wtg0WS', compDir)
        #edit an attribute
        tag = componentSoup.findChild('powerCurveDataPoints')
        param = tag.findChild('ws')
        param.attrs['unit'] = 'ft/s'
        #call writeComponentSoup
        self.u.writeComponentSoup('wtg0WS',compDir,componentSoup)
        #check file is created
        self.assertEqual(os.path.exists('wtg0WSDescriptor.xml'), True)
        #check file contains tag value
        f = open('wtg0WSDescriptor.xml')
        newSoup = BeautifulSoup(f.read(),'xml')
        tag = newSoup.findChild('powerCurveDataPoints')
        param = tag.findChild('ws')
        self.assertEqual(param.attrs['unit'],'ft/s')
        f.close()
        return
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

if __name__ == '__main__':
    unittest.main()
