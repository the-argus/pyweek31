import arcade

from constants.game import SPRITE_SCALING


class MouseCursor(arcade.Sprite):
    def __init__(self):
        self.main_path = "resources/mouse/mouse_cursor"
        super().__init__(f"{self.main_path}.png", SPRITE_SCALING)
        self.load_textures()

    def set_cursor(self, fuel_level):
        if fuel_level == 1:
            self.texture = self.fuel_list[2]
        if fuel_level == 2:
            self.texture = self.fuel_list[1]
        if fuel_level == 3:
            self.texture = self.fuel_list[0]

    def load_textures(self):
        self.sprite_base = arcade.Sprite(f"{self.main_path}.png", SPRITE_SCALING)
        self.fuel_list = []
        for i in range(3):
            texture = arcade.load_texture(f"{self.main_path}_fuel{i}.png")
            self.fuel_list.append(texture)
