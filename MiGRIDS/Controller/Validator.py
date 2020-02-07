# Projet: MiGRIDS
# Created by: # Created on: 11/15/2019
import pandas as pd
from enum import Enum
from MiGRIDS.Controller.GenericSender import GenericSender
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler
from MiGRIDS.UserInterface.qdateFromString import qdateFromString


class ValidatorTypes(Enum):
    DataObject=0    #DataClass object
    NetCDFList=1    #list of netcdf files for model
    SetupXML=2      #setup xml
    SetSetupXML=3   #set setup xml
    AttributeXML=4  #attribute xml
    InputData=5     #portion of setup xml pertinant to create DataClass object


class Validator:
    """
    Description: Class and subroutines to validate all inputs and emit valid/notvalid signals
    Attributes: 
        
        
    """

    def __init__(self):
        self.sender = GenericSender()
        self.dbhandler = ProjectSQLiteHandler()


    def validate(self,ValidatorType,input=None):
        isValid = self.isValid(ValidatorType, input)
        self.sender.message(ValidatorType.name,str(isValid))
        return isValid

    def isValid(self,ValidatorType, input):
        fnName = 'validate' + ValidatorType.name
        try:
            method = self.__getattribute__(fnName) #find the appropriate validation method
            return method(input)
        except KeyError as k:
            print(k)


    def validateDataObject(self,dataObject):
        #TODO complete implementation - check column names match specified input
        try:
            for df in dataObject.fixed:
                if not isinstance(df.index, pd.DatetimeIndex):
                    return False
                if len(df.columns) <= 0:
                    return False

            return True
        except KeyError as k:
            return False
        except AttributeError as a:
            return False

        return False #if it gets to here, something is not valid


    def validateNetCDFList(self,nList):
        '''netcdf requirements:
        continuous index without na
        1 value field,
        at least 1 load nc, and 1 component nc'''
        #TODO implement
        if len(nList)>1:
            return True
        else:
            return False
    def validateInputData(self,files = None):
        '''Requirements:
        each input file is linked to 1 or more component,
        date format is specified,
        '''
        #TODO implement checks on input file specifications
        return True
    def validateSetupXML(self,xml):
        #TODO implement
        return True
    def validateSetSetupXML(self,xml):
        #TODO implement
        return True
    def validateAttributeXMLt(self,xml):
        #TODO implement
        return True


    def validateRunTimeSteps(self,lodf):
        #run time steps need to either equal the range of the data set or be a subset within the dataset
        def indexValue(minmax):
            if minmax == 'min':
                return min([min(df.index) for df in lodf])
            else:
                return max([max(df.index) for df in lodf])

        dataStart = indexValue('min').replace(tzinfo=None)
        dataEnd = indexValue('max').replace(tzinfo=None)
        apparentStart,apparentEnd = self.dbhandler.getSetupDateRange()

        if (apparentStart == None):
            # update Start
            self.dbhandler.updateRecord('setup',['_id'],[1],['date_start'],[dataStart])
        elif (dataStart.date() > qdateFromString(apparentStart).toPyDate()):
            self.dbhandler.updateRecord('setup', ['_id'], [1], ['date_start'], [dataStart])
        if (apparentEnd ==  None):
            #update End
            self.dbhandler.updateRecord('setup', ['_id'], [1], ['date_end'], [dataEnd])
        elif (dataEnd.date() < qdateFromString(apparentEnd).toPyDate()):
            self.dbhandler.updateRecord('setup', ['_id'], 1, ['date_end'], [dataEnd])

        return