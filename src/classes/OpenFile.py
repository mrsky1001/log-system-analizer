import os
from enum import Enum

from src.classes.PrintText import print_text, THEMES_MESSAGE
from src.modules.Settings import settings


class FORMATS_OPEN:
    READ = 'r'
    WRITE = 'w'
    APPEND = 'a'


def check_exist_file(filename, directory=settings.root_resources):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except Exception as e:
            print_text("Error: ", THEMES_MESSAGE.ERROR)
            print_text(e, THEMES_MESSAGE.ERROR)

    path = directory + filename

    if not os.path.isfile(path):
        with open(path, "w", newline=""):
            print_text('File ' + filename + ' created!', THEMES_MESSAGE.WARNING)

    return path


def open_file(filename, directory=settings.root_resources, type_open=FORMATS_OPEN.READ, attr=''):
    return open(check_exist_file(filename, directory), str(type_open) + attr, newline="")
