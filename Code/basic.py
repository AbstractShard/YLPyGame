import pygame
import numpy
import os

# region FUNCTIONS
def load_image(path: str, colorkey=0):
    if not os.path.exists(path):
        print(f"Path: {path} doesn't exists")
        return

    image = pygame.image.load(path)

    if colorkey:
        image = image.convert()

        if colorkey == -1:
            colorkey = image.get_at((0, 0))

        image.set_colorkey(colorkey)
        return image

    image = image.convert_alpha()
    return image


def get_distance(start: tuple, end: tuple) -> float:
    return pygame.math.Vector2(start).distance_to(pygame.math.Vector2(end))


def get_rotated(original_image: pygame.Surface, current_rect: pygame.Rect, angle: int) -> (pygame.Surface, pygame.Rect):
    rotated_image = pygame.transform.rotate(original_image, angle)
    new_rect = rotated_image.get_rect(center=current_rect.center)
    return rotated_image, new_rect


def get_rotated_around_pivot(original_image: pygame.Surface, current_image: pygame.Surface,
                             pivot: tuple, target: tuple, length: int) -> (pygame.Surface, pygame.Rect):
    offset = pygame.math.Vector2()
    offset.from_polar((length, 0))

    angle = int((pygame.math.Vector2(target) - pygame.math.Vector2(pivot)).as_polar()[1])
    pos = pivot + offset.rotate(angle)

    new_rect = current_image.get_rect(center=pos)
    new_image, new_rect = get_rotated(original_image, new_rect, -angle)
    return new_image, new_rect


