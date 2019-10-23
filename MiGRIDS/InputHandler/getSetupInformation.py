def getSetupInformation(setupXML):
    '''
    Creates a dictionary based on tags in the setup xml
    :param setupXML: [String] path to a setup xml file

    :return: Soup from setup xml
    '''

    from bs4 import BeautifulSoup

    try:#read the setupfile
        with open(setupXML, "r") as infile:
            contents = infile.read()
            soup = BeautifulSoup(contents, 'xml')
        return soup
    except FileNotFoundError as e:
        return None

def setupToDictionary(soup,setupXML):
    '''converts a soup object into a setup dictionary'''
    import os
    setupInfo={}
    try:
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


        setupInfo['projectPath'] = os.path.join(setupXML,'..','..','..')
        return setupInfo
    except:
        return None