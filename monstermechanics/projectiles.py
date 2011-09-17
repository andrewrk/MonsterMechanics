from .vector import v
from .geom import Circle

from .actor import Actor
from .digits import DamageActor


class Thistle(Actor):
    RESOURCES = {
        'level1': 'thistle-level1',
        'level2': 'thistle-level2',
        'level3': 'thistle-level3',
    }
    type = 'projectile'
    DEFAULT_PART = 'level1'

    multiplier = 1.0
    level = 1

    MAX_AGE = 5
    age = 0

    DAMAGE = 25, 50, 100

    def set_level(self, l):
        self.level = l
        self.set_part('level%d' % self.level)

    def update(self, dt):
        self.age += dt
        if self.age > self.MAX_AGE:
            self.world.destroy(self)
            return
        for enemy in self.world.get_enemies_for_name(self.name):
            part = enemy.colliding(self)
            if part:
                self.on_hit(part)

    def get_damage(self):
        return self.DAMAGE[self.level - 1] * self.multiplier
        
    def on_hit(self, part):
        damage = self.get_damage()
        self.world.damage_part(part, self.name, damage)
        self.world.destroy(self)


class Blood(Actor):
    RESOURCES = {
        'default': 'blood'
    }
    DEFAULT_PART = 'default'
    type = 'neutral'
    age = 0
    MAX_AGE = 3

    def update(self, dt):
        self.age += dt
        if self.age > self.MAX_AGE:
            self.world.destroy(self)
            return
