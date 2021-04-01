import arcade
import os
from constants.game import PARENT_DIR
from constants.animation import IDLE_CYCLE_LENGTH


class Animated(arcade.AnimatedWalkingSprite):
    """
    An extendable class to handle animations.
    """

    def __init__(self, *args):
        super().__init__(*args)

        self.face_direction = None
        self.idle_list = None

    def idle_textures(self, textures):
        texture_dir = os.path.join(PARENT_DIR, "resources")
        for texture in textures:
            texture_path = os.path.join(texture_dir, texture)
            self.idle_list.append(arcade.load_texture_pair(texture_path))
        self.texture = self.idle_list[0][0]
        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1 / 60):
        pass

