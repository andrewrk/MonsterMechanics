from vector import v
from geom import Circle

from actor import Actor


class Thistle(Actor):
    RESOURCES = {
        'level1': 'thistle-level1',
        'level2': 'thistle-level2',
        'level3': 'thistle-level3',
    }
    type = 'projectile'
    DEFAULT_PART = 'level1'

    MAX_AGE = 5
    age = 0

    def update(self, dt):
        self.age += dt
        if self.age > self.MAX_AGE:
            self.world.destroy(self)
        for enemy in self.world.get_enemies_for_name(self.name):
            part = enemy.colliding(self)
            if part:
                self.on_hit(part)
        
    def on_hit(self, part):
        self.deal_damage(part, self.name)
        print "hit", part
        self.world.destroy(self)

