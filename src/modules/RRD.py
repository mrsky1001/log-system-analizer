import os

import rrdtool
import re
from datetime import datetime
from pandas.io import json

from src.classes.OpenFile import open_file, FORMATS_OPEN, check_exist_file
from src.classes.PrintText import print_text, THEMES_MESSAGE
from src.modules import RRDFactory
from src.modules.MenuFactory import MenuFactory, init_menu_selected_rrd
from src.modules.Settings import settings

list_functions = ["info", "fetch", "graph", "xport", "dump", "change_params", "exit"]


class RRD:
    def __init__(self, name_host, description, path_to_database, file_name, start_point, end_point, type_command,
                 height, width):
        self.name_host = name_host
        self.description = description
        self.path_to_database = path_to_database
        self.file_name = file_name
        self.file = self.path_to_database + "/" + self.file_name
        self.start_point = start_point
        self.end_point = end_point
        self.first = rrdtool.first(self.file)
        self.last = rrdtool.last(self.file)
        self.lastupdate = rrdtool.lastupdate(self.file)
        self.type_command = type_command
        self.height = height
        self.width = width
        self.list_ds = self.parse_ds
        self.list_menu = []

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
            print_text(settings.local.error, THEMES_MESSAGE.ERROR)
            print_text(e, THEMES_MESSAGE.ERROR)
        return list_ds

    def display_menu(self, rrd_factory):
        menu_rrd = MenuFactory(settings.local.menu_rrd, settings,
                               lambda: init_menu_selected_rrd(settings, self, rrd_factory))
        menu_rrd.display_menu_repeat([self.name_host, self.file_name])

    def display_params(self):
        print_text(settings.local.params_rrd, THEMES_MESSAGE.INFO)

        for key, value in self.__dict__.items():
            print_text([key, " =", value])

    def display_info(self):
        print_text(settings.local.info_rrd, THEMES_MESSAGE.INFO)
        print_text(self.file)
        print_text(rrdtool.info(self.file))

    def generate_graph(self, column, directory):
        filename = column + ".png"
        path_to_save = check_exist_file(filename, directory)

        print_text(settings.local.start_generate + path_to_save + "...")

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
        except Exception as e:
            print_text(settings.local.error, THEMES_MESSAGE.ERROR)
            print_text(e, THEMES_MESSAGE.ERROR)
        print_text(settings.local.complete_graph, THEMES_MESSAGE.SUCCESS)

    def generate_graph_with_all_params(self):
        directory = settings.path_to_graphs + self.name_host + '/'
        filename = ''

        for column in self.list_ds:
            filename = "_" + column

        filename += ".png"
        path_to_save = check_exist_file(filename, directory)

        print_text(settings.local.start_generate + path_to_save + "...")

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
            print_text(settings.local.complete_graph, THEMES_MESSAGE.SUCCESS)
        except Exception as e:
            print_text(e, THEMES_MESSAGE.ERROR)

    def generate_graphs_on_all_params(self):
        directory = settings.path_to_graphs + self.name_host + '/'

        for column in self.list_ds:
            self.generate_graph(column, directory)

        print_text(settings.local.complete_graphs, THEMES_MESSAGE.SUCCESS)

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
        directory = settings.path_to_csv + self.name_host + '/'
        filename = self.file_name + ".csv"
        path_csv = directory + filename
        res_xport = self.xport()

        with open_file(filename, directory, FORMATS_OPEN.WRITE) as the_file:
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

        print_text(path_csv)
        print_text(settings.local.export_csv, THEMES_MESSAGE.SUCCESS)

        return path_csv
