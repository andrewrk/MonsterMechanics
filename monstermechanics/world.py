from .vector import v
from .physics import get_physics

from .digits import DamageActor

class World(object):
    def __init__(self):
        self.actors = []
        self.monsters = []
        physics = get_physics()
        self.world = physics.create_world(gravity=v(0, -500))
        self.world.create_ground(40)

    def add_monster(self, monster):
        self.monsters.append(monster)

    def remove_monster(self, monster):
        self.monsters.remove(monster)

    def get_monster_bounds(self):
        bounds = None
        for m in self.monsters:
            if bounds is None:
                bounds = m.get_bounds()
            else:
                bounds = bounds.union(m.get_bounds())
        return bounds

    def get_player(self):
        for m in self.monsters:
            if m.name == 'player':
                return m

    def get_enemies(self):
        return [m for m in self.monsters if m.name != 'player']

    def get_friends_for_name(self, name):
        return [m for m in self.monsters if m.name == name]

    def get_enemies_for_name(self, name):
        return [m for m in self.monsters if m.name != name]

    def update(self, dt):
        for m in self.monsters:
            m.update(dt)
        for a in self.actors:
            a.update(dt)
        self.world.update(dt)

    def draw(self):
        for a in self.actors:
            a.draw()

    def spawn(self, actor):
        self.actors.append(actor)
        actor.world = self
        try:
            create_body = actor.create_body
        except AttributeError:
            pass
        else:
            create_body(self.world)

    def damage_part(self, part, attacker_name, damage_amount):
        part.health -= damage_amount
        self.spawn(DamageActor(part.get_position(), int(damage_amount + 0.5)))
        if part.health <= 0:
            part.kill()

        friends = self.get_friends_for_name(attacker_name)
        for f in friends:
            f.add_mutagen(damage_amount * 1.5 / len(friends))

    def destroy(self, actor):
        self.actors.remove(actor)
        actor.world = None
        if actor.body:
            actor.body.destroy()
