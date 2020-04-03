
import os
import sqlite3 as lite

from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import getReferencedValue, isTagReferenced
from MiGRIDS.InputHandler.Component import Component
from MiGRIDS.Controller.makeXMLFriendly import xmlToString, stringToXML
from MiGRIDS.UserInterface.getFilePaths import getFilePath
from MiGRIDS.UserInterface.qdateFromString import asDate
from MiGRIDS.InputHandler.InputFields import *
import pandas as pd
import shlex
# field and table constants
# fields
PROJECTNAME = "project_name"
PROJECTID = "project_id"
STARTDATE = "date_start"
ENDDATE = "date_end"
SETNAME = "set_name"
SETID = "set_id"
ID = "_id"
TAG = "tag"
TAGVALUE = "tag_value"
COMPONENTID = "component_id"
COMPONENTTYPE = "componenttype"

# tables
SETUPTABLE = 'setup'
COMPONENTTABLE = "component"
SETCOMPONENTTABLE = "set_components"
INPUTFILETABLE = "input_files"
SETTABLE = "set_"

class ProjectSQLiteHandler:
    
    
    #database field names are the same as xml files but changed to all lowercase and non-alphabetical characters removed
    def dbName(self, xmlname):
        return xmlname.lower().replace(".", "")
    def __init__(self, database='project_manager'):

        self.connection = lite.connect(database)

        self.cursor = self.connection.cursor()
        invalidAttributeCombos = {}
        invalidAttributeCombos['wtg'] = [7, 12, 13, 14]
        invalidAttributeCombos['gen'] = [7, 14]
        invalidAttributeCombos['ees'] = [7, 11, 12, 13]
        invalidAttributeCombos['inv'] = [7, 11, 12, 13, 14]
        invalidAttributeCombos['tes'] = [11, 12, 13]
        invalidAttributeCombos['load'] = [1, 2, 7, 8, 9, 10, 11, 12, 13, 14]

    def closeDatabase(self):
        self.cursor.close()
        self.connection.close()

        return

    def getProjectPath(self):
        if self.tableExists('project'):
            projectPath = self.cursor.execute("select project_path from project").fetchone() #returns a tuple
            if projectPath is not None:
                return projectPath[0]

    def getProject(self):
        if self.tableExists('project'):
            project = self.cursor.execute("select project_name from project").fetchone()
            if project is not None:
                return project[0]
        return None

    def tableExists(self, table):
        try:
            self.cursor.execute("select * from " + table + " limit 1").fetchall()
        except Exception as e:
            e
            return False
        return True

    def createRefTable(self, tablename):
        self.cursor.execute("DROP TABLE  If EXISTS " + tablename)
        self.cursor.execute("""
        CREATE TABLE """ + tablename +
                            """( 
                            _id integer primary key,
                            sort_order integer,
                        code text unique,
                        description text);
                            """
                            )
        self.connection.commit()

    #String, ListOfTuples -> None
    def addRefValues(self, tablename, values):
        self.insertRecord(tablename,['sort_order','code','description'],values)

    def makeComponents(self):
        '''Uses the information in the project_manager database to make a list of Component Objects
        :return List of component objects'''
        loi = self.cursor.execute("SELECT componentnamevalue,component.componenttype,componentattributevalue,componentattributeunit from component_files join component on component_files.component_id = component._id where inputfile_id != -1 group by componentnamevalue, component.componenttype, componentattributevalue")
        loc = []
        for t in loi:
            try:
                c = Component(component_name=t[0],type=t[1],attribute=t[2],units=t[3],column_name=t[0]+t[2],scale=1,offset=0)
                loc.append(c)
            except TypeError as e:
                print("you must fill in all fiels to generate component netcdf files")

        return loc
    #makes the default database associated with every new project.
    def makeDatabase(self):
        print('Making default database')
        refTables = [
            'ref_component_attribute',
            'ref_component_type',
            'ref_date_format',
            'ref_time_format',
            'ref_data_format',
            'ref_power_units',
            'ref_attributes',
            'ref_time_units',
            'ref_speed_units',
            'ref_flow_units',
            'ref_voltage_units',
            'ref_current_units',
            'ref_irradiation_units',
            'ref_temperature_units',
            'ref_true_false',
            'ref_env_attributes',
            'ref_frequency_units',
            'ref_file_type'
        ]
        for r in refTables:
            self.createRefTable(r)
        #the time units table gets an extra field for converting time to seconds
        self.cursor.executescript("ALTER TABLE ref_time_units ADD COLUMN multiplier DOUBLE")
        #various file types can be read in through the user interface
        #TODO update wiki to add file conventions for reading in the various file types.
        self.addRefValues('ref_file_type',[(0,'CSV','Comma Seperated Values'),
                                           (1,'MET','MET text file'),
                                           (2,'TXT','Tab delimited'),
                                           (3, 'nc', 'netCDF'),])
        self.addRefValues('ref_current_units',[(0,'A','amps'),(1,'kA','kiloamps')])
        self.addRefValues('ref_frequency_units',[(0, 'Hz','hertz')])
        self.addRefValues('ref_temperature_units',[(0,'C','Celcius'),(1,'F','Farhenheit'),(2,'K','Kelvin')])
        self.addRefValues('ref_irradiation_units',[(0,'W/m2','Watts per square meter')])
        self.addRefValues('ref_flow_units',[(0,'m3/s', 'cubic meter per second'),(1, 'L/s', 'liters per second'),
                                            (2, 'cfm', 'cubic feet per meter'),(3,'gal/min','gallon per minute'),(4, 'kg/s', 'killograms per second')])
        self.addRefValues('ref_voltage_units',[(0,'V','volts'),(1, 'kV','kilovolts')])
        self.addRefValues('ref_true_false',[(0,'T','True'),(1,'F','False')])
        self.addRefValues('ref_speed_units', [(0, 'm/s','meters per second'),(1,'ft/s','feet per second'),
                                              (2,'km/hr','kilometers per hour'),(3,'mi/hr','miles per hour')])
        self.insertRecord('ref_time_units',['sort_order','code','description','multiplier'],[(0,'S','Seconds',1),(1,'m','Minutes',0.01667),(2,'ms','Milliseconds',0.001)])
        self.addRefValues('ref_date_format',[(0,'MM/DD/YY','(0[0-9]|1[0-2])/[0-3][0-9]/[0-9]{2}'),(1,'MM/DD/YYYY','(0[0-9]|[0-9]|1[0-2])/([0-3][0-9]|[0-9])/[0-9]{4}'),
                                                 (2,'YYYY/MM/DD','[0-9]{4}/(0[0-9]|1[0-2])/[0-9]{2}'),(3,'DD/MM/YYYY','[0-9]{2}/(0[0-9]|1[0-2])/[0-9]{4}'),
                                             (4, 'MM-DD-YY', '(0[0-9]|1[0-2])-[0-3][0-9]-[0-9]{2}'), (5, 'MM-DD-YYYY', '(0[0-9]|1[0-2])-[0-3][0-9]-[0-9]{4}'),
                                             (6, 'YYYY-MM-DD', '[0-9]{4}-(0[0-9]|1[0-2])-[0-9]{2}'), (7, 'DD-MM-YYYY', '[0-9]{2}-(0[0-9]|1[0-2])-[0-9]{4}'),
                                             (8, 'mon dd yyyy', '[a-z |A-z]{3} [0-9]{2} [0-9]{4}'),
                                             (9, 'days', '[0-9]+[.][0-9]+'),(10, 'seconds','[0-9]+')
                                                 ])
        self.addRefValues('ref_time_format',[(0,'HH:MM:SS','([0-9]|[0-2][0-9]):[0-5][0-9]:[0-5][0-9]'),(1,'HH:MM','([0-9]|[0-2][0-9]):[0-5][0-9]'),
                                             (2,'hours','[0-2][0-4][.]*[0-9]*'),
                                                 (3,'minutes','[0-6][0-9][.]*[0-9]*'),(4,'full seconds','[0-6][0-9]')
                                                 ])

        self.addRefValues('ref_data_format',[(0,'components + MET', 'Load and component data are seperate from wind data'),
                                             (1,'components', 'All component, load and environemtnal data is within a single timeseries file'),
                                             (2, 'component + load + environment', 'Seperate files for load, component and wind data.')
                            ])

        self.addRefValues('ref_component_type' ,[(0,'wtg', 'windturbine'),
        (1,'gen', 'diesel generator'), (2,'inv','inverter'),(3,'tes','thermal energy storage'),
                                                 (4, 'ees','energy storage'),(5, 'load', 'total load')])

        self.addRefValues('ref_power_units',[(0,'W', 'watts'), (1,'kW', 'Kilowatts'),(2,'MW','Megawatts'),
                                             (3, 'var', 'vars'),(4,'kvar','kilovars'),(5,'Mvar','Megavars'),
                                             (6, 'VA','volt-ampere'),(7,'kVA','kilovolt-ampere'),(8,'MVA','megavolt-ampere'),(9, 'pu',''),(10,'PU',''),(11,'PU*s','')])

        self.addRefValues('ref_attributes' ,[(0,'P', 'Real Power'), (1,'Q','Reactive Power'),(2,'S','Apparent Power'),
                                             (3,'PF','Power Factor'),(4,'V','Voltage'),(5, 'I', 'Current'),
                                             (6, 'f', 'Frequency'), (7,'TStorage','Internal Temperature Thermal Storage'),
                                             (8,'PAvail','Available Real Power'), (9,'QAvail','Available Reactive Power'),
                                             (10,'SAvail','Available Apparent Power'),(11,'WS', 'Windspeed'), (12,'IR', 'Solar Irradiation'),
                                                 (13,'WF','Waterflow'),(14,'Tamb','Ambient Temperature')])


        #merge unit reference tables
        self.cursor.execute("DROP TABLE IF EXISTS ref_units")
        self.cursor.executescript("CREATE TABLE ref_units (_id integer primary key, code text unique, description text)")
        unit_tables_tuple = self.cursor.execute("select name from sqlite_master where type = 'table' and name like '%units'").fetchall()
        for u in unit_tables_tuple:
            self.cursor.execute("INSERT INTO ref_units(code, description) SELECT code, description from " + u[0] + " Where code not in (select code from ref_units)")

        self.connection.commit()
        #project table
        self.cursor.execute("DROP TABLE IF EXISTS project")
        self.cursor.executescript("""CREATE TABLE project
        (_id  integer primary key,
        project_path text,
        project_name text,
        setupfile text);""")

        #component files contains information for loading component data
        #components can have different units, scale and offset in their input files than in their output files
        self.cursor.execute("DROP TABLE IF EXISTS component_files")
        self.cursor.executescript("""CREATE TABLE component_files
         (_id integer primary key,
         inputfile_id text,
         headernamevalue text,
         componenttype text,
         component_id integer,
         componentattributeunit text,
         componentattributevalue text,
         componentscale double,
         componentoffset double,
         UNIQUE (inputfile_id,component_id),
         FOREIGN KEY (componentattributeunit) REFERENCES ref_universal_units(code),
         FOREIGN KEY (componentattributevalue) REFERENCES ref_attributes(code)
         );""")
        self.connection.commit()


        #component contains information that is relevant to the loaded component data
        self.cursor.execute("DROP TABLE IF EXISTS component")
        self.cursor.executescript("""CREATE TABLE component
                 (_id integer primary key,
                 componenttype text,
                 componentnamevalue text UNIQUE,
                 FOREIGN KEY (componenttype) REFERENCES ref_component_type(code)
                 );""")
        self.connection.commit()

        self.cursor.execute("DROP TABLE IF EXISTS set_components")
        self.cursor.executescript("""
        CREATE TABLE IF NOT EXISTS set_components
        (_id integer primary key,
        set_id integer , 
        component_id integer,
        tag text NOT NULL,
        tag_value text NOT NULL,
        UNIQUE (set_id, component_id, tag,tag_value));""")


        self.cursor.execute("DROP TABLE IF EXISTS input_files")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS input_files
                (_id integer primary key,
                project_id integer,
                inputfiletypevalue text , 
                datatype text ,
                inputfiledirvalue text,
                inputtimestepvalue text,
                inputtimestepunit text,
                datechannelvalue text,
                datechannelformat text,
                timechannelvalue text,
                timechannelformat text,
                includechannels text,
                timezonevalue text,
                usedstvalue text,
                flexibleyearvalue text,
                inpututcoffsetvalue integer,
                UNIQUE(inputfiledirvalue),
                FOREIGN KEY (timechannelformat) REFERENCES ref_time_format(code),
                FOREIGN KEY (datechannelformat) REFERENCES ref_date_format(code));""")

        #The table optimize input only contains parameters that were changed from the default
        self.cursor.execute("Drop TABLE IF EXISTS optimize_input")
        self.cursor.executescript("""
                     CREATE TABLE IF NOT EXISTS optimize_input
                     (_id integer primary key,
                     parameter text,
                     parameter_value text);""")

        self.cursor.execute("DROP TABLE IF EXISTS set_")
        self.cursor.executescript("""
                               CREATE TABLE IF NOT EXISTS set_
                               (_id integer primary key,
                               project_id integer,
                               set_name unique,
                               date_start text,
                               date_end text,
                               timestepvalue integer,
                               timestepunit text,
                               runtimestepsvalue
                               );""")
        self.cursor.execute("DROP TABLE IF EXISTS pretty_names")
        self.cursor.executescript("""
                        CREATE TABLE IF NOT EXISTS pretty_names(
                        _id interger PRIMARY KEY,
                        table_name text,
                        field text,
                        pretty_name text,
                        UNIQUE (table_name,field)
                        )""")

        self.cursor.execute("DROP TABLE IF EXISTS run")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS run
                (_id integer primary key,
                set_id integer NOT NULL ,
                run_num text NOT NULL,
                base_case integer,
                started text,
                finished text,
                genptot text,
                genpch text,
                gensw text,
                genloadingmean text,
                gencapacitymean text,
                genfuelcons text,
                gentimeoff text,
                gentimeruntot text,
                genruntimeruntotkwh text,
                genoverloadingtime text,
                genoverLoadingkwh text,
                wtgpimporttot text,
                wtgpspilltot text,
                wtgpchtot text,
                eesspdistot text,
                eesspchtot text,
                eesssrctot text,
                eessoverloadingtime text,
                eessoverloadingkwh text,
                tessptot text,
                UNIQUE (set_id, run_num));""")


        self.cursor.execute("DROP TABLE IF EXISTS run_attributes")
        self.cursor.executescript("""
                        CREATE TABLE IF NOT EXISTS run_attributes
                        (_id integer primary key,
                        run_id integer NOT NULL ,
                        set_component_id text NOT NULL,
                        UNIQUE (run_id, set_component_id));""")

        #The setup table contains information used for reading in data files
        #setup should only ever have 1 record with an _id = 1
        self.cursor.execute("DROP TABLE IF EXISTS setup")
        self.cursor.executescript("""
                        CREATE TABLE IF NOT EXISTS setup
                        (_id integer primary key,
                        project_id integer,
                        date_start text,
                        date_end text,
                        timestepvalue integer,
                        timestepunit text,
                        runtimestepsvalue
                        );""")



        self.connection.commit()
    def clearTable(self,table):
        self.cursor.execute("Delete From " + table)
        self.connection.commit()
    def getSetupDateRange(self):
        '''

        :return: start and end are string datetime values in the start and end date fields in the setup table
        '''

        start = self.cursor.execute("select date_start from setup").fetchone()
        end = self.cursor.execute("select date_end from setup").fetchone()

        return start[0],end[0]
    def insertFirstSet(self,dict):
       self.insertDictionaryRow(SETTABLE,dict)
    def insertAllComponents(self,setName):
         self.cursor.execute("INSERT OR IGNORE INTO set_components (set_id, component_id, tag, tag_value) "
                             "SELECT set_._id, component._id,'None','None' FROM component, set_ "
                             "where set_.set_name = '" + setName + "'")
         self.connection.commit()
    def convertToSeconds(self,value,currentUnits):
        '''uses the multiplier field in ref_time_units to convert a value to seconds'''
        multiplier = self.getFieldValue('ref_time_units','multiplier','code',currentUnits)
        return round(value * multiplier,0)
    def getSetInfo(self,setName = 'set0'):
        '''
        Creates a dictionary of setup information for a specific set, default is set 0 which is the base case
        :param setName: String name of the set to get information for
        :return: dictionary of xml tags and values to be written to a setup.xml file
        '''
        setDict = {}


        def asDatasetIndex(value):
            '''
            The netcdf record index corresponding to a time in seconds since 1970-01-01.
            The index position is calculated based on the dateset start point as specified in the setup table.
            :param value:
            :return:
            '''
            if value == None:
                return value

            startPoint = asDate(self.getFieldValue(SETUPTABLE,STARTDATE,ID,'1'))
            if startPoint == None:
                #if there is not start date information we can't identify the position so None is returned
                return None
            dateDiff = pd.to_timedelta(startPoint - asDate(value),unit='s')
            if dateDiff < pd.to_timedelta('0 s'):
                dateDiff = pd.to_timedelta('0 s')
            interval = self.getFieldValue(SETUPTABLE,self.dbName(TIMESTEP),ID,1)
            record_position = dateDiff / interval
            return record_position

        #get tuple for basic set info
        values = self.cursor.execute("select project_name, timestepvalue, timestepunit, date_start, date_end,runtimestepsvalue from set_ join project on set_.project_id = project._id WHERE LOWER(set_name) = '" + setName.lower() + "'").fetchone()
        if values is not None:
            setDict[PROJECTNAME] = values[0]
            setDict[TIMESTEP] = str(values[1])
            setDict[TIMESTEPUNIT]=values[2]
            setDict[STARTDATE] = values[3]
            setDict[ENDDATE] = values[4]
            start = asDatasetIndex(str(values[3]))
            if start != None:
                setDict[RUNTIMESTEPS] = " ".join([str(asDatasetIndex(str(values[3]))),str(asDatasetIndex(str(values[4])))])
            else:
                setDict[RUNTIMESTEPS] = str(values[5])
            #as long as there was basic set up info look for component setup info
            #componentNames is a list of distinct components, order does not matter
            compTuple =  self.cursor.execute("SELECT group_concat(componentnamevalue,',') FROM "
                                                                   "(SELECT DISTINCT componentnamevalue as componentnamevalue FROM component "
                                                                   "JOIN set_components on component._id = set_components.component_id JOIN set_ "
                                                                   "on set_components.set_id = set_._id WHERE lower(set_name) = ? )", [setName.lower()]).fetchall()[0]
            setDict[COMPONENTNAMES] = compTuple[0]
        else:
            return None

        return setDict
    def encloseSpaces(thisString):
        if isinstance(thisString,str):
            if ' ' in thisString:
                return "'%s'" % thisString
        return thisString

    def getSetUpInfo(self):
        '''
        Creates a dictionary of setup information, default is set 0 which is the base case
        :return: dictionary of xml tags and values to be written to a setup.xml file
        '''
        setDict = {}

        #get tuple for basic set info
        values = self.cursor.execute("select project_name, timestepvalue, timestepunit, date_start, date_end from setup join project on setup.project_id = project._id").fetchone()
        if values is not None:
            setDict[PROJECTNAME] = values[0]
            setDict[TIMESTEP] = values[1]
            setDict[TIMESTEPUNIT]=values[2]
            setDict[STARTDATE] = values[3]
            setDict[ENDDATE] = values[4]
            setDict[RUNTIMESTEPS] = str(values[3]) + " " + str(values[4])
            #as long as there was basic set up info look for component setup info
            #componentNames is a list of distinct components, order does not matter
            setDict[COMPONENTNAMES] =  self.getComponentNames()

            #componentChannels has ordered lists for directories and the components they contain. A component can have data in more than one directory and file type, in which case it would
            #be listed more than once in componentChannels
            #We use a left join for input files to components so the input file directories will still get listed even if no components have been added
            # values = self.cursor.execute(
            # "select group_concat(COALESCE(REPLACE(inputfiledirvalue,' ','_'),'None'),' '), group_concat(COALESCE(REPLACE(inputfiletypevalue,' ','_'),'None'),' '),group_concat(componentnamevalue,' '),"
            # "group_concat(REPLACE(headernamevalue,' ','_'),' '),group_concat(REPLACE(componentattributevalue,' ',' '), ' '), group_concat(REPLACE(componentattributeunit,' ',' '), ' '),group_concat(COALESCE(REPLACE(datechannelvalue,' ','_'),'None'), ' '),group_concat(COALESCE(REPLACE(timechannelvalue,' ','_'),'None'),' '),"
            # "group_concat(COALESCE(REPLACE(datechannelformat,' ','_'),'None'), ' '),group_concat(COALESCE(REPLACE(timechannelformat,' ','_'),'None'), ' '), "
            # "group_concat(COALESCE(REPLACE(timezonevalue,' ','_'),'None'), ' '), group_concat(COALESCE(REPLACE(usedstvalue,' ','_'),'None'), ' '), group_concat(COALESCE(REPLACE(inpututcoffsetvalue,' ','_'),'None'), ' '), group_concat(COALESCE(REPLACE(flexibleyearvalue,' ','_'),'None'), ' ') "
            # "from input_files Left JOIN "
            # "(select component._id as component_id, inputfile_id, COALESCE(REPLACE(componentnamevalue,' ','_'),'None') as componentnamevalue, COALESCE(REPLACE(headernamevalue,' ',' '),'None') as headernamevalue, COALESCE(REPLACE(componentattributevalue,' ','_'),'None') as componentattributevalue, COALESCE(componentattributeunit,'None') as componentattributeunit from component_files "
            # "LEFT JOIN component on component._id = component_files.component_id ORDER BY component_id ) as components"
            # " ON components.inputfile_id = input_files._id ORDER BY input_files._id").fetchone()
            # #These are the input file specific info - should be none if data not entered
            values = self.cursor.execute(
            "select group_concat(COALESCE(inputfiledirvalue,'None'),';'), group_concat(COALESCE(inputfiletypevalue,'None'),';'),group_concat(componentnamevalue,';'),"
            "group_concat(headernamevalue,';'),group_concat(componentattributevalue, ';'), group_concat(componentattributeunit, ';'),group_concat(COALESCE(datechannelvalue,'None'), ';'),group_concat(COALESCE(timechannelvalue,'None'),';'),"
            "group_concat(COALESCE(datechannelformat,'None'), ';'),group_concat(COALESCE(timechannelformat,'None'), ';'), "
            "group_concat(COALESCE(timezonevalue,'None'), ';'), group_concat(COALESCE(usedstvalue,'None'), ';'), group_concat(COALESCE(inpututcoffsetvalue,'None'), ';'), group_concat(COALESCE(flexibleyearvalue,'None'), ';') "
            "from input_files Left JOIN "
            "(select component._id as component_id, inputfile_id, COALESCE(componentnamevalue,'None') as componentnamevalue, COALESCE(headernamevalue,'None') as headernamevalue, COALESCE(componentattributevalue,'None') as componentattributevalue, COALESCE(componentattributeunit,'None') as componentattributeunit from component_files "
            "LEFT JOIN component on component._id = component_files.component_id ORDER BY component_id ) as components"
            " ON components.inputfile_id = input_files._id ORDER BY input_files._id").fetchone()
            #values are ';' seperated at this point and need to be parsed to xml format
            if values is not None:
                setDict[FILEDIR] = stringToXML(values[0].split(';'))
                setDict[FILETYPE] = stringToXML(values[1].split(';'))
                setDict['componentChannels.' + COMPONENTNAME]= stringToXML(values[2].split(';'))
                setDict['componentChannels.' + HEADERNAME] = stringToXML(values[3].split(';'))
                setDict['componentChannels.' + COMPONENTATTRIBUTE] = stringToXML(values[4].split(';'))
                setDict['componentChannels.' + COMPONENTATTRIBUTEUNIT] = stringToXML(values[5].split(';'))
                setDict[DATECHANNEL]=stringToXML(values[6].split(';'))
                setDict[DATECHANNELFORMAT] = stringToXML(values[8].split(';'))
                setDict[TIMECHANNEL] = stringToXML(values[7].split(';'))
                setDict[TIMECHANNELFORMAT] = stringToXML(values[9].split(';'))
                setDict[TIMEZONE] =  stringToXML(values[10].split(';'))
                setDict[DST] = stringToXML(values[11].split(';'))
                setDict[UTCUNIT]  ='hr'
                setDict[UTCOFFSET]=stringToXML(values[12].split(';'))
                setDict[FLEXIBLEYEAR]=stringToXML(values[13].split(';'))

        else:
            return None

        return setDict
    def getNewSetInfo(self,setName):
        '''
        returns dictionary for attributes that are changed between an original setup file and a setup file for a setInfo
        :return: Dictionary of attributes that have new values
        '''
        setInfo = self.getSetInfo(setName)
        setup = self.getSetUpInfo()

        for k in list(setInfo.keys()):
            if (setInfo[k] == setup[k]) | (setInfo[k]=='None') | (setInfo[k]==None) :
                del setInfo[k]
        if STARTDATE in setInfo.keys():
            del setInfo[STARTDATE]
        if ENDDATE in setInfo.keys():
            del setInfo[ENDDATE]
        return setInfo
    def updateSetSetup(self, setName, setupDict):
        '''Update the set_ table for a specific set and make sure all set components are in the set_component table'''

        def asDatasetDateTime(value):
            '''values from set setup xml files are integer positions for records in netcdf files
            To convert to datetime we need to know where the set dataset starts in relation to the start
            in the setup file and the timestep interval
            :param value is a integer index position'''
            startPoint = asDate(self.getFieldValue(SETUPTABLE, STARTDATE, ID, '1')) #the start date of all generated netcdf files
            if startPoint is None:
                return None
            try:
                intervals = int(value)/int(self.getFieldValue(SETUPTABLE, self.dbName(TIMESTEP), ID, '1'))
            except ValueError as e:
                return startPoint
            currentDateTime = asDate(startPoint) + pd.to_timedelta(intervals, unit='s') #seconds between the start position and value
            return currentDateTime

        # update fields that are in the set table
        try:
            #set setup files only store record positions for runTimeSteps.
            #these need to be converted to datetimes for display and storing in datatable
           startdate = asDatasetDateTime(setupDict[RUNTIMESTEPS].split(" ")[0])
           enddate = asDatasetDateTime(setupDict[RUNTIMESTEPS].split(" ")[1])
        except IndexError as i:
            print("runtimesteps not start stop indices")
            startdate = asDatasetDateTime(setupDict[RUNTIMESTEPS])
            enddate = asDatasetDateTime(setupDict[RUNTIMESTEPS])
        #if the record already exists a -1 will be returned and updateRecord is run
        setId = self.insertRecord(SETTABLE,
                                  [self.dbName(TIMESTEPUNIT), self.dbName(TIMESTEP), self.dbName(RUNTIMESTEPS), STARTDATE, ENDDATE,
                                   'project_id',SETNAME],
                                  [setupDict[TIMESTEPUNIT], setupDict[TIMESTEP],
                                   setupDict[RUNTIMESTEPS], startdate, enddate, 1,setName])
        if setId == -1:
            self.updateRecord(SETTABLE,[SETNAME],[setName],
                                  [self.dbName(TIMESTEPUNIT), self.dbName(TIMESTEP), self.dbName(RUNTIMESTEPS), STARTDATE, ENDDATE],
                                  [setupDict[TIMESTEPUNIT], setupDict[TIMESTEP],setupDict[RUNTIMESTEPS], startdate, enddate])

        return
    def updateSetComponents(self,setName,loc):
        '''
        adds components listed in loc to the set_component table for the specified set and
        removes any components present that are not in loc. Tag is always None as this is base components for a set
        :param setName: String name of the set found in set_ table set_name column
        :param loc: List of String names of components to add to the set_component table
        :return: None
        '''
        setid = self.getSetId(setName)
        #the [0][0] notation is required because getId returns a list of tuples. We want the first item in the list
        # and first item in the tuple (which is only 1 item long)
        compid = [self.getId(COMPONENTTABLE,[self.dbName(COMPONENTNAME)],[c]) for c in loc]
        fields = [COMPONENTID,SETID,TAG,TAGVALUE]
        values =[(str(x),setid,'None','None') for x in compid]
        if len(values) <=0: #if values are empty then set has no components
            self.cursor.execute("DELETE FROM set_components WHERE set_id = ?", [setid])
        else:
            deleters =  "(" + ",".join([str(x) for x in filter(None, compid)]) + ")"

            self.cursor.execute("DELETE FROM set_components WHERE set_id = ? AND component_id not in " + deleters , [setid]) #AND component_id not in ('1','2')"
        self.insertRecord(SETCOMPONENTTABLE,fields,values)
        self.connection.commit()
        return
    def insertSetComponentTags(self,setName,lot):
        '''update tags in set_components with an attributeDictionary
        :param lot: is a list of tuples of the order name,tag,attr,value
        The value position of the tuple is sometimes a list, in which case it needs to be cycled through
        :return: None
        '''
        [self.insertTagRecord(t,self.getSetId(setName))for t in lot]
        return

    def insertTagRecord(self,record,setId):
        if isinstance(record[3],list):
            [self.insertRecord(SETCOMPONENTTABLE, [SETID, COMPONENTID, TAG, TAGVALUE],
                              [setId, record[0], record[1] + "." + record[2], v]) for v in record[3]]

        else:
            self.insertRecord(SETCOMPONENTTABLE, [SETID, COMPONENTID, TAG, TAGVALUE],[setId, record[0], record[1] + "." + record[2], record[3]])
    def insertRecord(self, table, fields, values):
        '''
        Insert a record in a specified table
        :param table: String name of the table to insert a record in
        :param fields: List of String field names
        :param values: List of values in to insert into fields
        :return: Integer id of last row inserted, if failed returns -1
        '''

        #if values is a list of values execue many
        string_fields = ','.join(fields)
        string_values = ','.join('?' * len(values))
        try:
            if isinstance(values[0], tuple):
                string_values = ','.join('?' * len(values[0]))
                self.cursor.executemany(
                    "INSERT OR REPLACE INTO " + table + "(" + string_fields + ")" + "VALUES (" + string_values + ")", values)

            else:
                self.cursor.execute("INSERT INTO " + table + "(" + string_fields + ")" + "VALUES (" + string_values + ")", values)
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(e)
            return -1
    def fetchIds(self,table,keyField,keyValue):
        ''' get the id of the first record with a keyField equal to the specified keyValue
        :param table: String name of the table to query
        :param keyField: List of String name of the table column to match
        :param keyValue: List of String value to find in the table
        :return: integer, -1 if a matching record is not found'''

        keyFields = ' AND '.join([str(a) + " = '" + str(b) + "'" for a, b in zip(keyField, keyValue)])
        lot = self.cursor.execute("SELECT _id from " + table + " WHERE " + keyFields).fetchall()
        if lot:
            return [i[0] for i in lot] #this makes it a list of ids
        else:
            return [-1]
    def getId(self,table,keyField,keyValue):
        '''returns only the first id found by a call to fetchIds'''
        return self.fetchIds(table,keyField,keyValue)[0]

    def getRuns(self,set_id):
        componentsInSet = self.getSetComponents(set_id)
        sqlStatement = self.createStatements(componentsInSet,set_id)
        set_component_combos = self.cursor.execute(sqlStatement).fetchall()
        return set_component_combos

    def getSetComponents(self, set_id):
        '''produces a list of component id's for a given set'''
        componentsInSet = self.cursor.execute("SELECT _id from component WHERE _id in "
                                          "(SELECT component_id FROM set_components WHERE set_id = ?) GROUP BY _id",
                                          [set_id]).fetchall()
        return componentsInSet

    def getSetComponentNames(self, setName ='Set0'):
        '''
        returns a list of names for components in the set_components table. Defaults to set0
        :param setName: String name of the set
        :return: list of string component names
        '''

        names = self.cursor.execute("select componentnamevalue from component JOIN set_components on component._id = set_components.component_id where "
                                    " set_id = (SELECT _id from set_ where set_name = '" + setName + "')").fetchall()
        if len(names) >0:
            names = [''.join(i) for i in names if i is not None]
            return pd.Series(names).tolist()
        return []
    def getSetComponentTags(self,set_id):
        lot = self.cursor.execute("SELECT _id from set_components where set_id = ? and tag_value != 'None' ",[set_id]).fetchall()
        return [self.getRecordDictionary(SETCOMPONENTTABLE,i[0]) for i in lot]
    def createStatements(self,componentList,setId):

        selectStatements = [self.createComponentStatement(c[0],setId) for c in componentList]
        selectStatements = sum(selectStatements, [])

        finalStatement ="SELECT * FROM " + ",".join(selectStatements)

        return finalStatement
    def createComponentStatement(self,compId,setId):
        def makeIntoStatement(tag):
            return  "Select _id FROM set_components WHERE set_id = " + str(setId) + " AND component_id = "+str(compId)+\
            " And tag = '" + str(tag[0] + "'")

        p = self.cursor.execute("SELECT tag from set_components where set_id = ? AND component_id = ? GROUP BY tag",
                                [str(setId),str(compId)]).fetchall()
        statements =  ["(" + makeIntoStatement(x) + ")" for x in p if x[0] != 'None']
        return statements
    def getFieldValue(self, table, wantedField, keyField, keyValue):
        ''' get the id of the first record with a keyField equal to the specified keyValue
        :param table: String name of the table to query
        :param wantedField: String name of the field to extract a value from
        :param keyField: String name of the table column to match
        :param keyValue: String value to find in the table
        :return: String, None if a matching record is not found'''
        try:
            i = self.cursor.execute("SELECT " + wantedField + " from " + table + " WHERE " + keyField + " = ?",[keyValue]).fetchone()
        except Exception as e:
            print(e)
            i = None
        finally:
            if i is not None:
                return str(i[0])
            else:
                return None
    def updateRecord(self,table, keyField,keyValue,fields,values):
        '''
        Update the fields for a specific record in a table. The record is identified by its keyField with the specified keyValue
        :param table: String table name of the table containing the record to update
        :param keyField: List of String name of the field containing the record identifier
        :param keyValue: List of Value to find in the keyField; records with this value in thier key field will be updated
        :param fields: List of String field names to update
        :param values: List of values to replace in respective fields
        :return: Boolean True if successfully updated
        '''
        updateFields = ', '.join([str(a) + " = '" + str(b) + "'" for a,b in zip(fields,values)])

        keyFields = ' AND '.join([str(a) + " = '" + str(b) + "'" for a,b in zip(keyField,keyValue)])
        try:
            self.cursor.execute("UPDATE " + table + " SET " + updateFields + " WHERE " + keyFields )
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            print(type(e))

            return False
        return

    def getRefInput(self, tables):
        '''
        returns a string that combines code and descriptor columns from a reference table into a single '-' sepearted string
        :param tables: List of tables to include in the list
        :return: a list of '-' seperated code and description columns from a reference table
        '''
        #table is a list of tables

        # create list of values for a combo box
        valueStrings = []
        for t in tables:
            values = pd.read_sql_query("SELECT code, description FROM " + t + " ORDER By sort_order", self.connection)

            for v in range(len(values)):
                valueStrings.append(values.loc[v, 'code'] + ' - ' + values.loc[v, 'description'])
        return valueStrings

    def getTypeCount(self,componentType):
        import re
        ''' finds the count of a specific component type within a project
        :param componentType: the type of component to get a count for
        :return integer count of a component type
        '''
        #get the highest component name (biggest number)
        finalName = self.cursor.execute("SELECT componentnamevalue FROM component where componenttype = '" + componentType + "' ORDER BY componentnamevalue DESC").fetchone()
        if finalName is not None:
            finalName=finalName[0]
            #extract the numbers in the name
            count = re.findall(r'\d+',finalName)
            #if there is more than one number use only the last number and add 1 to it
            #if there aren't any other components of that type return 0
            if len(count) > 0:
                count = int(count[0])
                return count +1
        return 0

    def dataCheck(self,table):
       '''
       Retrieve all the records from a table
       :param table: String name of the table to retrieve records from
       :return: List of tuples, each tuple is a record
       '''
       data = self.cursor.execute("SELECT * FROM " + table).fetchall()
       return data
    def updateFromDictionaryRow(self,tablename,rowDict,keyField,keyValue):
        '''
               Update the fields for a specific record in a table. The record is identified by its keyField with the specified keyValue
               :param tablename: String table name of the table containing the record to update
               :param rowDict: A single row of values where dictionary keys match columns and values that will be inserted
               :param keyField: List of String name of the field containing the record identifier
               :param keyValue: List of Value to find in the keyField; records with this value in thier key field will be updated
               :return: Boolean True if successfully updated
               '''
        #all column are lower case and can't have ., so make dictionary keys conform
        #all values need to be strings
        dict = {self.dbName(key): stringToXML(str(value).split(' ')) for key, value in rowDict.items() }
        updateFields = ', '.join([k + " = '" + str(dict[k]) + "'" for k in dict.keys()])

        keyFields = ' AND '.join([str(a) + " = '" + str(b) + "'" for a, b in zip(keyField, keyValue)])
        try:
            self.cursor.execute("UPDATE " + tablename + " SET " + updateFields + " WHERE " + keyFields)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            print(type(e))

            return False
        return

    def insertDictionaryRow(self,tablename, dict):
        '''
        Inserts a dictionary of values into a project_manager table.
        Dictionary is assumed to have keys that match column names and hold orderd lists of values corresponding to each row to be inserted
        :param tablename: String name of the table to insert records into
        :param dict: a dictionary of colums and values as lists
        :return:
        '''

        def maxLength(dict):
            m = 0
            for k in dict.keys():
                if isinstance(dict[k],list):
                    if len(dict[k]) > m:
                        m = len(dict[k])
            return m

        def replaceNone(val):
            if len(val) <= 0:
                return 'None'
            else:
                return val

        ml = maxLength(dict)
        keys = ','.join(dict.keys())
        question_marks = ','.join(list('?' * len(dict.keys())))

        values = list(tuple(zip(*dict.values())))
        ids = []
        for v in values: #need to loop so we get ids for every value
            try:
                self.cursor.execute('INSERT INTO ' + tablename + ' (' + keys + ') VALUES (' + question_marks + ')',v ) #if insertion fails the last id gets re-appended to the list
                self.connection.commit()
                ids.append(self.cursor.lastrowid)
            except lite.IntegrityError as e:
                oldid = self.getId(tablename,keys.split(','),list(v))
                if oldid == -1:
                    oldid = self.getId(tablename,keys.split(','),[replaceNone(val) for val in list(v)])
                ids.append(oldid)
            except Exception as e:
                pass


        if ml > len(self.getAllRecords(tablename)):
            print ('Information was missing for some records')
        return ids
    def insertFileDictionaryRow(self,tablename, dict):
        '''
        Inserts a dictionary of values into a project_manager table.
        Dictionary is assumed to have keys that match column names and hold orderd lists of values corresponding to each row to be inserted
        :param tablename: String name of the table to insert records into
        :param dict: a dictionary of colums and values as lists
        :return:
        '''

        def maxLength(dict):
            m = 0
            for k in dict.keys():
                if isinstance(dict[k],list):
                    if len(dict[k]) > m:
                        m = len(dict[k])
            return m

        def replaceNone(val):
            if len(val) <= 0:
                return 'None'
            else:
                return val

        ml = maxLength(dict)
        keys = ','.join(dict.keys())
        question_marks = ','.join(list('?' * len(dict.keys())))

        values = list(tuple(zip(*dict.values())))
        ids = []
        for v in values: #need to loop so we get ids for every value
            try:
                self.cursor.execute('INSERT INTO ' + tablename + ' (' + keys + ') VALUES (' + question_marks + ')',v ) #if insertion fails the last id gets re-appended to the list
                self.connection.commit()
                ids.append(self.cursor.lastrowid)
            except lite.IntegrityError as e:
                oldid = self.getId(tablename,['inputfiledirvalue'],[v[0]])
                ids.append(oldid)
            except Exception as e:
                pass


        if ml > len(self.getAllRecords(tablename)):
            print ('Information was missing for some records')
        return ids
    def updateComponent(self, dict):
        ''' updates a component record with values in the dictionary
        :param dict: a dictionary containing at least the attribute 'component_name' and one other attribute that matches a field name in the component table'''
        for k in [key for key in dict.keys() if key != self.dbName(COMPONENTNAME)]:
            try:
                self.cursor.execute("UPDATE component_files SET " + k + " = ? WHERE component_id = (SELECT _id from component WHERE componentnamevalue = ?)", [dict[k],dict[self.dbName(COMPONENTNAME)]])
            except Exception as e:
                print(e)
                print('%s column was not found in the data table' %k)
                continue
        self.connection.commit()

    def writeComponent(self,componentDict):
        '''
        determines if a component record needs to be created or updated and implements the correct function
        :param componentDict:
        :return: Boolean True if the records is new and was added to the table
        '''
        if len(self.cursor.execute("SELECT * FROM component where componentnamevalue = ?", [componentDict['component_name']]).fetchall()) > 0:
            self.updateComponent(componentDict)
        else:
            self.cursor.execute('INSERT INTO component (componentnamevalue) VALUES (?)', [componentDict['component_name']])
            self.connection.commit()
            self.updateComponent(componentDict)
            return True
        return False

    def getCodes(self,table):
        '''
        retrieves the code values from a table
        :param table: String name of a table containing the field 'code'
        :return: List of Strings
        '''

        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes

    def getComponentNames(self):
        '''
        returns a list of names for components in the components table.
        :return: list of string component names
        '''

        names = self.cursor.execute("select componentnamevalue from component").fetchall()
        if len(names) >0:
            names = [''.join(i) for i in names if i is not None]
            return pd.Series(names).tolist()
        return []

    def getSetComponentNames(self, setName ='Set0'):
        '''
        returns a list of names for components in the set_components table. Defaults to set0
        :param setName: String name of the set
        :return: list of string component names
        '''

        names = self.cursor.execute("select componentnamevalue from component JOIN set_components on component._id = set_components.component_id where "
                                    " set_id = (SELECT _id from set_ where set_name = '" + setName + "')").fetchall()
        if len(names) >0:
            names = [''.join(i) for i in names if i is not None]
            return pd.Series(names).tolist()
        return []

    def updateSetupInfo(self, setupDict,setupFilePath):
        '''
        Updates the database setup tables with information from the setup.xml file
        The setup file is a mesh of both input handler information and model run information.
        The Project_manager database only handles the portion of the setup file that is important for creating netdfs for model running
        The remaining attributes are modified directly in an interface to the xml file.
        :param setupDict: a dictionary extracted from a setup xml file
        :param setupFilePath is the path to the setup file
        :return: None
        '''
        #update actual setup fields - these have a single value and are used in models
        #update project table
        pid = self.insertRecord('project',['project_name','project_path','setupfile'],[setupDict['project'],setupDict['projectPath'],setupFilePath])

        def isdateOnly(value):
            '''determines if a string contains both date and time or just date values
            :returns True if the value only contains a date (no time)'''
            return ":" not in value
        #update fields that are in the setup table
        try:
            if isdateOnly(setupDict[RUNTIMESTEPS]):
                startdate = setupDict[RUNTIMESTEPS].split(" ")[0]
                enddate = setupDict[RUNTIMESTEPS].split(" ")[1]
            else:
                startdate = setupDict[RUNTIMESTEPS].split(" ")[0] + " " +setupDict[RUNTIMESTEPS].split(" ")[1]
                enddate = setupDict[RUNTIMESTEPS].split(" ")[2] + " " + \
                            setupDict[RUNTIMESTEPS].split(" ")[3]

        except IndexError as i:
            print("runtimesteps not start stop indices")
            startdate = None
            enddate = None

        setId = self.insertRecord(SETUPTABLE,[self.dbName(TIMESTEPUNIT),self.dbName(TIMESTEP),self.dbName(RUNTIMESTEPS),STARTDATE,ENDDATE,PROJECTID],
                          [setupDict[TIMESTEPUNIT],setupDict[TIMESTEP],setupDict[RUNTIMESTEPS],startdate,enddate,pid])

        #update input handler infomation
        #this information is in the from of space delimited ordered lists that require parsing and are used by the input handler
        self.parseInputHandlerAttributes(setupDict)

        return

    def getIDByPosition(self, tablename, position):
        try:
            return self.cursor.execute("SELECT _id FROM " + tablename + " ORDER by _id").fetchall()[position][0]
        except IndexError as e:
            return None
    def getInputPath(self, pathNum):
        '''returns the file folder for the given input file number (corrasponds to fileblock in setup page)'''
        path = self.cursor.execute("select inputfiledirvalue from input_files where _id = " + pathNum).fetchone()
        if path is not None:
           return path[0]
        return
    def getComponentTypes(self):
        loT = self.cursor.execute("select code,description from ref_component_type").fetchall()

        return loT
    def getCurrentComponentTypeCount(self):
        loT = self.cursor.execute("select code,description, count(componenttype) from ref_component_type LEFT JOIN component on ref_component_type.code = component.componenttype group by code").fetchall()
        return loT
    def getPossibleDateTimes(self):
        myTuple = self.cursor.execute("select d.description, t.description from ref_date_format as d, ref_time_format as t"
                                      " UNION "
                                      "SELECT '',t.description from ref_time_format as t"
                                      " UNION "
                                      " SELECT d.description, '' from ref_date_format as d").fetchall()
        myList = ["^" + (t[0] + " " + t[1]).strip() + "$" for t in myTuple]
        return myList

    def getCode(self, table, description):
        code = self.cursor.execute("select code from " + table + " WHERE description = ?",[description]).fetchone()
        if code != None:
            return code[0]
        else:
            return None


    def getAsRefTable(self,table,*args):
        '''
        get a list of id and code and description values from a reference table
        if rgs are provided those fields are returned instead of code and description
        :param table: String name of the reference table
        :return: List of tuples
        '''
        fields =[]
        for arg in args:
            fields.append(arg)
        if len(fields) == 0:
            fields = [ID, 'code','description']
        stringFields = str.join(",",fields)
        return self.cursor.execute("SELECT " + stringFields + " FROM " + table).fetchall()

    def getComponentByType(self,mytype):
        '''

        :param mytype:
        :return:
        '''
        codes = self.cursor.execute("select _id, componentnamevalue from component WHERE componenttype = ?", [mytype]).fetchall()
        return codes
    def getAllRecords(self,table):
        return self.cursor.execute("select * from " + table).fetchall()

    def parseInputHandlerAttributes(self, setupDict):
        '''
        Parses the portion of a setup dictionary (dictionary produced from setup.xml) into various project_manager tables
        that are relevent to the InputHandler.
        :param setupDict: A dictionary with keys that match a setup.xml files attributes
        :return: None
        '''

        def hasComponentData(componentDict):
            for k in componentDict.keys():
                if k in [self.dbName(HEADERNAME), self.dbName(COMPONENTATTRIBUTEUNIT),
                               self.dbName(COMPONENTATTRIBUTE)]:
                    if len(componentDict[k]) > 0:
                        return True
            return False
        allComponentNames = shlex.split(setupDict[COMPONENTNAMES])

        fileAttributes = [FILEDIR, FILETYPE, DATECHANNELFORMAT,
                          DATECHANNEL, TIMECHANNELFORMAT, TIMECHANNEL, TIMEZONE,
                          INPUTTIMESTEP, UTCOFFSET]
        componentFiles = [HEADERNAME, COMPONENTATTRIBUTEUNIT,
                               COMPONENTATTRIBUTE]  # plus file id and component id
        componentAttributes = [COMPONENTNAME]
        files = {self.dbName(key): shlex.split(value) for key, value in setupDict.items() if
                 key in fileAttributes}

        #sometimes setup files only contain the relative path to input files from the project directory

        files[self.dbName(FILEDIR)] = [self.checkPath(self.makePath(k)) for k in files[self.dbName(FILEDIR)]] #we need to convert the list filepath to a system filepath as a string
        components = {self.dbName(key): shlex.split(value) for key, value in setupDict.items() if
                      key in componentAttributes}
        filecomponents = {self.dbName(key): shlex.split(value) for key, value in setupDict.items() if
                      key in componentFiles}

        components[COMPONENTTYPE] = [self.inferComponentType(k) for k in components[self.dbName(COMPONENTNAME)]]
        compIds = []
        # insert the pieces
        if (files[self.dbName(FILEDIR)]!=[""]) & (files[self.dbName(FILEDIR)] != ['None']):
            #special accomodations taken for time channel which is frequently left empty.
            if len(files[self.dbName(TIMECHANNEL)]) <= 0:
                files[self.dbName(TIMECHANNEL)] = files[self.dbName(DATECHANNEL)]
            if len(files[self.dbName(TIMECHANNELFORMAT)]) <= 0:
                files[self.dbName(TIMECHANNELFORMAT)] = ['None'] * len(files[self.dbName(TIMECHANNEL)])

            idlist = self.insertFileDictionaryRow('input_files', files)
            filecomponents['inputfile_id'] = idlist
            compIds = self.extractComponentNamesOnly(components, setupDict)

            if hasComponentData(filecomponents):
                filecomponents[COMPONENTID] = compIds
                filecomponents[COMPONENTTYPE] = components[COMPONENTTYPE]
                self.addComponentsToFileInputTable(filecomponents)


         #if there are no input files specified components from the componentsnamesvalue attribute will be used to populate component table
        allComponentNames = [component for component in allComponentNames if component not in components['componentnamevalue']]
        allComponents = {'componentnamevalue': allComponentNames,
                         'componenttype': [self.inferComponentType(k) for k in allComponentNames]}
        non_data_components = self.extractComponentNamesOnly(allComponents, setupDict) #this puts them in the component table
        non_data_components = [o for o in non_data_components if o not in compIds]
        if len(non_data_components) > 0:
            allComponents[COMPONENTID] = non_data_components
            del allComponents['componentnamevalue']
            allComponents['inputfile_id'] = [-1] * len(allComponents[COMPONENTID])
            self.addComponentsToFileInputTable(allComponents)
        return fileAttributes + componentAttributes + componentFiles

    def addComponentsToFileInputTable(self, filecomponents):
        '''
        Inserts a dictionary of values into the file_components table
        :param filecomponents: dictionary with attributes that correspond to column names in the file_comppnents table
        :return list of integers that correspond to the id of records inserted.
        '''

        ids = self.insertDictionaryRow('component_files', filecomponents)

        return ids
    def extractComponentNamesOnly(self, components,setupDict):
        '''
        Insert component names from setuDict into the component table in project_manager
        :param components:
        :param setupDict: a dictionary of values read from a setup.xml file
        :return: list of integers associated with the id field in the component table
        '''
        # it is possible that he components have been created but not associaed with files yet.
        # in this case the components should be pulled from the componentnames.value attribute
        if (components[self.dbName(COMPONENTNAME)] == ['None']) | (components[self.dbName(COMPONENTNAME)] == [""]):
            components = self.swapComponentNamesOnly(setupDict)

        idlist = self.insertDictionaryRow(COMPONENTTABLE,
                                          components)  # duplicate components should fail here, but list will still be original length
        return idlist
    def swapComponentNamesOnly(self, setupDict):
        components = {self.dbName(key): xmlToString(value.split(' ')) for key, value in
                      setupDict.items() if key == COMPONENTNAMES}
        components[self.dbName(COMPONENTNAME)] = components[self.dbName(COMPONENTNAMES)]
        del components[self.dbName(COMPONENTNAMES)]
        components[COMPONENTTYPE] = [self.inferComponentType(k) for k in components[self.dbName(COMPONENTNAME)]]
        return components
    def makePath(self,stringlistpath):
        '''
        :param stringlistpath: a path that is a list written as a comma, backslash, double backslash or forward slash seperated string (as is found in setup xml
        :return:
        '''
        if isinstance(stringlistpath, list):
            return os.path.join(*stringlistpath)
        else:
            if(os.path.exists(os.path.abspath(stringlistpath))):
                return os.path.abspath(stringlistpath)
            elif os.path.exists(os.path.join(*[self.getProjectPath(),'..',stringlistpath])):
                return os.path.abspath(os.path.join(*[self.getProjectPath(), '..', stringlistpath]))
            else:
                return ''

    def inferComponentType(self,componentname):
        '''returns the string value of the component type extracted from the comonent name
        i.e wtg, ees'''
        import re
        try:
           match = re.match(r"([a-z]+)([0-9]+)", componentname, re.I)
           if match:
                componentType = match.group(1)
                return componentType
        except:
            return
    def addComponentsToSet(self,setid,loc):
        '''
        Adds a list of component names to the set_components table
        :param loc: A list of component names from the component table
        :param setid: the id of a valid set from the setup table
        :return: None. Updates the set_components table
        '''
        try:
            self.cursor.execute("INSERT INTO set_components (set_id, component_id, tag) SELECT " + setid + ", _id, 'None' FROM component WHERE componentnamevalue IN " + loc)
            self.connection.commit()
        except Exception as e:
            print(e)
    def getRecordDictionary(self,table, id):
        '''
        returns a selected record from the specified table with as a dictionary with fields as keys
        :param table: String table name to retrieve record from
        :param id: int the id of the record to retrieve
        :return: Dictionary
        '''

        conn = lite.connect('project_manager')

        conn.row_factory = lite.Row
        cursor = conn.cursor()

        row = cursor.execute("SELECT * FROM " + table + " WHERE _id = ?",[id]).fetchone()
        try:
            rowDict = dict(zip([c[0] for c in cursor.description], row))
        except TypeError as e:
            print(e)
            rowDict = {}
        finally:
            cursor.close()
            conn.close()

        return rowDict
    def getSetChanges(self,set_id):

        return self.cursor.execute("SELECT componentnamevalue,"
                         "tag, group_concat(tag_value,',') from "
                                   "set_components JOIN component ON set_components.component_id = component._id "
                                    "where set_id = ? AND tag != 'None' GROUP BY component.componentnamevalue,tag", [set_id]).fetchall()
    def getNextRun(self,setName):
        set_id = self.getSetId(setName)
        if set_id != (None,):
            nextRun = self.cursor.execute("SELECT run_num from run where set_id = ? and started is null ORDER BY run_num LIMIT 1",[set_id]).fetchall()
            try:
                runName = nextRun[0][0]
                return runName
            except IndexError:
                return None

        return None
    def updateRunStatus(self,setName,runNum,field):
        '''sets the designated field of the run table t 1'''
        self.updateRecord('run',[SETID,'run_num'],[self.getSetId(setName),runNum],[field],[1])
    def updateRunToFinished(self, setName, runNum):
        '''sets the finished field of the '''
        self.updateRunStatus(setName,runNum,'finished')
    def updateRunToStarted(self, setName, runNum):
        '''sets the finished field of the '''
        self.updateRunStatus(setName,runNum,'started')
    def hasResults(self,setName):
        results = self.cursor.execute("SELECT * from run where set_id = ?",[self.getSetId(setName)]).fetchall()
        df = pd.DataFrame(results)
        return not df[5:].isnull().all().all() #are all the columns after the finished column null?
    def hasBaseResults(self):
        results = self.cursor.execute("SELECT * from run where basecase = 1").fetchall()
        if results:
            return all([i == None for i in list(results[5:])])

        else:
            return False
    def updateBaseCase(self,setID,runId,isBase =True):
        '''updates the base case value for an individual run record to 1, setting all others to 0
        If the new baseCase run record id matches the old baseCase run record id False is returned,
        Otherwise queries are performed and True is returned'''
        originalBase = self.getId('run',[SETID,'base_case'],[setID,1])
        if originalBase != runId and isBase:
            self.updateRecord('run', [SETID], [setID], ['base_case'],
                              [0])  # all base cases set to 0 for the specified set
            self.updateRecord('run', [ID], [runId], ['base_case'], [1])  # new base case selected
            return True
        elif originalBase == runId and not isBase:
            self.updateRecord('run', [ID], [runId], ['base_case'], [0])  # base case removed
            return True
        else:
            return False
    def getSetId(self,setx):
        '''returns the _id value for a specified set in the set_ table
        :param setx is a string that contains either the set name number or the full set name
        :returns integer _id value for the set, -1 if none found.
        '''
        if setx.isdigit():
            setName = 'Set' + setx
        else:
            setName = setx
        return self.getId(SETTABLE,[SETNAME],[setName])
    def updateRunResult(self,setNum,runNum,rowDict):
        self.updateFromDictionaryRow('run',rowDict,[SETID,'run_num'],[self.getSetId(setNum),runNum])
    def checkMinimalData(self,projectSetDir):
        # at a minimum the database should have a setup record, a set record associated with the specified projectSetDir
        # and a run record for each run folder in the set dir
        # componenent records for each set
        #TODO write function
        return True
    def prepareForResults(self, projectSetDir):
        '''checks for necessary tables to be filled that are necessary to store results
        If tables are not populated loads info from project folder'''
        #TODO write function
        #is there already a project database with minimal data
        if self.checkMinimalData(projectSetDir):
            return True
        else:
            try:
                # self.loadSetUp()
                # self.loadComponents()
                # self.loadSet()
                # self.loadRun()
                #at this point result loading can commence
                return True
            except Exception as e:
                print(e)
                return False
    def modelsRun(self):
        return self.cursor.execute("SELECT * FROM run where finished = 1").fetchall()
    def getSetResults(self,setNum):
        #returns a dataframe of run table
        set_id = self.getSetId(setNum)
        tups = self.cursor.execute("SELECT * from run where set_id = ?",[set_id]).fetchall()
        col_name_list = [tuple[0] for tuple in self.cursor.description]
        if tups:
            return pd.DataFrame(tups,columns = col_name_list)
        else:
            return pd.DataFrame()
    def insertCompletedRun(self,setId,runNum):
        id = self.insertRecord('run',[SETID,'run_num','started','finished'],[setId,runNum,1,1])
        return id
    def insertRunComponent(self,run_id,set_component_id):
        id = self.insertRecord('run_attributes', ['run_id', 'set_component_id'], [run_id,set_component_id])
        return id
    def getRunXYValues(self,tag,metric):
        '''
        creates a dictionary of run results to display in the data plot.
        :param tag: String starting with setname followed by attribute tag
        :param metric: The metadata metric to display
        :return: dictionary of series and x y values
        '''
        def getRunFolder(runid):
            run_num = self.getFieldValue('run','run_num',ID,runid)
            setFolder = getFilePath(self.getFieldValue(SETTABLE,SETNAME,ID,self.getFieldValue('run',SETID,ID,runid)),projectFolder = self.getProjectPath())
            runFolder = getFilePath('Run'+run_num, set=setFolder)

            return runFolder

        def getActualValue(runid, v):
            if isTagReferenced(v):
                av = getReferencedValue(v,getRunFolder(runid))
                if isinstance(av,list):
                    return av[0]
                return av
            return v

        def dict_from_tuple(lot,d):
            if not lot:
                return d
            else:
                if (lot[0][4]) in d.keys():
                    d[lot[0][4]]['x'].append(getActualValue(lot[0][0],lot[0][1]))
                    d[lot[0][4]]['y'].append(getActualValue(lot[0][0],lot[0][2]))
                else:
                    d[lot[0][4]] = {}
                    d[lot[0][4]]['x']=[getActualValue(lot[0][0],lot[0][1])]
                    d[lot[0][4]]['y']=[getActualValue(lot[0][0],lot[0][2])]
                lot.pop(0)
                return dict_from_tuple(lot,d)

        tag = tag.split(" ")[1]
        resultTuples = self.cursor.execute("SELECT * FROM (SELECT run_id,tag_value," + metric + " FROM "
                             "run JOIN run_attributes ON run._id = run_attributes.run_id "
                              "JOIN set_components ON run_attributes.set_component_id = set_components._id "
                              "JOIN component on set_components.component_id = component._id "
                              "JOIN set_ on set_components.set_id = set_._id "
                              "WHERE componentnamevalue || '.' || tag = ?) as tagvalues "
"JOIN (SELECT run_id,group_concat(tag || ' ' || tag_value) as seriesname FROM run_attributes "
"JOIN set_components ON run_attributes.set_component_id = set_components._id "
                              "JOIN component on set_components.component_id = component._id "
                              "JOIN set_ on set_components.set_id = set_._id "
 "WHERE componentnamevalue || '.' || tag != ? GROUP BY run_id HAVING count(tag) > 1) as seriesValues "
"on tagvalues.run_id = seriesValues.run_id GROUP BY tagvalues.tag_value,seriesValues.seriesname ORDER BY CAST(tagvalues.tag_value as real) ASC",[tag,tag]).fetchall()

        return dict_from_tuple(resultTuples,{})

    def exportRunMetadata(self,setName):
        exportPath = getFilePath(setName, projectFolder=self.getProjectPath())

        strSQL = "SELECT * FROM run LEFT JOIN (SELECT run_id, " \
        "group_concat(componentnamevalue ||'.' || tag || ' = ' || tag_value) from run_attributes " \
        "JOIN set_components ON set_components._id = run_attributes.set_component_id " \
        "JOIN component on set_components.component_id = component._id WHERE " \
        "set_components.set_id = " + str(self.setId) + ") as ra ON run._id = ra.run_id " \
                                                       "GROUP BY run_id"
        self.exportView(strSQL,exportPath)
        return
    def exportView(self,strSql,exportPath):
        records = self.cursor.execute(strSql).fetchall()
        col_name_list = [tuple[0] for tuple in self.cursor.description]
        with open(exportPath,'w+') as csvFile:
            csvFile.write(col_name_list)
            csvFile.write("/n")
            for r in records:
                csvFile.write(r)

    def checkPath(self, filePath):
        '''converts the selected path to an existing path if it matches'''
        currentPaths = self.getAllRecords('input_files')
        for cpath in currentPaths:
            if os.path.abspath(filePath) == os.path.abspath(cpath[4]):
                filePath = cpath[4]
                return filePath
        return filePath