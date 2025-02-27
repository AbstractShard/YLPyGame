import pygame
import random

import player
import basic
import main


class Move(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.SPEED = 25 / main.FPS

    def enter(self, var):
        self.move_angle = random.randint(-45, 45)

    def run(self) -> str:
        if basic.get_distance(self.parent.rect.center, self.parent.player.rect.center) >= 70:
            return "SIMPLEPROJECTILE"

        try:
            move_vec = ((pygame.math.Vector2(self.parent.player.rect.center) -
                        pygame.math.Vector2(self.parent.rect.center)).normalize() * self.SPEED * -1).rotate(self.move_angle)

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


class SimpleProjectile(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.reload_frames = 100
        self.counter = {"reload": self.reload_frames}

    def run(self) -> str:
        if basic.get_distance(self.parent.rect.center, self.parent.player.rect.center) <= 70:
            return "MOVE"

        if self.counter["reload"]:
            self.counter["reload"] -= 1
            return ""

        proj = basic.Projectile(self.parent.rect.center, (7, 7), "circle",
                                "../Data/Distance/Hitboxes/simple_projectile.png", "../Data/Distance/Hitboxes/simple_projectile.png",
                                pygame.math.Vector2(self.parent.player.rect.center) - pygame.math.Vector2(self.parent.rect.center),
                                150 / main.FPS, 500, 15, 10, True, 50)

        self.parent.spawn_projectile(proj)
        self.counter["reload"] = self.reload_frames


class Distance(basic.StateMachine, basic.Entity):
    def __init__(self, player: player.Player, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(10, 20)):
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Distance/main.png",
                              "", pygame.Rect(0, 0, 10, 20), 0, 1, 1,
                              75, "../Data/Distance/hurtbox.png", (10, 20), True, "../Data/Distance/collider.png")

        self.STATES = {"MOVE": Move(self), "SIMPLEPROJECTILE": SimpleProjectile(self)}
        basic.StateMachine.__init__(self, self.STATES, "MOVE")

        self.player = player

    def update(self):
        basic.CSprite.update(self)

        self.update_frames()

        if self.curr_projectiles:
            if proj := self.check_projectiles():
                self.player.change_state("HITSTUN", proj.applied_hitstun_frames)

        self.update_states()