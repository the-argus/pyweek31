import arcade
import math

from constants.game import SCREEN_WIDTH, SCREEN_HEIGHT

class GameInstance:
    """
    This is an instance of the game and all of the different components needed to render it.
    """

    def __init__(self, window):

        # Reference to main window object
        self.window = window

        self.horizontal_key_list = []
        self.verticle_key_list = []

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        #toggle fullscreen
        if key == arcade.key.F:
            self.window.set_fullscreen(not self.window.fullscreen)
            if self.window.fullscreen:
                if SCREEN_WIDTH > SCREEN_HEIGHT:
                    self.window.screensize_multiplier = self.screensize[0]/SCREEN_WIDTH
                else:
                    self.window.screensize_multiplier = self.screensize[1]/SCREEN_HEIGHT
            else:
                self.window.set_size(self.window.original_size[0],self.window.original_size[1])
                self.window.screensize_multiplier = 1

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_draw(self):
        pass
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
        pass
