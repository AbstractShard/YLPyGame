import pygame
import random
import sys

import player
import basic
import melee
import distance

def get_level_data(path: str) -> list:
    with open(path, encoding="utf-8", mode="r") as file:
        data = list(map(lambda x: x.split(": "), map(str.strip, file.readlines())))

    replace_equasions = {}
    replace_data = filter(lambda x: "@" in "".join(x), data)

    data = list(filter(lambda x: ("#" not in "".join(x)) and ("@" not in "".join(x)) and ("".join(x)), data))

    for i in replace_data:
        equasion = list(map(str.strip, i[0].replace("@", "").split("=")))

        if equasion[0] not in replace_equasions:
            replace_equasions[equasion[0]] = equasion[1]

    for i in range(len(data)):
        for to_replace in replace_equasions.keys():
            if to_replace in "".join(data[i]):
                data[i] = ":".join(data[i]).replace(to_replace, replace_equasions[to_replace]).split(":")

    return data


class Level:
    def __init__(self, path_to_level: str):
        self.PLAYER_GROUP = pygame.sprite.Group()
        self.ENTITY_GROUP = pygame.sprite.Group()
        self.ENVIRONMENT_GROUP = pygame.sprite.Group()

        self.PLAYER = player.Player([self.PLAYER_GROUP], [self.ENVIRONMENT_GROUP], [self.ENTITY_GROUP])
        self.LEVEL_DATA = get_level_data(path_to_level)

        self.start()

    def start(self):
        for obj_data in self.LEVEL_DATA:
            to_import = obj_data[0].split(".")[0]

            exec(f"import {to_import}")
            eval(f"{obj_data[0]}({obj_data[1]})")

    def run(self, screen: pygame.Surface):
        pass

    def terminate(self):
        pygame.quit()
        sys.exit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.terminate()


class Wave:
    def __init__(self, units_data: dict, wave_length: int, spawn_units_under: int, spawn_rect: pygame.Rect,
                 spawn_cooldown_range: list):
        self.UNITS_DATA = units_data.copy()

        self.WAVE_LENGTH = wave_length
        self.SPAWN_UNITS_UNDER = spawn_units_under

        self.SPAWN_RECT = spawn_rect
        self.SPAWN_COOLDOWN_RANGE = spawn_cooldown_range

        self.curr_units = []
        self.used_units = 0
        self.counter = {"spawn": random.randint(*self.SPAWN_COOLDOWN_RANGE)}

    def spawn_unit(self):
        spawn_position = (random.randint(self.SPAWN_RECT.x, self.SPAWN_RECT.x + self.SPAWN_RECT.width),
                          random.randint(self.SPAWN_RECT.y, self.SPAWN_RECT.y + self.SPAWN_RECT.height))
        choosed_unit = random.choice(list(self.UNITS_DATA.keys()))
        unit = choosed_unit(*self.UNITS_DATA[choosed_unit])

        unit.fpos = spawn_position
        unit.rect.center = unit.fpos

        unit.update_collider()
        unit.update_boxes()

        self.curr_units.append(unit)
        self.used_units += 1

    def check_spawn(self):
        if len(self.curr_units) >= self.SPAWN_UNITS_UNDER:
            return

        if self.counter["spawn"] > 0:
            self.counter["spawn"] -= 1
            return

        self.spawn_unit()
        self.counter["spawn"] = random.randint(*self.SPAWN_COOLDOWN_RANGE)

    def run(self):
        if self.used_units >= self.WAVE_LENGTH:
            return

        for unit in self.curr_units:
            if not unit.alive():
                self.curr_units.remove(unit)
                del unit
                continue

        self.check_spawn()


class TestLevel(Level):
    def __init__(self):
        super().__init__("../Data/Levels/test_level.txt")

        self.wave = Wave({melee.Melee: (self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP]),
                          distance.Distance: (self.PLAYER, [self.ENTITY_GROUP], [self.ENVIRONMENT_GROUP], [self.PLAYER_GROUP])},
                         10, 3, pygame.Rect(150, 150, 150, 150), [100, 250])

    def run(self, screen: pygame.Surface):
        self.check_events()

        screen.fill("black")

        self.wave.run()

        self.PLAYER_GROUP.update()
        self.ENTITY_GROUP.update()

        self.ENVIRONMENT_GROUP.draw(screen)
        self.ENTITY_GROUP.draw(screen)
        self.PLAYER_GROUP.draw(screen)

        basic.draw_debug(screen, [self.ENVIRONMENT_GROUP, self.ENTITY_GROUP, self.PLAYER_GROUP])