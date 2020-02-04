import json

from MenuFactory import MenuFactory, MenuItem


class Settings:
    def __init__(self, path_to_settings="settings.json"):
        self.path = path_to_settings
        self.path_to_rrd_database = "rrd_database/"
        self.path_to_exports = "exports/"
        self.path_to_description_of_params = self.path_to_exports + "description_of_params/"
        self.path_to_merges_params = self.path_to_exports + "merges_params/"
        self.path_to_params_rrd = self.path_to_exports + "params_rrd/"
        self.path_to_graphs = self.path_to_exports + "graphs/"
        self.path_to_localization = "localization.json"
        self.localization = ""
        self.lang = "eng"
        self.start_point = "1419000000"
        self.end_point = "now"
        self.type_command = "AVERAGE"
        self.height_graph = "800"
        self.width_graph = "1024"
        self.init()

    def init(self):
        print("Load settings...")

        with open(self.path) as f:
            data = json.load(f)
            self.path_to_rrd_database = data['default']['path_to_rrd_database']
            self.path_to_exports = data['default']['path_to_exports']
            self.path_to_description_of_params = self.path_to_exports + data['default']['path_to_description_of_params']
            self.path_to_merges_params = self.path_to_exports + data['default']['path_to_merges_params']
            self.path_to_params_rrd = self.path_to_exports + data['default']['path_to_params_rrd']
            self.path_to_graphs = self.path_to_exports + data['default']['path_to_graphs']
            self.path_to_localization = data['default']['path_to_localization']
            self.start_point = data['default']['start_point']
            self.lang = data['default']['lang']
            self.end_point = data['default']['end_point']
            self.type_command = data['default']['type_command']
            self.height_graph = data['default']['height']
            self.width_graph = data['default']['width']
            self.load_localization(self.lang)

    def load_localization(self, lang):
        print("Load localization...")
        self.lang = lang

        with open(self.path_to_localization) as f:
            self.localization = json.load(f)[lang]

    def display_settings(self):
        print("path = " + self.path)
        print("path_to_rrd_database = " + self.path_to_rrd_database)
        print("path_to_exports = " + self.path_to_exports)
        print("path_to_description_of_params = " + self.path_to_description_of_params)
        print("path_to_merges_params = " + self.path_to_merges_params)
        print("path_to_params_rrd = " + self.path_to_params_rrd)
        print("path_to_graphs = " + self.path_to_graphs)
        print("path_to_localization = " + self.path_to_localization)
        print("localization = " + self.lang)
        print("start_point = " + self.start_point)
        print("end_point = " + self.end_point)
        print("type_command = " + self.type_command)
        print("height_graph = " + self.height_graph)
        print("width_graph = " + self.width_graph)

    def change_lang(self):
        menu = MenuFactory('Change language', lambda: [MenuItem('Russian', lambda: self.load_localization('rus')),
                                               MenuItem('English', lambda: self.load_localization('eng'))])

        menu.display_menu()
        print(self.lang)
