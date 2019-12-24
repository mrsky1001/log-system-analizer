import csv
import subprocess
import openpyxl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import rrdtool
import re, xmljson
import os
from tabulate import tabulate

from RRD import RRD


class MenuItem:
    def __init__(self, name, function):
        self.id = 0
        self.name = name
        self.function = function


class RRDFactory:
    def __init__(self, folder, start_point, end_point, type_command, height, width):
        self.list_menu = []
        self.start_point = start_point
        self.end_point = end_point
        self.type_command = type_command
        self.height = height
        self.width = width
        self.folder = folder
        self.list_all_params = []
        self.list_rrd = []
        self.parse_all_rrd()

        self.set_menu()

    def parse_all_rrd(self):
        print("\n---- RRD FACTORY. Load params from rrd-files ----")
        print("start parse ngraph ...")
        directory = "csv/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        p1 = subprocess.Popen(["perl", "parsengraph.pl"], stdout=subprocess.PIPE)
        p1.stdout.close()
        p1.terminate()
        print("Complete parse.")

        descriptions = []

        with open(directory + "table_description_params_rrd.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                descriptions.append(row)

        print("start load rrds...")
        for root, dirs, files in os.walk(self.folder):
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
                                  folder=root,
                                  file_name=filename,
                                  start_point=self.start_point,
                                  end_point=self.end_point,
                                  type_command=self.type_command,
                                  height=self.height,
                                  width=self.width)

                        list_ds = rrd.parse_ds
                        self.list_rrd.append(rrd)

                        for ds in list_ds:
                            self.list_all_params.append(str(rrd.name_host) + "." + str(ds))
                    except Exception as e:
                        print(e)
        print("Complete load.")

        return self.list_all_params

    def set_menu(self):
        self.list_menu.append(MenuItem("Display params", self.display_params))
        self.list_menu.append(MenuItem("Display list rrd-files", self.display_list_rrd_files))
        self.list_menu.append(MenuItem("Load RRD-file", str("")))
        self.list_menu.append(MenuItem("Parase to csv all rrd-files", self.csv_all_rrd))
        self.list_menu.append(MenuItem("Correlation selected rrd", self.correlation_matrix))

        i = 0
        for item in self.list_menu:
            i += 1
            item.id = str(i)

    def display_params(self):
        print("\n---- RRD FACTORY. Params ----")
        print("start_point = " + str(self.start_point))
        print("end_point = " + str(self.end_point))
        print("type_command = " + str(self.type_command))
        print("height = " + str(self.height))
        print("width = " + str(self.width))
        print("folder = " + str(self.folder))

    def display_menu(self):
        print("\n---- RRD FACTORY. Menu ----")

        for item in self.list_menu:
            print(str(item.id) + str(". " + item.name))

        ans = input("Selection: ")

        try:
            for item in self.list_menu:
                if item.id == ans:
                    item.function()
                    break
        except Exception as e:
            print("Error: ")
            print(e)

        self.display_menu()

    def display_list_rrd_files(self):
        print("\n---- RRD FACTORY. List rrd-files ----")
        list_headers = ["name", "description", "file"]
        list_rows = []

        for rrd in sorted(self.list_rrd, key=lambda rrd: rrd.name_host):
            list_rows.append(
                [rrd.name_host, rrd.description, re.findall("[^/]*\w+$", rrd.folder)[0] + '/' + rrd.file_name])

        table = tabulate(list_rows, headers=list_headers, tablefmt='orgtbl')
        print(table)

    def csv_all_rrd(self):
        print("\n---- RRD FACTORY. Generate CSV from all rrd ----")

        for rrd in self.list_rrd:
            print(rrd.csv_export())

    def csv_concat(self, rrd1, rrd2):
        print("\n---- RRD FACTORY. Generate CSV concatenation rrd ----")

        f1 = rrd1.csv_export()
        f2 = rrd2.csv_export()

        df1 = pd.read_csv(f1)
        df2 = pd.read_csv(f2)

        keys1 = list(df1)
        keys2 = list(df2)

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

    def correlation_matrix(self):
        print("\n---- RRD FACTORY. Correlation  ----")

        self.display_list_rrd_files()

        name_rrd1 = input("Input name rrd 1: ")
        name_rrd2 = input("Input name rrd 2: ")

        rrd1 = ""
        rrd2 = ""

        for rrd in self.list_rrd:
            if rrd.name_host == name_rrd1:
                rrd1 = rrd
            if rrd.name_host == name_rrd2:
                rrd2 = rrd

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
        sns.heatmap(corrmat, cmap=sns.diverging_palette(220, 10, as_cmap=True), square=True, ax=ax)

        directory = "graphs/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        plt.savefig(directory + 'correlation_matrix.png')
        plt.show()
        print("Complete correlation.")
