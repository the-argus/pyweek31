import math
import time

import arcade

from constants.game import (GRID_SIZE, ROOM_HEIGHT, ROOM_WIDTH,
                            SPRITE_IMAGE_SIZE, SPRITE_SCALING)
from constants.physics import PLAYER_MASS, PLAYER_SPEED
from constants.enemies import SHOOTING, FOLLOWING, ENEMY_FIRERATE
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

        self.state = SHOOTING

        # bullet characteristics
        self.bullet_speed = 10
        self.bullet_damage = 1
        self.bullet_speed_falloff = 0.99
        self.bullet_damage_falloff = 1

        self.shot_cooldown = 0

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
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1
        if self.path is not None and self.path and self.state == FOLLOWING:
            self.center_x = self.path[0][0]
            self.center_y = self.path[0][1]
            self.path.pop(0)
        elif self.state == SHOOTING and self.shot_cooldown == 0:
            if self.test_los(self.game_resources.player_sprite, SPRITE_IMAGE_SIZE, self.game_resources.wall_list):
                self.shot_cooldown = ENEMY_FIRERATE
                x = (self.center_x, self.game_resources.player_sprite.center_x)
                y = (self.center_y, self.game_resources.player_sprite.center_y)
                dir = math.atan2(y[1]-y[0],x[1]-x[0])
                xv = math.cos(dir) * self.bullet_speed
                yv = math.sin(dir) * self.bullet_speed
                self.game_resources.create_bullet((self.center_x,self.center_y), (xv,yv), self.bullet_damage, self.bullet_speed_falloff, self.bullet_damage_falloff)

    def test_los(self, sprite, width, barriers):
        """
        Tests to see if the enemy's line of sight on a sprite is obstructed by barriers.
        "Width" refers to the width of an opening required to confirm line of sight.
        """
        x = (self.center_x, sprite.center_x)
        y = (self.center_y, sprite.center_y)
        dir = math.atan2(y[1]-y[0],x[1]-x[0])
        original_hit_box = self.get_hit_box()
        hit_box = ((x[0] + (math.cos(dir+(math.pi/2)) * width/2), y[0] + (math.sin(dir+(math.pi/2)) * width/2)),
                   (x[0] + (math.cos(dir-(math.pi/2)) * width/2), y[0] + (math.sin(dir-(math.pi/2)) * width/2)),
                   (x[1] + (math.cos(dir+(math.pi/2)) * width/2), y[1] + (math.sin(dir+(math.pi/2)) * width/2)),
                   (x[1] + (math.cos(dir-(math.pi/2)) * width/2), y[1] + (math.sin(dir-(math.pi/2)) * width/2)))
        self.set_hit_box(hit_box)
        test = sign(len(arcade.check_for_collision_with_list(self, barriers)))
        self.set_hit_box(original_hit_box)
        return not test



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
