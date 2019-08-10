def stringToXML(myString, i = 0):
    '''xml files for this project use space delimited lists so spaces withing a single value get replaced with underscore
    :param myString: a string or list of strings to replace white space
    :return: String value of myString with white space filled with underscore'''

    def singleString(thisString):
        if isinstance(thisString,str):
           return thisString.replace('\s+','_')
        else:
            return thisString

    # If myString is a list alter all strings in the list
    if isinstance(myString, list):
        if i == len(myString):
            return myString
        else:
            myString[i] = singleString(myString[i])
            return xmlToString(myString, i + 1)
    else:  # if its a single string just alter the one string
        return singleString(myString)
    return myString


def xmlToString(myString,i = 0):
    import re
    '''xml files for this project use space delimited lists so underscores need to be replaced with whitespace to match actual file values'''
    def singleString(thisString):
        thisString = thisString.replace('_', ' ')
        #regex = re.compile(r"&(?!amp;|lt;|gt;)")
        #thisString = regex.sub("&amp;", thisString)
        return thisString

    # If myString is a list alter all strings in the list
    if isinstance(myString,list):
        if i == len(myString):
            return myString
        else:
            myString[i] = singleString(myString[i])
            return xmlToString(myString, i+1)
    else: #if its a single string just alter the one string
        return singleString(myString)
    return myString

