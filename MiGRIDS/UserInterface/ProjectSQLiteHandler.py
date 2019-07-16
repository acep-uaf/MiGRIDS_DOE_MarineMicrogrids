import pandas as pd

class ProjectSQLiteHandler:

    def __init__(self, database='project_manager'):
        import sqlite3 as lite
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
            projectPath = self.cursor.execute("select project_path from project").fetchone()
            if projectPath is not None:
                return projectPath[0]

    def tableExists(self, table):
        try:
            self.cursor.execute("select * from " + table + " limit 1").fetchall()
        except:
            return False
        return True
    #String, integer -> String
    '''def getComponentData(self, column, row):
        if column != '':
            values = self.cursor.execute("select " + column + " from components limit ?", [row+1]).fetchall()

            if (len(values) > row) :
                value = values[row][0]
                if value is not None:
                    return value

        return'''

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

    '''def getDataTypeCodes(self):
        return self.cursor.execute("Select code from ref_file_type").fetchall()'''

    def updateDefaultSetup(self,values):
        self.cursor.prepare(
            "UPDATE setup set date_start = ?, date_end = ?, component_names = ? where set_name = 'default'",
            [values['date_start'],values['date_end'],values['component_names']])
        self.connection.commit()

    #String, ListOfTuples -> None
    def addRefValues(self, tablename, values):

        self.cursor.executemany("INSERT INTO " + tablename + "(sort_order,code, description) VALUES (?,?,?)" ,values)
        self.connection.commit()

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
        self.addRefValues('ref_time_units',[(0,'S','Seconds'),(1,'m','Minutes')])
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
        project_name text);""")

        #component files contains information for loading component data
        self.cursor.execute("DROP TABLE IF EXISTS component_files")
        self.cursor.executescript("""CREATE TABLE component_files
         (_id integer primary key,
         component_id integer,
         inputfile integer,
         original_field_name text
         );""")
        self.connection.commit()


        #component contains information that is relevant to the loaded component data
        self.cursor.execute("DROP TABLE IF EXISTS component")
        self.cursor.executescript("""CREATE TABLE component
                 (_id integer primary key,
                 component_type text,
                 component_name text,
                 units text,
                 scale numeric,
                 offset numeric,
                 attribute text,       
                 FOREIGN KEY (component_type) REFERENCES ref_component_type(code),
                 FOREIGN KEY (units) REFERENCES ref_universal_units(code),
                 FOREIGN KEY (attribute) REFERENCES ref_attributes(code)
                  );""")
        self.connection.commit()

        self.cursor.execute("DROP TABLE IF EXISTS set_components")
        self.cursor.executescript("""
        CREATE TABLE IF NOT EXISTS set_components
        (_id integer primary key,
        set_id integer , 
        component_id integer,
        tag text,
        tag_value text);""")


        self.cursor.execute("DROP TABLE IF EXISTS input_files")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS input_files
                (_id integer primary key,
                project_id integer,
                inputfiletypevalue text , 
                datatype text ,
                inputfiledirvalue text,
                timestep text,
                datechannelvalue text,
                datechannelformat text,
                timechannelvalue text,
                timechannelformat text,
                includechannels text,
                timezonevalue text,
                usedstvalue text,
                FOREIGN KEY (timechannelformat) REFERENCES ref_time_format(code),
                FOREIGN KEY (datechannelformat) REFERENCES ref_date_format(code));""")

        #The table optimize input only contains parameters that were changed from the default
        self.cursor.execute("Drop TABLE IF EXISTS optimize_input")
        self.cursor.executescript("""
                     CREATE TABLE IF NOT EXISTS optimizer_input
                     (_id integer primary key,
                     parameter text,
                     parameter_value text);""")

        self.cursor.execute("DROP TABLE IF EXISTS run")
        self.cursor.executescript("""
                CREATE TABLE IF NOT EXISTS run
                (_id integer primary key,
                set_id text,
                set_name text
                run_name text);""")

        self.cursor.execute("DROP TABLE IF EXISTS setup")
        self.cursor.executescript("""
                        CREATE TABLE IF NOT EXISTS setup
                        (_id integer primary key,
                        project integer,
                        set_name unique,
                        date_start text,
                        date_end text,
                        timestep integer,
                        timeunit text
                        
                        );""")

        self.cursor.execute("INSERT INTO setup (set_name,timestep,date_start,date_end) values('default',1,'2016-01-01','2016-12-31')")

        '''self.cursor.execute("DROP TABLE IF EXISTS environment")
        self.cursor.executescript("""CREATE TABLE IF NOT EXISTS environment
                 (_id integer primary key,
                 inputfiledir text,
                 original_field_name text,
                 component_name text unique,
                 units text,
                 scale numeric,
                 offset numeric,
                 attribute text,
                 tags text,
                 
                 FOREIGN KEY (units) REFERENCES ref_universal_units(code),
                 FOREIGN KEY (attribute) REFERENCES ref_env_attributes(code)
                 
                 );""")
        '''

        self.connection.commit()
    def clearTable(self,table):
        self.cursor.execute("Delete From " + table)
        self.connection.commit()

    def getSetInfo(self,set='set0'):
        '''
        Creates a dictionary of setup information for a specific set, default is set 0 which is the base case
        :param set: String name of the set to get information for
        :return: dictionary of xml tags and values to be written to a setup.xml file
        '''
        setDict = {}
        #get tuple for basic set info
        values = self.cursor.execute("select project_name, timestep, timeunit, date_start, date_end from setup join project on setup.project = project._id where set_name = '" + set + "'").fetchone()
        if values is not None:
            setDict['project name'] = values[0]
            setDict['timestep.value'] = values[1]
            setDict['timestep.unit']=values[2]
            setDict['date_start'] = values[3]
            setDict['date_end'] = values[4]
            #as long as there was basic set up info look for component setup info
            #componentNames is a list of distinct components, order does not matter
            setDict['componentNames'] =  self.cursor.execute("SELECT group_concat(component_name,' ') from component join set_components on component._id = set_components.component_id "
                                                             "join setup on set_components.set_id = setup._id where set_name = '" + set + "'").fetchone()[0]



            #componentChannels has ordered lists for directories and the components they contain. A component can have data in more than one directory and file type, in which case it would
            #be listed more than once in componentChannels
            values = self.cursor.execute(
            "select group_concat(inputfiledirvalue,' '), group_concat(inputfiletypevalue,' '),group_concat(component_name,' '),"
            "group_concat(original_field_name, ' '),group_concat(attribute, ' '), group_concat(units, ' '),group_concat(datechannelvalue, ' '),group_concat(timechannelvalue,' '),"
            "group_concat(datechannelformat, ' '),group_concat(timechannelformat, ' '), "
            "group_concat(timezonevalue, ' '), group_concat(usedstvalue, ' ') "
            "from input_files join "
            "(select component._id as component_id, inputfile, component_name, original_field_name, attribute, units from component_files "
            "Inner JOIN component on component_files.component_id = component._id "
            "Inner Join set_components on component._id = set_components.component_id "
            "Inner Join setup on set_components.set_id = setup._id  where set_name = '" + set + "' ORDER BY component_id) as components"
            " ON components.inputfile = input_files._id ORDER BY input_files._id").fetchone()

            if values is not None:
                setDict['inputFileDir'] = values[0]
                setDict['inputFileType'] = values[1]
                setDict['componentChannels.componentName']= values[2]
                setDict['componentChannels.headerName'] = values[3]
                setDict['componentChannels.componentAttribute.value'] = values[4]
                setDict['componentChannels.componentAttribute.unit'] = values[5]
                setDict['dateChannel.value']=values[6]
                setDict['dateChannel.format'] = values[8]
                setDict['timeChannel.value'] = values[7]
                setDict['timeChannel.format'] = values[9]
                setDict['timeZone'] =  values[10]
                setDict['inputDST'] = values[11]

        else:
            return None

        return setDict
    #inserts a single record into a specified table given a list of fields to insert values into and a list of values
    #String, ListOfString, ListOfString
    def insertRecord(self, table, fields, values):
        '''
        Insert a record in a specified table
        :param table: String name of the table to insert a record in
        :param fields: List of String field names
        :param values: List of values in to insert into fields
        :return: Boolean True if record was added
        '''
        string_fields = ','.join(fields)
        string_values = ','.join('?' * len(values))
        try:
            self.cursor.execute("INSERT INTO " + table + "(" + string_fields + ")" + "VALUES (" + string_values + ")", values)
            self.connection.commit()
            return True
        except Exception as e:
            print(e)
            return False

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
        updateFields = ', '.join([a + " = '" + b + "'" for a,b in zip(fields,values)])

        keyFields = ', '.join([a + " = '" + b + "'" for a,b in zip(keyField,keyValue)])
        try:
            self.cursor.execute("UPDATE " + table + " SET " + updateFields + " WHERE " + keyFields
                                )
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
        finalName = self.cursor.execute("SELECT component_name FROM component where component_type = '" + componentType + "' ORDER BY component_name DESC").fetchone()
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



    #updates the component table with a key and values in a dictionary
    #Dictionary -> None
    def updateComponent(self, dict):
        for k in dict.keys():
            try:
                self.cursor.execute("UPDATE component SET " + k + " = ? WHERE component_name = ?", [dict[k],dict['component_name']])
            except:
                print('%s column was not found in the data table' %k)
        self.connection.commit()

    #determines if a component record needs to be created or updated and implements the correct function
    #returns true if the record is a new record and was added to the table
    #dictionary -> Boolean
    def writeComponent(self,componentDict):
        if len(self.cursor.execute("SELECT * FROM components where component_name = ?", [componentDict['component_name']]).fetchall()) > 0:
            self.updateComponent(componentDict)
        else:
            self.cursor.execute('INSERT INTO components (component_name) VALUES (?)', [componentDict['component_name']])
            self.updateComponent(componentDict)
            return True
        return False

    #returns a table of values for the code column in a a reference table
    #String -> pandas.Series
    def getCodes(self,table):

        import pandas as pd
        codes = pd.read_sql_query("select code from " + table + " ORDER BY sort_order", self.connection)

        codes = (codes['code']).tolist()

        return codes

    def getComponentNames(self):
        '''
        returns a list of names for components in the components table
        :return: list of string component names
        '''
        names = self.cursor.execute("select component_name from components").fetchall()
        if len(names) >0:
            names = [''.join(i) for i in names if i is not None]
            return pd.Series(names).tolist()
        return []

    def getComponentsTable(self, filter):
        '''

        :param filter: String name of inputfiledir
        :return: pandas.dataframe of component attributes editable in the component table
        '''
        sql = """select component_name, component_type, original_field_name, units,attribute from components where inputfiledir = ?"""
        df = pd.read_sql_query(sql,self.connection,params=[filter])
        '''sql = """select component_name, 'env', original_field_name, units,attribute from environment where inputfiledir = ?"""
        df.append(pd.read_sql_query(sql,self.connection,params=[filter]))'''
        return df
    def getInputPath(self, pathNum):
        '''returns the file folder for the given input file number (corrasponds to fileblock in setup page)'''
        path = self.cursor.execute("select inputfiledirvalue from input_files where _id = " + pathNum).fetchone()
        if path is not None:
           return path[0]
        return
    def dataComplete(self):
        required={'components':['original_field_name','component_type','component_name','units','attribute'],
'environment':['original_field_name','component_name','units','attribute'],
'project':['project_path']}
        for k in required.keys():
            condition = ' OR '.join(['{0} IS NULL'.format(x) for x in required[k]])
            m = self.cursor.execute("select * from " + k + " where " + condition).fetchall()
            if len(self.cursor.execute("select * from " + k + " where " + condition).fetchall()) > 1 :
                return False
        return True
    '''gets a list of possible component types from the ref_component_type table'''
    def getComponentTypes(self):
        loT = pd.read_sql_query("select code from ref_component_type",self.connection)
        loT = pd.Series(loT).tolist()
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

    def getAllRecords(self,table):
        return self.cursor.execute("select * from " + table).fetchall()