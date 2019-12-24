class Menu:
    def __init__(self, description, list_rrd):
        self.description = description
        self.rrd = rrd

    def display_info(self):
        print(self.description)

    def select_rrd(self):
        print("Select menu item:")

        i = 1
        for item in self.rrd.list_select_rrd:
            print(i, ") ", item)
            i += 1

        return input()
