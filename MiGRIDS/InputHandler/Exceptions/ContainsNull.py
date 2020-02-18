# Projet: MiGRIDS
# Created by: # Created on: 2/13/2020
# Purpose :  ContainsNull# Contains custom error class to be raised 

class ContainsNullException(Exception):
    """
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):
        self.message = message