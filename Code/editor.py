import pygame
import time
import sys
import os

import level

def terminate():
    pygame.quit()
    sys.exit()


SIZE = WIDTH, HEIGHT = 800, 600
FPS = 60
CLOCK = pygame.time.Clock()

LEVEL_PATH = input("Enter path to level .txt file: ").replace("\\", "/")

if not os.path.exists(LEVEL_PATH):
    print("ERROR: This file path doesn't exists.")
    terminate()
os.startfile(LEVEL_PATH)

previous_mtime = time.ctime(0)

if __name__ == "__main__":
    pygame.display.set_caption("editor")
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        curr_mtime = time.ctime(os.path.getmtime(LEVEL_PATH))  # getting last modified file time

        if previous_mtime != curr_mtime:
            SCREEN.fill("black")

            for obj in level.get_level_data(LEVEL_PATH):  # running trough level data
                SCREEN.blit(obj.image, obj.rect.center)  # visualizing level

            previous_mtime = curr_mtime

        pygame.display.flip()
        CLOCK.tick(FPS)