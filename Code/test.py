import pygame
import sys

import player
import melee
import distance
import basic

# MAIN
SIZE = WIDTH, HEIGHT = 800, 600
FPS = 60
CLOCK = pygame.time.Clock()

# GROUPS
PLAYER_GROUP = pygame.sprite.Group()
ENTITY_GROUP = pygame.sprite.Group()
ENVIRONMENT_GROUP = pygame.sprite.Group()
ROTATE_GROUP = pygame.sprite.Group()


class RotateSprite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(ROTATE_GROUP)

        self.orig_image = pygame.Surface((25, 25), pygame.SRCALPHA)
        self.image = self.orig_image
        self.image.fill("light blue")

        self.pivot = (150, 50)
        self.chain_lenght = 150
        self.offset = pygame.math.Vector2()
        self.offset.from_polar((self.chain_lenght, -0))
        self.angle = 0

        self.pos = self.pivot + self.offset
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        pygame.draw.line(SCREEN, "yellow", self.pivot, self.rect.center, 1)
        self.image, self.rect = basic.get_rotated_around_pivot(self.orig_image, self.image, self.pivot, pygame.mouse.get_pos(), self.chain_lenght)
        # mouse_offset = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.pivot)
        # mouse_angle = mouse_offset.as_polar()[1]
        # self.pos = self.pivot + self.offset.rotate(mouse_angle)
        # self.rect = self.image.get_rect(center=self.pos)
        #
        # self.image, self.rect = basic.get_rotated(self.orig_image, self.rect, -int(mouse_angle))

if __name__ == "__main__":
    pygame.display.set_caption("test")
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)

    PLAYER = player.Player([PLAYER_GROUP], [ENVIRONMENT_GROUP], [ENTITY_GROUP])
    WALL = basic.Part([ENVIRONMENT_GROUP], [], (50, 15), True)
    ROTATE_BLOCK = RotateSprite()
    MELEE = melee.Melee(PLAYER, [ENTITY_GROUP], [ENVIRONMENT_GROUP], [PLAYER_GROUP], (70, 70))
    DISTANCE = distance.Distance(PLAYER, [ENTITY_GROUP], [ENVIRONMENT_GROUP], [PLAYER_GROUP], (25, 150))

    # for i in range(50, 500, 25):
    #     distance.Distance(PLAYER, [ENTITY_GROUP], [ENVIRONMENT_GROUP], [PLAYER_GROUP], (i, 150))

    while True:
        SCREEN.fill("black")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill("black")

        PLAYER_GROUP.update()
        ENTITY_GROUP.update()

        ENVIRONMENT_GROUP.draw(SCREEN)
        PLAYER_GROUP.draw(SCREEN)
        ENTITY_GROUP.draw(SCREEN)
        ROTATE_GROUP.draw(SCREEN)

        ROTATE_GROUP.update()

        basic.draw_debug(SCREEN, [ENVIRONMENT_GROUP, PLAYER_GROUP, ENTITY_GROUP])
        pygame.draw.rect(SCREEN, "yellow", ROTATE_BLOCK.rect, 1)

        pygame.display.flip()
        CLOCK.tick(FPS)
    pygame.quit()