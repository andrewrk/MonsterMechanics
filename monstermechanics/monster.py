from __future__ import division, print_function, unicode_literals; range = xrange

from .components import *
from vec2d import Vec2d
import math

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
            my_offset = Vec2d(
                self.parent_pin.pin_radius * math.cos(rot),
                self.parent_pin.pin_radius * math.sin(rot))
            return parent_offset + my_offset
    
    def get_angle(self):
        "returns the angle of this part in radians relative to the base part"
        if self.parent_pin is None:
            return self.rotation
        else:
            parent_angle = self.parent_pin.parent.get_angle()
            my_angle = self.parent_pin.pin_angle + self.rotation
            return parent_angle + my_angle

    def draw(self, offset_pos=Vec2d(0,0), offset_angle=0):
        "update self and children's sprites to correct angle and position"
        absolute_pos = offset_pos + self.get_pos()
        absolute_pos.do(int)
        self.sprite.set_position(*absolute_pos)

        absolute_rotation = offset_angle + self.get_angle()
        self.sprite.rotation = -180 / math.pi * absolute_rotation

        for child_pin in self.child_pins:
            child_pin.child.draw(offset_pos, offset_angle)

class Monster(object):
    def __init__(self, head):
        "head - the BodyPart that represents the head of the monster"
        self.pos = Vec2d(0, 0)
        self.head = head

    def draw(self):
        self.head.draw(self.pos)
