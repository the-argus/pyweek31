from arcade import Sprite

class HDRSprite(arcade.Sprite):
    def __init__(self, *args):
        super().__init__(*args)
        self.brightness = 1
