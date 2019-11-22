import os

#gets the file path for a specific folder within the application data ouput structure
from MiGRIDS.Controller.Exceptions import NoMatchException


def getFilePath(designator,**kwargs):
    #must provide either a setupFolder or project folder and designator
    if kwargs.get("projectFolder") != None:
        setupFolder = os.path.join(kwargs.get("projectFolder"),*['InputData','Setup'])

    else:
        setupFolder = kwargs.get('setupFolder')
    if kwargs.get('set') != None: #directories are referenced from a set folder
        setupFolder = os.path.realpath(os.path.join(kwargs.get('set'), 'Setup'))
        if designator == 'Processed':
            return os.path.realpath(os.path.join(setupFolder,*['..','..','..','InputData','TimeSeriesData','ProcessedData']))
        if designator == 'TimeSeriesData':
            return os.path.realpath(os.path.join(setupFolder,*['..','..','..','InputData','TimeSeriesData']))
        elif designator == 'OutputData':
            return os.path.realpath(os.path.join(setupFolder, *['..', '..','OutputData']))
        elif designator[0:3] == 'Run':
            return os.path.realpath(os.path.join(setupFolder, *['..',  kwargs.get('set'), designator]))
        elif designator == 'Project':
            return os.path.realpath(os.path.join(setupFolder,*['..','..','..']))
        elif designator == 'Setup':
            return setupFolder
        elif designator == 'Optimize':
            return setupFolder
        else:
            raise NoMatchException
    else: #directories are referenced from project setup folder
        if designator == 'Processed':
            return os.path.realpath(os.path.join(setupFolder,*['..','TimeSeriesData','ProcessedData']))
        if designator == 'TimeSeriesData':
            return os.path.realpath(os.path.join(setupFolder,*['..','..','TimeSeriesData']))
        elif designator == 'Components':
            return os.path.realpath(os.path.join(setupFolder, *['..', 'Components']))
        elif designator == 'OutputData':
            return os.path.realpath(os.path.join(setupFolder, *['..', '..','OutputData']))
        elif (designator[0:3] == 'Set') & (designator[-2:] != 'up') :
            return os.path.realpath(os.path.join(setupFolder, *['..', '..','OutputData', designator]))
        elif designator[0:3] == 'Run':
            return os.path.realpath(os.path.join(setupFolder, *['..', '..','OutputData', kwargs.get('Set'), designator]))
        elif designator == 'Project':
            return os.path.realpath(os.path.join(setupFolder,*['..','..']))
        elif designator == 'Setup':
            return setupFolder
        elif designator == 'Optimize':
            return setupFolder
        else:
            raise NoMatchException


