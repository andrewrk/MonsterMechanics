from __future__ import division, print_function, unicode_literals; range = xrange

import math
import pyglet
import json

from vector import v

STYLE_NORMAL = 0
STYLE_VALID = 1
STYLE_INVALID = 2


class BodyPart(object):
    """Base class of all body parts.
    
    Parts support tangible physics, but are created in a ghost mode that shows
    where they would be inserted if the player releases the mouse. There is also
    the ability to display the part with a visual effect to indicate whether it
    can be created in its current position.
    
    To create a physics controller for the BodyPart (ie. make it non-virtual),
    use .create_body().

    """

    part_definitions = {}

    @classmethod
    def load(cls):
        try:
            name = cls.RESOURCE_NAME
        except AttributeError:
            name = cls.__name__.lower()

        try:
            definition = BodyPart.part_definitions[name]
        except KeyError:
            with pyglet.resource.file('components/%s.json' % name) as f:
                definition = json.loads(f.read())

            # add image to it
            img = pyglet.resource.image(definition['name'])
            # <mauve> [offset is] the amount you have to translate the image
            # <mauve> So -1 * the position of the centre in the image
            # also we have to flip the y axis because this is pyglet
            img.anchor_x = -definition['offset'][0]
            img.anchor_y = img.height+definition['offset'][1]
            definition['img'] = img

            # cache it
            BodyPart.part_definitions[name] = definition
        
        cls._img = definition['img']
        cls._shapes = [(v(0, 0), definition['radius'])]

    def __init__(self, pos):
        self.sprite = pyglet.sprite.Sprite(self._img)
        self.body = None
        self.set_position(pos)

    def set_style(self, style):
        """Set a display style for the part.
        """ 
        if style == STYLE_VALID:
            self.sprite.color = (0, 160, 0)
            self.sprite.opacity = 160
        elif style == STYLE_INVALID:
            self.sprite.color = (200, 0, 0)
            self.sprite.opacity = 160
        else:
            self.sprite.color = (255, 255, 255)
            self.sprite.opacity = 255
    
    def set_position(self, pos):
        if self.body:
            self.body.set_position(pos)
        else:
            self.sprite.position = pos

    def create_body(self, world):
        self.body = world.create_body(self._shapes)
        self.body.set_position(v(*self.sprite.position))

    def attach_part(self, part, pin_radius, pin_angle):
        pin = Pin(part, self, pin_radius, pin_angle)
        part.parent_pin = pin
        self.child_pins.append(pin)

    def draw(self):
        "update self and children's sprites to correct angle and position"
        if self.body:
            self.sprite.set_position(*self.body.get_position())
            self.sprite.rotation = -180 / math.pi * self.body.get_rotation()
        self.sprite.draw()
        #for child_pin in self.child_pins:
        #    child_pin.child.draw()

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
            v(min(p1.x, p2.x, p3.x, p4.x), min(p1.y, p2.y, p3.y, p4.y)),
            v(max(p1.x, p2.x, p3.x, p4.x), max(p1.y, p2.y, p3.y, p4.y)),
        )


class Head(BodyPart):
    """The head of the monster"""
    RESOURCE_NAME = 'head-level1'


class Lung(BodyPart):
    """Lungs that supply energy to connected parts"""


class Monster(object):
    @classmethod
    def create_initial(cls, world, pos):
        Head.load() 
        Lung.load() 
        head = Head(pos)
        head.create_body(world)
        lung = Lung(pos + v(80, 60)) 
        lung.create_body(world)
        head.body.attach(lung.body, pos + v(50, 30))
        return cls(world, [head, lung])

    def __init__(self, world, parts):
        self.world = world
        self.parts = parts

    def draw(self):
        for p in self.parts:
            p.draw()

    def cacheBoundingBox(self):
        "compute the bounding box and save it for future reference"
        self.sw_edge, self.ne_edge = self.head.get_bounding_box()
