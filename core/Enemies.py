import math
import arcade
import time

from constants.game import SPRITE_IMAGE_SIZE, SPRITE_SCALING
from constants.physics import PLAYER_DRAG, PLAYER_MASS, PLAYER_SPEED
from constants.game import ROOM_HEIGHT, ROOM_WIDTH, GRID_SIZE
from constants.enemies import ENEMY_SPEED, FLOATING_SPEED, CHARGE_SPEED
from core.collision_check import collision_check
from core.sign import sign


class Enemy(arcade.Sprite):
    """ Player Sprite"""

    def __init__(self, position, game_resources, sprite):

        # Set up parent class
        super().__init__(sprite, SPRITE_SCALING)
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

        self.barrier_list = arcade.AStarBarrierList(self,
                                                    self.wall_list,
                                                    GRID_SIZE,
                                                    0,
                                                    ROOM_WIDTH,
                                                    0,
                                                    ROOM_HEIGHT)
        self.calculate_astar()

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def on_update(self, delta_time):
        # if self.path is not None and self.path:
        #     self.center_x = self.path[0][0]
        #     self.center_y = self.path[0][1]
        #     self.path.pop(0)
        pass

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/wall_test.png", self.scale)

    def calculate_astar(self):
        self.path = arcade.astar_calculate_path(
            self.position,
            self.game_resources.player_sprite.position,
            self.barrier_list,
            diagonal_movement=False,
        )
        print(f"X{self.center_x} Y{self.center_y}")
        print(self.path)

    def on_draw(self):
        if self.path:
            arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)


class Default(Enemy):
    def __init__(self, position, game_resources):
        super().__init__(position, game_resources, "resources/wall_test.png")
        self.speed = ENEMY_SPEED


class Jetpack(Enemy):
    def __init__(self, position, game_resources):
        super().__init__(position, game_resources, "resources/floor_test.png")
        self.floating_speed = FLOATING_SPEED

    def on_update(self, delta_time):
        # move
        # if clear line of sight:
        #     move faster
        # if collision_check(self, 0, 0, self.wall_list):
        #     stun
