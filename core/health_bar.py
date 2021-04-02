import arcade

from constants.game import SCREEN_HEIGHT, SCREEN_WIDTH
from constants.health import (HEALTHBAR_HEIGHT, HEALTHBAR_OFFSET_Y,
                              HEALTHBAR_WIDTH)


class HealthBar:
    def __init__(self, max_health, game_resources):
        # Attributes for health
        self.max_health = max_health
        self.cur_health = max_health
        self.game_resources = game_resources

    def draw_health_bar(self):
        """ Draw the health bar """
        health_x = (
            self.game_resources.view_left + SCREEN_WIDTH - HEALTHBAR_WIDTH / 2 - 10
        )
        health_y = self.game_resources.view_bottom + SCREEN_HEIGHT - 10

        # Draw the 'unhealthy' background
        if self.cur_health < self.max_health:
            arcade.draw_rectangle_filled(
                center_x=health_x,
                center_y=health_y + HEALTHBAR_OFFSET_Y,
                width=HEALTHBAR_WIDTH,
                height=HEALTHBAR_HEIGHT,
                color=arcade.color.RED,
            )

        # Calculate width based on health
        health_width = HEALTHBAR_WIDTH * (self.cur_health / self.max_health)

        arcade.draw_rectangle_filled(
            center_x=health_x - 0.5 * (HEALTHBAR_WIDTH - health_width),
            center_y=health_y - 10,
            width=health_width,
            height=HEALTHBAR_HEIGHT,
            color=arcade.color.GREEN,
        )
