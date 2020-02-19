import unittest
import os
from MiGRIDS.UserInterface.XMLEditorHolder import XMLEditorHolder
from MiGRIDS.Controller.UIToInputHandler import UIHandler
class ModelEditorHolderTest(unittest.TestCase):

    def setUp(self):
        self.peht = XMLEditorHolder(0)

    def tearDown(self):
        del self.peht

    def test_getPredictorList(self):

        xmldict = self.peht.getPredictorFiles()
        self.assertIn('windpredict',list(xmldict.keys())) #this corresponds to wtg elsewhere
        self.assertIn('loadpredict', list(xmldict.keys()))
        self.assertListEqual(xmldict['loadpredict'],['LoadPredict0'])

    def test_getDispatchFiles(self):

        xmldict = self.peht.getDispatchFiles()
        self.assertIn('eesdispatch', list(xmldict.keys()))
        self.assertIn('gendispatch', list(xmldict.keys()))
        self.assertListEqual(xmldict['gendispatch'], ['GenDispatch0'])

    def test_getScheduleList(self):

        xmldict = self.peht.getScheduleFiles()
        self.assertIn('genschedule',list(xmldict.keys())) #this corresponds to wtg elsewhere
        self.assertListEqual(xmldict['genschedule'],['GenSchedule0'])

    def test_combineAllXmls(self):
        self.setXMLAttributes()
        xmldict = self.peht.combineAllXmls()
        self.assertIn('gendispatch', list(xmldict.keys()))
        self.assertListEqual(xmldict['loadpredict'], ['LoadPredict0'])

    def setXMLAttributes(self):
        self.peht.scheduleXMLs = self.peht.getScheduleFiles()
        self.peht.dispatchXMLs= self.peht.getDispatchFiles()
        self.peht.predictorXMLs = self.peht.getPredictorFiles()
        self.peht.minSRCXMLs = self.peht.getMinSrcFiles()

    def test_getSelectedModelsFromSetup(self):
        self.setXMLAttributes()
        self.peht.xmls = self.peht.combineAllXmls()
        setup = self.readInSetup()
        defaults = self.peht.getSelectedModelsFromSetup(setup)
        self.assertEqual(defaults['loadpredict'].lower(),'loadpredict1')
        return
    def readInSetup(self):
        file = os.path.join(os.path.dirname(__file__), '..', '..', 'MiGRIDSProjects', 'SampleProject', 'InputData', 'Setup',
                     'SampleProjectSetup.xml')
        handler = UIHandler()
        setup = handler.readInSetupFile(file)
        return setup

if __name__ == '__main__':
    unittest.main()
