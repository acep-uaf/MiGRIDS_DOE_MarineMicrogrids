# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 18, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is for the reading of a CSV file of the type generated by AVEC
from MiGRIDS.Controller.makeXMLFriendly import stringToXML


def readCsv(inputDict):
    '''
    Reads a single csv file formatted in the AVEC style
    :param inputDict:  fileName,fileLocation,columnNames,useNames,componentUnits, dateColumnName, dateColumnFormat, timeColumnName, dst
    :return: pandas.DataFrame of the csv data.
    '''

    # general imports
    import numpy as np
    import os
    import pandas as pd
    from MiGRIDS.InputHandler.processInputDataFrame import processInputDataFrame

    # process input variables
    # convert numpy arrays to lists
    if type(inputDict['componentChannels.headerName.value'])== np.ndarray:
        inputDict['componentChannels.headerName.value'] = inputDict['componentChannels.headerName.value'].tolist()
    if type(inputDict['componentChannels.componentName.value'])== np.ndarray:
        inputDict['componentChannels.componentName.value'] = inputDict['componentChannels.componentName.value'].tolist()
 

    #------------------- load the file -----------------------------
    df = pd.read_csv(os.path.join(inputDict['inputFileDir.value'],
                                  inputDict['fileName.value'])) # read as a data frame
    # check and see if the df column names match the input specification.
    # TODO: throw a catch in here in case it does not find the headers
    gotHeader = False
    columnNamesFromCSV = stringToXML(df.columns)
    if inputDict['componentChannels.headerName.value'][0] not in columnNamesFromCSV:
        # if the first row is not the header, look for it further down in the file
        for col in df.columns:
            a = df[col].astype(str)
            a = a.str.replace(r'\s+', '_')
            # get the matches for the column name
            idxMatch = a.index[a == inputDict['componentChannels.headerName.value'][0]].tolist()
            if len(idxMatch) != 0:
                df.columns = df.loc[idxMatch[0]].str.replace(r'\s+', '_')
                gotHeader = True
                break
        if gotHeader is False:
            raise ValueError('Input column names were not found in the CSV file.')
    inputDict['df'] = df
    df = processInputDataFrame(inputDict)

    return df
