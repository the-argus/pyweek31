import math
import array
import time

from PIL import Image

from arcade import Sprite
from arcade import SpriteList
from arcade import gl

class HDRSprite(arcade.SpriteList):
    def _calculate_sprite_buffer(self):

        if self.is_static:
            usage = 'static'
        else:
            usage = 'stream'

        def _calculate_pos_buffer():
            self._sprite_pos_data = array.array('f')
            # print("A")
            for sprite in self.sprite_list:
                self._sprite_pos_data.append(sprite.center_x)
                self._sprite_pos_data.append(sprite.center_y)

            self._sprite_pos_buf = self.ctx.buffer(
                data=self._sprite_pos_data,
                usage=usage
            )
            variables = ['in_pos']
            self._sprite_pos_desc = gl.BufferDescription(
                self._sprite_pos_buf,
                '2f',
                variables,
            )
            self._sprite_pos_changed = False

        def _calculate_size_buffer():
            self._sprite_size_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_size_data.append(sprite.width)
                self._sprite_size_data.append(sprite.height)

            self._sprite_size_buf = self.ctx.buffer(
                data=self._sprite_size_data,
                usage=usage
            )
            variables = ['in_size']
            self._sprite_size_desc = gl.BufferDescription(
                self._sprite_size_buf,
                '2f',
                variables)
            self._sprite_size_changed = False

        def _calculate_angle_buffer():
            self._sprite_angle_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_angle_data.append(sprite.angle)

            self._sprite_angle_buf = self.ctx.buffer(
                data=self._sprite_angle_data,
                usage=usage
            )
            variables = ['in_angle']
            self._sprite_angle_desc = gl.BufferDescription(
                self._sprite_angle_buf,
                '1f',
                variables,
            )
            self._sprite_angle_changed = False

        def _calculate_brightness_buffer():
            self._sprite_brightness_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_brightness_data.append(sprite.brightness)

            self._sprite_brightness_buf = self.ctx.buffer(
                data=self._sprite_brightness_data,
                usage=usage
            )
            variables = ['in_brightness']
            self._sprite_brightness_desc = gl.BufferDescription(
                self._sprite_brightness_buf,
                '1f',
                variables,
            )
            self._sprite_brightness_changed = False

        def _calculate_colors():
            self._sprite_color_data = array.array('B')

            for sprite in self.sprite_list:
                self._sprite_color_data.extend(sprite.color[:3])
                self._sprite_color_data.append(int(sprite.alpha))

            self._sprite_color_buf = self.ctx.buffer(
                data=self._sprite_color_data,
                usage=usage
            )
            variables = ['in_color']
            self._sprite_color_desc = gl.BufferDescription(
                self._sprite_color_buf,
                '4f1',
                variables,
                normalized=['in_color']
            )
            self._sprite_color_changed = False

        def _calculate_sub_tex_coords():
            """
            Create a sprite sheet, and set up subtexture coordinates to point
            to images in that sheet.
            """
            new_array_of_texture_names = []
            new_array_of_images = []
            new_texture = False
            if self.array_of_images is None or self._force_new_atlas_generation:
                new_texture = True
                self._force_new_atlas_generation = False

            # print()
            # print("New texture start: ", new_texture)

            for sprite in self.sprite_list:

                # noinspection PyProtectedMember
                if sprite.texture is None:
                    raise Exception("Error: Attempt to draw a sprite without a texture set.")

                name_of_texture_to_check = sprite.texture.name

                # Do we already have this in our old texture atlas?
                if name_of_texture_to_check not in self.array_of_texture_names:
                    # No, so flag that we'll have to create a new one.
                    new_texture = True
                    # print("New because of ", name_of_texture_to_check)

                # Do we already have this created because of a prior loop?
                if name_of_texture_to_check not in new_array_of_texture_names:
                    # No, so make as a new image
                    new_array_of_texture_names.append(name_of_texture_to_check)
                    if sprite.texture is None:
                        raise ValueError(f"Sprite has no texture.")
                    if sprite.texture.image is None:
                        raise ValueError(f"Sprite texture {sprite.texture.name} has no image.")
                    image = sprite.texture.image

                    # Create a new image with a transparent border around it to help prevent artifacts
                    tmp = Image.new('RGBA', (image.width+2, image.height+2))
                    tmp.paste(image, (1, 1))
                    tmp.paste(tmp.crop((1          , 1           , image.width+1, 2             )), (1            , 0             ))
                    tmp.paste(tmp.crop((1          , image.height, image.width+1, image.height+1)), (1            , image.height+1))
                    tmp.paste(tmp.crop((1          , 0           ,             2, image.height+2)), (0            , 0             ))
                    tmp.paste(tmp.crop((image.width, 0           , image.width+1, image.height+2)), (image.width+1, 0             ))

                    # Put in our array of new images
                    new_array_of_images.append(tmp)

            # print("New texture end: ", new_texture)
            # print(new_array_of_texture_names)
            # print(self.array_of_texture_names)
            # print()

            if new_texture:
                # Add back in any old textures. Chances are we'll need them.
                for index, old_texture_name in enumerate(self.array_of_texture_names):
                    if old_texture_name not in new_array_of_texture_names and self.array_of_images is not None:
                        new_array_of_texture_names.append(old_texture_name)
                        image = self.array_of_images[index]
                        new_array_of_images.append(image)

                self.array_of_texture_names = new_array_of_texture_names

                self.array_of_images = new_array_of_images
                # print(f"New Texture Atlas with names {self.array_of_texture_names}")

            # Get their sizes
            widths, heights = zip(*(i.size for i in self.array_of_images))

            grid_item_width, grid_item_height = max(widths), max(heights)
            image_count = len(self.array_of_images)
            root = math.sqrt(image_count)
            grid_width = int(math.sqrt(image_count))
            # print(f"\nimage_count={image_count}, root={root}")
            if root == grid_width:
                # Perfect square
                grid_height = grid_width
                # print("\nA")
            else:
                grid_height = grid_width
                grid_width += 1
                if grid_width * grid_height < image_count:
                    grid_height += 1
                # print("\nB")

            # Figure out sprite sheet size
            margin = 0

            sprite_sheet_width = (grid_item_width + margin) * grid_width
            sprite_sheet_height = (grid_item_height + margin) * grid_height

            if new_texture:

                # TODO: This code isn't valid, but I think some releasing might be in order.
                # if self.texture is not None:
                #     .Texture.release(self.texture_id)

                # Make the composite image
                new_image2 = Image.new('RGBA', (sprite_sheet_width, sprite_sheet_height))

                x_offset = 0
                for index, image in enumerate(self.array_of_images):

                    x = (index % grid_width) * (grid_item_width + margin)
                    y = (index // grid_width) * (grid_item_height + margin)

                    # print(f"Pasting {new_array_of_texture_names[index]} at {x, y}")

                    new_image2.paste(image, (x, y))
                    x_offset += image.size[0]

                # Create a texture out the composite image
                texture_bytes2 = new_image2.tobytes()
                self._texture = self.ctx.texture(
                    (new_image2.width, new_image2.height),
                    components=4,
                    data=texture_bytes2,
                )

                if self.texture_id is None:
                    self.texture_id = SpriteList.next_texture_id

                # new_image2.save("sprites.png")

            # Create a list with the coordinates of all the unique textures
            self._tex_coords = []
            offset = 1

            for index, image in enumerate(self.array_of_images):
                column = index % grid_width
                row = index // grid_width

                # Texture coordinates are reversed in y axis
                row = grid_height - row - 1

                x = column * (grid_item_width + margin) + offset
                y = row * (grid_item_height + margin) + offset

                # Because, coordinates are reversed
                y += (grid_item_height - (image.height - margin))

                normalized_x = x / sprite_sheet_width
                normalized_y = y / sprite_sheet_height

                start_x = normalized_x
                start_y = normalized_y

                normalized_width = (image.width-2*offset) / sprite_sheet_width
                normalized_height = (image.height-2*offset) / sprite_sheet_height

                # print(f"Fetching {new_array_of_texture_names[index]} at {row}, {column} => {x}, {y} normalized to {start_x:.2}, {start_y:.2} size {normalized_width}, {normalized_height}")

                self._tex_coords.append([start_x, start_y, normalized_width, normalized_height])

            # Go through each sprite and pull from the coordinate list, the proper
            # coordinates for that sprite's image.
            self._sprite_sub_tex_data = array.array('f')
            for sprite in self.sprite_list:
                index = self.array_of_texture_names.index(sprite.texture.name)
                for coord in self._tex_coords[index]:
                    self._sprite_sub_tex_data.append(coord)

            self._sprite_sub_tex_buf = self.ctx.buffer(
                data=self._sprite_sub_tex_data,
                usage=usage
            )

            self._sprite_sub_tex_desc = gl.BufferDescription(
                self._sprite_sub_tex_buf,
                '4f',
                ['in_sub_tex_coords'],
            )
            self._sprite_sub_tex_changed = False

        if len(self.sprite_list) == 0:
            return

        perf_time = time.perf_counter()

        _calculate_pos_buffer()
        _calculate_size_buffer()
        _calculate_angle_buffer()
        _calculate_brightness_buffer()
        _calculate_sub_tex_coords()
        _calculate_colors()

        # vertices = array.array('f', [
        #     #  x,    y,   u,   v
        #     -1.0, -1.0, 0.0, 0.0,
        #     -1.0, 1.0, 0.0, 1.0,
        #     1.0, -1.0, 1.0, 0.0,
        #     1.0, 1.0, 1.0, 1.0,
        # ])
        # self.vbo_buf = self.ctx.buffer(data=vertices)
        # vbo_buf_desc = gl.BufferDescription(
        #     self.vbo_buf,
        #     '2f 2f',
        #     ('in_vert', 'in_texture')
        # )

        # Can add buffer to index vertices
        # vao_content = [vbo_buf_desc,
        #                self._sprite_pos_desc,
        #                self._sprite_size_desc,
        #                self._sprite_angle_desc,
        #                self._sprite_sub_tex_desc,
        #                self._sprite_color_desc]
        vao_content = [self._sprite_pos_desc,
                       self._sprite_size_desc,
                       self._sprite_angle_desc,
                       self._sprite_sub_tex_desc,
                       self._sprite_color_desc,
                       self._sprite_brightness_desc]

        self._vao1 = self.ctx.geometry(vao_content)
        LOG.debug('[%s] _calculate_sprite_buffer: %s sec', id(self), time.perf_counter() - perf_time)

    def draw(self, **kwargs):
        """
        Draw this list of sprites.

        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.

        :param blend_function: Optional parameter to set the OpenGL blend function used for drawing the sprite list, such as
                        'arcade.Window.ctx.BLEND_ADDITIVE' or 'arcade.Window.ctx.BLEND_DEFAULT'
        """
        if len(self.sprite_list) == 0:
            return

        # What percent of this sprite list moved? Used in guessing spatial hashing
        self._percent_sprites_moved = self._sprites_moved / len(self.sprite_list) * 100
        self._sprites_moved = 0

        # Make sure window context exists
        if self.ctx is None:
            self.ctx = get_window().ctx
            # Used in drawing optimization via OpenGL
            self.program = self.ctx.sprite_list_program_cull

        if self._vao1 is None:
            self._calculate_sprite_buffer()

        self.ctx.enable(self.ctx.BLEND)
        if "blend_function" in kwargs:
            self.ctx.blend_func = kwargs["blend_function"]
        else:
            self.ctx.blend_func = self.ctx.BLEND_DEFAULT

        self._texture.use(0)

        if "filter" in kwargs:
            self._texture.filter = self.ctx.NEAREST, self.ctx.NEAREST

        self.program['Texture'] = self.texture_id

        texture_transform = None
        if len(self.sprite_list) > 0:
            # always wrap texture transformations with translations
            # so that rotate and resize operations act on the texture
            # center by default
            texture_transform = Matrix3x3().translate(-0.5, -0.5).multiply(self.sprite_list[0].texture_transform.v).multiply(Matrix3x3().translate(0.5, 0.5).v)
        else:
            texture_transform = Matrix3x3()
        self.program['TextureTransform'] = texture_transform.v

        if not self.is_static:
            if self._sprite_pos_changed:
                self._sprite_pos_buf.orphan()
                self._sprite_pos_buf.write(self._sprite_pos_data)
                self._sprite_pos_changed = False

            if self._sprite_size_changed:
                self._sprite_size_buf.orphan()
                self._sprite_size_buf.write(self._sprite_size_data)
                self._sprite_size_changed = False

            if self._sprite_angle_changed:
                self._sprite_angle_buf.orphan()
                self._sprite_angle_buf.write(self._sprite_angle_data)
                self._sprite_angle_changed = False

            if self._sprite_color_changed:
                self._sprite_color_buf.orphan()
                self._sprite_color_buf.write(self._sprite_color_data)
                self._sprite_color_changed = False

            if self._sprite_sub_tex_changed:
                self._sprite_sub_tex_buf.orphan()
                self._sprite_sub_tex_buf.write(self._sprite_sub_tex_data)
                self._sprite_sub_tex_changed = False

        self._vao1.render(self.program, mode=self.ctx.POINTS, vertices=len(self.sprite_list))
