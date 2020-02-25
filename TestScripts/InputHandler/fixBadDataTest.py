import unittest

import shutil

import numpy as np
from MiGRIDS.InputHandler.Component import Component
from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor
from MiGRIDS.InputHandler.fixBadData import *
from MiGRIDS.InputHandler.makeSoup import makeComponentSoup
from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag


class fixBadData_test (unittest.TestCase):

    def setUp(self):
        self.comps = [Component(column_name=n, component_name=n[0:4], attribute='P') for n in ['wtg0P', 'gen0P']]
        return

    def tearDown(self):
        if os.path.isdir("testProject"):
            shutil.rmtree("testProject")
        return
    def setupProject(self, comps):
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
        self.setupProject(comps)
        tsIndex = pd.date_range('2019-01-01 00:00:00', periods=10, freq='H')
        df = pd.DataFrame(index=tsIndex)
        for c in comps:
            descriptorxmlpath = os.path.join(self.setupFolder, '..', 'Components', ''.join([c.component_name, DESCXML]))
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
            cs = pd.Series(np.random.randint(int(low),int(high),10), index = tsIndex)
            cs.name = c.column_name
            df = pd.concat([df,cs],axis=1)
        return df

    def test_dieselNeeded(self):
        self.setupProject(self.comps)
        myI = iter(self.comps)
        d = dieselNeeded(myI,self.setupFolder,[n.column_name for n in self.comps])
        self.assertTrue(d)

        myI = iter(self.comps)
        writeXmlTag(os.path.join(self.compFolder,'wtg0Descriptor.xml'), 'isFrequencyReference','value', "TRUE")
        writeXmlTag(os.path.join(self.compFolder, 'wtg0Descriptor.xml'), 'isVoltageSource', 'value', "TRUE")
        d = dieselNeeded(myI, self.setupFolder, [n.column_name for n in self.comps])
        shutil.rmtree("testProject")
        self.assertFalse(d)
    def test_minMaxValid(self):
        b = minMaxValid(0,10)
        self.assertTrue(b)

        b = minMaxValid(10, 10)
        self.assertFalse(b)
        b = minMaxValid(10, 0)
        self.assertFalse(b)
        b = minMaxValid(None, 0)
        self.assertFalse(b)
    def test_attributeFromColumn(self):
        a = attributeFromColumn('wtg0P')
        self.assertEqual('P', a)
        a = attributeFromColumn('wtg0WS')
        self.assertEqual('WS', a)
        a = attributeFromColumn('wtg0G')
        self.assertEqual('G', a)
        a = attributeFromColumn('0wtg0G')
        self.assertEqual(None, a)
    def test_attributeFromColumn(self):
        a = componentNameFromColumn('wtg0P')
        self.assertEqual('wtg0', a)
        a = componentNameFromColumn('gen0WS')
        self.assertEqual('gen0',a)

        a = componentNameFromColumn('0gen0WS')
        self.assertEqual(None, a)
    def test_fillComponentTypeList(self):
        e, l, p = fillComponentTypeLists(self.comps)
        self.assertEqual(len(e),0)
        self.assertEqual(len(l), 0)
        self.assertEqual(len(p), 2)

        c = self.comps
        c = c + [Component(column_name='load0P',component_name='load0',attribute='P'),Component(column_name='wtg1WS',component_name = 'wtg1',attribute='WS')]
        e, l, p = fillComponentTypeLists(c)
        self.assertEqual(len(e), 1)
        self.assertEqual(len(l), 1)
        self.assertEqual(len(p), 2)
    def test_checkPowerComponents(self):
        comps = self.comps + [Component(column_name='load0P', component_name='load0', attribute='P'),
                              Component(column_name='wtg1WS', component_name='wtg1', attribute='WS')]

        df = self.createComponentDataframe(comps)
        baddata = {}
        for c in comps:
            descriptorxmlpath = os.path.join(self.setupFolder, '..', 'Components', ''.join([c.component_name, DESCXML]))
            xml = ET.parse(descriptorxmlpath)

            df,baddata = checkMinMaxPower(c,df,xml,baddata)
        self.assertTrue(len(baddata.keys())==0)
        self.assertTrue(len(df[pd.isnull(df).any(axis=1)]) == 0) #default xmls don't have minmax values
        #write at max value that will be exceeded for wtg0
        writeXmlTag(os.path.join(self.setupFolder, '..', 'Components', ''.join(['wtg0', DESCXML])),"POutMaxPa",'value',20)
        for c in comps:
            descriptorxmlpath = os.path.join(self.setupFolder, '..', 'Components', ''.join([c.component_name, DESCXML]))
            xml = ET.parse(descriptorxmlpath)

            df,baddata = checkMinMaxPower(c,df,xml,baddata)
            self.assertTrue('wtg0P' in baddata.keys())
            self.assertTrue(len(df[pd.isnull(df).any(axis=1)]) > 0)


if __name__ == '__main__':
    unittest.main()
