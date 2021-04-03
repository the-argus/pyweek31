import arcade

from Enemies import Enemy


class EnemyManager:

    def __init__(self, game_resources):
        self.enemy_list = arcade.sprite_list()
        self.game_resources = game_resources

    def spawn_enemy(self):
