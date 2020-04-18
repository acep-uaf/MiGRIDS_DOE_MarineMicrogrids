# Project: MiGRIDS
# Author: T. Morgan
# Date: June 26, 2019
# License: MIT License (see LICENSE file of this package for more information)

# Class to store preview information for an input timeseries file.
# Methods to extract field names, and date time columns and formats
# Input file can be CSV, TXT, nc or MET
# Preview is based on the first file found within a directory, and assumes all files within a directory follow the same format.

import os
import pandas as pd
from MiGRIDS.Controller.Exceptions.NoValidFilesError import NoValidFilesError
from MiGRIDS.Controller.Exceptions.NoMatchException import NoMatchException
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
import MiGRIDS.UserInterface.ModelFileInfoTable as F

class DirectoryPreview():
    '''Attributes:
        files - is a list of files
        header - is a list of field names collected from the first file read
        dateFormat - is the format of the date column, None if not available
        timeFormat - is the fomat of the time column, None if not available
        dateColumn - is  the date column, None if not available
        timeColumn - is  the time column, None if not available
        '''

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        try:
            self.files = self.listFiles()
            self.preview(self.files[0])
        except NoValidFilesError as e:
            raise e

    def listFiles(self):
        '''
        Creates a list of files found in a directory of a given file type
        Will through error if no files are found.
        :return: list of files found in a directory that match a specified file type
        '''
        try:
           lof = [os.path.join(self.__dict__.get(F.InputFileFields.inputfiledirvalue.name),f) for f in os.listdir(self.__dict__.get(F.InputFileFields.inputfiledirvalue.name)) if (f[- len(self.__dict__.get(F.InputFileFields.inputfiletypevalue.name)):] == self.__dict__.get(F.InputFileFields.inputfiletypevalue.name).replace('MET','txt')) | (f[- len(self.__dict__.get(F.InputFileFields.inputfiletypevalue.name)):] == self.__dict__.get(F.InputFileFields.inputfiletypevalue.name).lower())]
        except Exception as e:
            print(e)
            raise NoValidFilesError("No valid files found in directory")
        if len(lof) <= 0:
            raise NoValidFilesError("No valid files found in directory")
        return lof

    def preview(self, file):
        '''
        Calls to preview for a specific file type and file
        :param file: a CSV,TXT,MET, or nc file
        :return: list of field names within the specified file
        '''
        try:
            if (self.__dict__.get(F.InputFileFields.inputfiletypevalue.name).lower() == 'csv'):
                self.previewCSV(file)
            elif (self.__dict__.get(F.InputFileFields.inputfiletypevalue.name).lower() == 'met'):
                self.previewMET(file)
            elif (self.__dict__.get(F.InputFileFields.inputfiletypevalue.name).lower() == 'nc'):
                self.previewNetCDF(file)
            elif(self.__dict__.get(F.InputFileFields.inputfiletypevalue.name).lower() == 'txt'):
                self.previewTXT(file)
            return
        except AttributeError as e:
            print('Can not create preview. Input file type is not set')

    class datetime:
        #local datetime object to store format information
        '''attributes:
            timeFormat - a string expression matching a time format found in the ref_time_format table within project_manager database
            dateFormat - a string expression matching a date format found in the ref_date_format table within project_manager database
        '''
        timeFormat = None
        dateFormat = None

    def extractFormat(self,sample):
        '''
        Identifies what date and time format is used in a sample of a datetime string. Can only identify formats
        avaiable in the project_manager ref_date_format and ref_time_format tables.
        :param sample: a string date, time or datetime
        :return: a datetime object with string date and time format attributes
        '''
        import re
        dbhandler = ProjectSQLiteHandler()
        possibles = dbhandler.getPossibleDateTimes()
        matches = [p for p in possibles if re.match(p,sample) is not None]
        if len(matches) > 0:
            dt = self.datetime()
            if (len(matches[0].split(" "))>1 ):#if it splits we have date and time
                dt.dateFormat = dbhandler.getCode("ref_date_format", matches[0].split(" ")[0].replace("^","").replace("$",""))
                dt.timeFormat = dbhandler.getCode("ref_time_format", matches[0].split(" ")[1].replace("^","").replace("$",""))
            else:
                dt.dateFormat = dbhandler.getCode("ref_date_format", matches[0].split(" ")[0].replace("^", "").replace("$", ""))
                if dt.dateFormat == None:
                    dt.timeFormat = dbhandler.getCode("ref_time_format", matches[0].split(" ")[0].replace("^", "").replace("$", ""))
            return dt
        else:
            raise NoMatchException("No Datetime match","No datetime formats could be matched to these input files.")

    def whichColumns(self, matchField):
        '''
        Finds the position of matchField in a list of strings
        :param matchField: String to find in list of strings
        :return: list of positions that contain strings = to matchField
        '''
        return [i for i,d in enumerate(self.header) if matchField in d.lower()]

    def setDateTimeFromDataFrame(self,df):
        '''
        Assigns dateColumn, timeColumn, dateFormat and timeFormat attributes based on information
        contained in a dataframe. Date and time columns are identified by column names containing the
        words 'date' or 'time' respectively. Date/Time formats are extracted from the first values found
        in Date and Time columns within the dataframe.
        :param df: a pandas dataframe
        :return: None. Set's class attributes.
        '''
        try:
            self.__setattr__(F.InputFileFields.datechannelvalue.name,self.header[self.whichColumns('date')[0]])
            if(len(df)>0):
               sampleDate = df[self.__dict__.get(F.InputFileFields.datechannelvalue.name)][0]
            else:
                sampleDate = None

        except IndexError as e:
            # No date column found moves on to find time and date gets set to empty string
            sampleDate = ''

        finally:
            try:
               
                self.__setattr__(F.InputFileFields.timechannelvalue.name, self.header[self.whichColumns('time')[0]])
                sampleTime = df[self.__dict__.get(F.InputFileFields.timechannelvalue.name)][0]

            except IndexError as e:
                # no time column found, time gets set to empty string
                sampleTime = ''
            finally:
                try:
                    if (sampleDate == sampleTime):
                        datetimeformat = self.extractFormat(sampleDate)
                    else:
                        datetimeformat = self.extractFormat((str(sampleDate) + ' ' + str(sampleTime)).strip())

                    self.__setattr__(F.InputFileFields.datechannelformat.name,datetimeformat.dateFormat)
                    self.__setattr__(F.InputFileFields.timechannelformat.name,datetimeformat.timeFormat)
                except NoMatchException as e:
                    print(e.message)
                    self.__setattr__(F.InputFileFields.datechannelformat.name, None)
                    self.__setattr__(F.InputFileFields.timechannelformat.name, None)

    def previewCSV(self, file):
        '''
        Set class attributes based on input from a CSV file
        :param file: full path to a csv file
        :return: None
        '''
        df = pd.read_csv(file)  # read as a data frame
        self.header = df.columns.str.replace('\s+', '_')
        self.setDateTimeFromDataFrame(df)
        del(df)

    def previewTXT(self, file):
        '''
               Set class attributes based on input from a txt file
               :param file: full path to a txt file
               :return: None
               '''

        df = pd.read_table(file,'\t')  # read as a data frame
        self.header = df.columns.str.replace('\s+', '_')
        self.setDateTimeFromDataFrame(df)
        del(df)

    def previewMET(self, file):
        '''
         Set class attributes based on input from a MET file
         :param file: full path to a MET file
         :return: None
         '''
        metWORD = 'Date & Time Stamp'
        with open(file, 'r', errors='ignore') as openfile:
            self.header = self.lineFromKeyWord(metWORD,openfile)
            try:
                self.__setattr__(F.InputFileFields.datechannelvalue.name,self.header[self.whichColumns('date')[0]])
            except IndexError as e:
                self.__setattr__(F.InputFileFields.datechannelvalue.name,None)
            try:
                self.__setattr__(F.InputFileFields.timechannelvalue.name,self.header[self.whichColumns('time')[0]])
            except IndexError as e:
                self.__setattr__(F.InputFileFields.datechannelvalue.name,self.timecolumn,None)

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
                            if (sampleDate == sampleTime):
                                datetimeformat = self.extractFormat(sampleDate)
                            else:
                                datetimeformat = self.extractFormat((sampleDate + ' ' + sampleTime).strip())
                            self.__setattr__(F.InputFileFields.datechannelformat.name,datetimeformat.dateFormat)
                            self.__setattr__(F.InputFileFields.timechannelformat.name,datetimeformat.timeFormat)
                        except NoMatchException as e:
                            print(e.message)
                            self.__setattr__(F.InputFileFields.datechannelformat.name, None)
                            self.__setattr__(F.InputFileFields.timechannelformat.name, None)

    def previewNetCDF(self, file):
        '''
        Set class attributes based on input from a netCDF file
        :param file: full path to a netCDF file
        :return: None
        '''
        import netCDF4 as nc
        cdf = nc.Dataset(file, 'r')
        self.header = list(cdf.variables.keys()) #read a list of variables

        #look for date time columns
        try:
            self.__setattr__(F.InputFileFields.datechannelvalue.name, self.header[self.whichColumns('date')[0]])
            sampleDate = cdf.variables[self.__dict__.get(F.InputFileFields.datechannelvalue.name)]
        except IndexError as e:
            # No date column found moves on to find time and date gets set to empty string
            self.__setattr__(F.InputFileFields.datechannelvalue.name, '')
            sampleDate = ''
            print(e)
        finally:
            try:
                self.__setattr__(F.InputFileFields.timechannelvalue.name, self.header[self.whichColumns('time')[0]])
                var = cdf.variables[self.__dict__.get(F.InputFileFields.timechannelvalue.name)]
                sampleTime = var[0:1][0]
            except IndexError as e:
                # no time column found, time gets set to empty string
                self.__setattr__(F.InputFileFields.timechannelvalue.name,'')
                sampleTime = ''
            finally:
                #get format
                try:
                    if(self.__dict__.get(F.InputFileFields.datechannelvalue.name) == '') & (self.__dict__.get(F.InputFileFields.timechannelvalue.name) != ''):
                        self.__setattr__(F.InputFileFields.datechannelvalue.name,self.__dict__.get(F.InputFileFields.timechannelvalue.name))
                    if(self.__dict__.get(F.InputFileFields.datechannelvalue.name) != '') | (self.__dict__.get(F.InputFileFields.timechannelvalue.name) != ''):
                        if (sampleDate == sampleTime):
                            datetimeformat = self.extractFormat(sampleDate)
                        else:
                            datetimeformat = self.extractFormat((str(sampleDate) + ' ' + str(sampleTime)).strip())
                        self.__setattr__(F.InputFileFields.datechannelformat.name, datetimeformat.dateFormat)
                        self.__setattr__(F.InputFileFields.timechannelformat.name,datetimeformat.timeFormat)
                except NoMatchException as e:
                    print(e.message)
                    self.__setattr__(F.InputFileFields.datechannelformat.name, None)
                    self.__setattr__(F.InputFileFields.timechannelformat.name, None)

        cdf.close()

    def lineFromKeyWord(self,keyWord,openfile):
        '''
        Splits each line of a file based on tab spacing and returns the first line that contains the keyword
        in the first position as a list of strings
        :param keyWord: String to find in file, which identifies the line to return
        :param openfile: a connection to an open file
        :return: List of strings of which the first value contains the keyword, if the keyword is not found the
        returns None
        '''
        line = openfile.readline().split('\t')
        if keyWord in line[0]:
            return line
        else:
            return self.lineFromKeyWord(keyWord,openfile)