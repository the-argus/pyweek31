import math
import os
import random

import arcade

from constants.camera import FOLLOW, IDLE, LERP_MARGIN, LERP_SPEED
from constants.enemies import SPAWN_RADIUS
from constants.game import (GRID_SIZE, PLAYER_DEFAULT_START, ROOM_HEIGHT,
                            ROOM_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH,
                            SPRITE_SCALING)
from core.Enemies import Enemy
from core.MouseCursor import MouseCursor
from core.lerp import lerp
from core.PlayerCharacter import PlayerCharacter
from core.Bullet import Bullet


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

        # keep track of mouse
        self.mouse_x = 0
        self.mouse_y = 0

        # mouse cursor
        self.mouse_cursor = MouseCursor()

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
        self.wall_list = arcade.SpriteList(
            use_spatial_hash=True, spatial_hash_cell_size=16
        )  # contains all static objects which should have collision
        self.floor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.gui_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # player
        self.player_sprite = PlayerCharacter(PLAYER_DEFAULT_START, self)
        self.player_list.append(self.player_sprite)

        # enemies
        for i in range(3):
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

        self.gui_list.append(self.mouse_cursor)

    def on_draw(self):
        # draw all the lists
        self.wall_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        self.player_sprite.on_draw()
        self.player_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        self.bullet_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        self.enemy_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))
        self.gui_list.draw(filter=(arcade.gl.NEAREST, arcade.gl.NEAREST))

    def on_update(self, delta_time):
        # mouse cursor
        self.mouse_cursor.center_x = self.mouse_x + self.view_left
        self.mouse_cursor.center_y = self.mouse_y + self.view_bottom
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
        for bullet_sprite in self.bullet_list:
            bullet_sprite.on_update(delta_time)

        # screenshake and camera updates
        if self.shake_remain > 0:
            self.shake_x = random.randrange(-self.shake_strength, self.shake_strength)
            self.shake_y = random.randrange(-self.shake_strength, self.shake_strength)
            self.shake_remain -= 1
        else:
            self.shake_x = 0
            self.shake_y = 0
            self.shake_strength = 0

        # clamp viewport to room
        rightside_clamp = ROOM_WIDTH
        leftside_clamp = 0
        topside_clamp = ROOM_HEIGHT
        bottom_clamp = 0
        if not (0 < self.view_left + self.shake_x < rightside_clamp-SCREEN_WIDTH):
            self.view_left = min(rightside_clamp-SCREEN_WIDTH-self.shake_x,self.view_left)
            self.view_left = max(self.view_left,leftside_clamp-self.shake_x)
        if not (0 < self.view_bottom + self.shake_y < topside_clamp-SCREEN_HEIGHT):
            self.view_bottom = min(topside_clamp-SCREEN_HEIGHT-self.shake_y,self.view_bottom)
            self.view_bottom = max(self.view_bottom,bottom_clamp-self.shake_y)

        arcade.set_viewport(
            self.view_left + self.shake_x,
            (SCREEN_WIDTH) + self.view_left + self.shake_x,
            self.view_bottom + self.shake_y,
            (SCREEN_HEIGHT) + self.view_bottom + self.shake_y,
        )

    def screenshake(self, length, strength):
        self.shake_remain = int(abs(length))
        self.shake_strength = int(abs(strength))

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
        self.enemy_sprite = Enemy((start_x, start_y), self)
        for wall in self.wall_list:
            if len(arcade.check_for_collision_with_list(self.enemy_sprite, self.wall_list)) >= 1:
                flag = False
        if (
            self.calculate_distance_from_player(start_x, start_y) > SPAWN_RADIUS
            and flag
        ):
            self.enemy_list.append(self.enemy_sprite)
            return True
        else:
            return False

    def create_bullet(self, pos, vel, damage, speed_falloff, damage_falloff):
        new_bullet = Bullet(pos, vel, damage, speed_falloff, damage_falloff, self.game_instance.physics_engine, self)
        self.bullet_list.append(new_bullet)

    def calculate_distance_from_player(self, enemy_x, enemy_y):
        player_x = self.player_sprite.center_x
        player_y = self.player_sprite.center_y
        return math.sqrt(abs(enemy_x - player_x) ** 2 + abs(enemy_y - player_y) ** 2)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y
