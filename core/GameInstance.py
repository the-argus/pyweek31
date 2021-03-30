import math

import arcade

from constants.game import SCREEN_HEIGHT, SCREEN_WIDTH
from core.GameResource import GameResources


class GameInstance:
    """
    This is an instance of the game and all of the different components needed to render it.
    """

    def __init__(self, window):

        # Reference to main window object
        self.window = window

        self.horizontal_key_list = []
        self.verticle_key_list = []

        self.game_resources = GameResources(self)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        self.game_resources.player_sprite.on_key_press(key, modifiers)
        self.game_resources.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        self.game_resources.player_sprite.on_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.game_resources.player_sprite.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.game_resources.player_sprite.on_mouse_press(x, y, button, modifiers)

    def on_draw(self):
        self.game_resources.on_draw()

    def on_draw_scene(self):
        pass

    def on_draw_emissive(self):
        pass

    def on_draw_light_buffer(self):
        pass

    def on_draw_after_post(self):
        pass

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.game_resources.on_update(delta_time)
