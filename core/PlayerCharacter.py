import math

import arcade

from constants.enemies import ENEMY_BOUNCE, ENEMY_SPRITE_WIDTH
from constants.game import (
    FUEL_REGENERATION_TIME,
    JETPACK,
    JETPACK_BURST_COOLDOWN,
    JETPACK_BURST_LENGTH,
    JETPACK_DISTANCE_SCALE,
    MAX_JETPACK_SPEED,
    MAXFUEL,
    SPRITE_IMAGE_SIZE,
    SPRITE_SCALING,
    ANIMATION_SPEED
)
from constants.physics import (
    GRAVITY,
    JETPACK_FORCE,
    PLAYER_FRICTION,
    PLAYER_MASS,
    PLAYER_SPEED,
)
from core.animated import Animated
from core.dot_product import dot_product
from core.health_bar import HealthBar
from core.particles import fire_emitter
from core.PhysicsSprite import PhysicsSprite
from core.sign import sign


class PlayerCharacter(PhysicsSprite):
    """ Player Sprite"""

    def __init__(self, position, game_resources):

        # Set up parent class
        super().__init__("resources/player_static.png", SPRITE_SCALING)
        self.game_resources = game_resources

        self.load_textures()

        self.scale = SPRITE_SCALING

        self.health = HealthBar(100, game_resources)

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.activated = False

        # coords and physics
        self.center_x = position[0]
        self.center_y = position[1]
        self.mass = PLAYER_MASS
        self.friction = PLAYER_FRICTION
        self.press_force = PLAYER_SPEED
        self.max_extra_speed = 20
        self.max_speed = 4

        self.x_player_vel = 0
        self.y_player_vel = 0
        self.x_vel_extra = 0
        self.y_vel_extra = 0

        # Emitter
        self.emitter = None
        self.emitter_timeout = 0

        # gadget mode
        self.mode = JETPACK
        self.cooldown = False

        # jetpack physics
        self.jetpack_x = 0
        self.jetpack_y = 0
        self.max_jetpack_speed = MAX_JETPACK_SPEED
        self.fuel = MAXFUEL
        self.fuel_tick = 0
        self.fuel_gen = FUEL_REGENERATION_TIME
        self.jet_burst_tick = 0
        self.jet_engaged = False

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
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
            if not self.cooldown:
                self.fuel_changed(-1)

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

    def on_draw(self):
        # draw emitter
        if self.emitter:
            self.emitter.draw()
        # draw heathbar
        self.health.draw_health_bar()

    def on_update(self, delta_time):
        if self.emitter:
            self.emitter.update()

        # update jetpack burst
        if self.jet_burst_tick > 0:
            self.jet_burst_tick -= 1
            if self.jet_burst_tick <= 0:
                self.jet_burst_tick = -JETPACK_BURST_COOLDOWN
                self.jet_engaged = False
                self.cooldown = True

            self.run_emitter()

        elif self.jet_burst_tick < 0:
            self.jet_burst_tick += 1
            if self.jet_burst_tick >= 0:
                self.jet_burst_tick = 0
                self.cooldown = False

        # update jetpack fuel
        self.fuel_tick += 1 * (self.fuel < MAXFUEL)
        if self.fuel_tick > self.fuel_gen:
            self.fuel_tick = 0
            self.fuel_changed(1)

        # update animation
        self.animate(delta_time * ANIMATION_SPEED)

        # force from pressing buttons
        in_x = self.right_pressed - self.left_pressed
        in_y = self.up_pressed - self.down_pressed
        is_moving = True
        if not in_x and not in_y and not self.activated:
            is_moving = False
        dir = math.atan2(in_y, in_x)

        f_x = math.cos(dir) * self.press_force * is_moving
        f_y = math.sin(dir) * self.press_force * is_moving

        # force from bouncing off enemies
        enemy_hit_list = arcade.check_for_collision_with_list(
            self, self.game_resources.enemy_list.enemy_list
        )
        if len(enemy_hit_list):
            self.health.hurt()
            self.game_resources.screenshake(4, 3)
            hit_dir = math.atan2(
                self.center_y - enemy_hit_list[0].center_y,
                self.center_x - enemy_hit_list[0].center_x,
            )
            enemy_reflect_y = (
                sign(math.sin(hit_dir))
                * ENEMY_BOUNCE
                * (
                    1
                    - (enemy_hit_list[0].center_y - self.center_y)
                    / ((SPRITE_IMAGE_SIZE * math.sqrt(2)) * 2)
                )
            )
            enemy_reflect_x = (
                sign(math.cos(hit_dir))
                * ENEMY_BOUNCE
                * (
                    1
                    - (enemy_hit_list[0].center_x - self.center_x)
                    / ((SPRITE_IMAGE_SIZE * math.sqrt(2)) * 2)
                )
            )
        else:
            enemy_reflect_y = 0
            enemy_reflect_x = 0

        # force from using the jetpack
        if self.mode == JETPACK and self.jet_engaged and self.activated:
            mouse_dir = math.atan2(
                self.game_resources.mouse_y
                + self.game_resources.view_bottom
                - self.center_y,
                self.game_resources.mouse_x
                + self.game_resources.view_left
                - self.center_x,
            )
            mouse_dist = math.sqrt(
                (
                    self.game_resources.mouse_x
                    + self.game_resources.view_left
                    - self.center_x
                )
                ** 2
                + (
                    self.game_resources.mouse_y
                    + self.game_resources.view_bottom
                    - self.center_y
                )
                ** 2
            )
            dist_scale = JETPACK_FORCE * self.jetpack_distance_scaling(mouse_dist)
            jx_force = math.cos(mouse_dir) * dist_scale
            jy_force = math.sin(mouse_dir) * dist_scale
        else:
            jx_force = 0
            jy_force = 0

        self.jetpack_x += (
            (jx_force - self.friction * self.mass * GRAVITY * self.jetpack_x)
            / self.mass
            * delta_time
            / 0.05
        )
        self.jetpack_y += (
            (jy_force - self.friction * self.mass * GRAVITY * self.jetpack_y)
            / self.mass
            * delta_time
            / 0.05
        )

        self.x_vel_extra += (
            (enemy_reflect_x - self.friction * self.mass * GRAVITY * self.x_vel_extra)
            / self.mass
            * delta_time
            / 0.05
        )
        self.y_vel_extra += (
            (enemy_reflect_y - self.friction * self.mass * GRAVITY * self.y_vel_extra)
            / self.mass
            * delta_time
            / 0.05
        )

        self.x_player_vel += (
            (f_x - self.friction * self.mass * GRAVITY * self.x_player_vel)
            / self.mass
            * delta_time
            / 0.05
        )
        self.y_player_vel += (
            (f_y - self.friction * self.mass * GRAVITY * self.y_player_vel)
            / self.mass
            * delta_time
            / 0.05
        )

        # clamp velocities to max speeds
        clamped_player_speed = self.clamp_speed(
            self.x_player_vel, self.y_player_vel, self.max_speed
        )
        self.x_player_vel = clamped_player_speed[0]
        self.y_player_vel = clamped_player_speed[1]

        clamped_jetpack_speed = self.clamp_speed(
            self.jetpack_x, self.jetpack_y, self.max_jetpack_speed
        )
        self.jetpack_x = clamped_jetpack_speed[0]
        self.jetpack_y = clamped_jetpack_speed[1]

        clamped_extra_speed = self.clamp_speed(
            self.x_vel_extra, self.y_vel_extra, self.max_extra_speed
        )
        self.x_vel_extra = clamped_extra_speed[0]
        self.y_vel_extra = clamped_extra_speed[1]

        # create final velocity with extra velocities added
        self.x_vel = self.x_player_vel + self.jetpack_x + self.x_vel_extra
        self.y_vel = self.y_player_vel + self.jetpack_y + self.y_vel_extra

        # print(self.position)

    def run_emitter(self):
        mouse_x = self.game_resources.mouse_cursor.center_x
        mouse_y = self.game_resources.mouse_cursor.center_y
        x_dis = abs(mouse_x - self.center_x)
        y_dis = abs(mouse_y - self.center_y)
        angle = math.degrees(math.atan2(y_dis, x_dis))

        if mouse_x < self.center_x:
            angle = 180 - angle
        if mouse_y < self.center_y:
            angle = 360 - angle
        angle += 180

        self.emitter = fire_emitter(self.position, angle)

    def clamp_speed(self, xspeed, yspeed, max_speed):
        vec2 = math.sqrt(xspeed ** 2 + yspeed ** 2)
        if vec2 > max_speed:
            vel_dir = math.atan2(yspeed, xspeed)
            xs = max_speed * math.cos(vel_dir)
            ys = max_speed * math.sin(vel_dir)
            return (xs, ys)
        else:
            return (xspeed, yspeed)

    def fuel_changed(self, fuel):
        if fuel < 0 and self.fuel >= 1:
            self.jet_burst_tick = JETPACK_BURST_LENGTH
            self.jet_engaged = True
        self.fuel += fuel
        if self.fuel > MAXFUEL:
            self.fuel = MAXFUEL
        if self.fuel < 0:
            self.fuel = 0
        self.game_resources.mouse_cursor.set_cursor(self.fuel)

    def jetpack_distance_scaling(self, val):
        return 2 / (1 + math.pow(math.e, -abs(val) * JETPACK_DISTANCE_SCALE)) - 1

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/player_static.png", self.scale)
        self.idle_textures([
            "player/player_idle0.png",
            "player/player_idle1.png",
            "player/player_idle2.png",
            "player/player_idle3.png"
        ])
        self.walk_textures([
            "player/player_walk0.png",
            "player/player_walk1.png",
            "player/player_walk2.png",
            "player/player_walk3.png"
        ])
