import math

import arcade

from constants.game import SPRITE_IMAGE_SIZE, SPRITE_SCALING, JETPACK
from constants.physics import PLAYER_MASS, PLAYER_SPEED, JETPACK_FORCE, PLAYER_FRICTION
from constants.enemies import ENEMY_BOUNCE, ENEMY_SPRITE_WIDTH
from core.PhysicsSprite import PhysicsSprite
from core.sign import sign
from core.dot_product import dot_product


class PlayerCharacter(PhysicsSprite):
    """ Player Sprite"""

    def __init__(self, position, game_resources):

        # Set up parent class
        super().__init__("resources/player_static.png",SPRITE_SCALING)
        self.game_resources = game_resources

        self.load_textures()

        self.scale = SPRITE_SCALING

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.activated = False

        # coords and physics
        self.center_x = position[0]
        self.center_y = position[1]
        self.x_force = 0
        self.y_force = 0
        self.mass = PLAYER_MASS
        self.friction = PLAYER_FRICTION
        self.press_force = PLAYER_SPEED

        # gadget mode
        self.mode = JETPACK

        # jetpack physics
        self.jetpack_x = 0
        self.jetpack_y = 0

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
        elif key == arcade.key.SPACE:
            self.activated = True

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
        elif key == arcade.key.SPACE:
            self.activated = False

    def on_update(self, delta_time):
        # physics stuff, just take direction from pressed keys and convert to x and y of pressed_force and drag vector
        in_x = self.right_pressed - self.left_pressed
        in_y = self.up_pressed - self.down_pressed
        is_moving = True
        if not in_x and not in_y and not self.activated:
            is_moving = False
        dir = math.atan2(in_y, in_x)

        f_x = math.cos(dir) * self.press_force * is_moving
        f_y = math.sin(dir) * self.press_force * is_moving

        # force from bouncing off enemies
        enemy_hit_list = arcade.check_for_collision_with_list(self,self.game_resources.enemy_list)
        if len(enemy_hit_list):
            hit_dir = math.atan2(self.center_y-enemy_hit_list[0].center_y, self.center_x-enemy_hit_list[0].center_x)
            self.enemy_reflect_y = sign(math.sin(hit_dir))*ENEMY_BOUNCE*(1-(enemy_hit_list[0].center_y-self.center_y)/((SPRITE_IMAGE_SIZE*math.sqrt(2))*2))
            self.enemy_reflect_x = sign(math.cos(hit_dir))*ENEMY_BOUNCE*(1-(enemy_hit_list[0].center_x-self.center_x)/((SPRITE_IMAGE_SIZE*math.sqrt(2))*2))
        else:
            self.enemy_reflect_y = 0
            self.enemy_reflect_x = 0

        # force from using the jetpack
        if self.mode == JETPACK and self.activated:
            mouse_dir = math.atan2(self.game_resources.mouse_y+self.game_resources.view_bottom-self.center_y, self.game_resources.mouse_x+self.game_resources.view_left-self.center_x)
            self.jetpack_x = JETPACK_FORCE*math.cos(mouse_dir)
            self.jetpack_y = JETPACK_FORCE*math.sin(mouse_dir)
        else:
            self.jetpack_x = 0
            self.jetpack_y = 0

        self.x_force = f_x - drag_x + self.enemy_reflect_x + self.jetpack_x - self.friction*is_moving*sign(self.x_vel)
        self.y_force = f_y - drag_y + self.enemy_reflect_y + self.jetpack_y - self.friction*is_moving*sign(self.y_vel)

        self.x_vel += self.x_force / self.mass * delta_time / 0.05
        self.y_vel += self.y_force / self.mass * delta_time / 0.05
        # clamp velocity to max speed
        vel_vec2 = math.sqrt(self.x_vel**2 + self.y_vel**2)
        # while vel_vec2

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/player_static.png", self.scale)
