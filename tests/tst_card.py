"""
Pytest executes run().
Manually run in the project main directory.
"""
import sys, os
from kivy.app import runTouchApp, stopTouchApp
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from card import Card

def stub_click_handler(card):
    """stub_click_handler
    """
    if card.face_down:
        card.turn_up()
    else:
        card.turn_down()

stop_app = False
finished_callback = None

def check_stop_app():
    if stop_app:
        stopTouchApp()
    if finished_callback:
        finished_callback()

def stub_remove_from_board(test_card):
    test_card.remove_from_board()
    print("assert", "remove_from_board")
    assert test_card.removed
    assert test_card.bgcolor == "#9ACD32"
    assert test_card.source == "images/transparent_48.png"
    Clock.schedule_once(lambda *args: check_stop_app(), 6)

def stub_turn_down(test_card):
    test_card.turn_down()
    print("assert", "turn_down")
    assert test_card.face_down
    assert not test_card.removed
    assert test_card.bgcolor == "#999900"
    assert test_card.source == "images/transparent_48.png"
    Clock.schedule_once(lambda dt: stub_remove_from_board(test_card), 3)

def stub_turn_up(test_card):
    test_card.turn_up()
    print("assert", "turn_up")
    assert not test_card.face_down
    assert not test_card.removed
    assert test_card.bgcolor == "#ffff00"
    assert test_card.source != "images/transparent_48.png"
    Clock.schedule_once(lambda dt: stub_turn_down(test_card), 3)

def run(layout, finished_cb=None):
    global finished_callback

    test_card = Card("android", stub_click_handler, 0)
    layout.add_widget(test_card)
    finished_callback = finished_cb

    print("assert", "initial state")
    assert test_card.face_down
    assert not test_card.removed
    assert test_card.source == "images/transparent_48.png"
    Clock.schedule_once(lambda dt: stub_turn_up(test_card), 3)

if __name__ == "__main__":
    stop_app = True
    LAYOUT = GridLayout(cols=1, padding=100)
    run(LAYOUT)
    runTouchApp(widget=LAYOUT)
