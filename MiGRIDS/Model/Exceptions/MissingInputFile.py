# Projet: MiGRIDS
# Created by: # Created on: 10/16/2019
# Purpose :  MissingInputFile# Contains custom error class to be raised 

class MissingInputFileException(Exception):
    """
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):

        self.message = "A valid {} file was not found.".format(message)