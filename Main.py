from RRDFactory import RRDFactory
from Settings import Settings
from MenuFactory import MenuFactory, init_menu_rrd_factory

settings = Settings()

rrd_factory = RRDFactory(settings=settings)
rrd_factory.parse_all_rrd()

menu_rrd_factory = MenuFactory('Main menu', lambda: init_menu_rrd_factory(settings, rrd_factory))
menu_rrd_factory.display_menu_repeat()
