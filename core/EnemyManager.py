import random

import arcade

from core.Enemies import Enemy


class EnemyManager:
    def __init__(self, game_resources):
        self.enemy_list = arcade.SpriteList()
        self.game_resources = game_resources

    def spawn_enemy(self):
        tile = random.choice(self.game_resources.floor_list)
        enemy = Enemy(tile.position, self.game_resources)
        self.enemy_list.append(enemy)
