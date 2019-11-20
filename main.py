"""
Main module of the Find Pairs game.
"""
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from models import GAME as game
from models import Username
from board import Board
from controller import Controller
from score_board import ScoreBoard
from ws import close
#from models import CLK

class FindPairs(App, GridLayout):
    """FindPairs
    """
    def __init__(self, **kwargs):
        kwargs["cols"] = 1
        print("FindPairs cols=", kwargs["cols"])
        super(FindPairs, self).__init__(**kwargs)
        self.score_board = ScoreBoard(200, self.login_button_handler, self.join_game_handler,\
            size_hint=(1, None), height="30sp")
        self.add_widget(self.score_board)
        self.board = Board(self.card_click_handler, self.cb_after_faceup_delay)
        self.add_widget(self.board.get_widget())
        self.controller = Controller(self.board, self.score_board)

        self.size_text_frame = GridLayout(cols=1, size_hint=(1, None), height="30sp")
        self.size_text = Label(text="Number of pairs")
        self.size_text_frame.add_widget(self.size_text)
        self.size_text_frame.bind(size=lambda *args: self.set_bg(self.size_text_frame))

        self.levels = []
        self.current_level = 0
        self.num_of_pairs_frame = GridLayout(cols=7, size_hint=(1, None), height="50sp")
        self.num_of_pairs_frame.bind(size=lambda *args: self.set_bg(self.num_of_pairs_frame))
        for num_pairs in [5, 10, 15, 20, 25, 30]:
            self.levels.append(LevelButton(num_pairs, self.handle_click_num_pairs))
            self.num_of_pairs_frame.add_widget(self.levels[-1])

        self.num_of_pairs_frame.add_widget(Button(text="Next Level",\
            on_press=self.handle_click_next_level))

        self.add_widget(self.size_text_frame)
        self.add_widget(self.num_of_pairs_frame)

    def build(self):
        return self

    def set_bg(self, frame, *args):
        """set_bg
        """
        with frame.canvas.before:
            Color(rgb=get_color_from_hex("#9ACD32")) #777700"))
            Rectangle(pos=frame.pos, size=frame.size)

    def handle_click_num_pairs(self, num_pairs, change_level=False):
        """Handler for a number of pairs button
        """
        self.controller.send({"type":"create-game", "num_pairs":num_pairs,\
            "change-level":change_level})

    def handle_click_next_level(self, *args):
        """Handler for the next level button
        """
        self.current_level += 1
        num_pairs = int(self.levels[self.current_level].text)
        self.handle_click_num_pairs(num_pairs, change_level=True)

    def card_click_handler(self, card):
        """card_click_handler
        """
        self.controller.send({"type":"card-click", "message":{"gameId":game["id"],\
            "userName":Username.val, "cardI": card.card_ind}})

    def cb_after_faceup_delay(self):
        """cb_after_faceup_delay
        """
        if game["state"]["gameover"]:
            if len(game["state"]["players"]) > 1:
                self.score_board.render_gameover(game["state"])
        else:
            self.score_board.render_turn(game["state"]["turn"])

    def login_button_handler(self, username, *args):
        """login_button_handler
        """
        self.controller.send({"type":"my-name", "message":username})

    def join_game_handler(self, game):
        """join_game_handler
        """
        self.controller.send({"type":"join-game", "message":game})

    def on_stop(self):
        """on_stop
        """
        close()
        #CLK.stop()


class LevelButton(Button):
    """LevelButton
    """
    def __init__(self, num_pairs, click_handler):
        super().__init__(text=str(num_pairs), on_press=lambda *args: click_handler(num_pairs))

if __name__ == '__main__':
    print(Window.size)
    FindPairs().run()
