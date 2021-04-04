import arcade
import math

from core.PhysicsSprite import PhysicsSprite
from constants.game import SPRITE_SCALING, BULLET_SCALE_RANGE

class Bullet(PhysicsSprite):
    def __init__(self, pos, vel, damage, speed_falloff, damage_falloff, physics_engine, game_resources):
        super().__init__("resources/bullets/muzzle_flash.png", SPRITE_SCALING)
        self.load_textures()
        self.physics_engine = physics_engine
        self.game_resources = game_resources

        self.center_x = pos[0]
        self.center_y = pos[1]

        self.x_vel = vel[0]
        self.y_vel = vel[1]

        self.speed = math.sqrt(self.x_vel**2 + self.y_vel**2)

        self.damage = damage
        self.speed_falloff = speed_falloff
        self.damage_falloff = damage_falloff

        # match the scale of the sprite to the damage of the bullet
        damage_scale = (2/(1+math.pow(math.e,-abs(self.damage))) - 1)
        self.scale = (BULLET_SCALE_RANGE[1]-BULLET_SCALE_RANGE[0])*damage_scale + BULLET_SCALE_RANGE[0]

        self.bounces = 0

        self.is_muzzle_flash = 1
        self.change_frame = 4

        self.set_hit_box( ((2,2), (-2,2),
                           (-2,-2), (2,-2)
                         ))

    def on_update(self, delta_time):
        if self.is_muzzle_flash < self.change_frame:
            self.is_muzzle_flash += 1
            self.set_texture(0)
        else:
            self.set_texture(1)
        self._set_angle(math.degrees(math.atan2(self.y_vel, self.x_vel)))
        self.x_vel *= self.speed_falloff
        self.y_vel *= self.speed_falloff
        self.damage *= self.damage_falloff

        player_hit = arcade.check_for_collision_with_list(self, self.game_resources.player_list)
        if player_hit is not None:
            if len(player_hit) >= 1:
                player_hit[0].health.hurt()
                self.game_resources.screenshake(5, 6)
                self.kill()

        if self.speed_falloff == 1 and math.sqrt(self.x_vel**2 + self.y_vel**2) < self.speed:
            self.kill()

    def jank_kill(self):
        self.kill()

    def load_textures(self):
        self.sprite_base = arcade.Sprite("resources/bullets/bullet.png", self.scale)
        self.append_texture(arcade.load_texture("resources/bullets/bullet.png"))
