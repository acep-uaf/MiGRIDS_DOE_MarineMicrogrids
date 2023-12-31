# Projet: MiGRIDS
# Created by: # Created on: 10/28/2019
# Purpose :  getAllRuns
import re
import glob
import os

def getAllRuns(projectSetDir):
    def getNumber(mystring):
        d = re.findall(r'\d+', mystring)
        if d:
            return int(d[0])
        else:
            return None

    # os.chdir(projectSetDir)
    runDirs = glob.glob(os.path.join(projectSetDir, 'Run*/'))
    runs = [getNumber(os.path.basename(os.path.normpath(x))) for x in runDirs]
    return runs

def getAllSets(projectDir):
    '''
    Returns a list of directories titled Set... within a project output folder
    :param projectDir:
    :return: List of set directories
    '''
   # os.chdir(projectSetDir)
    setsDirs = glob.glob(os.path.join(projectDir, 'Set*/'))

    return setsDirs