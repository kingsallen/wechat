# coding=utf-8


class InfraOperationError(Exception):
    pass

class MyException(Exception):

    def __init__(self, message=None):
        self.message = message
