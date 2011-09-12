from Box2D import *
from Box2D import b2Vec as vec

GRAVITY = vec(0, -10)
W = 10000

class Actor(object):    
    def draw(self):
        pass


class World(object):
    """Combines a scenegraph and a physics engine."""

    def __init__(self):
        self.actors = []
        self.setup_physics()

    def setup_physics(self):
        self.physics = b2World(GRAVITY, True)
        ground = self.physics.CreateBody()
        ground_shape = b2BoxDef(

        floor = self.world.CreateBody(b2BodyDef())
        floorbox = b2PolygonDef()
        floorbox.SetAsBox(-W, 30, W, 0)
        floorbox.CreateShape(floorbox)



    def spawn(self, actor):
       self.actors.append(actor)

