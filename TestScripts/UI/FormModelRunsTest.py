import unittest
import os
import sys
from PyQt5 import QtWidgets, QtSql

from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from MiGRIDS.Controller.UIHandler import UIHandler
from MiGRIDS.InputHandler.getSetupInformation import getSetupInformation
from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag
from MiGRIDS.Model.Operational.generateRuns import generateRuns
from MiGRIDS.UserInterface.FormModelRuns import FormModelRun, SetsAttributeEditorBlock
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from shutil import copyfile

from MiGRIDS.UserInterface.getFilePaths import getFilePath


class FormModelRunsTest(unittest.TestCase):
    app = QtWidgets.QApplication(sys.argv)

    @classmethod
    def setUpClass(cls):
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('project_manager')
        handler = ProjectSQLiteHandler()
        handler.makeDatabase()

    def setUp(self):
        self.window = QtWidgets.QMainWindow()
        self.F = FormModelRun(self.window)
        self.controller = UIHandler()
        self.window.show()
        self.handler = ProjectSQLiteHandler()


    def tearDown(self):
        self.clearDatabase()
        self.handler = None
        del self.F
        self.window.close()



    def test_setupSetup(self):
        self.insertTestData()
        editor = self.F.findChild(SetsAttributeEditorBlock)
        editor.setupSet()
        projectSetup = os.path.join(getFilePath('Setup',projectFolder=self.handler.getProjectPath()),
                                    self.handler.getProject() + 'Setup.xml')
        setSetup = os.path.join(getFilePath('Set0',projectFolder=self.handler.getProjectPath()),*['Setup',
                                    self.handler.getProject() +'Set0' + 'Setup.xml'])
        self.assertNotEqual(readXmlTag(projectSetup,'timeStep','value'),readXmlTag(setSetup,'timeStep','value'))

    '''def test_calculateRuns(self):
        self.insertTestData()
        editor = self.F.findChild(SetsAttributeEditorBlock)
        print(self.handler.getAllRecords('set_components'))
        editor.setupRuns()

        testfiles = [name
            for (parent, subdirs, files) in os.walk(self.handler.getProjectPath())
            for name in files + subdirs if name[-2:] !='db']
        runs1 = [r for r in testfiles if r[0:3] == 'Run']
        rund1 = [r for r in testfiles if ('Run0' in r) & (r[-3:]=='xml')]
        self.createOriginalRuns()
        originalfiles = [
            name
            for (parent, subdirs, files) in os.walk('testProject1/OutputData')
            for name in files + subdirs if name[-2:] !='db'
        ]
        runs2 = [r for r in originalfiles if r[0:3] == 'Run']
        rund2 = [r for r in originalfiles if ('Run0' in r) & (r[-3:]=='xml')]
        #there are four runs with different values in ees xml files
        xmlfiles = [
            os.path.join(parent,name)
            for (parent, subdirs, files) in os.walk(os.path.join(self.handler.getProjectPath(),*['OutputData','Set0']))
            for name in files + subdirs if 'ees0' in name
        ]


        self.assertTrue(len(self.compareOneToAll('PInMaxPa','30',list(xmlfiles),[])) == 2)
        self.assertTrue(len(self.compareOneToAll('PInMaxPa', '40', list(xmlfiles), [])) == 2)
        self.assertTrue(len(self.compareOneToAll('POutMaxPa', '40', list(xmlfiles), [])) == 2)
        self.assertTrue(len(self.compareOneToAll('ratedDuration', '900', list(xmlfiles), [])) == 2)
        #folders and files in originalRuns and in runs should be the same except attribute xmls
        self.assertListEqual(runs1,runs2)

        self.assertListEqual(rund1, rund2)'''

    def compareOneToAll(self,tag,value, xmls,returns):
        if len(xmls) > 0:
            #if the component tag and value are found in another xml return true
            foundvalue = readXmlTag(xmls[0], tag, 'value')

            if (isinstance(foundvalue,list)) & (not isinstance(value,list)):
                foundvalue = foundvalue[0]
            if foundvalue == value:
                returns.append(xmls[0])

            xmls.pop(0)
            return self.compareOneToAll(tag,value,xmls,returns)
        else:
            return returns

    def insertTestData(self):
        self.handler.insertRecord("project",['project_name','project_path','setupfile'],['SampleProject1',os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects','SampleProject1'),
                                                                                         os.path.join(*[
                                                                                             os.path.dirname(__file__),
                                                                                             '..', '..',
                                                                                             'MiGRIDSProjects',
                                                                                             'SampleProject1','InputData','Setup','SampleProject1Setup.xml'])])
        self.handler.insertRecord("setup", ['date_start', 'date_end', 'timestepvalue', 'timestepunit' ], ['','',1,'s'])

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
        self.handler.insertRecord('component',
                                  ['componenttype', 'componentnamevalue'],
                                  ['ees', 'ees0'])
        self.handler.insertRecord('component',
                                  ['componenttype', 'componentnamevalue'],
                                  ['gen', 'gen0'])
        self.handler.insertRecord('component',
                                  ['componenttype', 'componentnamevalue'],
                                  ['gen', 'gen1'])
        self.handler.insertRecord('component',
                                  ['componenttype', 'componentnamevalue'],
                                  ['tes', 'tes0'])

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

        self.handler.insertRecord('set_',['project_id','set_name','timestepvalue','timestepunit'],
                                  [1,'Set0',10,'s'])

        self.handler.insertRecord('set_components',['set_id','component_id','tag','tag_value'],[1,1,'None','None'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 2, 'None', 'None'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 3, 'None', 'None'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 4, 'None', 'None'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 5, 'None', 'None'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 6, 'None', 'None'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 3, 'PInMaxPa.value', '30'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 3, 'PInMaxPa.value', '40'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 3, 'POutMaxPa.value', 'ees0.PInMaxPa.value'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 3, 'ratedDuration.value', '900'])
        self.handler.insertRecord('set_components', ['set_id', 'component_id', 'tag', 'tag_value'],
                                  [1, 3, 'ratedDuration.value', '1800'])
        self.handler.connection.commit()

    def createOriginalRuns(self):
        #create a project set folder
        fakeset = os.path.join(*["testProject1",'OutputData','Set0'])
        os.makedirs(fakeset,exist_ok=True)
        attributexml = os.path.join(fakeset,'testProject1Set0Attributes.xml')
        setupFolder = os.path.join(*["testProject1", 'InputData', 'Setup'])
        compFolder = os.path.join(*["testProject1", 'InputData', 'Components'])
        os.makedirs(setupFolder,exist_ok=True)
        os.makedirs(compFolder, exist_ok=True)
        xmls = os.listdir(
            os.path.join(os.path.dirname(__file__), *['..', '..', 'MiGRIDS', 'Model', 'Resources', 'Setup']))

        [copyfile(os.path.join(os.path.dirname(__file__), *['..', '..', 'MiGRIDS', 'Model', 'Resources', 'Setup', x]),
                  os.path.join(setupFolder, os.path.basename(x).replace('project', 'testProject1'))) for x in xmls]


        components = ["ees0","wtg0", "gen0", "gen1", "load0", "tes0"]



        for i,cpt in enumerate(components):  # for each component

           self.controller.makeComponentDescriptor(cpt,compFolder)

        #[copyfile(os.path.join(os.path.dirname(__file__), *['..', '..', 'MiGRIDS', 'Model', 'Resources', 'Components', x]),
           #                 os.path.join(compFolder,os.path.basename(x).replace('project',''))) for x in xmls]
        setupFile = os.path.join(setupFolder,'testProject1Setup.xml')

        #create a setup file
        #read the soup from the template
        template = os.path.join(os.path.dirname(__file__), *['..','..', 'MiGRIDS', 'Model', 'Resources', 'Setup'],
                                'projectSetup.xml')

        templateSoup = getSetupInformation(template)
        self.controller.writeSoup(templateSoup,os.path.join(setupFolder,'testProject1Setup.xml'))
        # set the componentNames
        writeXmlTag(setupFile,'componentNames','value',"ees0 wtg0 gen0 gen1 load0 tes0")
             #create an attribute xml
        #read the template
        template = os.path.join(os.path.dirname(__file__),*['..','..','MiGRIDS','Model','Resources','Setup'],'projectSetAttributes.xml')
        templateSoup = self.controller.getSetAttributeXML(template)
        self.controller.writeSoup(templateSoup,attributexml)
        writeXmlTag(attributexml,'compName','value',"ees0 ees0 ees0")
        writeXmlTag(attributexml, 'compTag', 'value', "PInMaxPa POutMaxPa ratedDuration")
        writeXmlTag(attributexml, 'compAttr', 'value', "value value value")
        writeXmlTag(attributexml, 'compValue', 'value', "30,40 ees0.PInMaxPa.value 900,1800")
        writeXmlTag(attributexml, 'setupTag', 'value', "componentNames runTimeSteps timeStep")
        writeXmlTag(attributexml, 'setupAttr', 'value', "value value value value value value")
        writeXmlTag(attributexml, 'setupValue', 'value', "ees0,wtg0,gen0,gen1,load0,tes0 all 10")

        #copy dispatc,predict and schedule to setup folder
        setupFolder

        #generate runs
        generateRuns(os.path.join(os.path.dirname(os.path.abspath(__file__)),fakeset))
    def clearDatabase(self):
        tablelist = ['setup','set_components','component','component_files','project','run','input_files']
        for t in tablelist:
            self.handler.clearTable(t)

if __name__ == '__main__':
    unittest.main()
