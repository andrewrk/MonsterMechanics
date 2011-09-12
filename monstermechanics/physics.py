"""Abstraction of physics libraries.

The rationale for this abstraction is that our demands on the physics libraries
are very few, but there are so many incompatible versions of popular physics
libraries that it is problematic to find common ground to work from. By
abstracting them it is easier to see what our demands are so taht we can
replace the physics library easily or even write our own.

"""
from vector import Vector


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

    def local_to_world(self, point):
        """Return the position of point relative to the body in world space."""

    def get_position(self):
        """Gets the position of the body. Subclasses should implement this method
        to work in a more efficient way"""
        return self.local_to_world(Vector(0, 0))

    def set_position(self, pos):
        raise NotImplementedError("AbstractPhysics.set_position()")

    def attach(self, other, anchor_point):
        """Attach this body to another body using a pin joint at anchor_point""" 
        raise NotImplementedError("AbstractPhyscs.attach()")


class AbstractPhysics(object):
    def create_world(self, gravity):
        """Return a world, with constant gravity equal to gravity."""
        raise NotImplementedError("AbstractPhysics.create_world()")


def get_physics():
    from .box2d_physics import Box2DPhysics
    return Box2DPhysics()
