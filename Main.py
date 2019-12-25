from RRDFactory import RRDFactory

rrd_factory = RRDFactory(folder="rrd/",
                         start_point="1419000000",
                         end_point="now",
                         type_command="AVERAGE",
                         height=800,
                         width=1024)

rrd_factory.display_menu()
