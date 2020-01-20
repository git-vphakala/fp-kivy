"""
test_app executes run().
Manually run in the project main directory.
"""
import sys, os
from kivy.app import runTouchApp, stopTouchApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.clock import Clock as KivyClock

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from score_board import ScoreBoard, sort_by_num_player

stop_app = False
finished_callback = None
score_board = None

def check_stop_app():
    if stop_app:
        stopTouchApp()
    if finished_callback:
        finished_callback()

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

def run(layout, finished_cb=None):
    global finished_callback
    global score_board

    finished_callback = finished_cb
    layout.padding = [0, 0, 0, 0]

    # menu.render_gameover
    players_scores = list(zip(["Veera", "Helmi"], [2, 8]))
    print("assert", "players_scores", players_scores)
    players_scores.sort(key=sort_by_num_player, reverse=True)
    assert players_scores[0][0] == "Helmi"
    assert players_scores[0][1] == 8

    players_scores = list(zip(["Tiku", "Taku"], [4, 1]))
    print("assert", "players_scores", players_scores)
    players_scores.sort(key=sort_by_num_player, reverse=True)
    assert players_scores[0][0] == "Tiku"
    assert players_scores[0][1] == 4

    players_scores = list(zip(["Veera", "Helmi", "Tiku", "Taku"], [2, 8, 4, 1]))
    print("assert", "players_scores", players_scores)
    players_scores.sort(key=sort_by_num_player, reverse=True)
    assert players_scores[0][0] == "Helmi"
    assert players_scores[0][1] == 8

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
    layout.add_widget(test_buttons)
    layout.add_widget(score_board)

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
            KivyClock.schedule_once(lambda dt: check_stop_app(), 5)

        KivyClock.schedule_once(change_turn, 3)

    KivyClock.schedule_once(game_tests, 3)

if __name__ == "__main__":
    stop_app = True
    LAYOUT = GridLayout(cols=1)
    run(LAYOUT)
    runTouchApp(widget=LAYOUT)
