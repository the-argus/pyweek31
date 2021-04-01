import arcade


def collision_check(sprite, new_x, new_y, wall_list):
    original_hit_box = sprite.get_hit_box()
    hit_box = [list(num) for num in list(original_hit_box)]

    if len(hit_box) != 4:
        pass
        #raise ValueError("Sprite's hitbox does not have 4 points")
    else:
        translated_box = hit_box
        for i in range(len(hit_box)):
            translated_box[i][0] += new_x - sprite.center_x
            translated_box[i][1] += new_y - sprite.center_y
        translated_tuple_box = [tuple(item) for item in translated_box]
        sprite.set_hit_box(tuple(translated_tuple_box))
        collide = len(arcade.check_for_collision_with_list(sprite, wall_list))
        sprite.set_hit_box(original_hit_box)
        if collide:
            return True
        else:
            return False
