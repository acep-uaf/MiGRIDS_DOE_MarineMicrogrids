'''
created by: T. Morgan June 25, 2019
DirectoryPreview holds attributes and methods related to a directory of input files
It is assumed that all files within a directory are in the same format (i.e. same file type and header information)
attribute: files is a list of files
attribute: header is a list of field names collected from the first file read
attribute: date format is the format of the date column
attribute: time format is the fomat of the time column
'''
import keyword
import os
from MiGRIDS.Controller.Exceptions.NoValidFilesError import NoValidFilesError
from MiGRIDS.Controller.Exceptions.NoMatchException import NoMatchException
from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler


class DirectoryPreview:

    def __init__(self, directory, fileType):
        #TODO check directory and filetype are not none
        self.directory = directory
        self.fileType = fileType
        try:
            self.files = self.listFiles()
            #TODO check there is atleast 1 file
            self.preview(self.files[0])
        except NoValidFilesError as e:
            raise e

    def listFiles(self):
        try:
            print(self.fileType)
            print(len(self.fileType))

            lof = [os.path.join(self.directory,f) for f in os.listdir(self.directory) if (f[- len(self.fileType):] == self.fileType) | (f[- len(self.fileType):] == self.fileType.lower())]
        except:
            raise NoValidFilesError
        if len(lof) <= 0:
            raise NoValidFilesError
        return lof

    def preview(self, file):
        if (self.fileType.lower() == 'csv'):
            headerlist = self.previewCSV(file)
        elif (self.fileType.lower() == 'met'):
            headerlist = self.previewMET(file)
        elif (self.fileType.lower() == 'nc'):
            headerlist = self.previewNetCDF(file)
        elif(self.fileType.lower() == 'txt'):
            headerlist = self.previewTXT(file)
        return headerlist
    class datetime:
        timeFormat = None
        dateFormat = None

    def extractFormat(self,sample):
        import re
        dbhandler = ProjectSQLiteHandler()
        possibles = dbhandler.getPossibleDateTimes()
        matches = [p for p in possibles if re.match(p,sample) is not None]
        if len(matches) > 0:
            dt = self.datetime()
            dt.dateFormat = dbhandler.getCode("ref_date_format", matches[0].split(" ")[0].replace("^","").replace("$",""))
            dt.timeFormat = dbhandler.getCode("ref_time_format", matches[0].split(" ")[1].replace("^","").replace("$",""))
            return dt
        else:
            raise NoMatchException("No Datetime match","No datetime formats could be matched to these input files.")

    def whichColumns(self, matchField):
        return [i for i,d in enumerate(self.header) if matchField in d.lower()]

    def setDateTimeFromDataFrame(self,df):
        try:
            self.dateColumn = self.header[self.whichColumns('date')[0]]
            sampleDate = df[self.dateColumn][0]

        except IndexError as e:
            # No date column found moves on to find time and date gets set to empty string
            sampleDate = ''
            print(e)
        finally:
            try:
                self.timeColumn = self.header[self.whichColumns('time')[0]]
                sampleTime = df[self.timeColumn][0]

            except IndexError as e:
                # no time column found, time gets set to empty string
                sampleTime = ''
            finally:
                try:
                    datetimeformat = self.extractFormat((sampleDate + ' ' + sampleTime).strip())
                    self.dateFormat = datetimeformat.dateFormat
                    self.timeFormat = datetimeformat.timeFormat
                except NoMatchException as e:
                    print(e.message)
                    self.dateFormat = None
                    self.timeFormat = None

    def previewCSV(self, file):
        import pandas as pd
        df = pd.read_csv(file)  # read as a data frame
        self.header = df.columns.str.replace('\s+', '_')
        self.setDateTimeFromDataFrame(df)
        del(df)


    def previewTXT(self, file):
        import pandas as pd
        df = pd.read_table(file,'\t')  # read as a data frame
        self.header = df.columns.str.replace('\s+', '_')
        self.setDateTimeFromDataFrame(df)
        del(df)


    def previewMET(self, file):
        with open(file, 'r', errors='ignore') as openfile:
            self.header = self.lineFromKeyWord('date',openfile)
            self.dateColumn = self.header[self.whichColumns('date')]
            self.timeColumn = self.header[self.whichColumns('time')]

            dataline = openfile.readline().split('\t')
            if len(dataline) != 0:
                try:
                    sampleDate = dataline[self.whichColumns('date')[0]]
                except IndexError as e:
                    #No date column found moves on to find time and date gets set to empty string
                    sampleDate =''
                    print(e)
                finally:
                    try:
                        sampleTime = dataline[self.whichColumns('time')[0]]
                    except IndexError as e:
                        #no time column found, time gets set to empty string
                        sampleTime = ''
                    finally:
                        try:
                            datetimeformat = self.extractFormat((sampleDate + ' ' + sampleTime).strip())
                            self.dateFormat = datetimeformat.dateFormat
                            self.timeFormat = datetimeformat.timeFormat
                        except NoMatchException as e:
                            print(e.message)
                            self.dateFormat = None
                            self.timeFormat = None




    def previewNetCDF(self, file):
        import netCDF4 as nc
        cdf = nc.Dataset(file, 'r')
        self.header = cdf.variables  #read a list of variables
        #TODO add date/time column interpretation
        cdf.close()


    def lineFromKeyWord(self,keyWord,openfile):
        line = openfile.readline().split('\t')
        if keyWord in line[0]:
            return line
        else:
            self.lineFromKeyWord(keyWord,openfile)