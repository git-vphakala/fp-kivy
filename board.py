"""board.py
"""
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from card import Card
from models import TWO_CARDS_FACEUP_DELAY

class Filler(GridLayout):
    """Filler
    """
    def __init__(self, **kwargs):
        super(Filler, self).__init__(**kwargs)

    def on_size(self, *args):
        """on_size
        """
        self.canvas.clear()
        with self.canvas:
            Color(rgb=get_color_from_hex("#9ACD32")) # "#777700"))
            Rectangle(pos=self.pos, size=self.size)

class Board(GridLayout):
    """Board
    """
    def __init__(self, card_click_handler, cb_after_faceup_delay, **kwargs):
        kwargs["cols"] = 1
        super(Board, self).__init__(**kwargs)
        # self.icons = icons
        self.card_click_handler = card_click_handler
        self.cb_after_faceup_delay = cb_after_faceup_delay
        self.board = GridLayout(cols=5, size_hint_y=1, spacing=5, padding=5)
        self.board.bind(size=self.board_on_size)
        self.__filler = Filler(cols=1, size_hint_y=1)
        self.add_widget(self.board)
        self.add_widget(self.__filler)
        print("Board.__init__")

    def on_size(self, *args):
        print("Board.on_size", len(self.children))

    def board_on_size(self, *args):
        print("Board.board_on_size", len(self.board.children))
        self.board.canvas.before.clear()
        with self.board.canvas.before:
            Color(rgb=get_color_from_hex("#9ACD32")) # "#777700"))
            Rectangle(pos=self.board.pos, size=self.board.size)

    def set_board(self, board):
        """
        board = [ "xi", "yi", "zi", ... ], where x,y,z=[1..numPairs] and i=[a,b]
        """
        print("Board.set_board", board)
        face_value_map = {1:"android", 2:"google", 3:"github", 4:"fort-awesome", 5:"youtube-play",
                          6:"twitter", 7:"snapchat", 8:"whatsapp", 9:"linux", 10:"apple",
                          11:"firefox", 12:"font-awesome", 13:"chrome", 14:"html5", 15:"amazon",
                          16:"skype", 17:"stack-overflow", 18:"wikipedia-w", 19:"superpowers",
                          20:"windows", 21:"dropbox", 22:"drupal", 23:"edge", 24:"empire",
                          25:"envira", 26:"facebook", 27:"flickr", 28:"gitlab", 29:"glide",
                          30:"gg", 31:"git", 32:"forumbee", 33:"get-pocket"}
        self.clear_widgets()
        self.board.clear_widgets()

        if len(board) > 30:
            self.board.cols = 6
        else:
            self.board.cols = 5

        if len(board) > 20:
            filler_size_hint_y = 0
        elif len(board) > 10:
            filler_size_hint_y = 0.3
        else:
            filler_size_hint_y = 1
        self.add_widget(self.board)
        for i, card in enumerate(board):
            card_name = face_value_map[int(card[:-1])]
            #icon_facedown, icon_faceup = self.icons.get_card_icons_by_name(card_name)
            self.board.add_widget(Card(card_name, self.card_click_handler, i), index=i)
        self.__filler = Filler(cols=1, size_hint_y=filler_size_hint_y)
        self.add_widget(self.__filler)

    def render_game_state(self, game_state):
        """render_game_state
        param game_state
            {}, the fields of the state are set in game_logic-module
        """
        removed = 1
        pair_found = False

        for gl_card in game_state["faceUp"]:
            card_ind = gl_card["position"]
            ui_card = self.board.children[card_ind]
            ui_card.turn_up()
            if removed == 1:
                removed = gl_card["removed"]

        two_cards_faceup = False
        if len(game_state["faceUp"]) == 2:
            two_cards_faceup = True
            if removed == 1:
                pair_found = True

        if two_cards_faceup:
            self.__game_state = game_state
            game_state["faceup-delay"] = True
            if pair_found:
                Clock.schedule_once(self.remove_from_board, TWO_CARDS_FACEUP_DELAY)
            else: # not a pair
                Clock.schedule_once(self.to_facedown, TWO_CARDS_FACEUP_DELAY)

    def to_facedown(self, dt):
        """Turn faceUp cards to facedown
        """
        for gl_card in self.__game_state["faceUp"]:
            card_ind = gl_card["position"]
            ui_card = self.board.children[card_ind]
            ui_card.turn_down()
        self.__game_state["faceup-delay"] = False
        self.cb_after_faceup_delay()

    def remove_from_board(self, dt):
        """Remove a pair from the board
        """
        for gl_card in self.__game_state["faceUp"]:
            print("Board.remove_from_board", gl_card["position"])
            card_ind = gl_card["position"]
            ui_card = self.board.children[card_ind]
            ui_card.remove_from_board()
        self.__game_state["faceup-delay"] = False
        self.cb_after_faceup_delay()

    def get_widget(self):
        """get_widget
        """
        return self

