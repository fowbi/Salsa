# -*- coding: utf-8 -*-



class SalsaException(Exception):
    "Custom Salsa Exception."
    def __init__(self, message):
        Exception.__init__(self, message)


class SalsaConnectionException(SalsaException):
    "Connection related exceptions"
    pass
