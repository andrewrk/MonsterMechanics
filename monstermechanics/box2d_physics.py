"""Physics as implemented using Box2D 2.0.2 svn20100109 as in Ubuntu maverick"""

from Box2D import *
from .physics import *
from vector import v


PHYSICS_WIDTH = 5000
PHYSICS_HEIGHT = 2500


class Box2DPhysics(AbstractPhysics):
    def create_world(self, gravity):
        world_bounds = b2AABB()
        bound = v(PHYSICS_WIDTH, PHYSICS_HEIGHT)
        world_bounds.lowerBound = bound * -0.5
        world_bounds.upperBound = bound * 0.5
        return Box2DWorld(b2World(world_bounds, gravity, True))


class Box2DWorld(AbstractWorld):
    def __init__(self, world):
        self.world = world

    def update(self, dt):
        self.world.Step(dt, 20, 16)

    def create_ground(self, y):
        ground = self.world.GetGroundBody()

        groundshape = b2PolygonDef()
        groundshape.SetAsBox(PHYSICS_WIDTH, y * 2, (0, 0), 0)
        ground.CreateShape(groundshape)
        self.ground = Box2DBody(self, ground)
        return self.ground

    def create_body(self, circles, density=1, restitution=0.1, friction=0.5):
        bodydef = b2BodyDef()
        body = self.world.CreateBody(bodydef)

        for centre, radius in circles:
            circledef = b2CircleDef()
            circledef.localPosition = centre
            circledef.radius = radius
            circledef.density = density
            circledef.restitution = restitution
            circledef.friction = friction
            body.CreateShape(circledef)

        body.SetMassFromShapes()
        return Box2DBody(self, body)


class Box2DBody(AbstractBody):
    def __init__(self, world, body):
        self.world = world
        self.body = body

    def remove(self):
        self.world.world.DestroyBody(self.body)

    def get_position(self):
        return v(*self.body.GetPosition())

    def set_position(self, v):
        self.body.position = v

    def get_rotation(self):
        return self.body.angle

    def local_to_world(self, point):
        return self.body.LocalToWorld(point)
