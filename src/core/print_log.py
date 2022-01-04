#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Handle the output in the screen of the logs.
"""


def print_log(text: str, shows: bool = False):
    """
    It validates if it will show the log in console or not.

    :type text: str
    :param text: The text which will be displayed.

    :type shows: bool
    :param shows: The flag which.
    """
    if shows:
        print()
        print(text)
