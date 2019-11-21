"""score_board.py\n
Contains\n
countdown clock\n
display for the scored points\n
"""
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout  import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.utils import get_color_from_hex
from ui_clock import Clock
from models import set_num_players, set_num_pairs, set_id, set_level_time, set_in_device
#, set_timer_conf

class GameButton(Button):
    """GameButton
    """
    def __init__(self, game, join_game_handler, **kwargs):
        kwargs["on_press"] = self.handle_click
        kwargs["text"] = str(game[1]) + ", pairs=" + str(game[2])
        super(GameButton, self).__init__(**kwargs)
        self.game = game
        self.join_game_handler = join_game_handler

    def handle_click(self, *args):
        """handle_click
        """
        print("GameButton.handle_click", self.game[0])
        self.join_game_handler(self.game)

class MenuButton(ButtonBehavior, Image):
    """MenuButton
    """
    def __init__(self, login_button_handler, join_game_handler, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.bind(on_press=self.open_modal)
        self.modal = ModalView(size_hint=(1, .6))
        self.modal_body = GridLayout(rows=2, size_hint_x=0.8, padding=[0, 20, 0, 0], spacing=5)
        self.modal.add_widget(self.modal_body)
        self.username_widget = TextInput(multiline=False, size_hint=(1, None), height="30sp")
        self.modal_body.add_widget(self.username_widget)
        self.login_button_handler = login_button_handler
        self.join_game_handler = join_game_handler
        anchor = AnchorLayout(anchor_y='top')
        self.login_button = Button(text="login", size_hint=(None, None), width="50sp",\
            height="30sp", on_press=self.onclick_login_button)
        anchor.add_widget(self.login_button)
        self.modal_body.add_widget(anchor)
        self.online_list = Label()
        self.games_list = GridLayout(cols=5)

    def open_modal(self, *args):
        """open_modal
        """
        self.modal.open()

    def close_modal(self):
        """close_modal
        """
        self.modal.dismiss()

    def onclick_login_button(self, *args):
        """onclick_login_button
        """
        username = self.username_widget.text
        if username:
            self.login_button_handler(username)

    def init_gaming(self, username):
        """init_gaming
        param username <str>
        """
        self.modal_body.clear_widgets()
        self.modal_body.rows = None
        self.modal_body.cols = 1
        self.modal_body.add_widget(Label(text="user name: " + username))
        self.modal_body.add_widget(self.online_list)
        self.modal_body.add_widget(self.games_list)

    def handle_online_list(self, online_list):
        """handle_online_list
        param online_list <list>
        """
        self.online_list.text = "Online: " + str(online_list)

    def handle_games_list(self, games_list):
        """handle_games_list
        param games_list = [[gameId, numPlayers, numPairs],[], ... ]
        """
        print("score_board.py:MenuButton.handle_games_list")
        self.games_list.clear_widgets()
        self.games_list.add_widget(Label(text="Games:", size_hint=(None, None), height="20sp",\
            width="50sp"))
        for game in games_list:
            self.games_list.add_widget(GameButton(game, self.join_game_handler,\
                size_hint=(None, None), height="20sp", width="80sp"))

    def wait_for_gaming(self, game):
        """wait_for_gaming
        param game = [gameId, numPlayers, numPairs]
        """
        set_id(game[0])
        set_num_players(game[1])
        set_num_pairs(game[2])
        set_level_time(200)
        set_in_device(False)
        self.modal_body.clear_widgets()
        self.modal_body.add_widget(Label(text="Waiting for the game to start."))
        self.modal_body.add_widget(Label(text=game[0] + ', ' + str(game[1]) + ', ' + str(game[2])))

    def render_gameover(self, game_state):
        """render_gameover
        """
        self.modal_body.clear_widgets()
        self.modal_body.add_widget(Label(text="Game over"))
        players_scores_sorted = list(zip(game_state["players"], game_state["scores"]))
        players_scores_sorted.sort(key=sort_by_num_player, reverse=True)
        players_ranked = []
        for i, item in enumerate(players_scores_sorted):
            player = {"name":item[0], "score":item[1]}
            player["rank"] = i + 1
            if i > 0:
                if player["score"] == players_ranked[-1]["score"]:
                    player["rank"] = players_ranked[-1]["rank"]
            players_ranked.append(player)
        game_result_table = GridLayout(cols=3)
        for player in players_ranked:
            game_result_table.add_widget(Label(text=str(player["rank"])))
            game_result_table.add_widget(Label(text=player["name"]))
            game_result_table.add_widget(Label(text=str(player["score"])))
        self.modal_body.add_widget(game_result_table)
        self.modal_body.add_widget(Button(text="Replay"))

def sort_by_num_player(item):
    """Sort helper for players_scores_sorted.sort in order to get the list sorted according the
    player's score
    """
    return item[1] # item = (username, score)

class PlayerLabel(Label):
    """PlayerLabel
    """
    def __init__(self, active, **kwargs):
        super(PlayerLabel, self).__init__(**kwargs)
        self.active = active

    def on_size(self, *args):
        """on_size
        """
        if self.active:
            color = "#ffff00"
        else:
            color = "#ffffb0"

        with self.canvas.before:
            Color(rgb=get_color_from_hex(color))
            RoundedRectangle(pos=self.pos, size=self.size)
        self.color = get_color_from_hex("#333300")

    def activate(self):
        """activate
        """
        self.active = True
        with self.canvas.before:
            Color(rgb=get_color_from_hex("#ffff00"))
            RoundedRectangle(pos=self.pos, size=self.size)

    def inactivate(self):
        """inactivate
        """
        self.active = False
        with self.canvas.before:
            Color(rgb=get_color_from_hex("#ffffb0"))
            RoundedRectangle(pos=self.pos, size=self.size)

class ScoreBoard(GridLayout):
    """ScoreBoard
    """
    __MENU_BUTTON_WIDTH = "30sp"

    def __init__(self, clock_countdown_start, login_button_handler, join_game_handler, **kwargs):
        kwargs["cols"] = 2
        super(ScoreBoard, self).__init__(**kwargs)
        self.col1 = GridLayout(cols=2, padding=[5, 0, 0, 0])
        self.menu = MenuButton(login_button_handler, join_game_handler, source=\
            "images/font-awesome_4-7-0_" + "bars" + "_48_0_333300_none.png",\
            size_hint_x=None, width=self.__MENU_BUTTON_WIDTH)
        self.col1.add_widget(self.menu)
        self.clock_countdown_start = clock_countdown_start
        self.ui_clock = Clock(self.clock_countdown_start, bold=True, font_size="20sp",\
            color=get_color_from_hex("#333300"))
        self.col1.add_widget(self.ui_clock)
        self.add_widget(self.col1)

        self.col2 = GridLayout(cols=2, padding=[5, 0, 0, 0])
        self.kv_score = Label(font_size="20sp", bold=True, text="0",\
            color=get_color_from_hex("#333300"))
        self.col2.add_widget(self.kv_score)
        self.add_widget(self.col2)

        self.players = []
        self.scores = []

    def on_size(self, *args):
        """on_size
        """
        try:
            with self.canvas.before:
                Color(rgb=get_color_from_hex("#ffffb0"))
                Rectangle(pos=self.pos, size=self.size)
        except AttributeError:
            pass

    def set_score(self, scores, in_device):
        """set_score
        param scores
            [<int>, <int>, ... numPlayers ]
        param in_device
            <boolean>
        """
        if in_device:
            self.kv_score.text = str(scores[0])
        else:
            for i, score in enumerate(scores):
                self.scores[i].text = str(score)

    def get_score(self):
        """
        get_score
        """
        return int(self.kv_score.text)

    def render_game_state(self, game_state):
        """
        render_game_state
        """
        self.set_score(game_state["scores"], game_state["in-device"])
        # self.render_turn(game_state["turn"])

    def init_clock(self, level_time):
        """init_clock
        """
        self.col1.remove_widget(self.ui_clock)
        self.ui_clock.stopped = True
        self.ui_clock = Clock(level_time, bold=True, font_size="20sp",\
            color=get_color_from_hex("#333300")) # Clock(level_time)
        self.col1.add_widget(self.ui_clock) #, index=1)

    def start_clock(self):
        """start_clock
        """
        self.ui_clock.init_time_counter()
        self.ui_clock.tick()

    def stop_clock(self):
        """
        stop_clock
        """
        self.ui_clock.stop()

    def get_clock_val(self):
        """get_clock_val\n
        return <int>\n
        """
        return self.ui_clock.get_current_value()

    def set_clock_timeout_trigger(self, callback):
        """set_clock_timeout_trigger
        param callback
            Called when the countdown clock has reached its minimum val.
        """
        self.ui_clock.set_timeout_trigger(callback)

    def render_my_name_ack(self, result_code, username):
        """render_my_name_ack
        param result_code <int>
            0: OK
            1: USER_DOES_NOT_EXIST
        param username <str>
        """
        if result_code == 0:
            self.menu.init_gaming(username)

    def render_online_list(self, online_list):
        """render_online_list
        param online_list <list>
        """
        self.menu.handle_online_list(online_list)

    def render_games_list(self, games_list):
        """render_games_list
        """
        self.menu.handle_games_list(games_list)

    def render_join_game_ack(self, result_code, game):
        """render_join_game_ack
        param result_code <int>
            0 = OK, otherwise error
        param game
            See MenuButton.wait_for_gaming, [gameId, numPlayers, numPairs]
        """
        if result_code == 0:
            self.menu.wait_for_gaming(game)

    def render_start_game(self, game_state, clock_timeout_callback):
        """render_start_game
        """
        self.menu.close_modal()
        if game_state["in-device"]:
            self.init_clock(game_state["game-max-len"])
            self.set_clock_timeout_trigger(clock_timeout_callback)
            self.start_clock()
        else:
            self.col1.clear_widgets()
            self.col2.clear_widgets()
            self.col1.cols = 3
            self.col2.cols = 3
            if len(game_state["players"]) == 2:
                player1 = PlayerLabel(game_state["turn"] == 1, text=game_state["players"][0])
                score1 = Label(text=str(game_state["scores"][0]),\
                    color=get_color_from_hex("#333300"))
                self.col1.add_widget(self.menu)
                self.col1.add_widget(player1)
                self.col1.add_widget(score1)

                player2 = PlayerLabel(game_state["turn"] == 2, text=game_state["players"][1])
                score2 = Label(text=str(game_state["scores"][1]),\
                    color=get_color_from_hex("#333300"))
                self.col2.add_widget(score2)
                self.col2.add_widget(player2)
                self.col2.add_widget(Image(source="images/transparent_48.png", size_hint_x=None,\
                    width=self.__MENU_BUTTON_WIDTH)) # this makes evenly sized cols

                self.players.append(player1)
                self.players.append(player2)
                self.scores.append(score1)
                self.scores.append(score2)

    def render_turn(self, turn):
        """render_turn
        """
        if len(self.players) > 1:
            if turn == 1:
                print("turn == 1", "activate", self.players[0].text,
                      "inactivate", self.players[1].text)
                self.players[0].activate()
                self.players[1].inactivate()
            else:
                print("turn != 1", "activate", self.players[1].text, 
                      "inactivate", self.players[0].text)
                self.players[0].inactivate()
                self.players[1].activate()

    def render_gameover(self, game_state):
        """render_gameover
        """
        self.menu.render_gameover(game_state)
        self.menu.open_modal()

if __name__ == "__main__":
    from kivy.app import runTouchApp, stopTouchApp
    from kivy.clock import Clock as KivyClock

    # menu.render_gameover
    players_scores = list(zip(["Veera", "Helmi"], [2, 8]))
    print("before sort", players_scores)
    players_scores.sort(key=sort_by_num_player, reverse=True)
    print(players_scores)

    players_scores = list(zip(["Tiku", "Taku"], [4, 1]))
    print("before sort", players_scores)
    players_scores.sort(key=sort_by_num_player, reverse=True)
    print(players_scores)

    players_scores = list(zip(["Veera", "Helmi", "Tiku", "Taku"], [2, 8, 4, 1]))
    print("before sort", players_scores)
    players_scores.sort(key=sort_by_num_player, reverse=True)
    print(players_scores)

    def login_button_handler(*args):
        """login_button_handler
        """
        score_board.render_my_name_ack(0, score_board.menu.modal_body.children[-1].text)

    def test_join_game_handler(game):
        """join_game_handler
        """
        print("assert", "test_join_game_handler", game)
        assert game[0] == "game2"
        assert game[1] == 3
        assert game[2] == 45
        score_board.render_join_game_ack(0, ["a-game-id", 2, 15])

    def handle_tstbtn_render_online_list(*args):
        """handle_tstbtn_render_online_list
        """
        score_board.render_online_list(["Tapu", "Patu", "Veera"])

    def handle_tstbtn_render_games_list(*args):
        """handle_tstbtn_render_games_list
        """
        score_board.render_games_list([["game1", 2, 15], ["game2", 3, 45]])

    def handle_tstbtn_render_start_game(*args):
        """handle_tstbtn_render_start_game
        """
        score_board.render_start_game({"in-device":False, "players":["Iines", "Aku"], "turn":1, "scores":[0, 0]}, None)

    def handle_tstbtn_render_turn1(*args):
        """handle_tstbtn_render_turn1
        """
        score_board.render_turn(1)

    def handle_tstbtn_render_turn2(*args):
        """handle_tstbtn_render_turn2
        """
        score_board.render_turn(2)

    def get_scores():
        """get_scores
        """
        scores = [0, 0]

        while True:
            if scores[0] + 3 > scores[1]:
                scores[1] += 1
            else:
                scores[0] += 1
            yield scores
    GET_SCORES = get_scores()

    def handle_tstbtn_render_game_state(*args):
        """handle_tstbtn_render_game_state
        """
        score_board.render_game_state({"scores":next(GET_SCORES), "in-device":False})

    test_view = GridLayout(cols=1)
    test_buttons = GridLayout(padding=5, cols=6, size_hint=(1, None), height="30sp")
    
    tstbtn_render_online_list = Button(text="online-list", on_press=handle_tstbtn_render_online_list)
    tstbtn_render_games_list = Button(text="game-list", on_press=handle_tstbtn_render_games_list)
    tstbtn_render_start_game = Button(text="start-game", on_press=handle_tstbtn_render_start_game)
    tstbtn_render_turn1 = Button(text="turn 1", on_press=handle_tstbtn_render_turn1)
    tstbtn_render_turn2 = Button(text="turn 2", on_press=handle_tstbtn_render_turn2)
    tstbtn_render_game_state = Button(text="game-state", on_press=handle_tstbtn_render_game_state)

    test_buttons.add_widget(tstbtn_render_online_list)
    test_buttons.add_widget(tstbtn_render_games_list)
    test_buttons.add_widget(tstbtn_render_start_game)
    test_buttons.add_widget(tstbtn_render_turn1)
    test_buttons.add_widget(tstbtn_render_turn2)
    test_buttons.add_widget(tstbtn_render_game_state)

    score_board = ScoreBoard(200, login_button_handler, test_join_game_handler,\
                             size_hint=(1, None), height="30sp")
    test_view.add_widget(test_buttons)
    test_view.add_widget(score_board)

    # user presses the menu button
    score_board.menu.dispatch("on_press")

    # user types the username and presses the login button
    score_board.menu.username_widget.text = "Hessu"
    score_board.menu.login_button.dispatch("on_press")
    print("assert", score_board.menu.modal_body.children[-1].text)
    assert score_board.menu.modal_body.children[-1].text == "user name: Hessu"

    # server sends online-list
    score_board.render_online_list(["Tatu", "Patu", "Veera"])
    print("assert", score_board.menu.online_list.text)
    assert score_board.menu.online_list.text == "Online: ['Tatu', 'Patu', 'Veera']"

    # server sends game-list
    score_board.render_games_list([["game1", 2, 15], ["game2", 3, 45]])
    print("assert", "len(score_board.menu.games_list)", "3")
    assert len(score_board.menu.games_list.children) == 3 # Label.text=Games: + btns for the games
    print("assert", "game2-btn", score_board.menu.games_list.children[0].text)
    assert score_board.menu.games_list.children[0].text == "3, pairs=45"
    print("assert", "game1-btn", score_board.menu.games_list.children[1].text)
    assert score_board.menu.games_list.children[1].text == "2, pairs=15"

    # user joins to a game by pressing the associated button
    score_board.menu.games_list.children[0].dispatch("on_press")
    print("assert", "waiting for the game")
    assert score_board.menu.modal_body.children[1].text == "Waiting for the game to start."
    print("assert", "waiting for the game, game-fields",
          score_board.menu.modal_body.children[0].text)
    assert score_board.menu.modal_body.children[0].text == "a-game-id, 2, 15"

    def game_tests(dt):
        """game_tests
        """
        # server sends start-game
        score_board.render_start_game({"in-device":False, "players":["Iines", "Aku"], "turn":1,\
            "scores":[0, 0]}, None)
        print("assert", "start-game")
        assert score_board.col1.children[1].text == "Iines"
        assert score_board.col2.children[1].text == "Aku"
        assert score_board.col1.children[1].active
        assert not score_board.col2.children[1].active

        def change_turn(dt):
            """change_turn
            """
            #server changes turn (via game-state)
            score_board.render_turn(2)
            print("assert", "change turn")
            assert not score_board.col1.children[1].active
            assert score_board.col2.children[1].active

            # server set score (via game-state)
            print("assert", "update score")
            score_board.render_game_state({"scores":[2, 7], "in-device":False})
            KivyClock.schedule_once(lambda dt: stopTouchApp(), 5)

        KivyClock.schedule_once(change_turn, 2)

    KivyClock.schedule_once(game_tests, 3)

    runTouchApp(widget=test_view)
