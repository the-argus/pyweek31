import arcade
import math

from core.PhysicsSprite import PhysicsSprite
from constants.game import SPRITE_SCALING, BULLET_SCALE_RANGE

class Bullet(PhysicsSprite):
    def __init__(self, pos, vel, damage, speed_falloff, damage_falloff, physics_engine, game_resources):
        super().__init__("resources/bullets/muzzle_flash.png", SPRITE_SCALING)
        self.physics_engine = physics_engine
        self.game_resources = game_resources

        self.center_x = pos[0]
        self.center_y = pos[1]

        self.x_vel = vel[0]
        self.y_vel = vel[1]

        self.damage = damage
        self.speed_falloff = speed_falloff
        self.damage_falloff = damage_falloff

        # match the scale of the sprite to the damage of the bullet
        damage_scale = (2/(1+math.pow(math.e,-abs(self.damage))) - 1)
        self.scale = (BULLET_SCALE_RANGE[1]-BULLET_SCALE_RANGE[0])*damage_scale + BULLET_SCALE_RANGE[0]

        self.bounces = 0

    def on_update(self, delta_time):
        self._set_angle(math.atan2(self.y_vel, self.x_vel))
        self.x_vel *= self.speed_falloff
        self.y_vel *= self.speed_falloff
        self.damage *= self.damage_falloff
        if math.sqrt(self.x_vel**2 + self.y_vel**2) <= 0.4:
            self.kill()
