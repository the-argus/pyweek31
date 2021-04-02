import math
import time

import arcade

from constants.game import (GRID_SIZE, ROOM_HEIGHT, ROOM_WIDTH,
                            SPRITE_IMAGE_SIZE, SPRITE_SCALING)
from constants.physics import PLAYER_MASS, ENEMY_SPEED
from core.PhysicsSprite import PhysicsSprite
from core.physics_engine import PhysicsEngine
from core.sign import sign


class Enemy(PhysicsSprite):
    """ Enemy Sprite"""

    def __init__(self, position, game_resources):

        # Set up parent class
        super().__init__("resources/enemy_static.png", SPRITE_SCALING)
        self.game_resources = game_resources
        self.wall_list = game_resources.wall_list
        self.player = game_resources.player_sprite
        self.path = None

        self.load_textures()

        self.scale = SPRITE_SCALING

        self.center_x = position[0]
        self.center_y = position[1]

        self.path = [
            self.game_resources.player_sprite.center_x,
            self.game_resources.player_sprite.center_y,
        ]

        self.barrier_list = arcade.AStarBarrierList(
            self, self.wall_list, GRID_SIZE, 0, ROOM_WIDTH, 0, ROOM_HEIGHT
        )
        self.calculate_astar()

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def on_update(self, delta_time):
        if self.path is not None and self.path:
            direction = math.atan2(self.path[0][1] - self.center_y, self.path[0][0] - self.center_x)
            print(direction)
            self.x_vel = math.cos(direction) * ENEMY_SPEED
            self.y_vel = math.sin(direction) * ENEMY_SPEED
            if math.sqrt((self.path[0][0] - self.center_x) ** 2 + (self.path[0][1] - self.center_y) ** 2) < GRID_SIZE / 2 - 1:
                self.path.pop(0)

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/enemy_static.png", self.scale)

    def calculate_astar(self):
        self.path = arcade.astar_calculate_path(
            self.position,
            self.game_resources.player_sprite.position,
            self.barrier_list,
            diagonal_movement=False,
        )
        # print(f"X{self.center_x} Y{self.center_y}")
        # print(self.path)

    def on_draw(self):
        if self.path:
            arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)


class Default(Enemy):
    def __init__(self, position, game_resources):
        super().__init__(position, game_resources)


class Jetpack(Enemy):
    def __init__(self, position, game_resources):
        super().__init__(position, game_resources)

    def on_update(self, delta_time):
        pass
        # move
        # if clear line of sight:
        #     move faster
        # if collision_check(self, 0, 0, self.wall_list):
        #     stun
