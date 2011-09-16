"""Physics as implemented using Box2D 2.0.2 svn20100109 as in Ubuntu maverick"""

from Box2D import *
from .physics import *
from vector import v


def make_bitmasks():
    namebits = {}
    for bit, (name, collideswith) in enumerate(COLLISION_CLASSES):
        namebits[name] = 1 << bit

    classes = {}
    for name, collideswith in COLLISION_CLASSES:
        mask = 0
        for c in collideswith:
            mask |= namebits[c]
        category = namebits[name]
        classes[name] = category, mask

    return classes


SCALE = 0.01

COLLISION_CLASSES = make_bitmasks()

PHYSICS_WIDTH = 5000
PHYSICS_HEIGHT = 2500


class Box2DPhysics(AbstractPhysics):
    def create_world(self, gravity):
        world_bounds = b2AABB()
        bound = v(PHYSICS_WIDTH, PHYSICS_HEIGHT)
        world_bounds.lowerBound = bound * -0.5
        world_bounds.upperBound = bound * 0.5
        return Box2DWorld(b2World(world_bounds, gravity * SCALE, True))


class Box2DWorld(AbstractWorld):
    def __init__(self, world):
        self.world = world
        self.update_callbacks = []

    def add_update_callback(self, c):
        self.update_callbacks.append(c)
    
    def update(self, dt):
        for c in self.update_callbacks:
            c(dt)
        self.world.Step(dt, 10, 8)

    def create_ground(self, y):
        ground = self.world.GetGroundBody()

        groundshape = b2PolygonDef()
        groundshape.filter.categoryBits = 0xffff
        groundshape.filter.maskBits = 0xffff
        groundshape.SetAsBox(PHYSICS_WIDTH, 1000, (0, y * SCALE - 1000), 0)
        ground.CreateShape(groundshape)
        self.ground = Box2DGround(self, ground)
        return self.ground

    def create_body(self, circles, density=0.00001, restitution=0.1, friction=0.5, collision_class=None):
        return Box2DBody(self, circles, density, restitution, friction, collision_class=collision_class)


class Box2DGround(AbstractBody):
    def __init__(self, world, body):
        self.world = world
        self.body = body

    def remove(self):
        self.world.world.DestroyBody(self.body)

    def get_position(self):
        return v(*self.body.GetPosition()) / SCALE

    def set_position(self, v):
        self.body.position = v * SCALE

    def get_rotation(self):
        return self.body.angle

    def local_to_world(self, point):
        return self.body.LocalToWorld(point) / SCALE

    def destroy(self):
        if self.body is not None:
            self.world.DestroyBody(self.body)
            self.body = None

    __del__ = destroy


class Box2DBody(AbstractBody):
    def __init__(self, world, circles, density=1, restitution=0.1, friction=1, collision_class=None):
        self.world = world
        self.circles = circles
        self.density = density
        self.restitution = restitution
        self.friction = friction
        if collision_class is None:
            self.collision_category = 0xffff
            self.collision_mask = 0xffff
        else:
            self.collision_category, self.collision_mask = COLLISION_CLASSES[collision_class]
        self.joints = []
        self.scale = 1.0

        bodydef = b2BodyDef()
        self.body = self.world.world.CreateBody(bodydef)
        self.create_shapes()
        self.body.SetMassFromShapes()
        self.origMassData = self.body.massData

    def create_shapes(self):
        self.shapes = []
        for centre, radius in self.circles:
            circledef = b2CircleDef()
            circledef.filter.categoryBits = self.collision_category
            circledef.filter.maskBits = self.collision_mask
            circledef.localPosition = centre * self.scale * SCALE
            circledef.radius = radius * self.scale * SCALE
            circledef.density = self.density
            circledef.restitution = self.restitution
            circledef.friction = self.friction
            self.shapes.append(self.body.CreateShape(circledef))

    def set_scale(self, scale):
        for shape in self.shapes:
            self.body.DestroyShape(shape)
        self.scale = scale
        self.create_shapes()
        massdata = b2MassData()
        massdata.mass = self.origMassData.mass * scale
        massdata.center = self.origMassData.center
        massdata.I = self.origMassData.I * scale
        self.body.massData = massdata
        for j in self.joints:
            j.rescale()

    def remove(self):
        self.world.world.DestroyBody(self.body)

    def get_position(self):
        return v(*self.body.GetPosition()) / SCALE

    def set_position(self, v):
        self.body.position = v * SCALE

    def get_rotation(self):
        return self.body.angle

    def set_rotation(self, radians):
        self.body.angle = radians

    def local_to_world(self, point):
        return v(*self.body.LocalToWorld(point)) / SCALE

    def set_velocity(self, vel):
        self.body.linearVelocity = vel * SCALE

    def apply_force(self, force, point):
        self.body.ApplyForce(force * SCALE, point * SCALE)

    def apply_impulse(self, impulse, point):
        self.body.ApplyImpulse(impulse * SCALE, point * SCALE)

    def apply_torque(self, torque):
        self.body.ApplyTorque(torque)

    def attach(self, another, anchor_point):
        joint = b2RevoluteJointDef()
        joint.maxMotorTorque = 1
        joint.motorSpeed = 0
        joint.enableMotor = True
        joint.Initialize(self.body, another.body, anchor_point * SCALE)
        j = StiffJoint(self.world, joint, self, another)
        self.joints.append(j)
        another.joints.append(j)
        self.world.add_update_callback(j.update)

    def destroy(self):
        for j in self.joints:
            j.destroy()
        if self.body is not None:
            self.world.world.DestroyBody(self.body)
            self.body = None

    __del__ = destroy


class StiffJoint(object):
    """Control for the motor of a revolution joint"""
    def __init__(self, world, jointdef, body1, body2):
        self.jointdef = jointdef
        self.world = world
        self.joint = world.world.CreateJoint(jointdef).getAsType() 
        self.body1 = body1
        self.body2 = body2
        self.b1_anchor = v(*self.jointdef.localAnchor1) / body1.scale
        self.b2_anchor = v(*self.jointdef.localAnchor2) / body2.scale

    def rescale(self):
        """Reposition the joint anchors to match the bodys' current scale"""
        self.world.world.DestroyJoint(self.joint)
        self.jointdef.localAnchor1 = self.b1_anchor * self.body1.scale
        self.jointdef.localAnchor2 = self.b2_anchor * self.body2.scale
        self.joint = self.world.world.CreateJoint(self.jointdef).getAsType() 

    def update(self, dt):
        angleError = self.joint.GetJointAngle()
        gain = 2
        self.joint.SetMotorSpeed(-gain * angleError)

    def destroy(self):
        if self.joint is not None:
            self.world.world.DestroyJoint(self.joint)
            self.body1.joints.remove(self)
            self.body2.joints.remove(self)
        self.joint = None

    __del__ = destroy
