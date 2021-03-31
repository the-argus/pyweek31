import math

import arcade

from constants.game import SPRITE_IMAGE_SIZE, SPRITE_SCALING
from constants.physics import PLAYER_DRAG, PLAYER_MASS, PLAYER_SPEED
from constants.enemies import ENEMY_BOUNCE, ENEMY_SPRITE_WIDTH
from core.collision_check import collision_check
from core.sign import sign
from core.dot_product import dot_product


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
        self.activated = False

        # coords and physics
        self.center_x = position[0]
        self.center_y = position[1]
        self.x_force = 0
        self.y_force = 0
        self.x_vel = 0
        self.y_vel = 0
        self.mass = PLAYER_MASS
        self.press_force = PLAYER_SPEED
        self.drag_constant = PLAYER_DRAG

        #determines if bouncing calculations have already been done
        self.is_bouncing = False
        self.hit_dir = 0
        self.collided_enemy = None

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
        # failsafe coordinates in case we need to revert changes
        failsafe_x = self.center_x
        failsafe_y = self.center_y

        # physics stuff, just take direction from pressed keys and convert to x and y of pressed_force and drag vector
        in_x = self.right_pressed - self.left_pressed
        in_y = self.up_pressed - self.down_pressed
        is_moving = True
        if not in_x and not in_y:
            is_moving = False
        dir = math.atan2(in_y, in_x)

        f_x = math.cos(dir) * self.press_force * is_moving
        f_y = math.sin(dir) * self.press_force * is_moving

        drag_x = sign(self.x_vel) * (self.x_vel ** 2) * self.drag_constant
        drag_y = sign(self.y_vel) * (self.y_vel ** 2) * self.drag_constant

        enemy_hit_list = arcade.check_for_collision_with_list(self,self.game_resources.enemy_list)
        if len(enemy_hit_list) >= 1 and not self.is_bouncing:
            self.hit_dir = math.atan2(self.center_y-enemy_hit_list[0].center_y, self.center_x-enemy_hit_list[0].center_x)
            self.is_bouncing = True
            self.collided_enemy = enemy_hit_list[0]
        elif len(enemy_hit_list) >= 1:
            self.enemy_reflect_y = ENEMY_BOUNCE*(1-(enemy_hit_list[0].center_y-self.center_y)/((SPRITE_IMAGE_SIZE*math.sqrt(2))*2))
            self.enemy_reflect_x = ENEMY_BOUNCE*(1-(enemy_hit_list[0].center_x-self.center_x)/((SPRITE_IMAGE_SIZE*math.sqrt(2))*2))
            if self.is_bouncing:
                self.update_bounce((math.cos(self.hit_dir),
                                    math.sin(self.hit_dir)))
        else:
            self.is_bouncing = False

        if not len(enemy_hit_list):
            self.enemy_reflect_y = 0
            self.enemy_reflect_x = 0

        if self.is_bouncing:
            #needs to be nested because the list wont exist if first condition isnt met
            if self.collided_enemy!= enemy_hit_list[0]:
                self.is_bouncing = False

        self.x_force = f_x - drag_x + self.enemy_reflect_x
        self.y_force = f_y - drag_y + self.enemy_reflect_y

        self.x_vel += self.x_force / self.mass * delta_time / 0.05
        self.y_vel += self.y_force / self.mass * delta_time / 0.05

        #Wall Collision

        if not collision_check(
            self,
            self.center_x + self.x_vel,
            self.center_y,
            self.game_resources.wall_list,
        ):
            self.center_x += self.x_vel * delta_time / 0.05
        else:
            test_x = 0
            for i in range(math.ceil(self.x_vel)):
                if not collision_check(
                    self,
                    self.center_x + test_x,
                    self.center_y,
                    self.game_resources.wall_list,
                ):
                    test_x += sign(self.x_vel)
                else:
                    test_x -= sign(self.x_vel)
                    break
            self.center_x += test_x
        if not collision_check(
            self,
            self.center_x,
            self.center_y + self.y_vel,
            self.game_resources.wall_list,
        ):
            self.center_y += self.y_vel * delta_time / 0.05
        else:
            test_y = 0
            for i in range(math.ceil(self.y_vel)):
                if not collision_check(
                    self,
                    self.center_x,
                    self.center_y + test_y,
                    self.game_resources.wall_list,
                ):
                    test_y += sign(self.y_vel)
                else:
                    test_y -= sign(self.y_vel)
                    break
            self.center_y += test_y

        if collision_check(
            self, self.center_x, self.center_y, self.game_resources.wall_list
        ):
            self.center_x = failsafe_x
            self.center_y = failsafe_y

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/player_static.png", self.scale)

    def update_bounce(self, normal):
        """Use normal (x,y) tuple to reflect current speed"""
        vel = (self.x_vel,self.y_vel)
        prod = 2*dot_product(normal,vel)
        r = [normal[0]*prod,normal[1]*prod]
        self.x_vel = (-r[0]+vel[0])*ENEMY_BOUNCE
        self.y_vel = (-r[1]+vel[1])*ENEMY_BOUNCE
        #Reflection = 2 * (normal dot velocity) * normal - velocity
