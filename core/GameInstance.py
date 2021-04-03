import math

import arcade

from constants.game import SCREEN_HEIGHT, SCREEN_WIDTH
from core.GameResource import GameResources
from core.physics_engine import PhysicsEngine


class GameInstance:
    """
    This is an instance of the game and all of the different components needed to render it.
    """

    def __init__(self, window):

        # Reference to main window object
        self.window = window

        self.game_resources = GameResources(self)

        self.physics_engine = PhysicsEngine()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        self.game_resources.player_sprite.on_key_press(key, modifiers)
        self.game_resources.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        self.game_resources.player_sprite.on_key_release(key, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        self.game_resources.on_mouse_motion(x, y, dx, dy)
        self.game_resources.player_sprite.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        self.game_resources.player_sprite.on_mouse_press(x, y, button, modifiers)

    def on_draw(self):
        self.game_resources.on_draw()

    def on_draw_scene(self):
        pass

    def on_draw_emissive(self):
        pass

    def on_draw_light_buffer(self):
        pass

    def on_draw_after_post(self):
        pass

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.game_resources.on_update(delta_time)

        # update any changes to walls
        self.physics_engine.set_obstacles(self.game_resources.wall_list)

        # update dynamic entities
        self.game_resources.player_sprite.on_update(delta_time)
        self.physics_engine.move_sprite(self.game_resources.player_sprite, delta_time)

        for sprite in self.game_resources.enemy_list.enemy_list:
            self.physics_engine.move_sprite(sprite, delta_time)

        for sprite in self.game_resources.bullet_list:
            if sprite is not None:
                wall = self.physics_engine.move_sprite(sprite, delta_time)
                if wall is not None:
                    sprite.bounces += 1
                    print((sprite.x_vel,sprite.y_vel))
                    reflection = self.physics_engine.bounce(sprite, wall, (sprite.x_vel, sprite.y_vel), True)
                    print(reflection)
                    sprite.x_vel = reflection[0]
                    sprite.y_vel = reflection[1]
