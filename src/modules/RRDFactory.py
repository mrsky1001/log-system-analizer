import csv
import subprocess
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import rrdtool
import re
import warnings

from Main import settings
from src.classes.OpenFile import open_file

warnings.filterwarnings("ignore")

import os
from tabulate import tabulate

from src.modules.RRD import RRD
from src.modules.MenuFactory import MenuItem, set_id


class RRDFactory:
    def __init__(self, ):
        self.list_all_params = []
        self.list_rrd = []
        self.list_item_menu = []
        self.selected_rrd = RRD

    def parse_all_rrd(self):
        print("Parsing ngraph for get a description of params ...")
        directory = settings.path_to_exports + "csv/"

        subprocess.Popen(["perl", "parsengraph.pl", settings.path_to_description_of_params], stdout=subprocess.PIPE)
        descriptions = []

        with open_file(directory + "table_description_params_rrd.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                descriptions.append(row)

        print("start load rrds...")
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
                                  height=settings.height,
                                  width=settings.width)

                        list_ds = rrd.parse_ds
                        self.list_rrd.append(rrd)

                        for ds in list_ds:
                            self.list_all_params.append(str(rrd.name_host) + "." + str(ds))
                    except Exception as e:
                        print(e)
        if len(self.list_rrd) > 0:
            self.selected_rrd = self.list_rrd[0]
        print("Complete load.")

        return self.list_all_params

    def select_rrd_file(self):
        print("\n---- RRD FACTORY. Select rrd-file ----")

        types_input = [MenuItem("Search on name of param", self.search_rrd_on_param),
                       MenuItem("Search on name of file", self.search_rrd_on_filename)]

        set_id(types_input)

        for item in types_input:
            print(str(item.id) + str(". " + item.name))

        ans = input("Select type input:")

        try:
            for item in types_input:
                if item.id == ans:
                    self.display_list_rrd_files()
                    item.function()
                    break
        except Exception as e:
            print("Error: ")
            print(e)

    def search_rrd_on_param(self):
        print("\n---- RRD FACTORY. Search rrd on param ----")
        param = input("Input name of rrd: ")

        for rrd in self.list_rrd:
            if rrd.name_host == param:
                self.selected_rrd = rrd
                print("Search successful.")
                break

        if type(self.selected_rrd) is not RRD:
            print("Not found!")
        else:
            self.selected_rrd.display_settings()

        return self.selected_rrd

    def search_rrd_on_filename(self):
        print("\n---- RRD FACTORY. Search rrd on filename ----")
        param = input("Input filename of rrd: ")

        self.selected_rrd = self.search_rrd(param)

        if type(self.selected_rrd) is not RRD:
            print("Not found!")
        else:
            self.selected_rrd.display_settings()

        return self.selected_rrd

    def display_list_rrd_files(self):
        list_headers = ["name", "description", "file"]
        list_rows = []

        for rrd in sorted(self.list_rrd, key=lambda rrd: rrd.name_host):
            list_rows.append(
                [rrd.name_host, rrd.description,
                 re.findall("[^/]*\w+$", rrd.path_to_database)[0] + '/' + rrd.file_name])

        table = tabulate(list_rows, headers=list_headers, tablefmt='orgtbl')
        with open("src/resources/csv/table_description_params_rrd.txt", 'w') as the_file:
            the_file.write(table)
        print(table)

    def export_params_all_rdd_files_to_csv(self):

        for rrd in self.list_rrd:
            print(rrd.csv_export())

    def csv_concat(self, rrd1, rrd2):

        f1 = rrd1.csv_export()
        f2 = rrd2.csv_export()

        df1 = pd.read_csv(f1)
        df2 = pd.read_csv(f2)

        keys1 = list(df1)
        keys2 = list(df2)

        print(keys1)
        print(keys2)

        for idx, row in df2.iterrows():
            data = df1[df1['timestamp'] == row['timestamp']]
            if data.empty:
                print("Warning! Data merge on time stamp is empty.")
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

        df1.to_csv(directory + "merge_" + rrd1.name_host + "_" + rrd2.name_host + ".csv", index=False, encoding='utf-8',
                   quotechar="", quoting=csv.QUOTE_NONE)
        return df1

    def search_rrd(self, file_name):
        for rrd in self.list_rrd:
            if rrd.file_name == file_name or re.sub(".rrd", "", rrd.file_name) == file_name:
                print("Search successful.")
                return rrd

    def correlation_rrd_files(self):

        self.display_list_rrd_files()

        rrd1 = self.search_rrd(input("Input file name of rrd 1: "))
        rrd2 = self.search_rrd(input("Input file name of rrd 2: "))

        if type(rrd1) is not RRD or type(rrd2) is not RRD:
            print("Incorrect input!")
            return

        data = self.csv_concat(rrd1, rrd2)
        print(data.to_string)
        print("Start correlation ...")
        corrmat = data.corr()

        directory = "correlation_table/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        try:
            path_save = directory + "correlation_" + rrd1.name_host + "_" + rrd2.name_host
            corrmat.to_excel(path_save + ".xlsx")
        except Exception as e:
            print(e)
        # with open(path_save + ".txt", 'w') as the_file:
        #     the_file.write(corrmat.to)

        print(corrmat)

        f, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(corrmat, cmap="YlGnBu", square=True, annot=True, ax=ax)

        directory = "graphs/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(directory + 'correlation_matrix_' + rrd1.name_host + "_" + rrd2.name_host + '.png')
        plt.show()
        plt.clf()
        plt.close()

        plt.subplots(figsize=(12, 8))
        sns.pairplot(data)
        plt.savefig(directory + 'correlation_hists_' + rrd1.name_host + "_" + rrd2.name_host + '.png')

        plt.show()
        print("Complete correlation.")
