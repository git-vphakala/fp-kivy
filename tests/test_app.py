import os
import sys
import re
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

# from tst_card import run as run_tst_card
# from tst_board import run as run_tst_board
# from tst_score_board import run as run_tst_score_board
# from tst_controller import run as run_tst_controller

class TstApp(App, GridLayout):
    def __init__(self, **kwargs):
        super(TstApp, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, padding=100)
        self.add_widget(self.layout)
        self.tsts = self.get_tst_modules(".") # []
        # self.tsts.append(run_tst_card)
        # self.tsts.append(run_tst_board)
        # self.tsts.append(run_tst_score_board)
        # self.tsts.append(run_tst_controller)
        Clock.schedule_once(lambda dt: self.tst_scheduler(), 3)

    def build(self):
        return self

    def get_tst_modules(self, path):
        tst_files = []
        sys.path.insert(1, os.path.join(sys.path[0], 'tests'))
        sys.path.insert(1, os.path.join(sys.path[0], '..'))

        for root, dirs, files in os.walk(path):
            tst_dir = re.search(r"tests$", r"{}".format(root))
            if tst_dir:
                for file in files:
                    if 'tst_' in file:
                        tst_files.append(file[:-3]) # os.path.join(root, file))
                        print("get_tst_modules", tst_files[-1])

        return list(map(__import__, tst_files))


    def tst_scheduler(self):
        tst = self.tsts.pop(0)
        print("tst_scheduler", tst.__name__)
        self.layout.clear_widgets()
        tst.run(self.layout, self.tst_finished)

    def tst_finished(self):
        if self.tsts:
            Clock.schedule_once(lambda dt: self.tst_scheduler(), 3)
        else:
            print("tst_finished", "all done")
            self.stop()

def test_app():
    TstApp(cols=1).run()

if __name__ == "__main__":
    test_app()
