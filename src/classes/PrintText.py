from termcolor import cprint
from enum import Enum


class THEME:
    def __init__(self, color):
        self.color = color


class THEMES_MESSAGE:
    ERROR = THEME('red')
    WARNING = THEME('yellow')
    SUCCESS = THEME('green')
    INFO = THEME('blue')
    MAIN = THEME(None)


def print_text(text, theme=THEMES_MESSAGE.MAIN):
    if isinstance(text, list):
        res = ' '.join((str(x) for x in text))
    else:
        res = text
    cprint(res, theme.color)
