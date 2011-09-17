import random


class AIController(object):
    def __init__(self, world, monster, name='enemy'):
        self.world = world
        self.monster = monster
        self.name = name
        self.target = None
        self.strategy = None
        self.time = 0

    def pick_target(self):
        try:
            self.target = self.world.get_enemies_for_name(self.name)[0]
        except IndexError:
            self.target = None

    def get_monster_x(self):
        return self.monster.get_bounds().br.x

    def get_enemy_x(self):
        return self.target.get_bounds().tl.x

    def update(self, dt):
        self.time += 0
        if self.target and not self.target.dead:
            if self.strategy is None:
                self.pick_strategy()
            else:
                self.strategy.update()
            self.monster.attack()
        else:
            self.strategy = None
            self.pick_target()

    def pick_strategy(self):
        strat = random.choice([AdvanceStrategy, RetreatStrategy])
        self.strategy = strat(self)


class AdvanceStrategy(object):
    def __init__(self, controller):
        self.controller = controller
        self.monster = controller.monster

    def update(self):
        if self.controller.get_monster_x() < self.controller.get_enemy_x() - 100:
            self.monster.right()
        else:
            self.controller.strategy = None


class RetreatStrategy(object):
    def __init__(self, controller):
        self.controller = controller
        self.monster = controller.monster
        self.start = self.controller.time

    def update(self):
        self.monster.left()
        if self.controller.time - self.start > 2:
            self.controller.strategy = None
