import arcade
import math

from constants.game import SPRITE_SCALING, SPRITE_IMAGE_SIZE
from constants.physics import PLAYER_SPEED, PLAYER_DRAG, PLAYER_MASS
from core.sign import sign

class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""

    def __init__(self, position, game_resources):

        # Set up parent class
        super().__init__("resources/player_static.png")
        self.game_resources = game_resources

        self.load_textures()

        self.scale = SPRITE_SCALING

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False

        #coords and physics
        self.center_x = position[0]
        self.center_y = position[1]
        self.x_force = 0
        self.y_force = 0
        self.x_vel = 0
        self.y_vel = 0
        self.mass = PLAYER_MASS
        self.press_force = PLAYER_SPEED
        self.drag_constant = PLAYER_DRAG

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def update_animation(self, delta_time: float = 1 / 60):
        pass

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def on_update(self, delta_time):
        #physics stuff, just take direction from pressed keys and convert to x and y of pressed_force and drag vector
        in_x = ((self.right_pressed)-(self.left_pressed))
        in_y = ((self.up_pressed)-(self.down_pressed))
        dir = 0
        if in_x != 0:
            dir = math.atan(in_y / in_x)
        elif in_y > 0:
            dir = 3.1415/2
        elif in_y < 0:
            dir = 3*3.1415/2

        is_moving = True
        if in_x == 0 and in_y == 0:
            is_moving = False
        f_x = math.cos(dir)*self.press_force*is_moving
        drag_x = sign(f_x) * (self.x_vel**2) * self.drag_constant
        f_y = math.sin(dir)*self.press_force*is_moving
        drag_y = sign(f_y) * (self.y_vel**2) * self.drag_constant

        self.x_force = f_x - drag_x
        self.y_force = f_y - drag_y

        self.x_vel += self.x_force/self.mass
        self.y_vel += self.y_force/self.mass

        self.center_x += self.x_vel
        self.center_y += self.y_vel

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/player_static.png",self.scale)
