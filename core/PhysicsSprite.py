import arcade
import math

from constants.physics import DEFAULT_MASS, DEFAULT_FRICTION, DEFAULT_MAXSPEED
from core.animated import Animated


class PhysicsSprite(Animated):
    """Adds variables required by core.physics_engine"""
    def __init__(self, *args):
        super().__init__(*args)
        self.x_vel = 0
        self.y_vel = 0
        self.mass = DEFAULT_MASS
        self.friction = DEFAULT_FRICTION
        self.max_speed = DEFAULT_MAXSPEED
