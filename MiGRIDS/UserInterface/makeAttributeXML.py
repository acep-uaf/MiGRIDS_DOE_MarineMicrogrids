# Projet: MiGRIDS
# Created by: T. Morgan # Created on: 8/16/2019

import datetime
import pandas as pd

#uses a set name and data model of component attribute changes to generate set#attribute.xml based on template
#string, Table -> Beautifulsoup
from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler


def makeAttributeXML(currentSet, compChanges, setChanges):
    soup = readTemplateAttributeXML()

    #fillSetInfo the soup to reflect the model
    #for each row in model


    #changes to component files

    #get a list of tuples for tag modifications

    updateComponentAttributes(currentSet, compChanges, soup)

    updateSetupAttributes(currentSet, setChanges, soup)
    return soup

def dropAttr(lotag):
        t = []
        a = []
        for l in lotag.split(','):
           t.append(".".join(l.split(".")[0:len(l.split(".")) - 1]))
           a.append(l.split(".")[-1])
        newT= ",".join(t)
        newA = ",".join(a)
        return newT, newA

def updateComponentAttributes(currentSet, compChanges,  soup):
    '''updates a soup with changes entered into the project database'''

    if len(compChanges) >0:
        compName, compTag, compValue = zip(*compChanges)
        splitTags = [dropAttr(t) for t in compTag]
        compTag,compAttr =list(zip(*splitTags))
        tag = soup.find('compName')
        tag.attrs['value'] = ' '.join(compName)
        tag = soup.find('compTag')
        tag.attrs['value'] = ' '.join(compTag)
        tag = soup.find('compAttr')
        tag.attrs['value'] = ' '.join(compAttr)
        tag = soup.find('compValue')
        tag.attrs['value'] = ' '.join(compValue)
        return soup

def updateSetupAttributes(currentSet, dataDict, soup):
    # Changes to setup file

    dataTuple = [(t, dataDict[t]) for t in dataDict.keys()]
    setupTag, setupValue = list(zip(*dataTuple))
    setupSplitTag = [dropAttr(t) for t in setupTag]
    setupTag, setupAttr = list(zip(*setupSplitTag))
    tag = soup.find('setupTag')
    tag.attrs['value'] = ' '.join(setupTag)
    tag = soup.find('setupAttr')
    tag.attrs['value'] = ' '.join(setupAttr)
    tag = soup.find('setupValue')
    tag.attrs['value'] = ' '.join(setupValue)
    return soup

def writeAttributeXML(soup,saveDir,setName):
    import os
    # write combined xml file
    if not os.path.exists(saveDir):
        os.makedirs(saveDir)
    f = open(os.path.join(saveDir,setName), "w")
    f.write(soup.prettify())
    f.close()
    return

def integerToTimeIndex(df, i):
    d = pd.to_datetime(df.index[int(i)]).date()
    return d

def timeStepsToInteger(d1,d2,df):

    d1 = datetime.datetime.strptime(d1, '%Y-%m-%d')
    d2 = datetime.datetime.strptime(d2, '%Y-%m-%d')

    #look in the dataframe to find the position of d1 and d2
    #where do we get the dataframe
    if (d1.date() > pd.to_datetime(df.index[0]).date())| (d2.date() < pd.to_datetime(df.last_valid_index()).date()):
        d1 = pd.to_datetime(df[d1:].first_valid_index())
        d2 = pd.to_datetime(df[:d2].last_valid_index())
        v1 = df.index.get_loc(d1)
        v2 = df.index.get_loc(d2)
        return ' '.join([str(v1),str(v2)])
    return 'all'

def readTemplateAttributeXML():
    from bs4 import BeautifulSoup
    import os
    # xml templates are in the model/resources/descriptor folder
    here = os.path.dirname(os.path.realpath(__file__))
    # pull xml from project folder
    resourcePath = os.path.join(here, '../Model/Resources/Setup')
    # get list of component prefixes that correspond to componentDescriptors

    # read the xml file

    infile_child = open(os.path.join(resourcePath, 'projectSetAttributes.xml'), "r")  # open
    contents_child = infile_child.read()
    infile_child.close()
    soup = BeautifulSoup(contents_child, 'xml')  # turn into soup
    parent = soup.childOf.string  # find the name of parent. if 'self', no parent file

    while parent != 'self':  # continue to iterate if there are parents
        fileName = parent + '.xml'
        infile_child = open(fileName, "r")
        contents_child = infile_child.read()
        infile_child.close()
        soup2 = BeautifulSoup(contents_child, 'xml')
        # find parent. if 'self' then no parent
        parent = soup2.childOf.string

        for child in soup2.component.findChildren():  # for each tag under component
            # check to see if this is already a tag. If it is, it is a more specific implementation, so don't add
            # from parent file
            if soup.component.find(child.name) is None:
                soup.component.append(child)

    return soup

