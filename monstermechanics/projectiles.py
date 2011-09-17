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

    level = 1

    MAX_AGE = 5
    age = 0

    DAMAGE = 100, 25, 50, 100

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
        return self.DAMAGE[self.level - 1]
        
    def on_hit(self, part):
        damage = self.get_damage()
        part.health -= damage
        if part.health <= 0:
            part.kill()

        friends = self.world.get_friends_for_name(self.name)
        for f in friends:
            f.add_mutagen(damage * 1.5 / len(friends))
        self.world.spawn(DamageActor(self.get_position(), damage))

        self.world.destroy(self)

