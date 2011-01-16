# -*- coding: utf-8 -*-
"""
This module contains the classes used for errors handling.
"""

class BitlyApiError(Exception):
    """
    Generic exception for API errors.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ArgumentError(BitlyApiError):
    """
    An invalid argument was given.
    """
    pass


class ArgTypeError(ArgumentError):
    """
    An argument does not have the expected type.
    """
    def __init__(self, arg, given, expected):
        self.value = "Argument '%s' has type '%s', expected '%s'." % (
            arg, given, expected
        )

    def __str__(self):
        return repr(self.value)
