import os
from enum import Enum

from src.classes.PrintText import print_text, THEMES
from src.modules.Settings import Settings
from Main import settings


class TYPE_OPEN(Enum):
    READ = 'r'
    WRITE = 'w'
    APPEND = 'a'


def open_file(filename, directory=settings.root_resources, type_open=TYPE_OPEN.READ, attr=''):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print_text("Error: ", THEMES.ERROR)
            print_text(e, THEMES.ERROR)

    path = directory + filename

    if not os.path.isfile(path):
        with open(path, "w", newline=""):
            print_text('File ' + filename + ' created!', THEMES.SUCCESS)

    return open(path, type_open + attr, newline="")
