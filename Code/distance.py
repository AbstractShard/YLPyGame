import pygame
import random

import player
import basic
import main

# movement
SPEED = 45 / main.FPS


class Move(basic.State):
    def enter(self, var):
        self.move_angle = random.randint(-45, 45)

    def run(self, parent) -> str:
        if basic.get_distance(parent.rect.center, parent.player.rect.center) >= 70:
            return "SIMPLEPROJECTILE"

        try:
            move_vec = ((pygame.math.Vector2(parent.player.rect.center) -
                        pygame.math.Vector2(parent.rect.center)).normalize() * SPEED * -1).rotate(self.move_angle)

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


class SimpleProjectile(basic.State):
    def __init__(self):
        super().__init__()

        self.reload_frames = 100
        self.counter = {"reload": self.reload_frames}

    def run(self, parent) -> str:
        if basic.get_distance(parent.rect.center, parent.player.rect.center) <= 70:
            return "MOVE"

        if self.counter["reload"]:
            self.counter["reload"] -= 1
            return ""

        proj = basic.Projectile(parent.rect.center, (5, 5), "circle",
                                pygame.math.Vector2(parent.player.rect.center) - pygame.math.Vector2(parent.rect.center),
                                150, 500, 15, 10, True, 50)

        parent.spawn_projectile(proj)
        self.counter["reload"] = self.reload_frames


STATES = {"MOVE": Move(), "SIMPLEPROJECTILE": SimpleProjectile()}


class Distance(basic.StateMachine, basic.Entity):
    def __init__(self, player: player.Player, groups: list, collide_with: list, to_attack: list, pos=(0, 0)):
        basic.StateMachine.__init__(self, STATES, "MOVE")
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, 50, (10, 20), True)

        self.setup_basics(pos, tsize=(10, 20), tcolor="purple")

        self.player = player

    def update(self):
        self.update_frames()

        if self.curr_projectiles:
            if proj := self.check_projectiles():
                self.player.change_state("HITSTUN", proj.applied_hitstun_frames)

        self.update_states(self)