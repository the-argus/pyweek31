import arcade
import math
import os
import random

from constants.game import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ROOM_WIDTH,
    ROOM_HEIGHT,
    SPRITE_SCALING,
    PLAYER_DEFAULT_START,
)
from constants.camera import LERP_MARGIN, LERP_SPEED, FOLLOW, IDLE
from core.lerp import lerp
from core.PlayerCharacter import PlayerCharacter


class GameResources:
    """
    All resource handling like maps and sprites and rendering
    """

    def __init__(self, game_instance):
        self.game_instance = game_instance

        # sets relative path to where this file is
        file_path = os.path.abspath(os.getcwd())
        os.chdir(file_path)

        # keep track of camera location
        self.view_bottom = 0
        self.view_left = 0

        # camera behavior and follow location
        self.behavior = FOLLOW
        self.follow_x = PLAYER_DEFAULT_START[0]
        self.follow_y = PLAYER_DEFAULT_START[1]

        # screenshake
        self.shake_remain = 0
        self.shake_strength = 1
        self.shake_x = 0
        self.shake_y = 0

        # list initilization
        self.wall_list = (
            arcade.SpriteList()
        )  # contains all static objects which should have collision
        self.floor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # player
        self.player_sprite = PlayerCharacter(PLAYER_DEFAULT_START, self)
        self.player_list.append(self.player_sprite)

        # placeholder room
        for i in range(int(ROOM_HEIGHT / 16)):
            wall1 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall2 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall1.center_x = 8
            wall1.center_y = i * 16
            wall2.center_x = ROOM_WIDTH - 8
            wall2.center_y = i * 16
            self.wall_list.append(wall1)
            self.wall_list.append(wall2)

        for i in range(int(ROOM_WIDTH / 16) + 1):
            wall1 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall2 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall1.center_x = i * 16
            wall1.center_y = 8
            wall2.center_x = i * 16
            wall2.center_y = ROOM_HEIGHT - 8
            self.wall_list.append(wall1)
            self.wall_list.append(wall2)

    def on_draw(self):
        # draw all the lists
        self.wall_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        self.player_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))

    def on_update(self, delta_time):
        # camera scrolling
        self.follow_x = self.player_sprite.center_x
        self.follow_y = self.player_sprite.center_y
        dist = math.sqrt(
            ((self.view_left + (SCREEN_WIDTH / 2)) - self.follow_x) ** 2
            + ((self.view_bottom + (SCREEN_HEIGHT / 2)) - self.follow_y) ** 2
        )
        if dist >= LERP_MARGIN:
            self.view_left = int(
                lerp(self.view_left, self.follow_x - (SCREEN_WIDTH / 2), LERP_SPEED)
            )
            self.view_bottom = int(
                lerp(self.view_bottom, self.follow_y - (SCREEN_HEIGHT / 2), LERP_SPEED)
            )

        self.player_sprite.on_update(delta_time)

        # screenshake and camera updates
        if self.shake_remain > 0:
            self.shake_x = random.randrange(-self.shake_strength, self.shake_strength)
            self.shake_y = random.randrange(-self.shake_strength, self.shake_strength)
            self.shake_remain -= 1
        else:
            self.shake_x = 0
            self.shake_y = 0

        arcade.set_viewport(
            self.view_left + self.shake_x,
            (SCREEN_WIDTH) + self.view_left + self.shake_x,
            self.view_bottom + self.shake_y,
            (SCREEN_HEIGHT) + self.view_bottom + self.shake_y,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.F:
            self.game_instance.window.set_fullscreen(
                not self.game_instance.window.fullscreen
            )
            arcade.set_viewport(
                self.view_left + self.shake_x,
                self.view_left + self.shake_x + SCREEN_WIDTH,
                self.view_bottom + self.shake_y,
                self.view_bottom + self.shake_y + SCREEN_HEIGHT,
            )
