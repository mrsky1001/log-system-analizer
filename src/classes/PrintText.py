from termcolor import cprint
from enum import Enum


class Color:
    def __init__(self, color):
        self.color = color


class THEMES(Enum):
    ERROR = Color('red')
    WARNING = Color('yellow')
    SUCCESS = Color('green')
    INFO = Color('black')


def print_text(text, theme=THEMES.INFO):
    print(theme)
    print(cprint(text, theme.color))
