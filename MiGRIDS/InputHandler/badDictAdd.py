# string, dictionary, string, list of indices -> dictionary
# adds a list of indices to a dictionary of bad values existing within a dataset.
def badDictAdd(component, currentDict, msg, loi):
    # if the component exists add the new error message to it, otherwise start a new set of component errror messages
    if isinstance(component,list):
        for c in component:
            try:
                currentDict[c][msg] = loi
            except KeyError:
                currentDict[c] = {msg: loi}
    else:
        try:
            currentDict[component][msg] = loi
        except KeyError:
            currentDict[component] = {msg: loi}
    return currentDict
