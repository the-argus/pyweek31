import arcade
import os
from constants.game import PARENT_DIR
from constants.animation import IDLE_CYCLE_LENGTH, LEFT_FACING, RIGHT_FACING


class Animated(arcade.Sprite):
    """
    An extendable class to handle animations.
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.face_direction = 0
        self.idle_list = []

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

    def animate(self, delta_time: float = 1 / 60):
        # Figure out if we need to flip face left or right
        if self.x_vel < 0 and self.face_direction == RIGHT_FACING:
            self.face_direction = LEFT_FACING
        elif self.x_vel > 0 and self.face_direction == LEFT_FACING:
            self.face_direction = RIGHT_FACING

        # Idle animation
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_list[0][self.face_direction]
            return

    def load_texture_pair(self, filename):
        """
        Load a texture pair, with the second being a mirror image.
        """
        return [
            arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True),
        ]
