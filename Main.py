from CorrelationMatrix import CorrelationMatrix
# from CorrelationGraph import CorrelationGraph
from Menu import Menu
from RRD import RRD
from RRDFactory import RRDFactory

# rrd = RRD(folder="/home/nk16/rrd/oraci2",
#           file_name="1feacfb555aec399cc81c9f74bacd3c1.rrd",
#           start_point="1419000000",
#           end_point="1420800000",
#           type_command="AVERAGE",
#           height=800,
#           width=1024
#           )

rrd_factory = RRDFactory(folder="rrd/",
                         start_point="1419000000",
                         end_point="now",
                         type_command="AVERAGE",
                         height=800,
                         width=1024)

rrd_factory.display_menu()
# corr_matrix = CorrelationMatrix(rrd=rrd)
# corr_graph = CorrelationGraph(rrd=rrd)
# menu = Menu(description="RRD tools.", rrd=rrd)

# rrd.display_attr()
# corr_matrix.display_matrix()
# corr_graph.display_graph()

# rrd.xport()
#
# print(x['meta'])

# f, ax = plt.subplots(figsize=(9, 8))
# sns.heatmap(corrmat, ax=ax, cmap="YlGnBu", linewidths=0.0001)
# plt.show()

# print("end plot")
# print(data)
# o = xmltodict.parse()
# print(json.dumps(o))

# menu.display_info()
# rrd.display_info()
# rrd.all_graph()
# rrd.all_on_one_graph()

