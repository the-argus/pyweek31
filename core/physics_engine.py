import math

import arcade

from constants.game import SPRITE_IMAGE_SIZE
from core.dot_product import dot_product
from core.sign import sign


class PhysicsEngine:
    """
    Handles the speeds and collisions of enemies and the player
    """

    def __init__(self):
        self.obstacles = []

    def set_obstacles(self, wall_list):
        # used by GameInstance to update any changes in walls
        self.obstacles = wall_list

    def move_sprite(self, sprite, delta_time):
        failsafe_x = sprite.center_x
        failsafe_y = sprite.center_y

        collided = None

        if not self.collision_check(
            sprite, sprite.center_x + sprite.x_vel, sprite.center_y
        ):
            sprite.center_x += sprite.x_vel * delta_time / 0.05
        else:
            test_x = 0
            for i in range(math.ceil(abs(sprite.x_vel))):
                if not self.collision_check(
                    sprite, sprite.center_x + test_x, sprite.center_y
                ):
                    test_x += sign(sprite.x_vel)
                else:
                    test_x += sign(sprite.x_vel)
                    collided = arcade.check_for_collision_with_list(sprite, self.obstacles)
                    test_x -= sign(sprite.x_vel)
                    break
            sprite.center_x += test_x
            sprite.x_vel = 0
        if not self.collision_check(
            sprite, sprite.center_x, sprite.center_y + sprite.y_vel
        ):
            sprite.center_y += sprite.y_vel * delta_time / 0.05
        else:
            test_y = 0
            for i in range(math.ceil(abs(sprite.y_vel))):
                if not self.collision_check(
                    sprite, sprite.center_x, sprite.center_y + test_y
                ):
                    test_y += sign(sprite.y_vel)
                else:
                    test_y += sign(sprite.y_vel)
                    if collided is not None:
                        if len(collided) == 0:
                            collided = arcade.check_for_collision_with_list(sprite, self.obstacles)
                    test_y -= sign(sprite.y_vel)
                    break
            sprite.center_y += test_y
            sprite.y_vel = 0
        if len(arcade.check_for_collision_with_list(sprite, self.obstacles)) >= 1:
            sprite.center_x = failsafe_x
            sprite.center_y = failsafe_y
        if collided is not None:
            if len(collided) >= 1:
                return collided[0]
            else:
                return None
        else:
            return None

    def collision_check(self, sprite, new_x, new_y):
        """
        Better collision check which takes the projected location of a sprite instead of its actual location
        """
        original_hit_box = sprite.get_hit_box()
        hit_box = [list(num) for num in list(original_hit_box)]

        translated_box = hit_box
        for i in range(len(hit_box)):
            translated_box[i][0] += new_x - sprite.center_x
            translated_box[i][1] += new_y - sprite.center_y
        translated_tuple_box = [tuple(item) for item in translated_box]
        sprite.set_hit_box(tuple(translated_tuple_box))
        collide = len(arcade.check_for_collision_with_list(sprite, self.obstacles))
        sprite.set_hit_box(original_hit_box)
        if collide >= 1:
            return True
        else:
            return False

    def bounce(self, sprite1, sprite2, speed, is_square):
        """
        bounces sprite one off of sprite two (reflects velocity)
        """
        # Use normal (x,y) tuple to reflect a speed vector
        reflect = [None,None]
        if is_square:
            normal = self.get_square_normal(sprite1,sprite2)
        else:
            normal = self.get_normal(sprite1,sprite2)
        prod = 2*dot_product(normal,speed)
        r = [normal[0]*prod,normal[1]*prod]
        reflect[0] = -r[0]+speed[0]
        reflect[1] = -r[1]+speed[1]
        return tuple(reflect)
        # Reflection = 2 * (normal dot velocity) * normal - velocity

    def get_normal(self, sprite1, sprite2):
        hit_dir = math.atan2(
            sprite1.center_y - sprite2.center_y, sprite1.center_x - sprite2.center_x
        )
        rx = sign(math.sin(hit_dir)) * (
            1
            - (enemy_hit_list[0].center_y - self.center_y)
            / ((SPRITE_IMAGE_SIZE * math.sqrt(2)) * 2)
        )
        ry = sign(math.cos(hit_dir)) * (
            1
            - (enemy_hit_list[0].center_x - self.center_x)
            / ((SPRITE_IMAGE_SIZE * math.sqrt(2)) * 2)
        )
        return (rx, ry)

    def get_square_normal(self, sprite1, sprite2):
        hit_dir = math.atan2(sprite1.center_y-sprite2.center_y, sprite1.center_x-sprite2.center_x)
        if hit_dir <= math.pi/4:
            return (1, 0)
        elif math.pi/4 > hit_dir >= math.pi*3/4:
            return (0, 1)
        elif math.pi*3/4 > hit_dir >= math.pi*5/4:
            return (-1, 0)
        elif math.pi*5/4 > hit_dir >= math.pi*7/4:
            return (0, -1)
        elif hit_dir > math.pi*7/4:
            return (1, 0)
        else:
            return None
