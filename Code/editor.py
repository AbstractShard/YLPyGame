import pygame
import time
import sys
import os

import level
import basic


class EditorLevel(level.Level):
    def __init__(self):
        super().__init__(LEVEL_PATH)

        self.prev_mtime = time.ctime(os.path.getmtime(LEVEL_PATH))

    def start(self):
        self.PLAYER_GROUP.remove(self.PLAYER_GROUP.sprites())
        self.ENTITY_GROUP.remove(self.ENTITY_GROUP.sprites())
        self.ENVIRONMENT_GROUP.remove(self.ENVIRONMENT_GROUP.sprites())

        self.LEVEL_DATA = level.get_level_data(LEVEL_PATH)
        super().start()

    def run(self, screen: pygame.Surface):
        self.check_events()

        screen.fill("black")

        curr_mtime = time.ctime(os.path.getmtime(LEVEL_PATH))
        if self.prev_mtime != curr_mtime:
            self.start()
            self.prev_mtime = curr_mtime

        self.PLAYER_GROUP.update()
        self.ENTITY_GROUP.update()

        self.ENVIRONMENT_GROUP.draw(screen)
        self.ENTITY_GROUP.draw(screen)
        self.PLAYER_GROUP.draw(screen)

        basic.draw_debug(screen, [self.ENVIRONMENT_GROUP, self.ENTITY_GROUP, self.PLAYER_GROUP])


SIZE = WIDTH, HEIGHT = 800, 640
FPS = 60
CLOCK = pygame.time.Clock()

LEVEL_PATH = input("Enter path to level .txt file: ").replace("\\", "/")
if not os.path.exists(LEVEL_PATH):
    sys.exit()
os.startfile(LEVEL_PATH)

if __name__ == "__main__":
    pygame.display.set_caption("editor")
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)

    EDITOR_LEVEL = EditorLevel()

    while True:
        EDITOR_LEVEL.run(SCREEN)

        pygame.display.flip()
        CLOCK.tick(FPS)