__author__ = 'roosevelt'

import os
import sys


def is_frozen():
    return hasattr(sys, "frozen")


def module_path():
    # encoding = sys.getfilesystemencoding()
    if is_frozen():
        return os.path.dirname(str(sys.executable))
    return os.path.dirname(str(__file__))
