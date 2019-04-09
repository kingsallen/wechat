# coding=utf-8


class InfraOperationError(Exception):
    def __init__(self, message=None):
        self.message = message


class MyException(Exception):

    def __init__(self, message=None):
        self.message = message
