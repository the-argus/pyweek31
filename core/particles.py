import arcade

from constants.particles import (
    DEFAULT_ALPHA,
    DEFAULT_EMIT_DURATION,
    DEFAULT_EMIT_INTERVAL,
    DEFAULT_PARTICLE_LIFETIME,
    DEFAULT_SCALE,
    TEXTURE,
)


def fire_emitter(center_pos, angle):
    """Interval, emit from center, velocity from angle with spread"""
    e = arcade.Emitter(
        center_xy=center_pos,
        emit_controller=arcade.EmitterIntervalWithTime(
            DEFAULT_EMIT_INTERVAL, DEFAULT_EMIT_DURATION
        ),
        particle_factory=lambda emitter: arcade.LifetimeParticle(
            filename_or_texture=TEXTURE,
            change_xy=arcade.rand_vec_spread_deg(angle, 45, 2.0),
            lifetime=DEFAULT_PARTICLE_LIFETIME,
            scale=DEFAULT_SCALE,
            alpha=DEFAULT_ALPHA,
        ),
    )
    return e
