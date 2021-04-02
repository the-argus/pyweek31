import math
import os
import random

import arcade

from constants.camera import FOLLOW, IDLE, LERP_MARGIN, LERP_SPEED
from constants.enemies import SPAWN_RADIUS
from constants.game import (
    PLAYER_DEFAULT_START,
    ROOM_HEIGHT,
    ROOM_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPRITE_SCALING,
    GRID_SIZE
)
from core.Enemies import Default, Jetpack
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
        self.wall_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=16) # contains all static objects which should have collision
        self.floor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # player
        self.player_sprite = PlayerCharacter(PLAYER_DEFAULT_START, self)
        self.player_list.append(self.player_sprite)

        # enemies
        for i in range(5):
            created = self.spawn_new_enemy()
            if not created:
                i -= 1

        # placeholder room
        for i in range(int(ROOM_HEIGHT / 16)):
            wall1 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall2 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall1.center_x = 8
            wall1.center_y = (i * 16) + 8
            wall2.center_x = ROOM_WIDTH - 8
            wall2.center_y = (i * 16) + 8
            self.wall_list.append(wall1)
            self.wall_list.append(wall2)

        for i in range(int(ROOM_WIDTH / 16)):
            wall1 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall2 = arcade.Sprite("resources/wall_test.png", SPRITE_SCALING)
            wall1.center_x = (i * 16) + 8
            wall1.center_y = 8
            wall2.center_x = (i * 16) + 8
            wall2.center_y = ROOM_HEIGHT - 8
            self.wall_list.append(wall1)
            self.wall_list.append(wall2)

    def on_draw(self):
        # draw all the lists
        self.wall_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        self.enemy_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
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
        for enemy_sprite in self.enemy_list:
            enemy_sprite.on_update(delta_time)

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

    def spawn_new_enemy(self):
        start_x = random.randint(0, ROOM_WIDTH)
        start_y = random.randint(0, ROOM_HEIGHT)
        flag = True

        type = random.randint(0, 1)
        if type == 0:
            self.enemy_sprite = Default((start_x, start_y), self)
        elif type == 1:
            self.enemy_sprite = Jetpack((start_x, start_y), self)
        for wall in self.wall_list:
            if arcade.check_for_collision(self.enemy_sprite, wall):
                flag = False
        if (
            self.calculate_distance_from_player(start_x, start_y) > SPAWN_RADIUS
            and flag
        ):
            self.enemy_list.append(self.enemy_sprite)
            return True
        else:
            return False

    def calculate_distance_from_player(self, enemy_x, enemy_y):
        player_x = self.player_sprite.center_x
        player_y = self.player_sprite.center_y
        return math.sqrt(abs(enemy_x - player_x) ** 2 + abs(enemy_y - player_y) ** 2)
