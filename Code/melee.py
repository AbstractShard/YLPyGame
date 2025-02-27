import pygame

import player
import basic
import main


class Move(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.SPEED = 65 / main.FPS

    def run(self) -> str:
        if basic.get_distance(self.parent.rect.center, self.parent.player.rect.center) <= 20:
            if not self.parent.STATES["SIMPLEATTACK"].counter["cooldown"]:
                return "SIMPLEATTACK"
            return ""

        try:
            move_vec = (pygame.math.Vector2(self.parent.player.rect.center) -
                        pygame.math.Vector2(self.parent.rect.center)).normalize() * self.SPEED

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


class SimpleAttack(basic.OrbitAttack, basic.State):
    def __init__(self, parent):
        basic.OrbitAttack.__init__(self, (0, 0), (15, 5),
                                   "../Data/Melee/Hitboxes/simple_attack.png", "../Data/Melee/Hitboxes/simple_attack.png",
                                   15, 15, 2, 5, 25, 100, 10)
        basic.State.__init__(self, parent)

        self.applied_hitstun_frames = 25

    def run(self) -> str:
        if self.attack_ended():
            return "MOVE"

        if self not in self.parent.curr_attacks:
            self.parent.make_attack(self, self.parent.player.rect.center)


class Melee(basic.StateMachine, basic.Entity):
    def __init__(self, player: player.Player, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(10, 20)):
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Melee/main.png",
                              "", pygame.Rect(0, 0, 10, 20), 0, 1, 1,
                              100, "../Data/Melee/hurtbox.png", (10, 20), True, "../Data/Melee/collider.png")

        self.STATES = {"MOVE": Move(self), "SIMPLEATTACK": SimpleAttack(self)}
        basic.StateMachine.__init__(self, self.STATES, "MOVE")

        self.player = player

    def update(self):
        basic.CSprite.update(self)

        self.update_frames()

        if self.curr_attacks:
            if atk := self.check_attacks():
                self.player.change_state("HITSTUN", atk.applied_hitstun_frames)

        self.update_states()