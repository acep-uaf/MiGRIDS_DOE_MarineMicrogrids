import pandas as pd
import os
import sqlite3 as lite
from MiGRIDS.InputHandler.Component import Component
from MiGRIDS.Controller.makeXMLFriendly import xmlToString

class ProjectSQLiteHandler:

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
        except:
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
        loi = self.cursor.execute("SELECT componentnamevalue,component.componenttype,componentattributevalue,componentattributeunit from component_files join component on component_files.component_id = component._id group by componentnamevalue, component.componenttype, componentattributevalue")
        loc = []
        for t in loi:
            c = Component(component_name=t[0],type=t[1],attribute=t[2],units=t[3],column_name=t[0]+t[2],scale=1,offset=0)
            loc.append(c)
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
        self.addRefValues('ref_date_format',[(0,'MM/DD/YY','(0[0-9]|1[0-2])/[0-3][0-9]/[0-9]{2}'),(1,'MM/DD/YYYY','(0[0-9]|1[0-2])/[0-3][0-9]/[0-9]{4}'),
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
         inputfile_id integer,
         headernamevalue text,
         componenttype text,
         component_id integer,
         componentattributeunit text,
         componentattributevalue text,
         componentscale double,
         componentoffset double,
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
                FOREIGN KEY (timechannelformat) REFERENCES ref_time_format(code),
                FOREIGN KEY (datechannelformat) REFERENCES ref_date_format(code));""")

        #The table optimize input only contains parameters that were changed from the default
        self.cursor.execute("Drop TABLE IF EXISTS optimize_input")
        self.cursor.executescript("""
                     CREATE TABLE IF NOT EXISTS optimizer_input
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

        self.cursor.execute("DROP TABLE IF EXISTS run")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS run
                (_id integer primary key,
                set_id text,
                run_name text,
                set_component_id);""")

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

        #self.cursor.execute("INSERT INTO setup (set_name,timestepvalue,date_start,date_end) values('default',1,'2016-01-01','2016-12-31')")



        self.connection.commit()
    def clearTable(self,table):
        self.cursor.execute("Delete From " + table)
        self.connection.commit()


    def getSetupDateRange(self):
        '''

        :param setName: String name of the set to get date range for
        :return: start and end are string datetime values in the start and end date fields in the setup table
        '''

        start = self.cursor.execute("select date_start from setup").fetchone()
        end = self.cursor.execute("select date_end from setup").fetchone()

        return start[0],end[0]

    def insertFirstSet(self,dict):
       self.insertDictionaryRow('set_',dict)
    def insertAllComponents(self,setName):
         self.cursor.execute("INSERT INTO set_components (set_id, component_id, tag, tag_value) SELECT set_._id, component._id,'None','None' FROM component, set_ where set_.set_name = '" + setName + "'")
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

        #get tuple for basic set info
        values = self.cursor.execute("select project_name, timestepvalue, timestepunit, date_start, date_end from set_ join project on set_.project_id = project._id WHERE LOWER(set_name) = '" + setName.lower() + "'").fetchone()
        if values is not None:
            setDict['project name'] = values[0]
            setDict['timeStep.value'] = values[1]
            setDict['timeStep.unit']=values[2]
            setDict['date_start'] = values[3]
            setDict['date_end'] = values[4]
            setDict['runTimeSteps.value'] = str(values[3]) + " " + str(values[4])
            #as long as there was basic set up info look for component setup info
            #componentNames is a list of distinct components, order does not matter
            compTuple =  self.cursor.execute("SELECT group_concat(componentnamevalue,' ') FROM "
                                                                   "(SELECT DISTINCT componentnamevalue as componentnamevalue FROM component "
                                                                   "JOIN set_components on component._id = set_components.component_id JOIN set_ "
                                                                   "on set_components.set_id = set_._id WHERE lower(set_name) = ? )", [setName.lower()]).fetchall()[0]
            setDict['componentNames.value'] = " ".join(compTuple)
        else:
            return None

        return setDict

    def getSetUpInfo(self):
        '''
        Creates a dictionary of setup information for a specific set, default is set 0 which is the base case
        :return: dictionary of xml tags and values to be written to a setup.xml file
        '''
        setDict = {}

        #get tuple for basic set info
        testSet = self.cursor.execute("select project_id, timestepvalue, timestepunit, date_start, date_end from setup").fetchall()
        values = self.cursor.execute("select project_name, timestepvalue, timestepunit, date_start, date_end from setup join project on setup.project_id = project._id").fetchone()
        if values is not None:
            setDict['project name'] = values[0]
            setDict['timeStep.value'] = values[1]
            setDict['timeStep.unit']=values[2]
            setDict['date_start'] = values[3]
            setDict['date_end'] = values[4]
            setDict['runTimeSteps.value'] = str(values[3]) + " " + str(values[4])
            #as long as there was basic set up info look for component setup info
            #componentNames is a list of distinct components, order does not matter
            setDict['componentNames.value'] =  self.getComponentNames()

            #componentChannels has ordered lists for directories and the components they contain. A component can have data in more than one directory and file type, in which case it would
            #be listed more than once in componentChannels
            #We use a left join for input files to components so the input file directories will still get listed even if no components have been added
            values = self.cursor.execute(
            "select group_concat(COALESCE(REPLACE(inputfiledirvalue,' ','_'),'None'),' '), group_concat(COALESCE(REPLACE(inputfiletypevalue,' ','_'),'None'),' '),group_concat(componentnamevalue,' '),"
            "group_concat(REPLACE(headernamevalue,' ','_'), ' '),group_concat(REPLACE(componentattributevalue,' ',' '), ' '), group_concat(REPLACE(componentattributeunit,' ',' '), ' '),group_concat(COALESCE(REPLACE(datechannelvalue,' ','_'),'None'), ' '),group_concat(COALESCE(REPLACE(timechannelvalue,' ','_'),'None'),' '),"
            "group_concat(COALESCE(REPLACE(datechannelformat,' ','_'),'None'), ' '),group_concat(COALESCE(REPLACE(timechannelformat,' ','_'),'None'), ' '), "
            "group_concat(COALESCE(REPLACE(timezonevalue,' ','_'),'None'), ' '), group_concat(COALESCE(REPLACE(usedstvalue,' ','_'),'None'), ' '), group_concat(COALESCE(REPLACE(inpututcoffsetvalue,' ','_'),'None'), ' '), group_concat(COALESCE(REPLACE(flexibleyearvalue,' ','_'),'None'), ' ') "
            "from input_files Left JOIN "
            "(select component._id as component_id, inputfile_id, COALESCE(REPLACE(componentnamevalue,' ','_'),'None') as componentnamevalue, COALESCE(REPLACE(headernamevalue,' ',' '),'None') as headernamevalue, COALESCE(REPLACE(componentattributevalue,' ','_'),'None') as componentattributevalue, COALESCE(componentattributeunit,'None') as componentattributeunit from component_files "
            "LEFT JOIN component on component._id = component_files.component_id ORDER BY component_id ) as components"
            " ON components.inputfile_id = input_files._id ORDER BY input_files._id").fetchone()

            if values is not None:
                setDict['inputFileDir.value'] = values[0]
                setDict['inputFileType.value'] = values[1]
                setDict['componentChannels.componentName.value']= values[2]
                setDict['componentChannels.headerName.value'] = values[3]
                setDict['componentChannels.componentAttribute.value'] = values[4]
                setDict['componentChannels.componentAttribute.unit'] = values[5]
                setDict['dateChannel.value']=values[6]
                setDict['dateChannel.format'] = values[8]
                setDict['timeChannel.value'] = values[7]
                setDict['timeChannel.format'] = values[9]
                setDict['timeZone.value'] =  values[10]
                setDict['inputDST.value'] = values[11]
                setDict['inputUTCOffset.unit']  ='hr'
                setDict['inputUTCOffset.value']=values[12]
                setDict['flexibleYear.value']=values[13]

        else:
            return None

        return setDict
    def getNewSetInfo(self,setName):
        '''
        returns dictionary for attributes that are changed between an original setup file and a setup file for a set
        :return: Dictionary of attributes that have new values
        '''
        set = self.getSetInfo(setName)
        setup = self.getSetUpInfo()

        for k in list(set.keys()):
            if set[k] == setup[k]:
                del set[k]
        return set
    def updateSetSetup(self, setName, setupDict):
        '''Update the set_ table for a specific set and make sure all set components are in the set_component table'''


        def dateOnly(value):
            '''determins if a string contains both date and time or just date values'''
            return ":" not in value

        # update fields that are in the set table
        try:
            if dateOnly(setupDict['runTimeSteps.value']):
                startdate = setupDict['runTimeSteps.value'].split(" ")[0]
                enddate = setupDict['runTimeSteps.value'].split(" ")[1]
            else:
                startdate = setupDict['runTimeSteps.value'].split(" ")[0] + " " + \
                            setupDict['runTimeSteps.value'].split(" ")[1]
                enddate = setupDict['runTimeSteps.value'].split(" ")[2] + " " + \
                          setupDict['runTimeSteps.value'].split(" ")[3]

        except IndexError as i:
            print("runtimesteps not start stop indices")
            startdate = None
            enddate = None
        #if the record already exists a -1 will be returned and updateRecord is run
        setId = self.insertRecord('set_',
                                  ['timestepunit', 'timestepvalue', 'runtimestepsvalue', 'date_start', 'date_end',
                                   'project_id','set_name'],
                                  [setupDict['timeStep.unit'], setupDict['timeStep.value'],
                                   setupDict['runTimeSteps.value'], startdate, enddate, 1,setName])
        if setId == -1:
            self.updateRecord('set_',['set_name'],[setName],
                                  ['timestepunit', 'timestepvalue', 'runtimestepsvalue', 'date_start', 'date_end'],
                                  [setupDict['timeStep.unit'], setupDict['timeStep.value'],setupDict['runTimeSteps.value'], startdate, enddate])

        return
    def updateSetComponents(self,setName,loc):
        '''
        adds components listed in loc to the set_component table for the specified set and
        removes any components present that are not in loc. Tag is always None as this is base components for a set
        :param setName: String name of the set found in set_ table set_name column
        :param loc: List of String names of components to add to the set_component table
        :return: None
        '''
        setid = self.getId('set_','set_name',setName)[0][0]
        #the [0][0] notation is required because getId returns a list of tuples. We want the first item in the list
        # and first item in the tuple (which is only 1 item long)
        compid = [self.getId('component','componentnamevalue',c)[0][0] for c in loc]
        fields = ['component_id','set_id','tag','tag_value']
        values =[(str(x),setid,'None','None') for x in compid]
        if len(values) <=0: #if values are empty then set has no components
            self.cursor.execute("DELETE FROM set_components WHERE set_id = ?", [setid])
        else:
            deleters =  "(" + ",".join([str(x) for x in filter(None, compid)]) + ")"

            self.cursor.execute("DELETE FROM set_components WHERE set_id = ? AND component_id not in " + deleters , [setid]) #AND component_id not in ('1','2')"
        self.insertRecord('set_components',fields,values)
        self.connection.commit()
        return
    def insertSetComponentTags(self,setName,lot):
        '''update tags in set_components with an attributeDictionary
        :param lot: is a list of tuples of the order name,tag,attr,value
        :return: None
        '''

        [self.insertRecord('set_components',['set_id','component_id','tag','tag_value'],[self.getId('set_','set_name',setName)[0][0],t[0],t[1]+"." + t[2],t[3]]) for t in lot]


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

    def getId(self,table,keyField,keyValue):
        ''' get the id of the first record with a keyField equal to the specified keyValue
        :param table: String name of the table to query
        :param keyField: String name of the table column to match
        :param keyValue: String value to find in the table
        :return: integer, -1 if a matching record is not found'''
        i = self.cursor.execute("SELECT _id from " + table + " WHERE " + keyField + " = ?",[keyValue]).fetchall()
        if i is not None:
            return i
        else:
            return [-1]
    def getRuns(self,set_id):
        componentsInSet = self.getSetComponents(set_id)
        sqlStatement = self.createStatements(componentsInSet,set_id)
        set_component_combos = self.cursor.execute(sqlStatement).fetchall()
        return set_component_combos
    def getSetComponents(self, set_id):
        componentsInSet = self.cursor.execute("SELECT _id from component WHERE _id in "
                                          "(SELECT component_id FROM set_components WHERE set_id = ?) GROUP BY _id",
                                          [set_id]).fetchall()
        return componentsInSet
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

        keyFields = ', '.join([str(a) + " = '" + str(b) + "'" for a,b in zip(keyField,keyValue)])
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

        ml = maxLength(dict)
        keys = ','.join(dict.keys())
        question_marks = ','.join(list('?' * len(dict.keys())))

        values = list(tuple(zip(*dict.values())))
        ids = []
        for v in values: #need to loop so we get ids for every value
            try:
                self.cursor.execute('INSERT INTO ' + tablename + ' (' + keys + ') VALUES (' + question_marks + ')',v ) #if insertion fails the last id gets re-appended to the list
                self.connection.commit()
            except Exception as e:
                print(e)

            finally:
                ids.append(self.cursor.lastrowid)
        if ml > len(ids):
            print ('Information was missing for some input files')
        return ids
    def updateComponent(self, dict):
        ''' updates a component record with values in the dictionary
        :param dict: a dictionary containing at least the attribute 'component_name' and one other attribute that matches a field name in the component table'''
        for k in [key for key in dict.keys() if key != 'componentnamevalue']:
            try:
                self.cursor.execute("UPDATE component_files SET " + k + " = ? WHERE component_id = (SELECT _id from component WHERE componentnamevalue = ?)", [dict[k],dict['componentnamevalue']])
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
        import pandas as pd
        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes
    def getComponentNames(self,):
        '''
        returns a list of names for components in the set_components table. Defaults to set0
        :param setName: String name of the set
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
    def updateSetupInfo(self, setupDict,setupFile):
        '''
        Updates the database setup tables with information from the setup.xml file
        The setup file is a mesh of both input handler information and model run information.
        The Project_manager database only handles the portion of the setup file that is important for creating netdfs for model running
        The remaining attributes are modified directly in an interface to the xml file.
        :param setupDict: a dictionary extracted from a setup xml file
        :return: None
        '''
        #update actual setup fields - these have a single value and are used in models
        #update project table
        pid = self.insertRecord('project',['project_name','project_path','setupfile'],[setupDict['project'],setupDict['projectPath'],setupFile])
        def dateOnly(value):
            '''determins if a string contains both date and time or just date values'''
            return ":" not in value
        #update fields that are in the setup table
        try:
            if dateOnly(setupDict['runTimeSteps.value']):
                startdate = setupDict['runTimeSteps.value'].split(" ")[0]
                enddate = setupDict['runTimeSteps.value'].split(" ")[1]
            else:
                startdate = setupDict['runTimeSteps.value'].split(" ")[0] + " " +setupDict['runTimeSteps.value'].split(" ")[1]
                enddate = setupDict['runTimeSteps.value'].split(" ")[2] + " " + \
                            setupDict['runTimeSteps.value'].split(" ")[3]

        except IndexError as i:
            print("runtimesteps not start stop indices")
            startdate = None
            enddate = None

        setId = self.insertRecord('setup',['timestepunit','timestepvalue','runtimestepsvalue','date_start','date_end','project_id'],
                          [setupDict['timeStep.unit'],setupDict['timeStep.value'],setupDict['runTimeSteps.value'],startdate,enddate,pid])

        #update input handler infomation
        #this information is in the from of space delimited ordered lists that require parsing and are used by the input handler
        self.parseInputHandlerAttributes(setupDict)

        return
    def getInputPath(self, pathNum):
        '''returns the file folder for the given input file number (corrasponds to fileblock in setup page)'''
        path = self.cursor.execute("select inputfiledirvalue from input_files where _id = " + pathNum).fetchone()
        if path is not None:
           return path[0]
        return
    '''gets a list of possible component types from the ref_component_type table'''
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
            fields = ['_id', 'code','description']
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
                if k in ['headernamevalue', 'componentattributeunit',
                               'componentattributevalue']:
                    if len(componentDict[k]) > 0:
                        return True
            return False

        fileAttributes = ['inputFileDir.value', 'inputFileType.value', 'dateChannel.format',
                          'dateChannel.value', 'timeChannel.format', 'timeChannel.value', 'timeZone.value',
                          'flexibleYear.value', 'inputtimestepvalue', 'inpututcoffsetvalue']
        componentFiles = ['headerName.value', 'componentAttribute.unit',
                               'componentAttribute.value']  # plus file id and component id
        componentAttributes = ['componentName.value']
        files = {key.lower().replace(".", ""): xmlToString(value.split(' ')) for key, value in setupDict.items() if
                 key in fileAttributes}
        #sometimes setup files only contain the relative path to input files from the project directory

        files['inputfiledirvalue'] = [self.makePath(k) for k in files['inputfiledirvalue']] #we need to convert the list filepath to a system filepath as a string
        components = {key.lower().replace(".", ""): xmlToString(value.split(' ')) for key, value in setupDict.items() if
                      key in componentAttributes}
        filecomponents = {key.lower().replace(".", ""): value.split(' ') for key, value in setupDict.items() if
                      key in componentFiles}

        components['componenttype'] = [self.inferComponentType(k) for k in components['componentnamevalue']]

        # insert the pieces
        if (files['inputfiledirvalue']!=[""]) & (files['inputfiledirvalue'] != ['None']):
            idlist = self.insertDictionaryRow('input_files', files)
            filecomponents['inputfile_id'] = idlist
            idlist = self.extractComponentNamesOnly(components, setupDict)

            if hasComponentData(filecomponents):
                filecomponents['component_id'] = idlist
                filecomponents['componenttype'] = components['componenttype']
                self.addComponentsToFileInputTable(filecomponents)
        else:
            #if there are no input files specified components from the componentsnamesvalue attribute will be used to populate component table
            idlist = self.extractComponentNamesOnly(components, setupDict)

            return fileAttributes + componentAttributes + componentFiles
    def addComponentsToFileInputTable(self, filecomponents):
        '''
        Inserts a dictionary of values into the file_components table
        :param filecomponents: dictionary with attributes that correspond to column names in the file_comppnents table
        :return list of integers that correspond to the id of records inserted.
        '''

        ids = self.insertDictionaryRow('component_files', filecomponents)
        print(self.getAllRecords('component_files'))
        return ids
    def extractComponentNamesOnly(self, components,setupDict):
        '''
        Insert component names from setuDict into the component table in project_manager
        :param setID: integer the set that these components are associated with
        :param setupDict: a dictionary of values read from a setup.xml file
        :return: list of integers associated with the id field in the component table
        '''
        # it is possible that he components have been created but not associaed with files yet.
        # in this case the components should be pulled from the componentnames.value attribute
        if (components['componentnamevalue'] == ['None']) | (components['componentnamevalue'] == [""]):
            components = self.swapComponentNamesOnly(setupDict)

        idlist = self.insertDictionaryRow('component',
                                          components)  # duplicate components should fail here, but list will still be original length
        return idlist
    def swapComponentNamesOnly(self, setupDict):
        components = {key.lower().replace(".", ""): xmlToString(value.split(' ')) for key, value in
                      setupDict.items() if key == 'componentNames.value'}
        components['componentnamevalue'] = components['componentnamesvalue']
        del components['componentnamesvalue']
        components['componenttype'] = [self.inferComponentType(k) for k in components['componentnamevalue']]
        return components
    def makePath(self,stringlistpath):
        '''

        :param stringlistpath: a path that is a list written as a comma seperated string (as is found in setup xml
        :return:
        '''
        aslist = stringlistpath.split(',')
        if aslist[0] == self.getProject(): #if the path specification starts with the project folder, make it a complete path by adding the path to the project folder
            return os.path.join(self.getProjectPath(),*aslist[1:])
        else:
            return os.path.join(*aslist)
    # returns a possible component type inferred from the components column name
    def inferComponentType(self,componentname):
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

        return self.cursor.execute("SELECT componentnamevalue, tag, group_concat(tag_value, ',')from "
                                   "set_components JOIN "
                                   "component on set_components.component_id = component._id "
                                    "where set_id = ? AND tag != 'None' GROUP BY componentnamevalue",[set_id]).fetchall()