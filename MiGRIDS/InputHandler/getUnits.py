# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 21, 2017
# License: MIT License (see LICENSE file of this package for more information)

#
def getUnits(projectName,projectDir):
    '''
     reads a series fo xml tags in component xml files and returns their values as a list
    :param projectName: [String] the name of a project
    :param projectDir: [String] the path where project files are saved
    :return: [ListOfString],[ListOfString],[ListOfString],[ListOfString],[ListOfString]
    '''
    # projectName is the name of the project *type string*
    # projectDir is the directory where the project setup xml file is located
    from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
    import numpy as np

    fileName = projectName + 'Setup.xml'
    # get header names of time series data to be manipulated to be used in the simulations

    headerTag = ['componentChannels','headerName']
    headerAttr = 'value'
    headerNames = readXmlTag(fileName,headerTag,headerAttr,projectDir)
    # get the units corresponding to header names
    attrTag = ['componentChannels','componentAttribute']
    attrAttr = 'unit'
    componentUnits = readXmlTag(fileName, attrTag, attrAttr, projectDir)
    # get the attributes (ie Power, wind speed, temperature, ...)
    attrTag = ['componentChannels', 'componentAttribute']
    attrAttr = 'value'
    componentAttributes = readXmlTag(fileName, attrTag, attrAttr, projectDir)
    # get the component name (ie gen1, wtg2,...)
    nameTag = ['componentChannels', 'componentName']
    nameAttr = 'value'
    componentNames = readXmlTag(fileName, nameTag, nameAttr, projectDir)
    # create new header names by combining the component name with the attribute (eg gen1P, wtg2WS, ...)
    newHeaderNames = np.core.defchararray.add(componentNames,
                                           componentAttributes)  # create column names to replace existing headers

    return headerNames, componentUnits, componentAttributes, componentNames, newHeaderNames
