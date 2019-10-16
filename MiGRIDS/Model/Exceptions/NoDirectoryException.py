# Projet: MiGRIDS
# Created by: # Created on: 10/16/2019
# Purpose :  NoDirectoryException# Contains custom error class to be raised None

class NoDirectoryException(Exception):
    """
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):
        self.message = message