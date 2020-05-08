import os

import rrdtool
import re
from datetime import datetime
from pandas.io import json

from src.classes.OpenFile import open_file, FORMATS_OPEN
from src.classes.PrintText import print_text, THEMES_MESSAGE
from src.modules import RRDFactory

list_functions = ["info", "fetch", "graph", "xport", "dump", "change_params", "exit"]


class RRD:
    def __init__(self, name_host, description, path_to_database, file_name, start_point, end_point, type_command, height, width):
        self.name_host = name_host
        self.description = description
        self.path_to_database = path_to_database
        self.file_name = file_name
        self.file = self.path_to_database + "/" + self.file_name
        self.start_point = start_point
        self.end_point = end_point
        self.first = rrdtool.first(self.file)
        self.last = rrdtool.last(self.file)
        # self.lastupdate = rrdtool.lastupdate(self.file)
        self.type_command = type_command
        self.height = height
        self.width = width
        self.list_ds = self.parse_ds

    @property
    def parse_ds(self):
        list_ds = []

        try:
            info = rrdtool.info(self.file)
            for ds in re.findall(r"ds\[\w+]\.index", r"" + json.dumps(info)):
                res = re.sub(r"\w+\[", "", ds)
                res = re.sub(r"].index", "", res)
                list_ds.append(res)
        except Exception as e:
            print_text("Error:", THEMES_MESSAGE.ERROR)
            print_text(e, THEMES_MESSAGE.ERROR)
        return list_ds

    def display_menu(self):
        print("\n---- RRD. Menu ----")

        for item in self.list_menu:
            print(str(item.id) + str(". " + item.name))

        ans = input("Selection: ")

        if ans == str(len(self.list_menu)):
            return

        try:
            for item in self.list_menu:
                if item.id == ans:
                    item.function()
                    break
        except Exception as e:
            print("Error: ")
            print_text(e, THEMES_MESSAGE.ERROR)

        self.display_menu()

    def set_menu(self):
        self.list_menu.append(RRDFactory.MenuItem("Display params", self.display_params))
        self.list_menu.append(RRDFactory.MenuItem("Show graph", self.all_on_one_graph))
        self.list_menu.append(RRDFactory.MenuItem("Show all graph", self.all_graph))
        self.list_menu.append(RRDFactory.MenuItem("Parse to csv rrd-file", self.csv_export))
        self.list_menu.append(RRDFactory.MenuItem("Exit", ""))

        RRDFactory.set_id(self.list_menu)

    def display_params(self):
        print("\n---- RRD. params ----")

        for key, value in self.__dict__.items():
            print(key, " =", value)

    def display_info(self):
        print("\n---- RRD. Info ----")
        print(self.file)
        print(rrdtool.info(self.file))

    def graph(self, column):
        directory = "graphs/" + column

        path_to_save = directory + ".png"

        print("\nStart generate " + path_to_save + "...")

        try:
            rrdtool.graph(path_to_save,
                          "--imgformat", "PNG",
                          "--height", str(self.height),
                          "--width", str(self.width),
                          "--start", self.start_point,
                          "--end", self.end_point,
                          "--vertical-label=Up times/day",
                          "DEF:" + column + "=" + self.file + ":" + column + ":AVERAGE:step=1",
                          "CDEF:cdef=" + column + ",1,*",
                          "LINE2:cdef#FF6666:\"" + column + "\"",
                          "AREA:cdef#FF6666")
        except Exception:
            print("error")
        print("Finish!")

    def all_on_one_graph(self):
        path_to_save = "graphs/" + self.path_to_database

        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

        for column in self.list_ds:
            path_to_save += "_" + column

        path_to_save += ".png"

        print("\nStart generate " + path_to_save + "...")

        colors = ["#ff0000", "#007fff", "#26d100", "#e0e000"]
        count_color = 0

        rrd_args = [path_to_save,
                    "--imgformat", "PNG",
                    "--height", str(self.height),
                    "--width", str(self.width),
                    "--start", self.start_point,
                    "--end", self.end_point,
                    "--vertical-label=Up times/day"]

        for column in self.list_ds:
            rrd_args.append("DEF:" + column + "=" + self.file + ":" + column + ":AVERAGE:step=60")
            rrd_args.append("CDEF:cdef_" + column + "=" + column + ",1,*")
            rrd_args.append("LINE2:cdef_" + column + colors[count_color] + ":\"" + column + "\"")
            rrd_args.append("GPRINT:cdef_" + column + ":AVERAGE:\"AVERAGE\:%8.0lf\"")
            rrd_args.append("GPRINT:cdef_" + column + ":MAX:\"Max\:%8.0lf \\n\"")

            count_color += 1

        try:
            rrdtool.graph(rrd_args)
            print("Finish!")
        except Exception as e:
            print_text(e, THEMES_MESSAGE.ERROR)

    def all_graph(self):
        print(self.file)
        for column in self.list_ds:
            self.graph(column)

        print("\nFinish generate graph's!")

    def dump(self):
        return rrdtool.dump(self.file)

    def xport(self):
        rrd_args = ["--start", self.start_point,
                    "--end", self.end_point]

        for column in self.list_ds:
            rrd_args.append("DEF:" + column + "=" + self.file + ":" + column + ":AVERAGE")
            rrd_args.append("CDEF:cdef_" + column + "=" + column + ",1,*")
            rrd_args.append("XPORT:" + column + ":\"" + column + "\"")

        res_xport = rrdtool.xport(rrd_args)
        return res_xport

    def parse_timestamp(self, timestamp):
        return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def csv_export(self):
        res_xport = self.xport()
        directory = "csv_rrd/"
        path_csv = directory + self.name_host + "." + self.file_name + ".csv"

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open_file(path_csv, FORMATS_OPEN.WRITE) as the_file:
            list_columns = res_xport["meta"]["legend"]
            data = res_xport["data"]
            start = res_xport["meta"]["start"]
            step = res_xport["meta"]["step"]
            end = res_xport["meta"]["end"]

            i = 0
            the_file.write("timestamp,")
            the_file.write("time,")
            for column in list_columns:
                i += 1
                line = re.sub("\"", "", column)
                if i < len(list_columns):
                    line += ","

                the_file.write(line)

            the_file.write("\n")

            timestamp = start - step
            for row in data:
                i = 0
                timestamp += step
                line = str(timestamp) + ", "
                line += self.parse_timestamp(timestamp) + ", "
                the_file.write(line)
                for column in row:
                    i += 1

                    line = str((0 if column is None else column))
                    if i < len(list_columns):
                        line += ","
                    the_file.write(line)
                the_file.write("\n")

        return path_csv
