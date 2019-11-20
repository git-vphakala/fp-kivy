"""card.py
"""
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.utils import get_color_from_hex

class Card(ButtonBehavior, Image):
    """Card
    """
    __BG_FACEDOWN = "#999900"
    __BG_FACEUP = "#ffff00"
    __BG_REMOVED = "#9ACD32" # "#000000"

    def __init__(self, name, click_handler, card_ind, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.face_down = True
        self.click_handler = click_handler
        self.card_ind = card_ind
        self.name = name
        self.source = "images/transparent_48.png" # font-awesome_4-7-0_" + name + "_48_0_333300_none.png"
        self.removed = False

    def on_press(self):
        if self.removed:
            pass
        else:
            print("Card pressed")
            self.click_handler(self)

    def on_size(self, *args):
        """on_size
        """
        # print("Card.on_size", self.size, self.pos)
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.__BG_FACEDOWN))
            RoundedRectangle(pos=self.pos, size=self.size)
            Color(rgb=get_color_from_hex("#ffff00"))
            Line(width=1, points=[self.pos[0]+10, self.pos[1]-1, self.pos[0]+self.width-10, self.pos[1]-1])
            Line(width=1, points=[self.pos[0]+self.width, self.pos[1]+10, self.pos[0]+self.width, self.pos[1]+self.height-6])

    def turn_up(self):
        """turn_up
        """
        print("Card.turn_up", self.card_ind)
        self.source = "images/font-awesome_4-7-0_" + self.name + "_48_0_333300_none.png"
        self.face_down = False
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.__BG_FACEUP))
            RoundedRectangle(pos=self.pos, size=self.size)

    def turn_down(self):
        """turn_down
        """
        self.source = "images/transparent_48.png"
        self.face_down = True
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.__BG_FACEDOWN))
            RoundedRectangle(pos=self.pos, size=self.size)

    def remove_from_board(self):
        """remove_from_board
        """
        self.removed = True
        self.source = "images/transparent_48.png"
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.__BG_REMOVED))
            Rectangle(pos=self.pos, size=self.size)
            Color(rgb=get_color_from_hex(self.__BG_REMOVED))
            Line(width=1, points=[self.pos[0]+6, self.pos[1]-1, self.pos[0]+self.width-6, self.pos[1]-1])
            Line(width=1, points=[self.pos[0]+self.width, self.pos[1]+3, self.pos[0]+self.width, self.pos[1]+self.height-3])
