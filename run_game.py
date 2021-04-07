#!/usr/bin/env python
import arcade
import os
import sys
import random

from postprocessing.post_processing_chain import PostProcessingChain
from postprocessing.render_target import RenderTarget

from postprocessing.effects.vignette import Vignette
from postprocessing.effects.greyscale import GreyScale
from postprocessing.effects.bloom import Bloom
from postprocessing.effects.tonemap import Tonemap
from postprocessing.effects.split_tone import SplitTone
from postprocessing.effects.chromatic_abberation import ChromaticAberration
from postprocessing.effects.template import Template


from typing import Iterable, Iterator
from typing import Any
from typing import TypeVar
from typing import List
from typing import Tuple
from typing import Optional
from typing import Union

import logging
import math
import array
import time

from PIL import Image

from arcade import Color
from arcade import Matrix3x3
from arcade import Sprite
from arcade import get_distance_between_sprites
from arcade import are_polygons_intersecting
from arcade import is_point_in_polygon

from arcade import rotate_point
from arcade import get_window
from arcade import Point
from arcade import gl

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

        #setup post processing
        self.setup_post_processing()

    def setup(self):
        """ Set up everything with the game """

        window_size = self.get_size()
        self.game_instance = GameInstance(self)

        # Set the background color
        # arcade.set_background_color(arcade.color.AMAZON)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.I:
            self.bloom.threshold -= 0.1
            print(self.bloom.threshold)
        if key == arcade.key.O:
            self.bloom.threshold += 0.1
            print(self.bloom.threshold)


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
        # draw to a render target instead of the screen
        self.render_target.bind_as_framebuffer()
        self.render_target.framebuffer_object.clear(arcade.color.AMAZON)

        # draw everything that needs to be drawn with post processing
        self.game_instance.filter_draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        # apply the post processing effect chain to the render target, and apply it to the screen
        self.post_processing.apply_effects(self.render_target.texture, self.ctx.screen)

        # draw the fullscreen text which needs to eventually removed once we get a settings screen
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

    def setup_post_processing(self):
        # create a new post-processing chain, this will automatically resize with anything you render through it
        self.post_processing = PostProcessingChain(self.ctx, self.get_size(), True)

        # allocate and add effects
        # not sure about this method of allocating a object / weird implicit factory thing

        self.bloom = self.post_processing.add_effect(Bloom)
        self.bloom.threshold = 1.9
        self.bloom.power = 1.0

        self.tonemap = self.post_processing.add_effect(Tonemap)
        self.tonemap.threshold = 2.0

        self.chromatic = self.post_processing.add_effect(ChromaticAberration)
        self.chromatic.axial = 1.0
        self.chromatic.distance_scale = 0.003

        self.greyscale = self.post_processing.add_effect(GreyScale)
        self.greyscale.strength = 0.5

        self.split_tone = self.post_processing.add_effect(SplitTone)

        self.vignette = self.post_processing.add_effect(Vignette)
        self.vignette.inner_distance = 0.1

        self.template = self.post_processing.add_effect(Template)

        size = self.get_size()
        self.render_target = RenderTarget(self.ctx, size, 'f2')


def main():
    """ Main method """
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
