# from src.modules.Settings import Settings
# from src.modules.RRDFactory import RRDFactory
from src.modules.Settings import settings
from src.modules.RRDFactory import rrd_factory
from src.modules.MenuFactory import MenuFactory, init_menu_rrd_factory

menu_rrd_factory = MenuFactory('Main menu', lambda: init_menu_rrd_factory(settings, rrd_factory))
menu_rrd_factory.display_menu_repeat()
