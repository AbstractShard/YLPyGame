import pygame
import basic

KEYBOARD = {"UP": pygame.K_w, "RIGHT": pygame.K_d, "DOWN": pygame.K_s, "LEFT": pygame.K_a}
MOUSE = {"LEFT": 0, "MIDDLE": 1, "RIGHT": 2}

ATTACK_BINDS = {("m", 0): "TestAttack"}
SIMULT_ATTACKS = 1

# region FUNCTIONS
def check_move() -> str:
    for key in KEYBOARD.values():
        if pygame.key.get_pressed()[key]:
            return "Move"
    return ""

def check_attacks() -> str:
    for bind_type, value in ATTACK_BINDS.keys():
        if (bind_type == "k" and pygame.key.get_pressed()[value]) or (bind_type == "m" and pygame.mouse.get_pressed()[value]):
            state = STATES[ATTACK_BINDS[(bind_type, value)]]

            if not state.ATTACK.counter["cooldown"] or state.ATTACK.counter["cooldown"] == state.ATTACK.cooldown:
                return state.__class__.__name__
    return ""
# endregion

# region STATES
class Idle(basic.State):
    def run(self, parent) -> str:
        if move := check_move():
            return move

        if atk := check_attacks():
            return atk

        return ""


class Move(basic.State):
    def __init__(self):
        self.MOVE_DIRS = {"UP": (0, -1), "RIGHT": (1, 0), "DOWN": (0, 1), "LEFT": (-1, 0)}
        self.SPEED = 1

    def run(self, parent) -> str:
        move_keys = [key for key, value in KEYBOARD.items() if pygame.key.get_pressed()[value]]

        if not move_keys:
            return "Idle"

        if atk := check_attacks():
            return atk

        for key in move_keys:
            move_vec = pygame.math.Vector2(self.MOVE_DIRS[key]).normalize() * self.SPEED

            parent.rect.move_ip(move_vec)
            parent.update_collider()
            parent.update_boxes()

            if parent.check_collisions():
                parent.rect.move_ip(-move_vec)
                parent.update_collider()
                parent.update_boxes()

        return ""


class TestAttack(basic.State):
    def __init__(self):
        self.ATTACK = basic.Attack((25, 5), (25, 5), "rect", 15, 25, 50, 50)

    def run(self, parent) -> str:
        if self.ATTACK.counter["frames"] <= 0 < self.ATTACK.counter["cooldown"]:
            return "Idle"

        if len(parent.curr_attacks) < SIMULT_ATTACKS and self.ATTACK not in parent.curr_attacks:
            parent.make_attack(self.ATTACK)
# endregion


STATES = {"Idle": Idle(), "Move": Move(), "TestAttack": TestAttack()}


class Player(basic.StateMachine, basic.Entity):
    def __init__(self, groups: list, collide_with: list, to_attack: list, pos=(0, 0)):
        basic.StateMachine.__init__(self, STATES, "Idle")
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, 100, (10, 20), True)

        self.setup_basics(pos, tsize=(10, 20), tcolor="red")

    def update(self):
        self.update_frames()

        if self.curr_attacks:
            self.check_attacks()

        self.update_states(self)