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
                        if message_type in (MESSAGE_TYPE_START_GAME, MESSAGE_TYPE_GAME_STATE):
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
            # self.__scoreboard.set_clock_timeout_trigger(self.on_game_timeout)
            # self.__scoreboard.init_clock(game_state["game-max-len"])
            # self.__scoreboard.start_clock()
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

        # Contoller._recv {"type": "start-game", "message": "{\"gameId\": \"df87b6e3-f698-4f77-aed0-a98261e061fb\",
        # \"board\": [\"1b\", \"4b\", \"5b\", \"3a\", \"4a\", \"2b\", \"3b\", \"2a\", \"1a\", \"5a\"], 
        # \"cards\": [{\"facedown\": true, \"removed\": false, \"faceValue\": \"1\", \"position\": 0}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"4\", \"position\": 1}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"5\", \"position\": 2}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"3\", \"position\": 3}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"4\", \"position\": 4}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"2\", \"position\": 5}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"3\", \"position\": 6}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"2\", \"position\": 7}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"1\", \"position\": 8}, 
        # {\"facedown\": true, \"removed\": false, \"faceValue\": \"5\", \"position\": 9}], 
        # \"turn\": 1, \"faceUp\": [], \"removed\": 0, \"scores\": [0, 0], \"gameover\": false, 
        # \"players\": [\"Veera\", \"Helmi\"]}"}
        # handle_message, type=start-game

    def handle_expired_timer(self, expired_timer):
        """handle_expired_timer
        """
        with self.__lock:
            if expired_timer[0] == game_logic.TIMERTYPE_GAME_MAX_LEN:
                print("expired: type={}, id={}".format(expired_timer[0], expired_timer[1]))
                self.__scoreboard.stop_clock()
                game_logic.set_state(game, "gameover", True)
