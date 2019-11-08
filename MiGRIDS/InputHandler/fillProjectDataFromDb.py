#fill project xml files
#String, ModelSetupInformation - > None


def fillProjectDataFromDb():
    '''
    Fills project xml files from a model object provided from the user interface.
    Assumes the project has already been initialized throught the UI and empty setup and component xml files exist.
    :param setupInfo: [ModelSetupInformation] contains setup information attributes
    :return: None
    '''
    # general imports
    import sys
    import os
    from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor
    from MiGRIDS.InputHandler.writeXmlTag import writeXmlTag
    from MiGRIDS.Controller.ProjectSQLiteHandler import ProjectSQLiteHandler

    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)
    dbhandler = ProjectSQLiteHandler()
    projectSetup = dbhandler.getProject() + 'Setup.xml'
    setupFolder = os.path.join(os.path.dirname(__file__),
                                    *['..', '..', 'MiGRIDSProjects', dbhandler.getProject(), 'InputData', 'Setup'])

    #each field in the setup table gets an xml tag that matches the setup.xml file
    generalSetupInfo = dbhandler.getSetUpInfo()
    if generalSetupInfo != None:
        for k in generalSetupInfo.keys():  # for each key in the model attributes
            tags = k.split('.')
            #read key values
            if len(tags)>1:
                attr = tags[len(tags)-1] #the last value after '.' is the attr
                value = generalSetupInfo[k]
                writeXmlTag(os.path.join(setupFolder,projectSetup), tags[len(tags) -2], attr, value)
            else:
                attr = k # the last value after '.' is the attr
                value = generalSetupInfo[k]
                writeXmlTag(os.path.join(setupFolder,projectSetup), k, attr, value)

        #look for component descriptor files for all componentName
        componentDir = os.path.join(setupFolder, *['..','Components'])

        #component is a string
        if (generalSetupInfo['componentNames.value'] is not None) &(generalSetupInfo['componentNames.value'] != 'None'):
            #use as list not string
            if isinstance(generalSetupInfo['componentNames.value'],str):
                generalSetupInfo['componentNames.value'] = generalSetupInfo['componentNames.value'].split(" ") #this should make it a list
            if isinstance(generalSetupInfo['componentNames.value'],list):
                for component in generalSetupInfo['componentNames.value']: # for each component

                     #if there isn't a component descriptor file create one
                     if not os.path.exists(os.path.join(componentDir, component + 'Descriptor.xml')):
                         createComponentDescriptor(component, componentDir)




