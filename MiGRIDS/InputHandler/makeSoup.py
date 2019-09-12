#string, string -> BeautifulSoup
#
def makeComponentSoup(component, saveDir):
    '''
    makes either a blank template soup or filled soup from existing component descriptor file
    assumes the component type is the first three characters of the component string.
    :param component: [String] the name of a component. The type is extracted from the name
    :param saveDir: [String] the directory  to save to.
    :return: BeautifulSoup
    '''
    import os
    import re
    from MiGRIDS.InputHandler.createComponentDescriptor import createComponentDescriptor
    from MiGRIDS.UserInterface.readComponentXML import readComponentXML

    def typeOfComponent(c):
        '''extracts the type of a component from its name
        :param c [String] the component name which consists of a component type + number'''
        match = re.match(r"([a-z]+)([0-9]+)", c, re.I)
        if match:
            componentType = match.group(1)
            return componentType
        return


    file = os.path.join(saveDir, component + 'Descriptor.xml')
    #if exists build soup
    if not os.path.isfile(file):
        # create a new xml based on template
        createComponentDescriptor(component, saveDir)

    componentType = typeOfComponent(component)
    mysoup = readComponentXML(componentType, file)

    return mysoup