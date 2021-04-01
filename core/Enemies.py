import math

import arcade

from constants.game import SPRITE_IMAGE_SIZE, SPRITE_SCALING
from constants.physics import PLAYER_SPEED
from core.PhysicsSprite import PhysicsSprite
from core.sign import sign


class Enemy(PhysicsSprite):
    """ Player Sprite"""

    def __init__(self, position, game_resources):

        # Set up parent class
        super().__init__("resources/enemy_static.png", SPRITE_SCALING)
        self.game_resources = game_resources
        self.speed = PLAYER_SPEED
        self.wall_list = game_resources.wall_list
        self.player = game_resources.player_sprite
        self.path = None

        self.load_textures()

        self.scale = SPRITE_SCALING

        self.center_x = position[0]
        self.center_y = position[1]

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def on_update(self, delta_time):
        pass

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/enemy_static.png", self.scale)
