# -*- coding: utf-8 -*-
"""
Created on Sat Oct  6 17:53:34 2018

@author: tcmorgan2
"""
import os
from MiGRIDS.InputHandler.getUnits import getUnits
from MiGRIDS.Analyzer.DataRetrievers.readXmlTag import readXmlTag
from bs4 import BeautifulSoup

def readSetupFile(fileName):
    ''' Reads a setup.xml file and creates a dictionary of attributes used during the data import process.
    :param: filename [String] a file path to a setup.xml file.
    :return [dictionary] containing attributes needed for loading data.'''
    try:
        # project name
        projectName = readXmlTag(fileName,'project','name')[0]
        setupDir = os.path.dirname(fileName)
        # input specification
        inputDictionary = {}
        f = open(fileName)
        soup = BeautifulSoup(f.read(),"lxml")
        for tag in soup.find_all():
            if tag.name not in ['component','childOf','type']:
                for a in tag.attrs:
                    inputDictionary[tag.name + "." + a]=tag[a]
    except Exception as e:
        print(e)
    finally:
        f.close()
    return inputDictionary


                