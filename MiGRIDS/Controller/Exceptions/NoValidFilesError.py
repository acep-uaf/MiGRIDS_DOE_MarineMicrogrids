# Project: MiGRIDS
# Author: T. Morgan
# Date: June 6, 2019
# License: MIT License (see LICENSE file of this package for more information)

# Contains custom error class to be raised if valid input files are not founds.


class NoValidFilesError(Exception):
    """
    Exception raised no valid file are found in an input directory.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):
        self.message = message