def draw_debug(screen, groups: list):
    for group in groups:
        for sprite in group.sprites():
            if sprite.collider:
                collider_image = pygame.Surface(sprite.collider.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(collider_image, "green", (0, 0, *sprite.collider.rect.size), 2)

                screen.blit(collider_image, sprite.collider.rect.topleft)

            if hasattr(sprite, "hurtbox"):
                hurtbox_image = pygame.Surface(sprite.hurtbox.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(hurtbox_image, "purple", (0, 0, *sprite.hurtbox.rect.size), 1)

                screen.blit(hurtbox_image, sprite.hurtbox.rect.topleft)

            if hasattr(sprite, "curr_attacks") and sprite.curr_attacks:
                for atk in sprite.curr_attacks:
                    atk_color = pygame.Color("white")

                    if atk.counter["startup"] > 0:
                        atk_color = pygame.Color("orange")

                    elif atk.counter["active"] > 0:
                        atk_color = pygame.Color("red")

                    elif atk.counter["recovery"] > 0:
                        atk_color = pygame.Color("blue")

                    if isinstance(atk, OrbitAttack):
                        pix_arr = pygame.surfarray.pixels3d(atk.collision_image)

                        for i in range(len(pix_arr)):
                            for j in range(len(pix_arr[i])):
                                pix_arr[i][j] = numpy.array(atk_color[:-1])

                        del pix_arr

                        screen.blit(atk.collision_image, atk.rect.topleft)
                        continue

                    atk_image = pygame.Surface(atk.rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(atk_image, atk_color, (0, 0, *atk.rect.size), 1)

                    screen.blit(atk_image, atk.rect.topleft)

            if hasattr(sprite, "curr_projectiles") and sprite.curr_projectiles:
                for proj in sprite.curr_projectiles:
                    proj_image = pygame.Surface(proj.rect.size, pygame.SRCALPHA)
                    pygame.draw.ellipse(proj_image, "white", (0, 0, *proj.rect.size), 1)

                    screen.blit(proj_image, proj.rect.topleft)
# endregion

# region CLASSES
class CSprite(pygame.sprite.Sprite):
    def __init__(self, groups: list, pos: tuple, size: tuple, img_path: str,
                 start_aname: str, start_arect: pygame.Rect, start_framerate: int, start_rows: int, start_columns: int,
                 colorkey=0):
        super().__init__(*groups)

        # other
        self.orig_image = load_image(img_path, colorkey)
        self.resize_to = size

        # animation
        self.animation_frames = {}
        self.add_animation(start_aname, self.orig_image, start_arect, start_framerate, start_rows, start_columns)

        self.a_data = {"name": start_aname, "a_frame": 0, "frame": self.animation_frames[start_aname]["framerate"], "play": True}

        # basic
        self.image = self.get_updated_image()

        self.fpos = pos
        self.rect = pygame.rect.Rect((0, 0), self.image.get_rect().size)
        self.rect.center = self.fpos

        self.mask = pygame.mask.from_surface(self.image)

    def add_animation(self, name: str, sheet: pygame.Surface, animation_rect: pygame.Rect, framerate: int, rows: int, columns: int):
        arect = animation_rect.copy()

        for i in range(0, columns * arect.height, arect.height):
            for j in range(0, rows * arect.width, arect.width):
                frame_location = arect.x + j, arect.y + i

                if name not in self.animation_frames.keys():
                    self.animation_frames[name] = {"animation": [sheet.subsurface(frame_location, arect.size)],
                                                   "framerate": framerate}
                    continue

                self.animation_frames[name]["animation"] += [sheet.subsurface(frame_location, arect.size)]

    def get_updated_image(self) -> pygame.Surface:
        return pygame.transform.scale(self.animation_frames[self.a_data["name"]]["animation"][self.a_data["a_frame"]], self.resize_to)

    def change_animation(self, name: str):
        self.a_data = {"name": name, "a_frame": 0, "frame": self.animation_frames[name]["framerate"], "play": True}

    def control_animation(self, play=True):
        self.a_data["play"] = play

    def update(self):
        if not self.a_data["play"]:
            return

        if self.a_data["frame"] > 0:
            self.a_data["frame"] -= 1
            return

        self.a_data["a_frame"] = (self.a_data["a_frame"] + 1) % len(self.animation_frames[self.a_data["name"]]["animation"])
        self.image = self.get_updated_image()
        self.a_data["frame"] = self.animation_frames[self.a_data["name"]]["framerate"]


class COLCSprite(CSprite):
    def __init__(self, pos: tuple, size: tuple, collision_type: str, img_path: str, collision_img_path: str,
                 start_aname="", start_arect=pygame.Rect(0, 0, 1, 1), start_framerate=0, start_rows=1, start_columns=1,
                 relative_pos=(0, 0), colorkey=0):
        super().__init__([], pos, size, img_path,
                         start_aname, start_arect, start_framerate, start_rows, start_columns,
                         colorkey)

        self.collision_image = load_image(collision_img_path)
        self.mask = pygame.mask.from_surface(self.collision_image)

        self.collision_type = collision_type
        self.relative_pos = relative_pos


class Attack(COLCSprite):
    def __init__(self, relative_pos: tuple, size: tuple, collision_type: str, img_path: str, collision_img_path: str,
                 startup_frames: int, active_frames: int, recovery_frames: int,
                 damage: int, cooldown: int, applied_invincibility_frames: int,
                 start_aname="", start_arect=pygame.Rect(0, 0, 1, 1), start_framerate=0, start_rows=1, start_columns=1,
                 movable=True, colorkey=0):
        super().__init__((0, 0), size, collision_type, img_path, collision_img_path,
                         start_aname, start_arect, start_framerate, start_rows, start_columns,
                         relative_pos, colorkey)

        self.startup_frames = startup_frames
        self.active_frames = active_frames
        self.recovery_frames = recovery_frames

        self.damage = damage
        self.cooldown = cooldown
        self.applied_invincibility_frames = applied_invincibility_frames
        self.movable = movable

        self.counter = {"startup": self.startup_frames, "active": self.active_frames, "recovery": self.recovery_frames,
                        "cooldown": 0}
        self.pos_diff = (0, 0)

    def setup(self, pos: tuple):
        self.rect.center = pos

        self.counter = {"startup": self.startup_frames, "active": self.active_frames, "recovery": self.recovery_frames,
                        "cooldown": self.cooldown}

        self.pos_diff = self.rect.center[0] - pos[0], self.rect.center[1] - pos[1]

    def check_collision(self, with_what) -> bool:
        if self.collision_type == "rect" and with_what.collision_type == "rect":
            if self.rect.colliderect(with_what.rect):
                return True

        elif self.collision_type == "circle" and with_what.collision_type == "circle":
            if pygame.sprite.collide_circle(self, with_what):
                return True

        else:
            if self.rect.colliderect(with_what.rect):
                if pygame.sprite.collide_mask(self, with_what):
                    return True

        return False

    def attack_ended(self) -> bool:
        if self.counter["recovery"] <= 0 < self.counter["cooldown"]:
            return True
        return False


class OrbitAttack(Attack):
    def __init__(self, relative_to_pivot_pos: tuple, size: tuple, img_path: str, collision_img_path: str,
                 length: int, startup_frames: int, active_frames: int, recovery_frames: int,
                 damage: int, cooldown: int, applied_invincibility_frames: int,
                 start_aname="", start_arect=pygame.Rect(0, 0, 1, 1), start_framerate=0, start_rows=1, start_columns=1,
                 colorkey=0):
        super().__init__(relative_to_pivot_pos, size, "mask", img_path, collision_img_path,
                         startup_frames, active_frames, recovery_frames, damage, cooldown, applied_invincibility_frames,
                         start_aname, start_arect, start_framerate, start_rows, start_columns,
                         True, colorkey)

        self.length = length

    def setup_orbit(self, pivot_pos: tuple, target: tuple):
        super().setup(pivot_pos)

        self.collision_image, self.rect = get_rotated_around_pivot(self.orig_image, self.collision_image, self.rect.center, target, self.length)
        self.mask = pygame.mask.from_surface(self.collision_image)

        self.pos_diff = self.rect.center[0] - pivot_pos[0], self.rect.center[1] - pivot_pos[1]


class Projectile(COLCSprite):
    def __init__(self, start_pos: tuple, size: tuple, collision_type: str, img_path: str, collision_img_path: str,
                 direction: pygame.math.Vector2, speed_divided_by_fps: int, destroy_frames: int,
                 damage: int, applied_invincibility_frames: int, do_bounce=False, applied_hitstun_frames=0,
                 start_aname="", start_arect=pygame.Rect(0, 0, 1, 1), start_framerate=0, start_rows=1, start_columns=1,
                 colorkey=0):
        super().__init__(start_pos, size, collision_type, img_path, collision_img_path,
                         start_aname, start_arect, start_framerate, start_rows, start_columns,
                         colorkey=colorkey)

        self.dir = direction.normalize()
        self.speed = speed_divided_by_fps

        self.damage = damage
        self.applied_invincibility_frames = applied_invincibility_frames
        self.applied_hitstun_frames = applied_hitstun_frames  # not used in this file

        self.do_bounce = do_bounce
        self.counter = {"destroy": destroy_frames}

    def move(self):
        self.fpos += self.dir * self.speed
        self.rect.center = self.fpos

    def check_collision(self, with_what) -> bool:
        if self.collision_type == "rect" and with_what.collision_type == "rect":
            if self.rect.colliderect(with_what.rect):
                return True

        elif self.collision_type == "circle" and with_what.collision_type == "circle":
            if pygame.sprite.collide_circle(self, with_what):
                return True

        else:
            if self.rect.colliderect(with_what.rect):
                if pygame.sprite.collide_mask(self, with_what):
                    return True

        return False

    def bounce(self):
        angle = self.dir.as_polar()[1]
        self.dir.rotate_ip(-angle * 2)


class Part(CSprite):
    def __init__(self, groups: list, collide_with: list, pos: tuple, size: tuple, img_path: str,
                 start_aname: str, start_arect: pygame.Rect, start_framerate: int, start_rows: int, start_columns: int,
                 have_collision=False, collider_img_path="", collider_size=(0, 0), collider_pos=(0, 0), colorkey=0):
        super().__init__(groups, pos, size, img_path,
                         start_aname, start_arect, start_framerate, start_rows, start_columns,
                         colorkey)

        self.collide_with = collide_with.copy()
        self.collider = COLCSprite(pos, collider_size, "rect", collider_img_path, collider_img_path, relative_pos=collider_pos) if have_collision else None

    def update_collider(self):
        self.collider.rect.center = (self.rect.center[0] + self.collider.relative_pos[0],
                                     self.rect.center[1] + self.collider.relative_pos[1])

    def check_collisions(self):
        for group in self.collide_with:
            for sprite in group.sprites():
                if not sprite.collider:
                    return

                if self.collider.collision_type == "rect" and sprite.collider.collision_type == "rect":
                    if self.collider.rect.colliderect(sprite.collider.rect):
                        return True

                elif self.collider.collision_type == "circle" and sprite.collider.collision_type == "circle":
                    if pygame.sprite.collide_circle(self.collider, sprite.collider):
                        return True

                else:
                    if self.collider.rect.colliderect(sprite.collider.rect):
                        if pygame.sprite.collide_mask(self.collider, sprite.collider):
                            return True
        return False


class Entity(Part):
    def __init__(self, groups: list, collide_with: list, to_attack: list, pos: tuple, size: tuple, img_path: str,
                 start_aname: str, start_arect: pygame.Rect, start_framerate: int, start_rows: int, start_columns: int,
                 health: int, hurtbox_img_path: str, hurtbox_size: tuple,
                 have_collision=False, collider_img_path="", collider_size=(10, 20), collider_pos=(0, 0),
                 hurtbox_pos=(0, 0), colorkey=0):
        super().__init__(groups, collide_with, pos, size, img_path,
                         start_aname, start_arect, start_framerate, start_rows, start_columns,
                         have_collision, collider_img_path, collider_size, collider_pos, colorkey)

        self.frame = 0
        self.health = health

        self.to_attack = to_attack.copy()
        self.curr_attacks = []
        self.curr_projectiles = []

        self.hurtbox = COLCSprite(pos, hurtbox_size, "rect", hurtbox_img_path, hurtbox_img_path, relative_pos=hurtbox_pos)
        self.invincibility_counter = 0

    def take_damage(self, dmg: int):
        if self.invincibility_counter:
            return

        self.health -= dmg

        if self.health <= 0:
            self.kill()

    def make_attack(self, atk: Attack, target=(0, 0)):
        pos_to_pass = (self.rect.center[0] + atk.relative_pos[0], self.rect.center[1] + atk.relative_pos[1])

        if isinstance(atk, OrbitAttack):
            atk.setup_orbit(pos_to_pass, target)
        else:
            atk.setup(pos_to_pass)

        self.curr_attacks.append(atk)

    def spawn_projectile(self, proj: Projectile):
        self.curr_projectiles.append(proj)

    def check_attacks(self):
        collided_attacks = []

        for atk in self.curr_attacks:
            if atk.counter["startup"] > 0 or atk.counter["active"] <= 0:
                continue

            for group in self.to_attack:
                for sprite in group.sprites():
                    if atk.check_collision(sprite.hurtbox) and not sprite.invincibility_counter:
                        sprite.take_damage(atk.damage)
                        sprite.invincibility_counter = atk.applied_invincibility_frames
                        collided_attacks.append(atk)

        return collided_attacks[0] if collided_attacks else None

    def check_projectiles(self):
        collided_damage_projectiles = []

        for proj in self.curr_projectiles:
            proj.move()

            for group in self.collide_with:
                for sprite in group.sprites():
                    if not sprite.collider:
                        continue

                    if proj.check_collision(sprite.collider):
                        if proj.do_bounce:
                            proj.bounce()
                            continue

                        self.curr_projectiles.remove(proj)

        for proj in self.curr_projectiles:
            for group in self.to_attack:
                for sprite in group.sprites():
                    if proj.check_collision(sprite.hurtbox) and not sprite.invincibility_counter:
                        sprite.take_damage(proj.damage)
                        sprite.invincibility_counter = proj.applied_invincibility_frames
                        collided_damage_projectiles.append(proj)

        return collided_damage_projectiles[0] if collided_damage_projectiles else None

    def update_frames(self):
        for atk in self.curr_attacks:
            if atk.counter["startup"] > 0:
                atk.counter["startup"] -= 1
                continue

            if atk.counter["startup"] <= 0 < atk.counter["active"]:
                atk.counter["active"] -= 1
                continue

            if atk.counter["active"] <= 0 < atk.counter["recovery"]:
                atk.counter["recovery"] -= 1
                continue

            if atk.counter["recovery"] <= 0 < atk.counter["cooldown"]:
                atk.counter["cooldown"] -= 1
                continue

            if atk.counter["cooldown"] <= 0:
                self.curr_attacks.remove(atk)

        for proj in self.curr_projectiles:
            if proj.counter["destroy"] > 0:
                proj.counter["destroy"] -= 1
                continue

            self.curr_projectiles.remove(proj)

        if self.invincibility_counter > 0:
            self.invincibility_counter -= 1

        self.frame = self.frame + 1 if self.curr_attacks else 0

    def update_boxes(self):
        self.hurtbox.rect.center = (self.rect.center[0] + self.hurtbox.relative_pos[0],
                                    self.rect.center[1] + self.hurtbox.relative_pos[1])

        for atk in self.curr_attacks:
            if atk.movable:
                atk.rect.center = self.rect.center[0] + atk.pos_diff[0], self.rect.center[1] + atk.pos_diff[1]

    def update(self):
        super().update()

        self.update_frames()


class State:
    def enter(self, var):
        pass

    def run(self, parent) -> str:
        return ""

    def exit(self):
        pass


class StateMachine:
    def __init__(self, states: dict, start_state: str):
        self.states = states.copy()

        self.curr_state = states[start_state]
        self.curr_state.enter(None)

        self.nested_states_depth = 25

    def change_state(self, new_state_name: str, enter_var=None):
        self.curr_state.exit()
        self.curr_state = self.states[new_state_name]
        self.curr_state.enter(enter_var)

    def update_states(self, parent):
        for _ in range(self.nested_states_depth):
            if new_state := self.curr_state.run(parent):
                self.change_state(new_state)
            else:
                break
# endregion