if __name__ == "__main__":
    from kivy.app import runTouchApp, stopTouchApp

    def get_game_state():
        """ game_state generator for testing
        """
        game_state_list = [
            # 1. player turned the first card
            {"faceUp":[{"facedown": False, "removed": False, "faceValue": "1b", "position": 0}]},

            # 2. player turned the second card (pair found)
            {"faceUp":[{"facedown": False, "removed": True, "faceValue": "1b", "position": 0},
                       {"facedown": False, "removed": True, "faceValue": "1a", "position": 1}]},

            # 3. player turned the first card
            {"faceUp":[{"facedown": False, "removed": False, "faceValue": "2b", "position": 2}]},

            # 4. player turned the second card (pair not found)
            {"faceUp":[{"facedown": False, "removed": False, "faceValue": "2a", "position": 2},
                       {"facedown": False, "removed": False, "faceValue": "3a", "position": 3}]},
        ]
        gsl_ind = 0
        while gsl_ind < len(game_state_list):
            yield game_state_list[gsl_ind]
            gsl_ind += 1

    GAME_STATE_GENERATOR = get_game_state()

    def assert_render_game_state():
        """assert_render_game_state
        """
        test_case_id = 1 # match with game_state_list
        while True:
            print("assert_render_game_state", test_case_id)
            if test_case_id == 1:
                test_case_id += 1
                if not test_board.board.children[0].face_down:
                    yield True
                else:
                    print("assert_render_game_state", "failed", test_case_id)
                    yield False
            elif test_case_id == 2:
                test_case_id += 1
                if not test_board.board.children[0].face_down and\
                   not test_board.board.children[1].face_down and\
                   not test_board.board.children[0].removed and\
                   not test_board.board.children[1].removed:
                    yield True
                else:
                    print("assert_render_game_state", "failed", test_case_id)
                    yield False
            elif test_case_id == 3:
                test_case_id += 1
                if not test_board.board.children[2].face_down:
                    yield True
                else:
                    print("assert_render_game_state", "failed", test_case_id)
                    yield False
            elif test_case_id == 4:
                test_case_id += 1
                if not test_board.board.children[2].face_down and\
                   not test_board.board.children[3].face_down and\
                   not test_board.board.children[2].removed and\
                   not test_board.board.children[3].removed:
                    yield True
                else:
                    print("assert_render_game_state", "failed", test_case_id)
                    yield False
            else:
                print("assert_render_game_state", "unexpected test case id", test_case_id)
                yield False

    RENDER_GAME_STATE_GENERATOR = assert_render_game_state()

    def test_card_click_handler(card):
        pass

    def test_render_game_state(dt):
        try:
            game_state = next(GAME_STATE_GENERATOR)
        except StopIteration:
            Clock.schedule_once(lambda dt: stopTouchApp(), 3)
        else:
            test_board.render_game_state(game_state)
            assert next(RENDER_GAME_STATE_GENERATOR)
            Clock.schedule_once(test_render_game_state, 5)

    def assert_cb_after_faceup_delay():
        """assert_cb_after_faceup_delay
        """
        test_case_id = 2 # match with game_state_list
        while True:
            print("assert_cb_after_faceup_delay", test_case_id)
            if test_case_id == 2:
                if test_board.board.children[0].removed and\
                   test_board.board.children[1].removed:
                    yield True
                else:
                    yield False
                test_case_id = 4 # next test case id
            elif test_case_id == 4:
                if not test_board.board.children[2].removed and\
                   not test_board.board.children[3].removed and\
                   test_board.board.children[2].face_down and\
                   test_board.board.children[3].face_down:
                    yield True
                else:
                    yield False
            else:
                yield False

    CB_AFTER_FACEUP_DELAY_GENERATOR = assert_cb_after_faceup_delay()

    def test_cb_after_faceup_delay():
        """test_cb_after_faceup_delay
        """
        assert next(CB_AFTER_FACEUP_DELAY_GENERATOR)

    test_board = Board(test_card_click_handler, test_cb_after_faceup_delay)
    layout = GridLayout(cols=1, padding=100)
    layout.add_widget(test_board)

    test_board.set_board(["1a", "1b", "2a", "3a"])
    Clock.schedule_once(test_render_game_state, 2)

    runTouchApp(layout)
