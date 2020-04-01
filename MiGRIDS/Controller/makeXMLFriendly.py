def stringToXML(myString, i = 0):
    '''xml files for this project use space delimited lists so spaces withing a single value quotes
    :param myString: a string or list of strings to replace white space
    :return: String value of myString with white space string surrounded with quotes'''

    def singleString(thisString):
        if isinstance(thisString,str):
            if ' ' in thisString:
                return '"%s"' % thisString
        return thisString


    # If myString is a list alter all strings in the list
    if isinstance(myString, list):
        if i == len(myString):
            return " ".join(myString)
        else:
            myString[i] = singleString(myString[i])
            return stringToXML(myString, i + 1)
    else:  # if its a single string just alter the one string
        return singleString(myString)
    return myString


def xmlToString(myString,i = 0):
    '''xml files for this project use space delimited lists so whitespace strings need to have quotes removed
     to match actual file values'''
    def singleString(thisString):
        thisString = thisString.strip('\"')
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

