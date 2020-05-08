import csv
import subprocess
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import rrdtool
import re
import warnings

from src.classes.PrintText import print_text, THEMES_MESSAGE
from src.classes.OpenFile import open_file, FORMATS_OPEN
from src.modules.Settings import settings

warnings.filterwarnings("ignore")

import os
from tabulate import tabulate

from src.modules.RRD import RRD
from src.modules.MenuFactory import MenuItem, set_id


class RRDFactory:
    def __init__(self):
        self.list_all_params = []
        self.list_rrd = []
        self.list_item_menu = []
        self.selected_rrd = RRD

    def parse_all_rrd(self):
        print_text(settings.local.parsing_ngraph)
        directory = settings.path_to_description_of_params

        try:
            subprocess.Popen(
                ["perl", settings.root_resources + "parsengraph.pl", settings.path_to_description_of_params],
                stdout=subprocess.PIPE).wait()
        except Exception as e:
            print_text(settings.local.parsing_ngraph_failed, THEMES_MESSAGE.ERROR)
            print_text(e, THEMES_MESSAGE.ERROR)

        descriptions = []

        with open_file("table_description_params_rrd.csv", directory, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                descriptions.append(row)

        print_text(settings.local.loading_rrds)
        for root, dirs, files in os.walk(settings.path_to_rrd_database):
            for filename in files:
                if filename.endswith(".rrd"):
                    try:
                        rrdtool.info(root + "/" + filename)

                        # name = re.findall("[^/]*\w+$", root)[0]
                        name = ""
                        description = ""

                        for item in descriptions:
                            if filename.lower() in item[2].lower():
                                name = item[0]
                                description = item[1]
                                break

                        rrd = RRD(name_host=name,
                                  description=description,
                                  path_to_database=root,
                                  file_name=filename,
                                  start_point=settings.start_point,
                                  end_point=settings.end_point,
                                  type_command=settings.type_command,
                                  height=settings.height_graph,
                                  width=settings.width_graph)

                        list_ds = rrd.parse_ds
                        self.list_rrd.append(rrd)

                        for ds in list_ds:
                            self.list_all_params.append(str(rrd.name_host) + "." + str(ds))
                    except Exception as e:
                        print_text(e, THEMES_MESSAGE.ERROR)
        if len(self.list_rrd) > 0:
            self.selected_rrd = self.list_rrd[0]
            print_text(settings.local.complete_load_rrds + "(" + str(len(self.list_rrd)) + ")", THEMES_MESSAGE.SUCCESS)
        else:
            print_text(settings.local.not_found_rrds, THEMES_MESSAGE.WARNING)

        return self.list_all_params

    def select_rrd_file(self):
        print_text(settings.local.menu_select_rrd_file, THEMES_MESSAGE.INFO)

        types_input = [MenuItem(settings.local.search_on_name_of_param, self.search_rrd_on_param),
                       MenuItem(settings.local.search_on_name_of_file, self.search_rrd_on_filename)]

        set_id(types_input)

        for item in types_input:
            print_text(str(item.id) + str(". " + item.name))

        ans = input(settings.local.input)

        try:
            for item in types_input:
                if item.id == ans:
                    self.display_list_rrd_files()
                    item.function()
                    break
        except Exception as e:
            print_text(settings.local.error, THEMES_MESSAGE.ERROR)
            print_text(e, THEMES_MESSAGE.ERROR)

    def search_rrd_on_param(self):
        print_text(settings.local.menu_of_search_rrd_on_param, THEMES_MESSAGE.INFO)
        param = input(settings.local.input_name_rrd)

        for rrd in self.list_rrd:
            if rrd.name_host == param:
                self.selected_rrd = rrd
                print_text(settings.local.search_successful, THEMES_MESSAGE.SUCCESS)
                break

        if type(self.selected_rrd) is not RRD:
            print_text(settings.local.not_found, THEMES_MESSAGE.WARNING)
        else:
            self.selected_rrd.display_settings()

        return self.selected_rrd

    def search_rrd_on_filename(self):
        print_text(settings.local.menu_of_search_rrd_on_filename, THEMES_MESSAGE.INFO)
        param = input(settings.local.input_filename_rrd)

        self.selected_rrd = self.search_rrd(param)

        if type(self.selected_rrd) is not RRD:
            print_text(settings.local.not_found, THEMES_MESSAGE.WARNING)
        else:
            self.selected_rrd.display_settings()

        return self.selected_rrd

    def display_list_rrd_files(self):

        list_headers = [settings.local.name, settings.local.description, settings.local.file]
        list_rows = []

        for rrd in sorted(self.list_rrd, key=lambda rrd: rrd.name_host):
            list_rows.append(
                [rrd.name_host, rrd.description,
                 re.findall("[^/]*\w+$", rrd.path_to_database)[0] + "/" + rrd.file_name])

        table = tabulate(list_rows, headers=list_headers, tablefmt="orgtbl")

        filename = "table_description_params_rrd.txt"
        with open_file(filename,
                       settings.path_to_description_of_params,
                       FORMATS_OPEN.WRITE) as the_file:
            the_file.write(table)
        print_text(settings.local.table_params_out_file + settings.path_to_description_of_params + filename)

        print_text(settings.local.show_table_params, THEMES_MESSAGE.INFO)
        if input(settings.local.input).lower() == settings.local.yes.lower():
            print_text(settings.local.list_rrds_table, THEMES_MESSAGE.INFO)
            print_text(table)

    def export_params_all_rdd_files_to_csv(self):

        for rrd in self.list_rrd:
            print_text(rrd.csv_export())

    def csv_concat(self, rrd1, rrd2):

        f1 = rrd1.csv_export()
        f2 = rrd2.csv_export()

        df1 = pd.read_csv(f1)
        df2 = pd.read_csv(f2)

        keys1 = list(df1)
        keys2 = list(df2)

        print_text(keys1)
        print_text(keys2)

        for idx, row in df2.iterrows():
            data = df1[df1["timestamp"] == row["timestamp"]]
            if data.empty:
                print_text(settings.local.data_merge_on_time_empty, THEMES_MESSAGE.WARNING)
                next_idx = len(df1)
                for key in keys2:
                    df1.at[next_idx, key] = df2.at[idx, key]

            else:
                i = int(data.index[0])
                for key in keys2:
                    if key not in keys1:
                        df1.at[i, key] = df2.at[idx, key]

        directory = "csv_merge/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        df1.to_csv(directory + "merge_" + rrd1.name_host + "_" + rrd2.name_host + ".csv", index=False, encoding="utf-8",
                   quotechar="", quoting=csv.QUOTE_NONE)
        return df1

    def search_rrd(self, file_name):
        for rrd in self.list_rrd:
            if rrd.file_name == file_name or re.sub(".rrd", "", rrd.file_name) == file_name:
                print_text(settings.local.search_successful, THEMES_MESSAGE.SUCCESS)
                return rrd

    def correlation_rrd_files(self):
        self.display_list_rrd_files()

        rrd1 = self.search_rrd(input(settings.local.input_filename_rrd_number + "1: "))
        rrd2 = self.search_rrd(input(settings.local.input_filename_rrd_number + "2: "))

        if type(rrd1) is not RRD or type(rrd2) is not RRD:
            print_text(settings.local.incorrect_input, THEMES_MESSAGE.ERROR)
            return

        data = self.csv_concat(rrd1, rrd2)
        print_text(data.to_string)
        print_text(settings.local.start_correlation)
        corrmat = data.corr()

        directory = "correlation_table/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        try:
            path_save = directory + "correlation_" + rrd1.name_host + "_" + rrd2.name_host
            corrmat.to_excel(path_save + ".xlsx")
        except Exception as e:
            print_text(e, THEMES_MESSAGE.ERROR)
        # with open(path_save + ".txt", "w") as the_file:
        #     the_file.write(corrmat.to)

        print_text(corrmat)

        f, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(corrmat, cmap="YlGnBu", square=True, annot=True, ax=ax)

        directory = "graphs/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(directory + "correlation_matrix_" + rrd1.name_host + "_" + rrd2.name_host + ".png")
        plt.show()
        plt.clf()
        plt.close()

        plt.subplots(figsize=(12, 8))
        sns.pairplot(data)
        plt.savefig(directory + "correlation_hists_" + rrd1.name_host + "_" + rrd2.name_host + ".png")

        plt.show()
        print_text(settings.local.complete_correlation, THEMES_MESSAGE.SUCCESS)


rrd_factory = RRDFactory()
rrd_factory.parse_all_rrd()
