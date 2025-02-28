import pygame
import random

import player
import basic
import main


class Move(basic.State):
    def __init__(self, parent):
        super().__init__(parent)

        self.SPEED = 50 / main.FPS

        self.parent.add_animation("MOVE", self.parent.orig_image, pygame.Rect(0, 20, 10, 20), 3, 3, 1)

    def enter(self, var):
        self.move_angle = random.randint(-45, 45)
        self.parent.change_animation("MOVE")

    def run(self) -> str:
        if basic.get_distance(self.parent.rect.center, self.parent.player.rect.center) > 100:
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

    def enter(self, var):
        self.parent.change_animation("MOVE", reverse=True)

    def run(self) -> str:
        if self.parent.a_data["name"] == "MOVE" and self.parent.a_data["ended"]:
            self.parent.change_animation("SIMPLEPROJECTILE", cycle=True)

        if basic.get_distance(self.parent.rect.center, self.parent.player.rect.center) <= 100:
            return "MOVE"

        if self.counter["reload"]:
            self.counter["reload"] -= 1
            return ""

        proj = basic.Projectile(self.parent.rect.center, (14, 14), "circle",
                                "../Data/Distance/Hitboxes/simple_projectile.png",
                                (14, 14), "../Data/Distance/Hitboxes/simple_projectile.png",
                                pygame.math.Vector2(self.parent.player.rect.center) - pygame.math.Vector2(self.parent.rect.center),
                                150 / main.FPS, 500, 15, 10, True, 50,
                                "SIMPLEPROJECTILE", pygame.Rect(0, 0, 14, 14), 3, 3, 1)
        proj.display.control_animation(cycle=True)

        self.parent.spawn_projectile(proj)
        self.counter["reload"] = self.reload_frames


class Distance(basic.StateMachine, basic.Entity):
    def __init__(self, player: player.Player, groups: list, collide_with: list, to_attack: list, pos=(0, 0), size=(20, 40)):
        basic.Entity.__init__(self, groups, collide_with, to_attack, pos, size, "../Data/Distance/main.png",
                              "SIMPLEPROJECTILE", pygame.Rect(0, 0, 10, 20), 7, 8, 1,
                              75, "../Data/Distance/hurtbox.png", (20, 40),
                              True, "../Data/Distance/collider.png", (20, 40))

        self.STATES = {"MOVE": Move(self), "SIMPLEPROJECTILE": SimpleProjectile(self)}
        self.player = player

        basic.StateMachine.__init__(self, self.STATES, "MOVE")

        self.control_animation(cycle=True)

    def update(self, image_rotated_by_angle=0):
        basic.CSprite.update(self, image_rotated_by_angle)

        self.update_frames()

        if self.curr_projectiles:
            if proj := self.check_projectiles():
                self.player.change_state("HITSTUN", proj.applied_hitstun_frames)

        self.update_states()

        for proj in self.curr_projectiles:
            basic.CSprite.update(proj.display)