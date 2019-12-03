from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

from tst_card import run as run_tst_card
from tst_board import run as run_tst_board

class TstApp(App, GridLayout):
    def __init__(self, **kwargs):
        super(TstApp, self).__init__(**kwargs)
        self.layout = GridLayout(cols=1, padding=100)
        self.add_widget(self.layout)
        self.tsts = []
        self.tsts.append(self.tst_card)
        self.tsts.append(self.tst_board)
        Clock.schedule_once(lambda dt: self.tst_scheduler(), 3)

    def build(self):
        return self

    def tst_scheduler(self):
        print("tst_scheduler")
        tst = self.tsts.pop(0)
        tst()

    def tst_finished(self):
        if self.tsts:
            Clock.schedule_once(lambda dt: self.tst_scheduler(), 3)
        else:
            print("tst_finished", "all done")
            self.stop()

    def tst_card(self):
        print("tst_card")
        self.layout.clear_widgets()
        run_tst_card(self.layout, self.tst_finished)

    def tst_board(self):
        print("tst_board")
        self.layout.clear_widgets()
        run_tst_board(self.layout, self.tst_finished)

def test_app():
    TstApp(cols=1).run()

if __name__ == "__main__":
    test_app()
