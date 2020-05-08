from src.classes.PrintText import print_text, THEMES_MESSAGE


def set_id(arr):
    i = 0
    for item in arr:
        i += 1
        item.id = str(i)


def init_menu_rrd_factory(settings, rrd_factory):
    print_text(settings.local.initialization_menu_rrd_database_factory)
    print_text(settings.local.local + settings.lang)

    list_item_menu = []

    list_item_menu.append(
        MenuItem(settings.local.display_settings, settings.display_settings))

    list_item_menu.append(MenuItem(settings.local.display_list_rrd_files,
                                   rrd_factory.display_list_rrd_files))
    list_item_menu.append(
        MenuItem(settings.local.select_rrd_file, rrd_factory.select_rrd_file))

    list_item_menu.append(MenuItem(settings.local.display_menu_selected_rrd_file,
                                   rrd_factory.selected_rrd.display_menu))
    list_item_menu.append(MenuItem(settings.local.export_params_all_rdd_files_to_csv,
                                   rrd_factory.export_params_all_rdd_files_to_csv))
    list_item_menu.append(
        MenuItem(settings.local.correlation_rrd_files, rrd_factory.correlation_rrd_files))

    list_item_menu.append(MenuItem(settings.local.change_lang, settings.change_lang))

    list_item_menu.append(MenuItem(settings.local.exit, exit))

    return list_item_menu


def init_menu_selected_rrd(settings, selected_rrd):
    list_item_menu = []

    list_item_menu.append(
        MenuItem(settings.local.display_settings, selected_rrd.display_settings))

    list_item_menu.append(MenuItem(settings.local.display_list_rrd_files,
                                   selected_rrd.display_list_rrd_files))
    list_item_menu.append(
        MenuItem(settings.local.select_rrd_file, selected_rrd.select_rrd_file))

    list_item_menu.append(MenuItem(settings.local.display_menu_selected_rrd_file,
                                   selected_rrd.selected_rrd.display_menu))

    list_item_menu.append(MenuItem(settings.local.export_params_all_rdd_files_to_csv,
                                   selected_rrd.export_params_all_rdd_files_to_csv))

    list_item_menu.append(MenuItem(settings.local.correlation_rrd_files,
                                   selected_rrd.correlation_rrd_files))

    list_item_menu.append(MenuItem(settings.local.change_lang, settings.change_lang))

    list_item_menu.append(MenuItem(settings.local.exit, exit))

    return list_item_menu


class MenuItem:
    def __init__(self, name, function):
        self.id = 0
        self.name = name
        self.function = function


class MenuFactory:
    def __init__(self, title, init_function):
        self.title = title
        self.list_item_menu = []
        self.init_function = init_function

    def display_menu_repeat(self):
        self.display_menu()
        self.display_menu_repeat()

    def display_menu(self):
        self.list_item_menu = self.init_function()
        set_id(self.list_item_menu)

        print_text("\n" + self.title, THEMES_MESSAGE.INFO)

        for item in self.list_item_menu:
            print_text(str(item.id) + str("." + item.name))

        ans = input("Selection:")

        try:
            for item in self.list_item_menu:
                if item.id == ans:
                    item.function()
                    break
        except Exception as e:
            print_text("Error:")
            print_text(e)
