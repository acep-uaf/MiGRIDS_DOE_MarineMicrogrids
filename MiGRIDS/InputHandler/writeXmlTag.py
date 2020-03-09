# Project: MiGRIDS
# Author: T. Morgan
# Date: September 17, 2020
# License: MIT License (see LICENSE file of this package for more information)

# write a value to an xml tag
def writeXmlTag(fileName,tag,attr,value):
    '''
    Writes a value to a specified tag and attribute within an xml file.
    :param fileName: [String] name of the xml to write
    :param tag: [String] tag to write
    :param attr: [String] attribute to write
    :param value: [String] value to write
    :param fileDir: [String] path to xml file
    :return: None
    '''
    # general imports
    import os
    import numpy as np
    from bs4 import BeautifulSoup

    # open file and read into soup
    with open(fileName, "r+") as infile:  # open
        contents_child =infile.read()
        soup = BeautifulSoup(contents_child, 'xml')  # turn into soup

        def findTag(soup,mytag):
            '''matches a tag in soup regardless of case'''
            a = soup.find(mytag)
            if a == None:
                a = soup.find(lambda tag:tag.name.lower() ==mytag.lower())
            return a
        # assign value
        if isinstance(tag,(list,tuple)): # if tag is a list or tuple, itereate down
            a = findTag(soup,tag[0])

            for i in range(1,len(tag)): # for each other level of tags, if there are any
                a = a.find(tag[i])
        else: # if it is just one string
            a = findTag(soup,tag)
        # convert value to strings if not already
        if isinstance(value, (list, tuple, np.ndarray)): # if a list or tuple, iterate
            value = [str(e) for e in value]
        else:
            value = str(value)
        if a is not None:
            a[attr] = value

    with open(fileName, 'w') as infile:
        # save again
        infile.write(soup.prettify())


    return
