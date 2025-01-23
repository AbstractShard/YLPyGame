import pygame
import os


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


class CSprite(pygame.sprite.Sprite):
    def __init__(self, pos: tuple, size: tuple, collision_type: str):
        super().__init__()

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill("white")

        self.rect = pygame.Rect(pos, self.image.get_rect().size)
        self.mask = pygame.mask.from_surface(self.image)

        self.collision_type = collision_type


class Attack(CSprite):
    def __init__(self, pos: tuple, size: tuple, collision_type: str, frame_time: int, damage: int, cooldown: int, movable=True):
        super().__init__(pos, size, collision_type)

        self.frame_time = frame_time
        self.damage = damage
        self.cooldown = cooldown
        self.movable = movable

        self.can_attack = True
        self.relative_pos = pos
        self.exit_frame = 0
        self.counter = self.cooldown

    def setup(self, move_pos: tuple, exit_frame: int):
        self.rect.x, self.rect.y = move_pos

        self.can_attack = True
        self.exit_frame = exit_frame
        self.counter = self.cooldown


class Part(pygame.sprite.Sprite):
    def __init__(self, groups: list, collide_with: list, pos: tuple, have_collision=False, collider_size=(50, 50)):
        super().__init__(*groups)

        # basics
        self.image = None
        self.rect = None

        # collision
        self.collide_with = collide_with.copy()
        self.collider = CSprite(pos, collider_size, "rect") if have_collision else None

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
        self.collider.rect.move_ip(self.rect.x - self.collider.rect.x, self.rect.y - self.collider.rect.y)
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
    def __init__(self, groups: list, collide_with: list, to_attack: list, pos: tuple, health: int, hurtbox_size: tuple, have_collision=False, collider_size=(10, 20)):
        super().__init__(groups, collide_with, pos, have_collision, collider_size)

        self.frame = 0
        self.health = health

        self.to_attack = to_attack.copy()
        self.curr_attacks = []

        self.hurtbox = CSprite(pos, hurtbox_size, "rect")

        # for testing
        if self.__class__ == Entity:
            self.setup_basics(pos, tsize=(10, 20), tcolor="green")

    def take_damage(self, dmg: int):
        self.health -= dmg

        if self.health <= 0:
            self.kill()

    def make_attack(self, atk: Attack):
        atk.setup((self.rect.x + atk.relative_pos[0], self.rect.y + atk.relative_pos[1]), self.frame + atk.frame_time)
        self.curr_attacks.append(atk)

    def check_attacks(self):
        for atk in self.curr_attacks:

            is_hit = False

            for group in self.to_attack:
                for sprite in group.sprites():
                    if not atk.can_attack:
                        continue

                    if atk.collision_type == "rect" and sprite.hurtbox.collision_type == "rect":
                        if atk.rect.colliderect(sprite.hurtbox.rect):
                            sprite.take_damage(atk.damage)
                            is_hit = True

                    elif atk.collision_type == "circle" and sprite.hurtbox.collision_type == "circle":
                        if pygame.sprite.collide_circle(atk, sprite.hurtbox):
                            sprite.take_damage(atk.damage)
                            is_hit = True

                    else:
                        if atk.rect.colliderect(sprite.rect):
                            if pygame.sprite.collide_mask(atk, sprite.hurtbox):
                                sprite.take_damage(atk.damage)
                                is_hit = True

            if is_hit:
                atk.can_attack = False

    def update_frames(self):
        for atk in self.curr_attacks:
            if atk.exit_frame == self.frame:
                atk.can_attack = False
                continue

            if not atk.can_attack:
                atk.counter -= 1

            if atk.counter <= 0:
                self.curr_attacks.remove(atk)

        self.frame = self.frame + 1 if self.curr_attacks else 0

    def update_boxes(self):
        self.hurtbox.rect.move_ip(self.rect.x - self.hurtbox.rect.x, self.rect.y - self.hurtbox.rect.y)

        for atk in self.curr_attacks:
            if atk.movable:
                atk.rect.move_ip(self.rect.x - atk.rect.x, self.rect.y - atk.rect.y)


class Player(Entity):
    def __init__(self, groups: list, collide_with: list, to_attack: list):
        super().__init__(groups, collide_with, to_attack, (0, 0), 100, (10, 20), True, (10, 20))

        # part
        self.setup_basics((0, 0), tsize=(10, 20), tcolor="red")

        # binds
        self.keyboard = {"UP": pygame.K_w, "RIGHT": pygame.K_d, "DOWN": pygame.K_s, "LEFT": pygame.K_a}
        self.mouse = {"LEFT": 0, "MIDDLE": 1, "RIGHT": 2}

        # movement
        self.move_dirs = {"UP": (0, -1), "RIGHT": (1, 0), "DOWN": (0, 1), "LEFT": (-1, 0)}
        self.speed = 1

        # attack
        TEST_ATTACK = Attack((25, 5), (25, 5), "rect", 15, 25, 1000)

        self.attack_binds = {"LEFT": TEST_ATTACK, "MIDDLE": None, "RIGHT": None}
        self.simult_attacks = 1

    def movement(self):
        for key, value in self.keyboard.items():
            if pygame.key.get_pressed()[value]:
                move_vec = pygame.math.Vector2(self.move_dirs[key]).normalize() * self.speed

                self.rect.move_ip(move_vec)
                self.update_collider()
                self.update_boxes()

                if self.check_collisions():
                    self.rect.move_ip(-move_vec)
                    self.update_collider()
                    self.update_boxes()

    def attack(self):
        self.update_frames()

        if self.curr_attacks:
            self.check_attacks()

        for key, value in self.mouse.items():
            if pygame.mouse.get_pressed()[value] and self.attack_binds[key]:
                if len(self.curr_attacks) < self.simult_attacks and self.attack_binds[key] not in self.curr_attacks:
                    self.make_attack(self.attack_binds[key])