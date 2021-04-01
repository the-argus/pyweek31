import arcade
import math

from core.dot_product import dot_product
from constants.game import SPRITE_IMAGE_SIZE

class PhysicsEngine:
    """
    Handles the speeds and collisions of enemies and the player
    """
    def __init__(self):
        self.obstacles = []

    def set_obstacles(self,wall_list):
        # used by GameInstance to update any changes in walls
        self.obstacles = wall_list

    def move_sprite(self,sprite,delta_time):
        failsafe_x = sprite.center_x
        failsafe_y = sprite.center_y

        if not collision_check(
            sprite,
            sprite.center_x + sprite.x_vel,
            sprite.center_y,
            self.obstacles
        ):
            sprite.center_x += sprite.x_vel * delta_time / 0.05
        else:
            test_x = 0
            for i in range(math.ceil(sprite.x_vel)):
                if not collision_check(
                    sprite,
                    sprite.center_x + test_x,
                    sprite.center_y,
                    self.obstacles
                ):
                    test_x += sign(sprite.x_vel)
                else:
                    test_x -= sign(sprite.x_vel)
                    break
            sprite.center_x += test_x
        if not collision_check(
            sprite,
            sprite.center_x,
            sprite.center_y + sprite.y_vel,
            self.obstacles,
        ):
            sprite.center_y += sprite.y_vel * delta_time / 0.05
        else:
            test_y = 0
            for i in range(math.ceil(sprite.y_vel)):
                if not collision_check(
                    sprite,
                    sprite.center_x,
                    sprite.center_y + test_y,
                    self.obstacles,
                ):
                    test_y += sign(sprite.y_vel)
                else:
                    test_y -= sign(sprite.y_vel)
                    break
            sprite.center_y += test_y

        if collision_check(
            sprite, sprite.center_x, sprite.center_y, self.obstacles
        ):
            sprite.center_x = failsafe_x
            sprite.center_y = failsafe_y

    def collision_check(self,sprite, new_x, new_y):
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
        if collide:
            return True
        else:
            return False

    def bounce(self, sprite1, sprite2, speed):
        """
        bounces sprite one off of sprite two (reflects velocity)
        """
        # Use normal (x,y) tuple to reflect a speed vector
        reflect = [None,None]
        normal = get_normal(sprite1,sprite2)
        prod = 2*dot_product(normal,speed)
        r = [normal[0]*prod,normal[1]*prod]
        reflect[0] = -r[0]+speed[0]
        reflect[1] = -r[1]+speed[1]
        return tuple(reflect)
        #Reflection = 2 * (normal dot velocity) * normal - velocity

    def get_normal(self, sprite1, sprite2):
        hit_dir = math.atan2(sprite1.center_y-sprite2.center_y, sprite1.center_x-sprite2.center_x)
        rx = sign(math.sin(hit_dir))*(1-(enemy_hit_list[0].center_y-self.center_y)/((SPRITE_IMAGE_SIZE*math.sqrt(2))*2))
        ry = sign(math.cos(hit_dir))*(1-(enemy_hit_list[0].center_x-self.center_x)/((SPRITE_IMAGE_SIZE*math.sqrt(2))*2))
        return (rx,ry)
