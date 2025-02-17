import pygame
import os

# region FUNCTIONS
def load_image(name: str, colorkey=0):
    fullname = os.path.join("Data", name)

    if not os.path.isfile(fullname):
        print("no such file had been found.")
        return

    image = pygame.image.load(fullname)

    if colorkey:
        image = image.convert()

        if colorkey == -1:
            colorkey = image.get_at((0, 0))

        image.set_colorkey(colorkey)
        return image

    image = image.convert_alpha()
    return image


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
                    atk_image = pygame.Surface(atk.rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(atk_image, "red" if atk.counter["frames"] else "white", (0, 0, *atk.rect.size), 1)

                    screen.blit(atk_image, atk.rect.topleft)
# endregion

# region CLASSES
class CSprite(pygame.sprite.Sprite):
    def __init__(self, start_pos: tuple, size: tuple, collision_type: str, relative_pos=None):
        super().__init__()

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill("white")

        self.rect = pygame.Rect(start_pos, self.image.get_rect().size)
        self.mask = pygame.mask.from_surface(self.image)

        self.collision_type = collision_type
        self.relative_pos = relative_pos if relative_pos else (0, 0)


class Attack(CSprite):
    def __init__(self, relative_pos: tuple, size: tuple, collision_type: str, active_frames: int, damage: int,
                 cooldown: int, applied_invincibility_frames: int, movable=True):
        super().__init__((0, 0), size, collision_type, relative_pos)

        self.active_frames = active_frames
        self.damage = damage
        self.cooldown = cooldown
        self.applied_invincibility_frames = applied_invincibility_frames
        self.movable = movable

        self.counter = {"frames": self.active_frames,
                        "cooldown": self.cooldown}

    def setup(self, pos: tuple):
        self.rect.x, self.rect.y = pos

        self.counter = {"frames": self.active_frames,
                        "cooldown": self.cooldown}


class Part(pygame.sprite.Sprite):
    def __init__(self, groups: list, collide_with: list, pos: tuple,
                 have_collision=False, collider_size=(50, 50), collider_pos=None):
        super().__init__(*groups)

        # basics
        self.image = None
        self.rect = None

        # collision
        self.collide_with = collide_with.copy()
        self.collider = CSprite(pos, collider_size, "rect", collider_pos) if have_collision else None

        # for testing
        if self.__class__ == Part:
            self.setup_basics(pos)

    def setup_basics(self, pos: tuple, img_name="", colorkey=0, tsize=(50, 50), tcolor="grey"):
        if img_name:
            self.image = load_image(img_name, colorkey)
        else:
            self.image = pygame.Surface(tsize, pygame.SRCALPHA)
            self.image.fill(tcolor)

        self.rect = pygame.Rect(pos, self.image.get_rect().size)

    def update_collider(self, update_mask=False):
        self.collider.rect.x = self.rect.x + self.collider.relative_pos[0]
        self.collider.rect.y = self.rect.y + self.collider.relative_pos[1]

        if update_mask:
            self.collider.mask = pygame.mask.from_surface(self.collider.image)

    def check_collisions(self) -> bool:
        for group in self.collide_with:
            for sprite in group.sprites():
                if not sprite.collider:
                    continue

                if self.collider.collision_type == "rect" and sprite.collider.collision_type == "rect":
                    if self.collider.rect.colliderect(sprite.collider.rect):
                        return True

                elif self.collider.collision_type == "circle" and sprite.collider.collision_type == "circle":
                    if pygame.sprite.collide_circle(self.collider, sprite.collider):
                        return True

                else:
                    if self.rect.colliderect(sprite.rect):
                        if pygame.sprite.collide_mask(self.collider, sprite.collider):
                            return True
        return False


class Entity(Part):
    def __init__(self, groups: list, collide_with: list, to_attack: list, pos: tuple, health: int, hurtbox_size: tuple,
                 have_collision=False, collider_size=(10, 20), collider_pos=None, hurtbox_pos=None):
        super().__init__(groups, collide_with, pos, have_collision, collider_size, collider_pos)

        self.frame = 0
        self.health = health

        self.to_attack = to_attack.copy()
        self.curr_attacks = []

        self.hurtbox = CSprite(pos, hurtbox_size, "rect", hurtbox_pos)
        self.invincibility_counter = 0

        # for testing
        if self.__class__ == Entity:
            self.setup_basics(pos, tsize=(10, 20), tcolor="green")

    def take_damage(self, dmg: int):
        if self.invincibility_counter:
            return

        self.health -= dmg

        if self.health <= 0:
            self.kill()

    def make_attack(self, atk: Attack):
        atk.setup((self.rect.x + atk.relative_pos[0], self.rect.y + atk.relative_pos[1]))
        self.curr_attacks.append(atk)

    def check_attacks(self):
        for atk in self.curr_attacks:
            if atk.counter["frames"] <= 0:
                continue

            for group in self.to_attack:
                for sprite in group.sprites():
                    if atk.collision_type == "rect" and sprite.hurtbox.collision_type == "rect":
                        if atk.rect.colliderect(sprite.hurtbox.rect):
                            if not sprite.invincibility_counter:
                                sprite.take_damage(atk.damage)
                                sprite.invincibility_counter = atk.applied_invincibility_frames

                    elif atk.collision_type == "circle" and sprite.hurtbox.collision_type == "circle":
                        if pygame.sprite.collide_circle(atk, sprite.hurtbox):
                            if not sprite.invincibility_counter:
                                sprite.take_damage(atk.damage)
                                sprite.invincibility_counter = atk.applied_invincibility_frames

                    else:
                        if atk.rect.colliderect(sprite.rect):
                            if pygame.sprite.collide_mask(atk, sprite.hurtbox):
                                if not sprite.invincibility_counter:
                                    sprite.take_damage(atk.damage)
                                    sprite.invincibility_counter = atk.applied_invincibility_frames

    def update_frames(self):
        for atk in self.curr_attacks:
            if atk.counter["frames"] > 0:
                atk.counter["frames"] -= 1

            if atk.counter["frames"] <= 0 < atk.counter["cooldown"]:
                atk.counter["cooldown"] -= 1

            if atk.counter["cooldown"] <= 0:
                self.curr_attacks.remove(atk)

        if self.invincibility_counter > 0:
            self.invincibility_counter -= 1

        self.frame = self.frame + 1 if self.curr_attacks else 0

    def update_boxes(self):
        self.hurtbox.rect.x = self.rect.x + self.hurtbox.relative_pos[0]
        self.hurtbox.rect.y = self.rect.y + self.hurtbox.relative_pos[1]

        for atk in self.curr_attacks:
            if atk.movable:
                atk.rect.x = self.rect.x + atk.relative_pos[0]
                atk.rect.y = self.rect.y + atk.relative_pos[1]

    def update(self):
        self.update_frames()


class State:
    def enter(self):
        pass

    def run(self, parent) -> str:
        return ""

    def exit(self):
        pass


class StateMachine:
    def __init__(self, states: dict, start_state: str):
        self.states = states.copy()
        self.curr_state = states[start_state]
        self.nested_states_depth = 25

    def change_state(self, new_state_name: str):
        self.curr_state.exit()
        self.curr_state = self.states[new_state_name]
        self.curr_state.enter()

    def update_states(self, parent):
        for _ in range(self.nested_states_depth):
            if new_state := self.curr_state.run(parent):
                self.change_state(new_state)
            else:
                break
# endregion