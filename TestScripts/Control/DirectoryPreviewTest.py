import unittest
import os
from PyQt5 import QtSql
from MiGRIDS.Controller.DirectoryPreview import DirectoryPreview
from MiGRIDS.Controller.Exceptions.NoMatchException import NoMatchException
from MiGRIDS.Controller.Exceptions.NoValidFilesError import NoValidFilesError
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler

class DirectoryPreviewTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('project_manager')

        handler = ProjectSQLiteHandler()
        # get the name of the last project worked on
        handler.makeDatabase()

    def setUp(self):
        #create a project directory with a project_database
        self.path ='C:\\Users\\tmorga22\\Documents\\MiGRIDS\\MiGRIDSProjects\\SampleProject\\InputData\\TimeSeriesData\\RawData\\HighRes'
        self.path = os.path.join(os.path.dirname(__file__),'..','..','MiGRIDSProjects','SampleProject','InputData','TimeSeriesData','RawData','HighRes')

        self.subpath = os.path.join(os.path.dirname(__file__), '..','..','MiGRIDSProjects', 'SampleProject', 'InputData',
                             'TimeSeriesData')


    #object created
    def test_createEmptyObject(self):
        with self.assertRaises(NoValidFilesError):
            o = DirectoryPreview()

    #Raise error if no directory provided
    def test_createEmptyFileType(self):
        with self.assertRaises(NoValidFilesError):
            o = DirectoryPreview(inputfiletypevalue='csv')

    #test is dependent on data files in sample project
    #create valid object with date column and valid date format
    def test_createObject(self):
        o=DirectoryPreview(inputfiledirvalue=self.path,inputfiletypevalue='csv')
        self.assertEqual(o.inputfiledirvalue,self.path)
        self.assertEqual(o.datechannelvalue,'DATE')
        self.assertEqual(o.datechannelformat,"YYYY-MM-DD")

    #object with empty directory
    def test_EmptyDirectory(self):
        with self.assertRaises(NoValidFilesError):
            o = DirectoryPreview(inputfiledirvalue = self.subpath, inputfiletypevalue='csv')

    #test listFiles method
    def test_listFilesSampleProject(self):
        o = DirectoryPreview(inputfiledirvalue=self.path,inputfiletypevalue='csv')
        self.assertEqual(len(o.listFiles()),3)

    def test_extractDateTimeFormat(self):
        o = DirectoryPreview(inputfiledirvalue=self.path,inputfiletypevalue='csv')
        self.assertEqual(o.extractFormat('2018-09-22 08:11').dateFormat,"YYYY-MM-DD")
        self.assertEqual(o.extractFormat('2018-09-22 08:11').timeFormat, "HH:MM")
        self.assertEqual(o.extractFormat('08:11').timeFormat, "HH:MM")
        self.assertEqual(o.extractFormat('01/01/2019').dateFormat, "MM/DD/YYYY")
        with self.assertRaises(NoMatchException):
            o.extractFormat('June 09, 2018')

    def test_previewcsv(self):
        file =self.writeTestDateCSV()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__),inputfiletypevalue="csv")
        self.assertListEqual(list(o.header),['date','v1'])
        self.assertEqual(o.datechannelvalue,'date')
        self.assertEqual(o.datechannelformat, "MM/DD/YYYY")
        with self.assertRaises(AttributeError):
            o.timechannelvalue == None
        self.assertEqual(o.timechannelformat,"HH:MM")
        self.deleteTestFile(file)

        file =self.writeTestDaysCSV()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__),inputfiletypevalue= "csv")
        self.assertListEqual(list(o.header), ['date', 'v1'])
        self.assertEqual(o.datechannelvalue, 'date')
        self.assertEqual(o.datechannelformat, "days")
        with self.assertRaises(AttributeError):
            o.timechannelvalue== None
        self.assertEqual(o.timechannelformat, None)
        self.deleteTestFile(file)

    def test_previewMET(self):
        file = self.writeTestMET()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__), inputfiletypevalue="MET")

        self.assertEqual(o.header[0],'Date & Time Stamp')
        #the time and date columns will be the same field
        self.assertEqual(o.datechannelvalue, 'Date & Time Stamp')
        self.assertEqual(o.datechannelformat, 'YYYY-MM-DD')
        self.assertEqual(o.timechannelvalue, 'Date & Time Stamp')
        self.assertEqual(o.timechannelformat, 'HH:MM:SS')
        self.deleteTestFile(file)

    def test_previewtxt(self):
        file = self.writeTestDateTXT()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__),inputfiletypevalue="txt")
        self.assertListEqual(list(o.header), ['date', 'v1'])
        self.assertEqual(o.datechannelvalue, 'date')
        self.assertEqual(o.datechannelformat, "MM/DD/YYYY")
        with self.assertRaises(AttributeError):
            o.timechannelvalue== None

        self.assertEqual(o.timechannelformat, "HH:MM")
        self.deleteTestFile(file)

        file = self.writeTestDaysTXT()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__), inputfiletypevalue="txt")
        self.assertListEqual(list(o.header), ['date', 'v1'])
        self.assertEqual(o.datechannelvalue, 'date')
        self.assertEqual(o.datechannelformat, "days")
        with self.assertRaises(AttributeError):
            o.timechannelvalue == None
        self.assertEqual(o.timechannelformat, None)
        self.deleteTestFile(file)
    def test_previewCDF(self):
        file = self.writeTestDateNetCDF()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__), inputfiletypevalue="nc")
        self.assertListEqual(list(o.header), ['time', 'value'])
        self.assertEqual(o.datechannelvalue, 'time')
        self.assertEqual(o.datechannelformat, "MM/DD/YYYY")
        self.assertEqual(o.timechannelvalue, 'time')
        self.assertEqual(o.timechannelformat, "HH:MM")
        self.deleteTestFile(file)

        file = self.writeTestDaysNetCDF()
        o = DirectoryPreview(inputfiledirvalue=os.path.dirname(__file__), inputfiletypevalue="nc")
        self.assertListEqual(list(o.header), ['time', 'value'])
        #self.assertEqual(o.dateColumn, 'time')
        #self.assertEqual(o.dateFormat, "days")
        self.assertEqual(o.timechannelvalue, 'time')
        self.assertEqual(o.timechannelformat, None)
        self.deleteTestFile(file)

    def deleteTestFile(self,file):
        os.remove(file)

    def writeTestDateCSV(self):
        import csv
        with open(os.path.join(os.path.dirname(__file__), "test.csv"), 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(
                ['date', 'v1'])
            writer.writerows([('09/22/2019 08:11', 1.0), ('09/22/2019 08:12', 1.1), ('09/22/2019 08:13', 1.2)])

        return os.path.join(os.path.dirname(__file__), "test.csv")

    def writeTestDaysCSV(self):
        import csv
        with open(os.path.join(os.path.dirname(__file__), "test.csv"), 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(
                ['date', 'v1'])
            writer.writerows([('890706086.124', 1.0), ('890706086.178', 1.1), ('890706086.212', 1.2)])

        return os.path.join(os.path.dirname(__file__), "test.csv")
    def writeTestDateTXT(self):
        with open(os.path.join(os.path.dirname(__file__),"test.txt"), 'w', newline='') as f:

            f.write(
                'date\tv1\n')
            f.writelines(
            [('09/22/2019 08:11\t1.0\n'),('09/22/2019 08:12\t1.1\n'),('09/22/2019 08:13\t1.2\n')])

        return os.path.join(os.path.dirname(__file__),"test.txt")

    def writeTestDaysTXT(self):

        with open(os.path.join(os.path.dirname(__file__), "test.txt"), 'w', newline='') as f:
            f.write(
                'date\tv1\n')
            f.writelines([('890706086.124\t1.0\n'), ('890706086.178\t1.1\n'), ('890706086.212\t1.2\n')])

        return os.path.join(os.path.dirname(__file__), "test.txt")

    def writeTestDateNetCDF(self):
        import netCDF4
        import numpy as np

        rootgrp = netCDF4.Dataset(os.path.join(os.path.dirname(__file__),"test.nc"), 'w',format='NETCDF4')
        rootgrp.createDimension('time', None)  # create dimension for all called time
        # create the time variable
        rootgrp.createVariable('time', str, 'time')  # create a var using the varnames
        rootgrp.variables['time'][:] = np.array(['09/22/2019 08:11','09/22/2019 08:12','09/22/2019 08:13']) # fill with values
        # create the value variable
        rootgrp.createVariable('value', float, 'time')  # create a var using the varnames
        rootgrp.variables['value'][:] = np.array([1.2,1.3,1.4])  # fill with values
        # assign attributes
        rootgrp.variables['time'].units = 'seconds'  # set unit attribute
        rootgrp.variables['value'].units = 'Kw'  # set unit attribute
        rootgrp.variables['value'].Scale = 1  # set unit attribute
        rootgrp.variables['value'].offset =  0  # set unit attribute
        # close file
        rootgrp.close()
        return os.path.join(os.path.dirname(__file__),"test.nc")

    def writeTestDaysNetCDF(self):
        import netCDF4
        import numpy as np

        rootgrp = netCDF4.Dataset(os.path.join(os.path.dirname(__file__), "test.nc"), 'w', format='NETCDF4')
        rootgrp.createDimension('time', None)  # create dimension for all called time
        # create the time variable
        rootgrp.createVariable('time', float, 'time')  # create a var using the varnames
        rootgrp.variables['time'][:] = ['890706086.124','890706086.178', '890706086.212']  # fill with values
        # create the value variable
        rootgrp.createVariable('value', float, 'time')  # create a var using the varnames
        rootgrp.variables['value'][:] = np.array([1.2, 1.3, 1.4])  # fill with values
        # assign attributes
        rootgrp.variables['time'].units = 'seconds'  # set unit attribute
        rootgrp.variables['value'].units = 'Kw'  # set unit attribute
        rootgrp.variables['value'].Scale = 1  # set unit attribute
        rootgrp.variables['value'].offset = 0  # set unit attribute
        # close file
        rootgrp.close()
        return os.path.join(os.path.dirname(__file__), "test.nc")
    #this test does not write a MET file from scratch, but uses the file in the sample project
    def writeTestMET(self):
        from shutil import copyfile
        copyfile(os.path.join(self.subpath,'RawData','RawWind','met0.txt'), os.path.join(os.path.dirname(__file__), "met0.txt"))
        return os.path.join(os.path.dirname(__file__), "met0.txt")


if __name__ == '__main__':
    unittest.main()

