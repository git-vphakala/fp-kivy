"""
test_app executes run().
Manually run in the project main directory.
"""
import sys, os
import json
from kivy.app import runTouchApp, stopTouchApp
from kivy.uix.gridlayout import GridLayout

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from controller import Controller
from models import set_in_device, set_state
from models import MESSAGE_TYPE_START_GAME, MESSAGE_TYPE_GAME_STATE, MESSAGE_TYPE_MY_NAME_ACK,\
    MESSAGE_TYPE_ONLINE_LIST, MESSAGE_TYPE_GAMES_LIST, MESSAGE_TYPE_JOIN_GAME_ACK
import game_logic
import ws
from ws import store

stop_app = False
finished_callback = None

def check_stop_app():
    if stop_app:
        stopTouchApp()
    if finished_callback:
        finished_callback()

test_case_id = 0
recv_tcids = []

class Board():
    """test-stub
    """
    def render_game_state(self, game_state):
        print("assert", "Board.render_game_state", game_state)
        assert game_state == {'in-device': False, 'board': ['1a', '1b', '2a', '3a'],\
            'gameover': False}

    def set_board(self, board):
        print("assert", "Board.set_board", board)
        assert board == ['1a', '1b', '2a', '3a']

class ScoreBoard():
    """test-stub
    """
    def set_clock_timeout_trigger(self, game_timeout):
        pass
    def render_my_name_ack(self, rc, message):
        """test-stub
        """
        print("assert", "my-name-ack", rc, message)
        assert rc == 0 and message == "module-test"
    def stop_clock(self):
        """test-stub
        """
        print("stub", "ScoreBoard.stop_clock")

    def render_join_game_ack(self, rc, message):
        """test-stub
        """
        print("assert", "join-gme-ack", rc, message)
        assert rc == 0 and message == "recv-tc-2"

    def render_game_state(self, game_state):
        print("stub", "ScoreBoard.render_game_state", game_state)
        assert game_state == {'in-device': False, 'board': ['1a', '1b', '2a', '3a'],\
            'gameover': False}

    def render_start_game(self, game_state, on_game_timeout):
        print("assert", "ScoreBoard.render_start_game", game_state)
        assert game_state == {"in-device":False, "board":["1a", "1b", "2a", "3a"]}

    def render_online_list(self, online_list):
        print("assert", "ScoreBoard.render_online_list", online_list, type(online_list))
        assert online_list == ["user-id-x", "user-id-y", "user-id-z"]

    def render_games_list(self, games_list):
        print("assert", "ScoreBoard.render_games_list", games_list, type(games_list))
        assert games_list == [["game-id-x", 2, 10], ["game-id-y", 3, 15], ["game-id-z", 4, 20]]

def conn():
    """overwrite ws.conn
    """
    print("tst_controller", "conn-stub")
    return True

def send(msg):
    """overwrite ws.send
    """
    if test_case_id == 1:
        print("assert", "Controller.send", "my-name")
        assert msg == '{"type": "my-name", "message": "module-test"}'
        return True
    elif test_case_id == 2:
        print("assert", "Controller.send", "join-game")
        assert msg == '{"type": "join-game", "message": "module-test"}'
        return True
    elif test_case_id == 3:
        print("assert", "Controller.send", "card-click", msg)
        assert msg == '{"type": "card-click", "message": {"gameId": "module-test-3", "userName": "module-test-user-3", "cardI": 3}}'
        return True
    return False

def recv():
    """overwrite ws.recv()\n
    Create a case for the desired test case id (match with run_tests which
    appends it to the @global recv_tcids.
    A case is executed when Controller calls recv again (calls in 0.1 sec intervals).

    @return True  message has been received
    @return False no message
    """
    try:
        tcid = recv_tcids.pop(0)
    except IndexError:
        return False
    else:
        if tcid == 1:
            store["message"] = '{"type":"my-name-ack","rc":0,"message":"module-test"}'
            return True
        if tcid == 2:
            store["message"] = '{"type":"join-game-ack","rc":0,"message":"recv-tc-2"}'
            return True
        if tcid == 4:
            store["message"] = json.dumps({"type":MESSAGE_TYPE_START_GAME,\
                    "message":json.dumps({"in-device":False, "board":["1a", "1b", "2a", "3a"]})})
            return True
        if tcid == 5:
            store["message"] = json.dumps({"type":MESSAGE_TYPE_GAME_STATE,\
                "message":json.dumps({"in-device":False, "board":["1a", "1b", "2a", "3a"],\
                    "gameover":False})})
            return True
        if tcid == 6:
            store["message"] = json.dumps({"type":MESSAGE_TYPE_ONLINE_LIST,\
                "message":json.dumps(["user-id-x", "user-id-y", "user-id-z"])})
            return True
        if tcid == 7:
            store["message"] = json.dumps({"type":MESSAGE_TYPE_GAMES_LIST,\
                "message":json.dumps([["game-id-x", 2, 10], ["game-id-y", 3, 15],\
                    ["game-id-z", 4, 20]])})
            return True
        if tcid == 9999:
            check_stop_app()
            return True
        raise NotImplementedError("recv: Unexpected text case id:" + str(tcid))

def game_logic_play(game, message):
    """overwrite game_logic.play
    """
    print("game_logic_play", game, message)
    if "module-test-dummy" in game["state"]:
        game["state"]["module-test-dummy"] += 1
    else:
        game["state"]["module-test-dummy"] = 1

game_logic.play = game_logic_play
ws.conn = conn
ws.send = send
ws.recv = recv

def run(layout, finished_cb=None):
    global finished_callback
    global score_board
    global test_case_id
    global recv_tcids

    finished_callback = finished_cb

    test_controller = Controller(Board(), ScoreBoard())

    test_case_id = 1
    test_controller.send({"type":"my-name", "message":"module-test"})
    recv_tcids.append(test_case_id)

    test_case_id = 2
    test_controller.send({"type":"join-game", "message":"module-test"})
    recv_tcids.append(test_case_id)

    test_case_id = 3
    set_state({"faceup-delay":False, "gameover":True})
    set_in_device(False)
    test_controller.send({"type":"card-click", "message":{"gameId":"module-test-3",\
        "userName":"module-test-user-3", "cardI": 3}})

    # receive start-game
    test_case_id = 4
    recv_tcids.append(test_case_id)

    # receive game-state
    test_case_id = 5
    recv_tcids.append(test_case_id)

    # receive online-list
    test_case_id = 6
    recv_tcids.append(test_case_id)

    # receive game-list
    test_case_id = 7
    recv_tcids.append(test_case_id)

    # end test
    test_case_id = 9999
    recv_tcids.append(test_case_id)

if __name__ == "__main__":
    stop_app = True
    LAYOUT = GridLayout(cols=1)
    run(LAYOUT)
    runTouchApp(widget=LAYOUT)
