# Projet: MiGRIDS
# Created by: # Created on: 7/29/2019
# Purpose :  componentSupport

def inferComponentName(compName):
    import re
    try:
        match = re.match(r"([a-z]+)([0-9]+)([a-z]+)", compName, re.I)
        if match:
            componentName = match.group(0) + match.group(1)
            return componentName
    except:
        return


# returns a possible component type inferred from the components column name
def inferComponentType(compName):
    import re
    try:
        match = re.match(r"([a-z]+)([0-9]+)", compName, re.I)
        if match:
            componentType = match.group(1)
            return componentType
    except:
        return
