import pygame

import level

SIZE = WIDTH, HEIGHT = 800, 640
FPS = 60
CLOCK = pygame.time.Clock()


# region LEVELS
class IntroLevel(level.Level):
    def __init__(self):
        super().__init__("../Data/Levels/intro_level.txt")

        self.intro_block = self.ENVIRONMENT_GROUP.sprites()[0]

    def run(self, screen: pygame.Surface):
        global current_level

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()

            if event.type == pygame.KEYDOWN and event.dict["key"] == pygame.K_SPACE:
                if self.intro_block.a_data["a_frame"] == len(self.intro_block.animation_frames[self.intro_block.a_data["name"]]["animation"]) - 1:
                    current_level += 1
                    continue

                self.intro_block.a_data = {"name": self.intro_block.a_data["name"],
                                           "a_frame": self.intro_block.a_data["a_frame"] + 1,
                                           "frame": self.intro_block.animation_frames[self.intro_block.a_data["name"]]["framerate"],
                                           "play": True, "cycle": False, "reverse": False, "ended": False}
                self.intro_block.image = self.intro_block.get_updated_image()[0]

        screen.fill("black")

        self.ENVIRONMENT_GROUP.update()
        self.ENVIRONMENT_GROUP.draw(screen)


class FirstLevel(level.Level):
    def __init__(self):
        super().__init__("../Data/Levels/first_level.txt")

        import melee

        self.wave = level.Wave({melee.Melee: [self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP]]},
                               5, 2, pygame.Rect(80, 80, 640, 480), [100, 150], 100)

        self.PLAYER.fpos = (400, 320)
        self.PLAYER.rect.center = self.PLAYER.fpos

        self.PLAYER.update_collider()
        self.PLAYER.update_boxes()

    def run(self, screen: pygame.Surface):
        global current_level

        self.check_events()

        screen.fill("black")

        if not self.PLAYER.alive():
            current_level = 0
            recreate_levels()

        if self.wave.run():
            current_level += 1

        self.PLAYER_GROUP.update()
        self.ENTITY_GROUP.update()

        self.ENVIRONMENT_GROUP.draw(screen)

        [player.draw(screen) for player in self.PLAYER_GROUP.sprites()]
        [entity.draw(screen) for entity in self.ENTITY_GROUP.sprites()]


class SecondLevel(level.Level):
    def __init__(self):
        super().__init__("../Data/Levels/second_level.txt")

        import melee
        import distance

        self.wave = level.Wave(
            {melee.Melee: [self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP]],
             distance.Distance: [self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP]]},
            10, 2, pygame.Rect(80, 80, 640, 480), [100, 150], 100)

        self.PLAYER.fpos = (400, 320)
        self.PLAYER.rect.center = self.PLAYER.fpos

        self.PLAYER.update_collider()
        self.PLAYER.update_boxes()

    def run(self, screen: pygame.Surface):
        global current_level

        self.check_events()

        screen.fill("black")

        if not self.PLAYER.alive():
            current_level = 0
            recreate_levels()

        if self.wave.run():
            current_level += 1

        self.PLAYER_GROUP.update()
        self.ENTITY_GROUP.update()

        self.ENVIRONMENT_GROUP.draw(screen)

        [player.draw(screen) for player in self.PLAYER_GROUP.sprites()]
        [entity.draw(screen) for entity in self.ENTITY_GROUP.sprites()]


class ThirdLevel(level.Level):
    def __init__(self):
        super().__init__("../Data/Levels/third_level.txt")

        import melee
        import distance

        self.wave = level.Wave(
            {melee.Melee: [self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP]],
             distance.Distance: [self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP]]},
            25, 3, pygame.Rect(80, 80, 640, 480), [100, 150], 100)

        self.PLAYER.fpos = (400, 320)
        self.PLAYER.rect.center = self.PLAYER.fpos

        self.PLAYER.update_collider()
        self.PLAYER.update_boxes()

    def run(self, screen: pygame.Surface):
        global current_level

        self.check_events()

        screen.fill("black")

        if not self.PLAYER.alive():
            current_level = 0
            recreate_levels()

        if self.wave.run():
            current_level += 1

        self.PLAYER_GROUP.update()
        self.ENTITY_GROUP.update()

        self.ENVIRONMENT_GROUP.draw(screen)

        [player.draw(screen) for player in self.PLAYER_GROUP.sprites()]
        [entity.draw(screen) for entity in self.ENTITY_GROUP.sprites()]


class OutroLevel(level.Level):
    def __init__(self):
        super().__init__("../Data/Levels/outro_level.txt")

        self.outro_block = self.ENVIRONMENT_GROUP.sprites()[0]

    def run(self, screen: pygame.Surface):
        global current_level

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()

            if event.type == pygame.KEYDOWN and event.dict["key"] == pygame.K_SPACE:
                if self.outro_block.a_data["a_frame"] == len(self.outro_block.animation_frames[self.outro_block.a_data["name"]]["animation"]) - 1:
                    self.terminate()

                self.outro_block.a_data = {"name": self.outro_block.a_data["name"],
                                           "a_frame": self.outro_block.a_data["a_frame"] + 1,
                                           "frame": self.outro_block.animation_frames[self.outro_block.a_data["name"]]["framerate"],
                                           "play": True, "cycle": False, "reverse": False, "ended": False}
                self.outro_block.image = self.outro_block.get_updated_image()[0]

        screen.fill("black")

        self.ENVIRONMENT_GROUP.update()
        self.ENVIRONMENT_GROUP.draw(screen)
# endregion


def recreate_levels():
    global INTRO, FIRST, SECOND, THIRD, OUTRO

    INTRO = IntroLevel()
    FIRST = FirstLevel()
    SECOND = SecondLevel()
    THIRD = ThirdLevel()
    OUTRO = OutroLevel()


if __name__ == "__main__":
    pygame.display.set_caption("MINUTES")
    pygame.init()

    SCREEN = pygame.display.set_mode(SIZE)

    current_level = 0

    INTRO = IntroLevel()
    FIRST = FirstLevel()
    SECOND = SecondLevel()
    THIRD = ThirdLevel()
    OUTRO = OutroLevel()

    while True:
        if not current_level:
            INTRO.run(SCREEN)

        elif current_level == 1:
            FIRST.run(SCREEN)

        elif current_level == 2:
            SECOND.run(SCREEN)

        elif current_level == 3:
            THIRD.run(SCREEN)

        else:
            OUTRO.run(SCREEN)

        pygame.display.flip()
        CLOCK.tick(FPS)