import unittest
from MiGRIDS.UserInterface.PredictEditorHolder import PredictEditorHolder

class PredictEditorHolderTest(unittest.TestCase):

    def test_createClass(self):
        peht = PredictEditorHolder(0)
        self.assertEqual(peht.set, 0)

    def test_getPredictorList(self):
        peht = PredictEditorHolder(0)
        xmldict = peht.getPredictorFiles()

        self.assertIn('wtg',list(xmldict.keys()))
        self.assertIn('load', list(xmldict.keys()))
        self.assertIn('ess', list(xmldict.keys()))
        self.assertIn('wtg', list(xmldict.keys()))
if __name__ == '__main__':
    unittest.main()
