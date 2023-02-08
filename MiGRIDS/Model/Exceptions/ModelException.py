class ModelException(Exception):
    """
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of error
    """

    def __init__(self, message):

        self.message = "Model cannot be run with specified inputs.".format(message)