# Project: MiGRIDS
# Author: T. Morgan
# Date: June 26, 2019
# License: MIT License (see LICENSE file of this package for more information)

# Contains custom error class to be raised if a valid date time format cannot be automatically detected.

class NoMatchException(Exception):
    """
    Exception raised if the datetime format cannot be automatically detected.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):

        self.message = message