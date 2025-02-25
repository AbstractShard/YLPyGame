import pygame

import level

# MAIN
SIZE = WIDTH, HEIGHT = 800, 600
FPS = 60
CLOCK = pygame.time.Clock()

# class RotateSprite(pygame.sprite.Sprite):
#     def __init__(self):
#         super().__init__(ROTATE_GROUP)
#
#         self.orig_image = pygame.Surface((25, 25), pygame.SRCALPHA)
#         self.image = self.orig_image
#         self.image.fill("light blue")
#
#         self.pivot = (150, 50)
#         self.chain_lenght = 150
#         self.offset = pygame.math.Vector2()
#         self.offset.from_polar((self.chain_lenght, -0))
#         self.angle = 0
#
#         self.pos = self.pivot + self.offset
#         self.rect = self.image.get_rect(center=self.pos)
#
#     def update(self):
#         pygame.draw.line(SCREEN, "yellow", self.pivot, self.rect.center, 1)
#         self.image, self.rect = basic.get_rotated_around_pivot(self.orig_image, self.image, self.pivot, pygame.mouse.get_pos(), self.chain_lenght)
#         # mouse_offset = pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(self.pivot)
#         # mouse_angle = mouse_offset.as_polar()[1]
#         # self.pos = self.pivot + self.offset.rotate(mouse_angle)
#         # self.rect = self.image.get_rect(center=self.pos)
#         #
#         # self.image, self.rect = basic.get_rotated(self.orig_image, self.rect, -int(mouse_angle))

if __name__ == "__main__":
    pygame.display.set_caption("test")
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)

    TEST_LEVEL = level.TestLevel()

    # test_group = pygame.sprite.Group()
    #
    # Test = basic.Part([test_group], [], (400, 300), (150, 150), "C:/Users/Богдан/Desktop/Projects/data/dragon.png",
    #                   5, "IDLE", (0, 0), 2, 8, True, "C:/Users/Богдан/Desktop/Projects/data/dragon.png", collider_size=(150, 150))

    # import player
    # player_group = pygame.sprite.Group()
    #
    # player = player.Player([player_group], [test_group], [])

    # PLAYER = player.Player([PLAYER_GROUP], [ENVIRONMENT_GROUP], [ENTITY_GROUP])
    # WALL = basic.Part([ENVIRONMENT_GROUP], [], (50, 15), True)
    # ROTATE_BLOCK = RotateSprite()
    # MELEE = melee.Melee(PLAYER, [ENTITY_GROUP], [ENVIRONMENT_GROUP], [PLAYER_GROUP], (70, 70))
    # DISTANCE = distance.Distance(PLAYER, [ENTITY_GROUP], [ENVIRONMENT_GROUP], [PLAYER_GROUP], (25, 150))
    # for i in range(50, 500, 25):
    #     distance.Distance(PLAYER, [ENTITY_GROUP], [ENVIRONMENT_GROUP], [PLAYER_GROUP], (i, 150))

    while True:
        TEST_LEVEL.run(SCREEN)
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         import sys
        #         pygame.quit()
        #         sys.exit()

        # SCREEN.fill("black")

        # player_group.update()
        # test_group.update()
        #
        # test_group.draw(SCREEN)
        # player_group.draw(SCREEN)

        # basic.draw_debug(SCREEN, [test_group, player_group])

        pygame.display.flip()
        CLOCK.tick(FPS)
    pygame.quit()