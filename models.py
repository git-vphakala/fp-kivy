"""
Models for Find Pairs game
"""
import uuid
#import time
#from timer_mgr import TimerManager, TR_OK
#from clock import Clock

TWO_CARDS_FACEUP_DELAY = 1

MESSAGE_TYPE_MY_NAME_ACK = "my-name-ack"
MESSAGE_TYPE_ONLINE_LIST = "online-list"
MESSAGE_TYPE_GAMES_LIST = "game-list"
MESSAGE_TYPE_START_GAME = "start-game"
MESSAGE_TYPE_GAME_STATE = "game-state"
MESSAGE_TYPE_JOIN_GAME_ACK = "join-game-ack"

#TIMER_CONF = {}
"""
def set_timer_conf(key, val):
    set_timer_conf

    TIMER_CONF[key] = val

def poll_timer(args):
    poll_timer

    result, expired_timer = TIMER_MANAGER.poll_timer()
    if result == TR_OK:
        if "expired-timer-callback" in TIMER_CONF:
            TIMER_CONF["expired-timer-callback"](expired_timer)

TIMER_MANAGER = TimerManager()
CLK = Clock(start=True, time_counter=int(time.perf_counter()), tick_callback=poll_timer)
"""

class Username():
    """Username
    """
    val = ""

def set_username(val):
    """set_username
    param val <str>
    """
    Username.val = val

GAME = {
    "id": '',
    "state": {},
    "numPlayers": 1,
    "numPairs": 0,
    "level-time": 0,
    "in-device": True
}
def set_id(uid=None):
    """set_id
    """
    if not uid:
        GAME["id"] = str(uuid.uuid4())
    else:
        GAME["id"] = uid

def set_state(state):
    """set_state
    """
    GAME["state"] = state

def set_num_players(num_players):
    """
    set_num_players
    """
    GAME["numPlayers"] = num_players

def set_num_pairs(num_pairs):
    """
    set_num_pairs
    """
    GAME["numPairs"] = num_pairs

def set_level_time(level_time):
    """
    level_time <int>
    """
    GAME["level-time"] = level_time

def set_in_device(val):
    """set_in_device
    param val <boolean>
        True if the game is a single game without the server
        False if the game is controlled by the server
    """
    GAME["in-device"] = val

if __name__ == "__main__":
    set_username("Hessu")
    print(Username.val)
