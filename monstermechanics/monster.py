from __future__ import division, print_function, unicode_literals; range = xrange

from .components import *
from vec2d import Vec2d
import math
import pyglet

def trig(angle):
    return Vec2d(math.cos(angle), math.sin(angle))

class Pin(object):
    "The connection between pinned body parts"
    def __init__(self, child, parent, pin_radius, pin_angle):
        """
        child - body part to pin to parent
        parent - body part to pin child to
        pin_radius - distance between child's anchor point and parent's
                     anchor point
        pin_angle - relative angle which points from parent's anchor point
                    to child's anchor point
        """
        self.child = child
        self.parent = parent
        self.pin_radius = pin_radius
        self.pin_angle = pin_angle

class BodyPart(object):
    def __init__(self, sprite):
        """
        sprite - a pyglet sprite
        """
        self.sprite = sprite
        # radians
        self.rotation = 0
        # see Pin class
        self.parent_pin = None
        self.child_pins = []

    def attach_part(self, part, pin_radius, pin_angle):
        pin = Pin(part, self, pin_radius, pin_angle)
        part.parent_pin = pin
        self.child_pins.append(pin)

    def get_pos(self):
        "returns a vec2d of the position of this part relative to the base part"
        if self.parent_pin is None:
            return Vec2d(0,0)
        else:
            parent_offset = self.parent_pin.parent.get_pos()
            rot = self.parent_pin.parent.get_angle() + self.parent_pin.pin_angle
            my_offset = self.parent_pin.pin_radius * trig(rot)
            return parent_offset + my_offset
    
    def get_angle(self):
        "returns the angle of this part in radians relative to the base part"
        if self.parent_pin is None:
            return self.rotation
        else:
            parent_angle = self.parent_pin.parent.get_angle()
            my_angle = self.parent_pin.pin_angle + self.rotation
            return parent_angle + my_angle

    def draw(self):
        "update self and children's sprites to correct angle and position"
        self.sprite.set_position(*self.get_pos().done(int))

        absolute_rotation = self.get_angle()
        self.sprite.rotation = -180 / math.pi * absolute_rotation

        self.sprite.draw()
        for child_pin in self.child_pins:
            child_pin.child.draw()

    def get_bounding_box(self):
        sw, ne = self._get_bounding_box()
        for child in self.child_pins:
            child_sw, child_ne = child.child.get_bounding_box()
            sw.x = min(sw.x, child_sw.x)
            sw.y = min(sw.y, child_sw.y)
            ne.x = max(ne.x, child_ne.x)
            ne.y = max(ne.y, child_ne.y)
        return sw, ne

    def _get_bounding_box(self):
        cx, cy = -self.sprite.image.anchor_x, -self.sprite.image.anchor_y
        cx2, cy2 = self.sprite.image.width + cx, self.sprite.image.height + cy
        rot_trig = trig(self.get_angle())
        rot_trig2 = trig(self.get_angle()+math.pi/2)
        p1 = cx *  rot_trig + cy2 * rot_trig2
        p2 = cy2 * rot_trig + cx2 * rot_trig2
        p3 = cx2 * rot_trig + cy  * rot_trig2
        p4 = cy *  rot_trig + cx  * rot_trig2
        return (
            Vec2d(min(p1.x, p2.x, p3.x, p4.x), min(p1.y, p2.y, p3.y, p4.y)),
            Vec2d(max(p1.x, p2.x, p3.x, p4.x), max(p1.y, p2.y, p3.y, p4.y)),
        )

class Monster(object):
    def __init__(self, head):
        "head - the BodyPart that represents the head of the monster"
        self.pos = Vec2d(0, 0)
        self.head = head
        # offset from self.pos to edges, computed when you call cacheBoundingBox
        self.sw_edge = Vec2d(0, 0)
        self.ne_edge = Vec2d(0, 0)

    def draw(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self.pos.x, self.pos.y, 0.0)
        self.head.draw()
        pyglet.gl.glPopMatrix()

    def cacheBoundingBox(self):
        "compute the bounding box and save it for future reference"
        self.sw_edge, self.ne_edge = self.head.get_bounding_box()
