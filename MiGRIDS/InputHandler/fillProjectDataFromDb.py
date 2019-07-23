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
    from MiGRIDS.UserInterface.ProjectSQLiteHandler import ProjectSQLiteHandler

    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)
    dbhandler = ProjectSQLiteHandler()
    projectSetup = dbhandler.getProject() + 'Setup.xml'
    setupFolder = os.path.join(os.path.dirname(__file__),
                                    *['..', '..', 'MiGRIDSProjects', dbhandler.getProject(), 'InputData', 'Setup'])

    #each field in the setup table gets an xml tag
    generalSetupInfo = dbhandler.getSetInfo('set0')
    for k in generalSetupInfo.keys():  # for each key in the model attributes
        #read key values

        for v in generalSetupInfo[k].keys():
            attr = v
            value = generalSetupInfo[k][v]
            writeXmlTag(projectSetup, k, attr, value, setupFolder)


    #look for component descriptor files for all componentName
    componentDir = os.path.join(setupInfo.setupFolder, *['..','Components'])

    #component is a string
    if (setupInfo.componentNames.value is not None):
        #use as list not string
        if (len(setupInfo.componentNames.value.split()) >0):
            for component in setupInfo.componentNames.value.split(): # for each component

                 #if there isn't a component descriptor file create one
                 if not os.path.exists(os.path.join(componentDir, component + 'Descriptor.xml')):
                     createComponentDescriptor(component, componentDir)



