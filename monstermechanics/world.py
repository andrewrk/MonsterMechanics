from .vector import v
from .physics import get_physics


class World(object):
    def __init__(self):
        self.actors = []
        physics = get_physics()
        self.world = physics.create_world(gravity=v(0, -500))
        self.world.create_ground(40)

    def update(self, dt):
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

    def destroy(self, actor):
        self.actors.remove(actor)
        actor.world = None
        if actor.body:
            actor.body.destroy()
