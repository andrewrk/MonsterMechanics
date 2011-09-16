"""Abstraction of physics libraries.

The rationale for this abstraction is that our demands on the physics libraries
are very few, but there are so many incompatible versions of popular physics
libraries that it is problematic to find common ground to work from. By
abstracting them it is easier to see what our demands are so taht we can
replace the physics library easily or even write our own.

"""
from vector import Vector

# Collision classes and the other classes they collide with
# These should be baked into bitmasks or whatever by the physics engine
COLLISION_CLASSES = [
    ('playerarm', ['playerarm', 'enemyarm', 'enemybody', 'enemyprojectile']),
    ('playerbody', ['playerbody', 'enemyarm', 'enemybody', 'enemyprojectile']),
    ('playerprojectile', ['enemybody', 'enemyarm', 'enemyprojectile']),
    ('enemyarm', ['enemyarm', 'playerarm', 'playerbody', 'playerprojectile']),
    ('enemybody', ['enemybody', 'playerarm', 'playerbody', 'playerprojectile']),
    ('enemyprojectile', ['playerbody', 'playerarm', 'playerprojectile']),
    ('neutral', [])
]

class AbstractWorld(object):
    def update(self, dt):
        """Update then physics of world."""
        raise NotImplementedError("AbstractWorld.update()")

    def create_ground(self, y):
        """Create an infinite floor plane"""

    def create_body(self, circles, density):
        """Creates a body consisting of multiple circles.

        circles should be a list of tuples (centre, radius)
        """
        raise NotImplementedError("AbstractPhysics.create_body()")


class AbstractBody(object):
    def get_rotation(self):
        """Return the rotation of the body in radians"""

    def set_rotation(self, radians):
        """Set the rotation of the body in radians"""

    def local_to_world(self, point):
        """Return the position of point relative to the body in world space."""

    def get_position(self):
        """Gets the position of the body. Subclasses should implement this method
        to work in a more efficient way"""
        return self.local_to_world(Vector(0, 0))

    def set_position(self, pos):
        """Sets the position of the body."""
        raise NotImplementedError("AbstractBody.set_position()")

    def set_scale(self, scale):
        """Scale the body to a fraction of its original size."""
        raise NotImplementedError("AbstractBody.set_scale()")

    def attach(self, other, anchor_point):
        """Attach this body to another body using a pin joint at anchor_point.
        
        Returns a Joint object.
        """ 
        raise NotImplementedError("AbstractPhyscs.attach()")

    def set_velocity(self, vel):
        raise NotImplementedError("AbstractPhysics.set_velocity()")

    def apply_force(self, force, world_point):
        raise NotImplementedError("AbstractPhysics.apply_force()")

    def apply_impulse(self, impulse, world_point):
        raise NotImplementedError("AbstractPhysics.apply_impulse()")

    def apply_torque(self, torque):
        raise NotImplementedError("AbstractPhysics.apply_torque()")

    def destroy(self):
        """Destroy the body and all joints."""
        raise NotImplementedError("AbstractPhysics.destroy()")


class AbstractPhysics(object):
    def create_world(self, gravity):
        """Return a world, with constant gravity equal to gravity."""
        raise NotImplementedError("AbstractPhysics.create_world()")


def get_physics():
    from .box2d_physics import Box2DPhysics
    return Box2DPhysics()
