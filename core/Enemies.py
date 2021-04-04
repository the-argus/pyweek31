import math
import time

import arcade

from constants.game import (
    GRID_SIZE,
    ROOM_HEIGHT,
    ROOM_WIDTH,
    SPRITE_IMAGE_SIZE,
    SPRITE_SCALING,
    ANIMATION_SPEED
)
from constants.physics import ENEMY_SPEED, PLAYER_MASS
from core.physics_engine import PhysicsEngine
from constants.enemies import SHOOTING, FOLLOWING, ENEMY_FIRERATE
from core.PhysicsSprite import PhysicsSprite
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

        self.state = SHOOTING

        # bullet characteristics
        self.bullet_speed = 10
        self.bullet_damage = 1
        self.bullet_speed_falloff = 1
        self.bullet_damage_falloff = 1

        self.shot_cooldown = 0

        self.load_textures()

        self.scale = SPRITE_SCALING

        self.center_x = position[0]
        self.center_y = position[1]

        self.path = [
            (
                self.game_resources.player_sprite.center_x,
                self.game_resources.player_sprite.center_y,
            )
        ]

        self.barrier_list = arcade.AStarBarrierList(
            self, self.wall_list, GRID_SIZE, 0, ROOM_WIDTH, 0, ROOM_HEIGHT
        )

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def on_update(self, delta_time):
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1

        self.calculate_astar()
        self.animate(delta_time * ANIMATION_SPEED)

        if self.path:
            self.path.pop(0)

        if self.path is not None:
            if len(self.path) > 1:

                dir = math.atan2(self.path[1][1]-self.center_y, self.path[1][0]-self.center_x)
                x_speed = math.cos(dir) * ENEMY_SPEED
                y_speed = math.sin(dir) * ENEMY_SPEED

                """
                if self.center_x < self.path[1][0]:
                    x_speed = ENEMY_SPEED
                else:
                    x_speed = -ENEMY_SPEED
                if self.center_y < self.path[1][1]:
                    y_speed = ENEMY_SPEED
                else:
                    y_speed = -ENEMY_SPEED
                """

                self.y_vel = y_speed
                self.x_vel = x_speed

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



    def calculate_astar(self):
        self.path = arcade.astar_calculate_path(
            self.position,
            self.game_resources.player_sprite.position,
            self.barrier_list,
            diagonal_movement=False,
        )

    def draw_path(self):
        if self.path:
            arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/enemy_static.png", self.scale)
        self.idle_textures([
            "enemies/enemy_idle0.png",
            "enemies/enemy_idle1.png",
            "enemies/enemy_idle2.png",
            "enemies/enemy_idle3.png"
        ])
        self.walk_textures([
            "enemies/enemy_walk0.png",
            "enemies/enemy_walk1.png",
            "enemies/enemy_walk2.png",
            "enemies/enemy_walk3.png"
        ])

    def jank_kill(self):
        self.kill()


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
