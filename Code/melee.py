import pygame
import random

import player
import basic
import main


class Move(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.SPEED = random.randint(122, 125) / main.FPS

    def run(self) -> str:
        if basic.get_distance(self.parent.rect.center, self.parent.player.rect.center) <= 40:
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
        basic.OrbitAttack.__init__(self, (0, 0), (30, 10),
                                   "../Data/Melee/Hitboxes/simple_attack_collision.png",
                                   (40, 20), "../Data/Melee/Hitboxes/simple_attack.png",
                                   30, 15, 2, 5, 25, 100, 10,
                                   "SIMPLEATTACK", pygame.Rect(0, 0, 20, 10), 0, 11, 2)
        basic.State.__init__(self, parent)

        self.applied_hitstun_frames = 25

        self.animation_rotation = 0
        self.display.control_animation(play=False)

    def get_animation_rotation(self) -> int:
        return int((pygame.math.Vector2(self.parent.player.rect.center) - pygame.math.Vector2(self.parent.rect.center)
                    ).as_polar()[1]) * -1

    def enter(self, var):
        self.display.change_animation("SIMPLEATTACK")

    def run(self) -> str:
        if self.attack_ended():
            return "MOVE"

        if self not in self.parent.curr_attacks:
            self.parent.make_attack(self, self.parent.player.rect.center)
            self.animation_rotation = self.get_animation_rotation()

        basic.CSprite.update(self.display, self.animation_rotation)


class Melee(basic.StateMachine, basic.Entity):
    def __init__(self, player: player.Player, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(20, 40)):
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Melee/main.png",
                              "MOVE", pygame.Rect(0, 0, 10, 20), 5, 8, 2,
                              100, "../Data/Melee/hurtbox.png", (20, 40),
                              True, "../Data/Melee/collider.png", (20, 40))

        self.STATES = {"MOVE": Move(self), "SIMPLEATTACK": SimpleAttack(self)}
        self.player = player

        basic.StateMachine.__init__(self, self.STATES, "MOVE")

        self.control_animation(cycle=True)

    def update(self, image_rotated_by_angle=0):
        basic.CSprite.update(self, image_rotated_by_angle)

        self.update_frames()

        if self.curr_attacks:
            if atk := self.check_attacks():
                self.player.change_state("HITSTUN", atk.applied_hitstun_frames)

        self.update_states()