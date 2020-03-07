# Projet: MiGRIDS
# Created by: # Created on: 2/20/2020
# Purpose :  DataValidationError# Contains custom error class to be raised 

class DataValidationError(Exception):
    """
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):

        self.message = self.descriptiveMessage(message)

    def descriptiveMessage(self,m):
        if m ==1:
            return "Missing power components. Datasets must have at least 1 power component."
        if m ==2:
            return "Missing load components. Datasets must have at least 1 load column."
        if m ==3:
            return "I don't know what is wrong, but your data is wonky."