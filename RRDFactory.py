import csv
import subprocess

import rrdtool
import tempfile
import re, xmljson
import os
from tabulate import tabulate
from pandas.io import json

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
        p1 = subprocess.Popen(["perl", "parsengraph.pl"], stdout=subprocess.PIPE)
        p1.stdout.close()
        p1.terminate()

        descriptions = []

        with open("csv/table_description_params_rrd.csv", "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                descriptions.append(row)

        for root, dirs, files in os.walk(self.folder):
            for filename in files:
                if filename.endswith(".rrd"):
                    try:
                        rrdtool.info(root + "/" + filename)

                        name = re.findall("[^/]*\w+$", root)[0]
                        description = ""

                        for item in descriptions:
                            if item[0] == name:
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

        return self.list_all_params

    def set_menu(self):
        self.list_menu.append(MenuItem("Display params", self.display_params))
        self.list_menu.append(MenuItem("Display list rrd-files", self.display_list_rrd_files))
        self.list_menu.append(MenuItem("Load RRD-file", str("")))

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

        for rrd in self.list_rrd:
            list_rows.append([rrd.name_host, rrd.description, rrd.file_name])

        print(list_rows)
        table = tabulate(list_rows, headers=list_headers, tablefmt='orgtbl')
        print(table)

    def csv_all_rrd(self):
        print("\n---- RRD FACTORY. Generate CSV from all rrd ----")
        path_csv = "csv/params_from_all_rrd.csv"
        #
        # with open(path_csv, 'w') as the_file:
        #     for root, dirs, files in os.walk(self.folder):
        #         for filename in files:
        #             rrd = RRD(folder=root,
        #                       file_name=filename,
        #                       start_point=self.start_point,
        #                       end_point=self.end_point,
        #                       type_command=self.type_command,
        #                       height=self.height,
        #                       width=self.width)
        #
        #             res_xport = rrd.xport()
        #
        #             list_columns = res_xport['meta']['legend']
        #             data = res_xport['data']
        #
        #             i = 0
        #             for column in list_columns:
        #                 i += 1
        #                 line = re.sub("\"", "", column)
        #                 if i < len(list_columns):
        #                     line += ","
        #
        #                 the_file.write(line)
        #
        #             the_file.write("\n")
        #
        #             for row in data:
        #                 i = 0
        #                 for column in row:
        #                     i += 1
        #
        #                     line = str((0 if column is None else column))
        #                     if i < len(list_columns):
        #                         line += ","
        #                     the_file.write(line)
        #                 the_file.write("\n")
