import sys, os
from kivy.base import EventLoop
from kivy.app import runTouchApp, stopTouchApp
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from board import Board

stop_app = False
test_board = None
finished_callback = None

def check_stop_app():
    if stop_app:
        stopTouchApp()
    if finished_callback:
        finished_callback()

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

def stub_card_click_handler(card):
    print("assert", "card_click_handler", card.name)
    assert card.face_down and not card.removed

def verify_render_game_state(dt):
    try:
        game_state = next(GAME_STATE_GENERATOR)
    except StopIteration:
        test_board.board.children[3].dispatch("on_press")
        Clock.schedule_once(lambda dt: check_stop_app(), 3)
    else:
        test_board.render_game_state(game_state)
        assert next(RENDER_GAME_STATE_GENERATOR)
        Clock.schedule_once(verify_render_game_state, 5)

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

def stub_cb_after_faceup_delay():
    """stub_cb_after_faceup_delay
    """
    assert next(CB_AFTER_FACEUP_DELAY_GENERATOR)

def run(layout, finished_cb=None):
    """entry point of the test
    """
    global test_board
    global finished_callback

    test_board = Board(stub_card_click_handler, stub_cb_after_faceup_delay)
    layout.add_widget(test_board)
    finished_callback = finished_cb

    test_board.set_board(["1a", "1b", "2a", "3a"])
    Clock.schedule_once(verify_render_game_state, 2)

if __name__ == "__main__":
    stop_app = True
    LAYOUT = GridLayout(cols=1, padding=100)
    run(LAYOUT)
    runTouchApp(widget=LAYOUT)
