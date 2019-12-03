"""card.py
"""
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.utils import get_color_from_hex

class Card(ButtonBehavior, Image):
    """
    param name <str>
        Card's face image name. This is inserted to the name template in turn_up().
        The image must exist in the images-directory.
    param click_handler
        Callback which called on_press if the card has not been removed
    param card_ind <int>
        Position in the board
    - - -
    attribute face_down <boolean>
        True: the card is face down. 
        False: the card is face up.
    attribute removed <boolean>
        True: the card has been removed from the board
        False: the card is on the board
    - - -
    method turn_up
        Called when the face of the card should be seen.
    method turn_down
        Called when the face should be hidden.
    method remove_from_board
        Called when the card is removed for the board.
    """
    __BG_FACEDOWN = "#999900"
    __BG_FACEUP = "#ffff00"
    __BG_REMOVED = "#9ACD32"
    __BORDER_FACEDOWN = __BG_FACEUP
    __IMAGE_FACEDOWN = "transparent_48.png"

    def __init__(self, name, click_handler, card_ind, images_dir="images/", **kwargs):
        super(Card, self).__init__(**kwargs)
        self.face_down = True
        self.click_handler = click_handler
        self.card_ind = card_ind
        self.name = name
        self.source = images_dir + self.__IMAGE_FACEDOWN
        self.removed = False
        self.bgcolor = None
        self.images_dir = images_dir

    def on_press(self):
        if self.removed:
            pass
        else:
            print("Card pressed")
            self.click_handler(self)

    def on_size(self, *args):
        """on_size
        """
        self.bgcolor = self.__BG_FACEDOWN
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.bgcolor))
            RoundedRectangle(pos=self.pos, size=self.size)
            Color(rgb=get_color_from_hex(self.__BORDER_FACEDOWN)) # "#ffff00"))
            Line(width=1, points=[self.pos[0]+10, self.pos[1]-1, self.pos[0]+self.width-10,\
                self.pos[1]-1])
            Line(width=1, points=[self.pos[0]+self.width, self.pos[1]+10, self.pos[0]+self.width,\
                self.pos[1]+self.height-6])

    def turn_up(self):
        """turn_up
        """
        print("Card.turn_up", self.card_ind)
        self.source = self.images_dir + "font-awesome_4-7-0_" + self.name + "_48_0_333300_none.png"
        self.face_down = False
        self.bgcolor = self.__BG_FACEUP
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.bgcolor))
            RoundedRectangle(pos=self.pos, size=self.size)

    def turn_down(self):
        """turn_down
        """
        self.source = self.images_dir + self.__IMAGE_FACEDOWN
        self.face_down = True
        self.bgcolor = self.__BG_FACEDOWN
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.bgcolor))
            RoundedRectangle(pos=self.pos, size=self.size)

    def remove_from_board(self):
        """remove_from_board
        """
        self.removed = True
        self.source = self.images_dir + self.__IMAGE_FACEDOWN
        self.bgcolor = self.__BG_REMOVED
        with self.canvas.before:
            Color(rgb=get_color_from_hex(self.bgcolor))
            Rectangle(pos=self.pos, size=self.size)
            Color(rgb=get_color_from_hex(self.__BG_REMOVED))
            Line(width=1, points=[self.pos[0]+6, self.pos[1]-1, self.pos[0]+self.width-6,\
                self.pos[1]-1])
            Line(width=1, points=[self.pos[0]+self.width, self.pos[1]+3, self.pos[0]+self.width,\
                self.pos[1]+self.height-3])
