# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: November 3, 2017
# License: MIT License (see LICENSE file of this package for more information)

# fill in information about the project into the descriptor and setup xml files
#
#String, ModelSetupInformation - > None
def fillProjectData(projectDir=None):
    '''
    Calls function to create project data files depending on what parameters are provided
    If a projectDir is specified then files are created from csv files found in that directory
    If not projectDir is specified information contained in project_manager database is used to create input files.
    :param projectDir: [string] the directory that project data is saved in. If none, the project directory will be retrieved from the project
    manager database and xml files will be filled from information in the database.
    :return: None
    '''
    # general imports
    import sys
    import os
    here = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(here)
    from MiGRIDS.InputHandler.fillProjectDataFromCSV import fillProjectDataFromCSV
    from MiGRIDS.InputHandler.fillProjectDataFromDb  import fillProjectDataFromDb
    if projectDir is not None:
        fillProjectDataFromCSV(projectDir)
    elif projectDir is None:
        fillProjectDataFromDb()
    return