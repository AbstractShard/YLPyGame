import pygame

import basic
import main

MOVEMENT = {pygame.K_w: (0, -1), pygame.K_d: (1, 0), pygame.K_s: (0, 1), pygame.K_a: (-1, 0)}
ATTACKS = {("MOUSE", 0): "LIGHTATTACK"}


# region FUNCTIONS
def to_movement() -> bool:
    for bind in MOVEMENT.keys():
        if pygame.key.get_pressed()[bind]:
            return True
    return False

def to_attack(parent) -> str:
    for bind_type, bind in ATTACKS.keys():
        if (bind_type == "KEYBOARD" and pygame.key.get_pressed()[bind]) or (bind_type == "MOUSE" and pygame.mouse.get_pressed()[bind]):
            atk = parent.STATES[ATTACKS[(bind_type, bind)]]

            if not atk.counter["cooldown"]:
                return atk.__class__.__name__.upper()
    return ""
# endregion

# region STATES
class Idle(basic.State):
    def enter(self, var):
        self.parent.change_animation("IDLE")
        self.parent.control_animation(cycle=True)

    def run(self) -> str:
        if to_movement():
            return "MOVE"

        if atk := to_attack(self.parent):
            return atk


class Move(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.SPEED = 60 / main.FPS

    def run(self) -> str:
        move_dirs = [dir for bind, dir in MOVEMENT.items() if pygame.key.get_pressed()[bind]]

        if not move_dirs:
            return "IDLE"

        if atk := to_attack(self.parent):
            return atk

        try:
            move_vec = pygame.math.Vector2()
            for direction in move_dirs:
                move_vec += direction
            move_vec = move_vec.normalize() * self.SPEED

            self.parent.fpos += move_vec
            self.parent.rect.center = self.parent.fpos

            self.parent.update_collider()
            self.parent.update_boxes()

            if self.parent.check_collisions():
                self.parent.fpos -= move_vec
                self.parent.rect.center = self.parent.fpos

                self.parent.update_collider()
                self.parent.update_boxes()

        except ValueError:
            pass


class Hitstun(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent.add_animation("HITSTUN", self.parent.orig_image, pygame.Rect(0, 20, 10, 20), 3, 5, 1)

    def enter(self, var):
        self.hitstun_counter = var if var is not None else 0
        self.parent.change_animation("HITSTUN")

    def run(self) -> str:
        if self.hitstun_counter <= 0:
            return "IDLE"

        self.hitstun_counter -= 1


class LightAttack(basic.OrbitAttack, basic.State):
    def __init__(self, parent):
        basic.OrbitAttack.__init__(self, (0, 0), (15, 15),
                                   "../Data/Player/Hitboxes/light_attack.png", "../Data/Player/Hitboxes/light_attack.png",
                                   15, 2, 1, 3, 25, 50, 50)
        basic.State.__init__(self, parent)

    def run(self) -> str:
        if self.attack_ended():
            return "IDLE"

        if self not in self.parent.curr_attacks:
            self.parent.make_attack(self, pygame.mouse.get_pos())
# endregion

class Player(basic.StateMachine, basic.Entity):
    def __init__(self, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(10, 20)):
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Player/main.png",
                              "IDLE", pygame.Rect(0, 0, 10, 20), 7, 20, 1,
                              200, "../Data/Player/hurtbox.png", (10, 20),
                              True, "../Data/Player/collider.png")

        self.STATES = {"IDLE": Idle(self), "MOVE": Move(self), "HITSTUN": Hitstun(self), "LIGHTATTACK": LightAttack(self)}
        basic.StateMachine.__init__(self, self.STATES, "IDLE")

        self.control_animation(cycle=True)

    def update(self):
        basic.CSprite.update(self)

        self.update_frames()

        if self.curr_attacks:
            self.check_attacks()

        self.update_states()