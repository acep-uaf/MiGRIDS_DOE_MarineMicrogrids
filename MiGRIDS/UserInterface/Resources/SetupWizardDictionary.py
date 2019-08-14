# Projet: MiGRIDS
# Created by: # Created on: 8/12/2019
# Purpose :  SetupWizardDictionary

dlist = [
            {'title': 'Dates to model', 'prompt': 'Enter the timespan you would like to include in the model.', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'runTimesteps', 'folder': False, 'dates':True},
            {'title': 'System Components','prompt':'Indicate the number of each type of component to include.','sqltable': None,
             'sqlfield': None, 'reftable': None, 'name': 'componentNames'
            },
            {'title': 'Timestep', 'prompt': 'Enter desired timestep', 'sqltable': None, 'sqlfield': None,
              'reftable': 'ref_time_units', 'name': 'timeStep', 'folder': False},
            {'title': 'Project', 'prompt': 'Enter the name of your project', 'sqltable': None,
              'sqlfield': None, 'reftable': None, 'name': 'project', 'folder': False}
        ]
