#!/usr/bin/env python
import os
import sys

import arcade

# The major, minor version numbers your require
MIN_VER = (3, 7)

if sys.version_info[:2] < MIN_VER:
    sys.exit("This game requires Python {}.{}.".format(*MIN_VER))

from constants.game import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH
from core.GameInstance import GameInstance


class GameWindow(arcade.Window):
    """ Main Window """

    def __init__(self, width, height, title):
        """ Create the variables """

        # sets relative path to where this file is
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        super().__init__(width, height, title)
        self.game_instance: Optional[GameInstance] = None
        # Save original size when we exit fullscreen
        self.original_size = self.get_size()
        # screensize multiplier so that the viewport gets scaled up in fullscreen
        self.screensize_multiplier = (
            arcade.window_commands.get_display_size()[0] / SCREEN_WIDTH
        )

    def setup(self):
        """ Set up everything with the game """

        window_size = self.get_size()
        self.game_instance = GameInstance(self)

        # Set the background color
        # arcade.set_background_color(arcade.color.AMAZON)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        self.game_instance.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        self.game_instance.on_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        """passes mouse info to the gameinstance on_mouse_motion but properly scaled to any screensize changes"""
        if self.fullscreen:
            scaledx = int(x / self.screensize_multiplier)
            scaledy = int(y / self.screensize_multiplier)
            scaleddx = dx / self.screensize_multiplier
            scaleddy = dy / self.screensize_multiplier
            self.game_instance.on_mouse_motion(scaledx, scaledy, dx, dy)
        else:
            self.game_instance.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        """passes mouse info to the gameinstance on_mouse_press but properly scaled to any screensize changes"""
        scaledx = x / self.screensize_multiplier
        scaledy = y / self.screensize_multiplier
        self.game_instance.on_mouse_press(scaledx, scaledy, button, modifiers)

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.game_instance.on_update(delta_time)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.game_instance.on_draw()
        text_size = 10
        margin = 2
        if not self.game_instance.window.fullscreen:
            arcade.draw_text(
                "Press F to toggle between full screen and windowed mode",
                (SCREEN_WIDTH // 2) + self.game_instance.game_resources.view_left,
                margin + self.game_instance.game_resources.view_bottom,
                arcade.color.WHITE,
                text_size,
                anchor_x="center",
            )


def main():
    """ Main method """
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
