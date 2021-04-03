import os

import arcade

from constants.animation import (IDLE_CYCLE_LENGTH, LEFT_FACING, RIGHT_FACING,
                                 WALK_CYCLE_LENGTH)
from constants.game import PARENT_DIR


class Animated(arcade.Sprite):
    """
    An extendable class to handle animations.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.face_direction = 0
        self.idle_list = []
        self.cur_idle = 0
        self.idle_delta = 0

        self.walk_list = []
        self.cur_walk = 0
        self.walk_delta = 0

    def idle_textures(self, textures):
        texture_dir = os.path.join(PARENT_DIR, "resources")
        for texture in textures:
            texture_path = os.path.join(texture_dir, texture)
            self.idle_list.append(self.load_texture_pair(texture_path))
        self.texture = self.idle_list[0][0]
        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        self.set_hit_box(self.texture.hit_box_points)

    def walk_textures(self, textures):
        texture_dir = os.path.join(PARENT_DIR, "resources")
        for texture in textures:
            texture_path = os.path.join(texture_dir, texture)
            self.walk_list.append(self.load_texture_pair(texture_path))

    def animate(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.x_vel < 0 and self.face_direction == RIGHT_FACING:
            self.face_direction = LEFT_FACING
        elif self.x_vel > 0 and self.face_direction == LEFT_FACING:
            self.face_direction = RIGHT_FACING

        # Idle animation
        if self.idle_list:
            if (
                self.x_vel > -1
                and self.x_vel < 1
                and self.y_vel > -1
                and self.y_vel < 1
            ):
                self.texture = self.idle_list[self.cur_idle][self.face_direction]
                self.idle_delta += delta_time
                if self.idle_delta > IDLE_CYCLE_LENGTH:
                    self.cur_idle += 1
                    self.idle_delta = 0
                if self.cur_idle >= len(self.idle_list):
                    self.cur_idle = 0

        # walk animation
        if self.walk_list:
            if self.x_vel < -1 or self.x_vel > 1 or self.y_vel < -1 or self.y_vel > 1:
                self.texture = self.walk_list[self.cur_walk][self.face_direction]
                self.walk_delta += delta_time
                if self.walk_delta > WALK_CYCLE_LENGTH:
                    self.cur_walk += 1
                    self.walk_delta = 0
                if self.cur_walk >= len(self.walk_list):
                    self.cur_walk = 0

        """
        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.face_direction
        self.texture = self.walk_textures[frame][direction]
        """

    def load_texture_pair(self, filename):
        """
        Load a texture pair, with the second being a mirror image.
        """
        return [
            arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True),
        ]
