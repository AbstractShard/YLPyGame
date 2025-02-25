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
    def run(self, parent) -> str:
        if to_movement():
            return "MOVE"

        if atk := to_attack(parent):
            return atk


class Move(basic.State):
    def __init__(self):
        super().__init__()

        self.SPEED = 60 / main.FPS

    def run(self, parent) -> str:
        move_dirs = [dir for bind, dir in MOVEMENT.items() if pygame.key.get_pressed()[bind]]

        if not move_dirs:
            return "IDLE"

        if atk := to_attack(parent):
            return atk

        try:
            move_vec = pygame.math.Vector2()
            for direction in move_dirs:
                move_vec += direction
            move_vec = move_vec.normalize() * self.SPEED

            parent.fpos += move_vec
            parent.rect.center = parent.fpos

            parent.update_collider()
            parent.update_boxes()

            if parent.check_collisions():
                parent.fpos -= move_vec
                parent.rect.center = parent.fpos

                parent.update_collider()
                parent.update_boxes()

        except ValueError:
            pass


class Hitstun(basic.State):
    def enter(self, var):
        self.hitstun_counter = var if var is not None else 0

    def run(self, parent) -> str:
        if self.hitstun_counter <= 0:
            return "IDLE"

        self.hitstun_counter -= 1


class LightAttack(basic.OrbitAttack, basic.State):
    def __init__(self):
        basic.OrbitAttack.__init__(self, (0, 0), (15, 15), "../Data/Player/Hitboxes/light_attack.png",
                                   15, 2, 1, 3, 25, 50, 50)
        basic.State.__init__(self)

    def run(self, parent) -> str:
        if self.attack_ended():
            return "IDLE"

        if self not in parent.curr_attacks:
            parent.make_attack(self, pygame.mouse.get_pos())
# endregion

class Player(basic.StateMachine, basic.Entity):
    def __init__(self, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(10, 20)):
        self.STATES = {"IDLE": Idle(), "MOVE": Move(), "HITSTUN": Hitstun(), "LIGHTATTACK": LightAttack()}

        basic.StateMachine.__init__(self, self.STATES, "IDLE")
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Player/main.png",
                              0, "", (0, 0), 1, 1,
                              200, "../Data/Player/hurtbox.png", (10, 20),
                              True, "../Data/Player/collider.png")

    def update(self):
        self.update_frames()

        if self.curr_attacks:
            self.check_attacks()

        self.update_states(self)