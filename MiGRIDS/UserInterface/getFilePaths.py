import os

#gets the file path for a specific folder within the application data ouput structure
def getFilePath(designator,**kwargs):
    #must provide either a setupFolder or project folder and designator
    if kwargs.get("projectFolder") != None:
        setupFolder = os.path.join(kwargs.get("projectFolder"),*['InputData','Setup'])
    else:
        setupFolder = kwargs.get('setupFolder')

    if designator == 'Processed':
        return os.path.join(setupFolder,*['..','TimeSeriesData','ProcessedData'])
    elif designator == 'Components':
        return os.path.join(setupFolder, *['..', 'Components'])
    elif designator == 'OutputData':
        return os.path.join(setupFolder, *['..', '..','OutputData'])
    elif (designator[0:3] == 'Set') & (designator[-2:] != 'up') :
        return os.path.join(setupFolder, *['..', '..','OutputData', designator])
    elif designator[0:3] == 'Run':
        return os.path.join(setupFolder, *['..', '..','OutputData', kwargs.get('Set'), designator])
    elif designator == 'Project':
        return os.path.join(setupFolder,*['..','..'])
    elif designator == 'Setup':
        return setupFolder

