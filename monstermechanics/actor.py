import math
import json
import pyglet

from vector import v
from geom import Circle


def load_resource(resource_file):
    with pyglet.resource.file('components/%s.json' % resource_file) as f:
        definition = json.loads(f.read())

    # load the associated image
    img = pyglet.resource.image(definition['name'])
    # <mauve> [offset is] the amount you have to translate the image
    # <mauve> So -1 * the position of the centre in the image
    # also we have to flip the y axis because this is pyglet
    img.anchor_x = -definition['offset'][0]
    img.anchor_y = img.height + definition['offset'][1]
    definition['img'] = img

    offset = v(definition['offset'])
    circles = [Circle(v(0, 0), definition['radius'])]
    for p in definition.get('points', []):
        centre = v(p['offset']) + offset
        circles.append(Circle(v(centre.x, -centre.y), p['radius']))
    definition['shapes'] = circles 
    return definition


class Actor(object):
    """Base class for objects that appear in and possibly interact with the world"""
    @classmethod
    def load(cls):
        if hasattr(cls, 'resources') or not hasattr(cls, 'RESOURCES'):
            return
        cls.resources = {}
        for name, resource_file in cls.RESOURCES.items():
            cls.resources[name] = load_resource(resource_file)

    def __init__(self, pos, name='player'):
        self.sprite = None
        self.name = name
        self.body = None
        self.set_default_part()
        self.scale = 1.0
        self.set_position(pos)
        self._joints = []

    def set_default_part(self):
        self.set_part(self.DEFAULT_PART)

    def set_part(self, name):
        if self.name == 'enemy':
            qname = 'enemy-' + name
        else:
            qname = name
        try:
            self.part = self.resources[qname]
        except KeyError:
            self.load()
            self.part = self.resources[name]

        self.sprite = pyglet.sprite.Sprite(self.part['img'])
        if self.body:
            self.body.set_shapes(self.part['shapes'])
            self.sprite.position = self.body.get_position()

    def set_scale(self, scale):
        """Set the scale of the actor."""
        self.scale = scale
        self.sprite.scale = self.scale
        self.body.set_scale(self.scale)

    def draw(self):
        "update self and children's sprites to correct angle and position"
        if self.body:
            self.sprite.set_position(*self.body.get_position())
            self.sprite.rotation = -180 / math.pi * self.body.get_rotation()
        self.sprite.draw()

    def update(self, dt):
        """Update the object. The default implementation does nothing."""

    def get_shapes(self):
        """Return the physics volumes in the shape."""
        return [Circle(c * self.scale, r * self.scale) for c, r in self.part['shapes']]
    
    def get_base_shape(self):
        return self.get_shapes()[0]

    def get_position(self):
        if self.body:
            return self.body.get_position()
        else:
            return v(*self.sprite.position)

    def set_position(self, pos):
        """Move the part."""
        if self.body:
            self.body.set_position(pos)
        else:
            self.sprite.position = pos

    def create_body(self, world):
        """Create the physics body for the part"""
        #print "Spawning", self.__class__.__name__, self.name + self.type
        self.body = world.create_body(self.get_shapes(), collision_class=self.name + self.type)
        self.body.set_position(v(*self.sprite.position))
