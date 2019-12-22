import rrdtool
import tempfile
import re, xmljson

from pandas.io import json

list_functions = ["info", "fetch", "graph", "xport", "dump", "change_params", "exit"]


class RRD:
    def __init__(self, folder, file_name, start_point, end_point, type_command, height, width):
        self.folder = folder
        self.file_name = file_name
        self.file = self.folder + self.file_name
        self.start_point = start_point
        self.end_point = end_point
        self.type_command = type_command
        self.height = height
        self.width = width
        self.list_ds = self.parse_ds()

    def parse_ds(self):
        info = rrdtool.info(self.file)
        list_ds = []

        for ds in re.findall(r'ds\[\w+]\.index', r"" + json.dumps(info)):
            res = re.sub(r'\w+\[', '', ds)
            res = re.sub(r'].index', '', res)
            list_ds.append(res)

        return list_ds

    def display_attr(self):
        print("\n---- RRD params ----")

        for key, value in self.__dict__.items():
            print(key, " =", value)

    def display_info(self):
        print("\n---- RRD Info ----")
        print(self.file)
        print(rrdtool.info(self.file))

    def graph(self, column):
        path_to_save = "graphs/" + column + ".png"
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
        print("\n---- RRD. All one graph ----")
        path_to_save = "graphs/"

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
            print(e)

    def all_graph(self):
        print("\n---- RRD Graph's ----")
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

    def csv_export(self):
        res_xport = self.xport()
        path_csv = "csv/" + self.file_name + ".csv"

        with open(path_csv, 'w') as the_file:
            list_columns = res_xport['meta']['legend']
            data = res_xport['data']

            i = 0
            for column in list_columns:
                i += 1
                line = re.sub("\"", "", column)
                if i < len(list_columns):
                    line += ","

                the_file.write(line)

            the_file.write("\n")

            for row in data:
                i = 0
                for column in row:
                    i += 1

                    line = str((0 if column is None else column))
                    if i < len(list_columns):
                        line += ","
                    the_file.write(line)
                the_file.write("\n")

        return path_csv
