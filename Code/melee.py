import pygame

import player
import basic
import main


class Move(basic.State):
    def __init__(self):
        super().__init__()

        self.SPEED = 65 / main.FPS

    def run(self, parent) -> str:
        if basic.get_distance(parent.rect.center, parent.player.rect.center) <= 20:
            if not parent.STATES["SIMPLEATTACK"].counter["cooldown"]:
                return "SIMPLEATTACK"
            return ""

        try:
            move_vec = (pygame.math.Vector2(parent.player.rect.center) -
                        pygame.math.Vector2(parent.rect.center)).normalize() * self.SPEED

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


class SimpleAttack(basic.OrbitAttack, basic.State):
    def __init__(self):
        basic.OrbitAttack.__init__(self, (0, 0), (15, 5),
                                   "../Data/Melee/Hitboxes/simple_attack.png", "../Data/Melee/Hitboxes/simple_attack.png",
                                   15, 15, 2, 5, 25, 100, 10)
        basic.State.__init__(self)

        self.applied_hitstun_frames = 25

    def run(self, parent) -> str:
        if self.attack_ended():
            return "MOVE"

        if self not in parent.curr_attacks:
            parent.make_attack(self, parent.player.rect.center)


class Melee(basic.StateMachine, basic.Entity):
    def __init__(self, player: player.Player, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(10, 20)):
        self.STATES = {"MOVE": Move(), "SIMPLEATTACK": SimpleAttack()}

        basic.StateMachine.__init__(self, self.STATES, "MOVE")
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Melee/main.png",
                              "", pygame.Rect(0, 0, 10, 20), 0, 1, 1,
                              100, "../Data/Melee/hurtbox.png", (10, 20), True, "../Data/Melee/collider.png")

        self.player = player

    def update(self):
        basic.CSprite.update(self)

        self.update_frames()

        if self.curr_attacks:
            if atk := self.check_attacks():
                self.player.change_state("HITSTUN", atk.applied_hitstun_frames)

        self.update_states(self)