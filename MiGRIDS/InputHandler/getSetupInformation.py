def getSetupInformation(setupXML):
    '''
    Creates a dictionary based on tags in the setup xml
    :param setupXML: [String] path to a setup xml file

    :return: Dictionary with tags from setup.xml as keys
    '''

    from bs4 import BeautifulSoup
    import os
    #read the setupfile
    infile = open(setupXML, "r")
    contents = infile.read()

    soup = BeautifulSoup(contents, 'xml')
    setupInfo={}
    # # get project name
    setupInfo['project'] = soup.project.attrs['name']

    # get children
    children = soup.findChildren()  # get all children
    #find all the children and assign them to the setupInfo model
    for i in range(len(children)):
        #the project tag is different so skip it here
        if children[i].name != 'project':
            setupInfo[children[i].name] = children[i].name
            if children[i].attrs is not None:
                for k in children[i].attrs.keys():
                    setupInfo[children[i].name + "." + k]= children[i][k]

    infile.close()
    setupInfo['projectPath'] = os.path.join(setupXML,'..','..','..')
    return setupInfo