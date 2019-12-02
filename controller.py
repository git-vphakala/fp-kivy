"""controller.py
"""
import json
from threading import Lock
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import DictProperty, BooleanProperty
from models import GAME as game
from models import MESSAGE_TYPE_START_GAME, MESSAGE_TYPE_GAME_STATE, MESSAGE_TYPE_MY_NAME_ACK,\
    MESSAGE_TYPE_ONLINE_LIST, MESSAGE_TYPE_GAMES_LIST, MESSAGE_TYPE_JOIN_GAME_ACK
from models import set_num_players, set_num_pairs, set_id, set_level_time, set_state, set_username #, set_timer_conf
import game_logic
from ws import conn, send, recv, store

class Controller(Widget):
    """Controller
    """
    reply_message = DictProperty({})

    def __init__(self, board, score_board, **kwargs):
        super(Controller, self).__init__(**kwargs)
        self.__board = board
        self.__scoreboard = score_board
        self.__lock = Lock()
        # set_timer_conf("expired-timer-callback", self.handle_expired_timer)
        self.counter = 0
        self.game_timeout = BooleanProperty(defaultvalue=False)
        self.__scoreboard.set_clock_timeout_trigger(self.game_timeout)
        Clock.schedule_interval(self._recv, 0.1)

    def send(self, message):
        """
        Send messages to the game logic. Sender can be the view or the timer manager.\n
        Before the message is handled the lock is acquired.
        """
        with self.__lock:
            if message["type"] == "card-click":
                if game["state"]["faceup-delay"]:
                    return
                if not game["in-device"]:
                    msg_str = json.dumps(message)
                    ret_val = send(msg_str)
                    if not ret_val:
                        print("Controller.send ws.send failed", json.dumps(message))
                    else:
                        print("Controller.send", "card-click", "to server", msg_str)
                    return

                prev_state = json.dumps(game["state"])
                game_logic.play(game, message["message"])
                if json.dumps(game["state"]) != prev_state:
                    # Counter is needed so that kivy notices that the dictproperty has been changed
                    self.counter += 1
                    self.reply_message = {
                        "type": MESSAGE_TYPE_GAME_STATE,
                        "message": game["state"],
                        "counter": self.counter
                    }

            elif message["type"] == "create-game":
                set_id()
                set_num_players(1)
                set_num_pairs(message["num_pairs"])
                set_level_time(message["num_pairs"] * 2 * 5)
                game_logic.init(game, message["change-level"])
                print("Controller.send", game["state"]["board"])
                self.reply_message = {
                    "type": MESSAGE_TYPE_START_GAME,
                    "message": game["state"]
                }

            elif message["type"] == "join-game":
                print("Controller.send", "join-game")
                ret_val = send(json.dumps(message))
                if not ret_val:
                    print("Controller.send ws.send failed", json.dumps(message))

            elif message["type"] == "my-name":
                if "ws" not in store:
                    connected = conn()
                    if not connected:
                        print("Controller.send: ws.conn failed")
                        return
                ret_val = send(json.dumps(message))
                if not ret_val:
                    print("Controller.send ws.send failed", json.dumps(message))

    def _recv(self, *args):
        """_recv
        """
        # print("_recv")
        while recv():
            if "message" in store:
                #print("_recv:", store["message"])
                try:
                    ws_message = json.loads(store["message"])
                except json.JSONDecodeError:
                    print("Controller._recv", "JSONDecodeError", store["message"])
                else:
                    message_type = ws_message["type"]
                    if message_type is None:
                        print("Controller._recv", "no type in message", store["message"])
                    else:
                        if message_type in (MESSAGE_TYPE_START_GAME, MESSAGE_TYPE_GAME_STATE,\
                            MESSAGE_TYPE_ONLINE_LIST, MESSAGE_TYPE_GAMES_LIST):
                            try:
                                ws_message["message"] = json.loads(ws_message["message"])
                            except json.JSONDecodeError:
                                print("Controller._recv", "ws_message, JSONDecodeError", ws_message["message"])
                                return
                        print("Contoller._recv", store["message"])
                        self.reply_message = ws_message

    def on_reply_message(self, *args):
        """on_reply_message
        """
        self.handle_message()

    def on_game_timeout(self, *args):
        """on_game_timeout
        """
        print("Controller.on_game_timeout")
        self.__scoreboard.stop_clock()
        game_logic.set_state(game, "gameover", True)

    def handle_message(self):
        """Handle messages from the game_logic to the view
        """
        print("handle_message, type=" + self.reply_message["type"])

        if self.reply_message["type"] == MESSAGE_TYPE_START_GAME:
            game_state = self.reply_message["message"]
            if not game_state["in-device"]:
                set_state(game_state)
            self.__board.set_board(game_state["board"])
            self.__scoreboard.render_start_game(game_state, self.on_game_timeout)
            print("Controller.handle_message", MESSAGE_TYPE_START_GAME, game_state["board"])

        elif self.reply_message["type"] == MESSAGE_TYPE_GAME_STATE:
            game_state = self.reply_message["message"]
            if not game_state["in-device"]:
                set_state(game_state)
            if game_state["gameover"]:
                self.__scoreboard.stop_clock()
            self.__board.render_game_state(game_state)
            self.__scoreboard.render_game_state(game_state)

        elif self.reply_message["type"] == MESSAGE_TYPE_MY_NAME_ACK:
            if "rc" in self.reply_message:
                if self.reply_message["rc"] == 0:
                    if "message" in self.reply_message:
                        set_username(self.reply_message["message"])
                        self.__scoreboard.render_my_name_ack(self.reply_message["rc"],\
                            self.reply_message["message"])
                    else:
                        print("Controller.handle_message", "no message", MESSAGE_TYPE_MY_NAME_ACK)
                else:
                    self.__scoreboard.render_my_name_ack(self.reply_message["rc"], None)
            else:
                print("Controller.handle_message", "no rc", MESSAGE_TYPE_MY_NAME_ACK)

        elif self.reply_message["type"] == MESSAGE_TYPE_ONLINE_LIST:
            if "message" in self.reply_message:
                self.__scoreboard.render_online_list(self.reply_message["message"])
            else:
                print("Controller.handle_message", "no message", MESSAGE_TYPE_ONLINE_LIST)

        elif self.reply_message["type"] == MESSAGE_TYPE_GAMES_LIST:
            if "message" in self.reply_message:
                self.__scoreboard.render_games_list(self.reply_message["message"])
            else:
                print("Controller.handle_message", "no message", MESSAGE_TYPE_GAMES_LIST)

        elif self.reply_message["type"] == MESSAGE_TYPE_JOIN_GAME_ACK:
            if "rc" in self.reply_message:
                if self.reply_message["rc"] == 0:
                    if "message" in self.reply_message:
                        self.__scoreboard.render_join_game_ack(self.reply_message["rc"],\
                            self.reply_message["message"])
                    else:
                        print("Controller.handle_message", "no message", MESSAGE_TYPE_JOIN_GAME_ACK)
                else:
                    self.__scoreboard.render_join_game_ack(self.reply_message["rc"], None)
            else:
                print("Controller.handle_message", "no rc", MESSAGE_TYPE_JOIN_GAME_ACK)

    def handle_expired_timer(self, expired_timer):
        """handle_expired_timer
        """
        with self.__lock:
            if expired_timer[0] == game_logic.TIMERTYPE_GAME_MAX_LEN:
                print("expired: type={}, id={}".format(expired_timer[0], expired_timer[1]))
                self.__scoreboard.stop_clock()
                game_logic.set_state(game, "gameover", True)

if __name__ == "__main__":
    from kivy.app import runTouchApp, stopTouchApp
    from models import set_in_device

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

    def run_tests(dt):
        """run_tests
        """
        global test_case_id
        global recv_tcids
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

    Clock.schedule_once(run_tests, 3)
    runTouchApp()
