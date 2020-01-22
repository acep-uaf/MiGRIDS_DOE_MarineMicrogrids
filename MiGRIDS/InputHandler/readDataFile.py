# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)
# assumes the first column is always a date column
# reads data files from user and outputs a dataframe.
def readDataFile(inputDict):
    # inputSpecification points to a script to accept data from a certain input data format *type string*
    # fileLocation is the dir where the data files are stored. It is either absolute or relative to the GBS project InputData dir *type string*
    # fileType is the file type. default is csv. All files of this type will be read from the dir *type string*
    # columnNames, if specified, is a list of column names from the data file that will be returned in the dataframe.
    # otherwise all columns will be returned. Note indexing starts from 0.*type list(string)*
    
    ####### general imports #######
    import pandas as pd
    import os
    import importlib.util
    import numpy as np
    from MiGRIDS.InputHandler.readAllTimeSeries import readAllTimeSeries
    from MiGRIDS.InputHandler.readWindData import readWindData
    from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
    from MiGRIDS.InputHandler.Component import Component

    
    ### convert inputs to list, if not already
    if not isinstance(inputDict['componentChannels.headerName.value'],(list,tuple,np.ndarray)):
        inputDict['componentChannels.headerName.value'] = [inputDict['componentChannels.headerName.value']]
    if not isinstance(inputDict['componentChannels.componentName.value'], (list, tuple, np.ndarray)):
        inputDict['componentChannels.componentName.value'] = [inputDict['componentChannels.componentName.value']]
    if not isinstance(inputDict['componentChannels.componentAttribute.unit'], (list, tuple, np.ndarray)):
        inputDict['componentChannels.componentAttribute.unit'] = [inputDict['componentChannels.componentAttribute.unit']]
    if not isinstance(inputDict['componentChannels.componentAttribute.value'], (list, tuple, np.ndarray)):
        inputDict['componentChannels.componentAttribute.value'] = [inputDict['componentChannels.componentAttribute.value']]
    
    
    # get just the filenames ending with fileType. check for both upper and lower case
    # met files are text.
    if inputDict['inputFileType.value'].lower() == 'met':
        inputDict['inputFileName.value'] = [f for f in os.listdir(inputDict['inputFileDir.value']) if
                     os.path.isfile(os.path.join(inputDict['inputFileDir.value'],f)) & (f.endswith('TXT') or f.endswith('txt'))]
    else:
        inputDict['fileNames.value'] = [f for f in os.listdir(inputDict['inputFileDir.value']) if
                     os.path.isfile(os.path.join(inputDict['inputFileDir.value'],f)) & (f.endswith(inputDict['inputFileType.value'].upper()) or f.endswith(inputDict['inputFileType.value'].lower()))]
       
    df = pd.DataFrame()
    ####### Parse the time series data files ############
    # depending on input specification, different procedure
    if inputDict['inputFileType.value'].lower() =='csv':
        #TODO multiprocess call here
        df = readAllTimeSeries(inputDict)
        #readAllTimeSeries(inputDict,result)
    elif inputDict['inputFileType.value'].lower() == 'met':
        #TODO multiprocess call here
        fileDict, df = readWindData(inputDict)
    # while result:
    #     concat(result)
    # convert units
    if np.all(inputDict['componentChannels.componentAttribute.unit'] != None):
        # initiate lists

        listOfComponents = []
        if inputDict['componentChannels.componentAttribute.value'] != None:
            for i in range(len(inputDict['componentChannels.componentAttribute.unit'])): #for each channel make a component object
       
                # cd to unit conventions file
                dir_path = os.path.dirname(os.path.realpath(__file__))                
                unitConventionDir = os.path.join(dir_path, *['..','Analyzer','UnitConverters'])
                # get the default unit for the data type
                units = readXmlTag('internalUnitDefault.xml', ['unitDefaults', inputDict['componentChannels.componentAttribute.value'][i]], 'units', unitConventionDir)[0]
                # if the units don't match, convert
                if units.lower() != inputDict['componentChannels.componentAttribute.unit'][i].lower():
                    unitConvertDir = os.path.join( dir_path,*['..','Analyzer','UnitConverters','unitConverters.py'])
                    funcName = inputDict['componentChannels.componentAttribute.unit'][i].lower() + '2' + units.lower()
                    # load the conversion
                    spec = importlib.util.spec_from_file_location(funcName, unitConvertDir)
                    uc = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(uc)
                    x = getattr(uc, funcName)
                    # update data
                    df[inputDict['componentChannels.componentName.value'][i]] = x(df[inputDict['componentChannels.componentName.value'][i]])
                # get the scale and offset
                scale = readXmlTag('internalUnitDefault.xml', ['unitDefaults', inputDict['componentChannels.componentAttribute.value'][i]], 'scale',
                                   unitConventionDir)[0]
                offset = readXmlTag('internalUnitDefault.xml', ['unitDefaults', inputDict['componentChannels.componentAttribute.value'][i]], 'offset',
                                    unitConventionDir)[0]
               
                
                df[inputDict['componentChannels.componentName.value'][i]] = df[inputDict['componentChannels.componentName.value'][i]]*int(scale) + int(offset)
                # get the desired data type and convert
                datatype = readXmlTag('internalUnitDefault.xml', ['unitDefaults', inputDict['componentChannels.componentAttribute.value'][i]], 'datatype',
                                      unitConventionDir)[0]
                
                listOfComponents.append(Component(
                        component_name = inputDict['componentChannels.componentName.value'],
                        column_name=inputDict['componentChannels.headerName.value'][i],
                        units=units,scale=scale,
                        offset=offset,datatype=datatype,
                        attribute=inputDict['componentChannels.componentAttribute.value']))

   
    #drop unused columns
    df = df[inputDict['componentChannels.componentName.value'] + ['DATE']]
    df['source'] = inputDict['inputFileDir.value']
    return df, listOfComponents

