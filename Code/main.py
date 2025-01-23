import pygame
import sys

import basic

# consts
SIZE = WIDTH, HEIGHT = 800, 600
FPS = 60
CLOCK = pygame.time.Clock()

# groups
PLAYER_GROUP = pygame.sprite.Group()
ENTITY_GROUP = pygame.sprite.Group()
ENVIRONMENT_GROUP = pygame.sprite.Group()

if __name__ == "__main__":
    pygame.display.set_caption("test")
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)

    # testing
    PLAYER = basic.Player([PLAYER_GROUP], [ENVIRONMENT_GROUP, ENTITY_GROUP], [ENTITY_GROUP])
    WALL = basic.Part([ENVIRONMENT_GROUP], [], (50, 15), True)
    ENTITY = basic.Entity([ENTITY_GROUP], [], [], (15, 100), 100, (10, 20), True, (10, 20))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill("black")

        PLAYER.movement()
        PLAYER.attack()

        ENVIRONMENT_GROUP.draw(SCREEN)
        ENTITY_GROUP.draw(SCREEN)
        PLAYER_GROUP.draw(SCREEN)

        pygame.display.flip()
        CLOCK.tick(FPS)
    pygame.quit()