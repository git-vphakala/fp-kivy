"""game_logic\n
init()
play()
set_state(key, value)
"""
from random import shuffle
import time
#from models import TIMER_MANAGER
#from timer_mgr import TR_TOOMANY

TIMERTYPE_GAME_MAX_LEN = "TIMER-GAME-MAX-LEN"

def init(game, change_level):
    """init\n
    game:
        models.GAME
    change_level:
        boolean
    """
    pair_list = []
    card_ids = ["a", "b"]
    scores = [0] * game["numPlayers"]
    players = []
    board = []
    cards = []

    for pair in range(1, game["numPairs"] + 1):
        pair_list.append(str(pair))

    for pair_name in pair_list:
        for card_id in card_ids:
            board.append(pair_name + card_id)
            cards.append({"facedown": True, "removed": False, "faceValue": pair_name})

    board_cards = list(zip(board, cards))
    shuffle(board_cards)
    board, cards = zip(*board_cards)
    for i, card in enumerate(cards):
        card["position"] = i

    # match_list = list(models.Match.objects.filter(game_id=game.gameId).values_list())
    # match_list.sort(key=sort_by_num_player)
    # for match in match_list:
    #     print("game_logic.play: type(match)=" + str(type(match)) + ", match=" + str(match))
    #     players.append(match[2]) # 2 == user

    if change_level:
        scores = game["state"]["scores"]

    game_len = game["level-time"]
    #release_code, max_len_timer =\
    #    TIMER_MANAGER.setup_timer(game_len, (TIMERTYPE_GAME_MAX_LEN, game["id"]))
    #if release_code == TR_TOOMANY:
    #    print("No more timers available. Can not initialize game state.")
    #    game["state"] = {}
    #    return

    game["state"] = {
        # "gameId": str(game.gameId),
        "board": board,
        "cards": cards,
        "turn": 1,
        "faceUp":[],
        "removed":0,
        "scores":scores,
        "gameover": False,
        "players": players,
        "start-time": int(time.time()),
        "game-max-len": game_len,
        "max-len-timer": 0, # max_len_timer
        "faceup-delay": False,
        "in-device": True
    }

def play(game, message):
    """
    game: models.GAME
    message: {cardI:<int>}
    """
    game_state = game["state"]

    if game_state["gameover"]:
        print("game is over")
        return

    card_i = message["cardI"]
    if card_i < 0 or card_i >= len(game_state["cards"]):
        print("game_logic.play: invalid cardI=" + card_i + ", gameId=" + game.gameId +
              ", userName=" + message["userName"])
        return

    card = game_state["cards"][card_i]

    if len(game_state["faceUp"]) == 2 and card["facedown"]:
        game_state["faceUp"].clear()

    if len(game_state["faceUp"]) < 2 and card["facedown"]:
        game_state["cards"][card_i]["facedown"] = card["facedown"] = False
        game_state["faceUp"].append(card)
        print("game_logic.play: turned, cardI=" + str(card_i))

    if len(game_state["faceUp"]) > 1:
        print("game_logic.play: two cards are face-up")
        if game_state["faceUp"][0]["faceValue"] == game_state["faceUp"][1]["faceValue"]:
            print("game_logic.play: pair found")
            for i, card in enumerate(game_state["faceUp"]):
                removed_card_i = game_state["faceUp"][i]["position"]
                game_state["cards"][removed_card_i]["removed"] = True
                game_state["faceUp"][i]["removed"] = True

            # game_state["faceUp"].clear()
            game_state["removed"] += 1
            scores_i = 0 # player_inturn[0][3] - 1 # Match[3] == numPlayer (1..Game.numPlayers)
            game_state["scores"][scores_i] += 1
            if game_state["removed"] == game["numPairs"]:
                game_state["gameover"] = True
                end_time = int(time.time())
                time_based_score = game["level-time"] - (end_time - game_state["start-time"])
                game_state["scores"][scores_i] += time_based_score
                # TIMER_MANAGER.cancel_timer(game_state["max-len-timer"])
                print("game_logic.play: gameover, time_based_score =", time_based_score)
            # else:
            #     game_state["turn"] = change_turn(game_state["turn"], game_state["players"])
        else:
            print("game_logic.play: Not a pair. Return cards back to the face-down state.")
            for i, card in enumerate(game_state["faceUp"]):
                returned_card_i = game_state["faceUp"][i]["position"]
                game_state["cards"][returned_card_i]["facedown"] = True
            # game_state["turn"] = change_turn(game_state["turn"], game_state["players"])

def set_state(game, key, val):
    """set_state\n
    game:
        models.GAME
    key:
        game_state[key]
    val:
        a valid value for the associated key of the game_state
    """
    if "state" in game and key in game["state"]:
        game["state"][key] = val
