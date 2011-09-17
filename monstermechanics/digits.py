import pyglet
from pyglet import gl

from .vector import v
from .actor import Actor

MUTAGEN_COLOR = (170, 212, 0)
DAMAGE_COLOR = (160, 44, 44)


class Digits(object):
    ANCHOR_LEFT = 0
    ANCHOR_CENTER = 0.5
    ANCHOR_RIGHT = 1

    @classmethod
    def load(cls):
        imgs = []
        for i in range(10):
            path = 'ui/digits/g%d.png' % i
            imgs.append(pyglet.resource.image(path))
        cls.images = imgs

    def __init__(self, pos, value=0, anchor=ANCHOR_RIGHT):
        self.pos = pos
        self.anchor = anchor
        self.value = value
        self.display_value = value
        self.color = MUTAGEN_COLOR
        self.alpha = 255

    def set(self, value):
        self.value = value

    def get_digits(self):
        return [int(c) for c in str(int(self.display_value + 0.5))]

    def get_width(self):
        w = 0
        for d in self.get_digits():
            w += self.images[d].width
        return w
    
    def update(self, dt):
        self.display_value = self.value + (self.display_value - self.value) * 0.1 ** (dt * 2)

    def draw(self):
        p = self.pos
        w = self.get_width()
        p += v(-1, 0) * w * self.anchor

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        col = self.color + (self.alpha,)
        gl.glColor4ub(*col)
        for d in self.get_digits():
            img = self.images[d]
            img.blit(*p)
            p += v(1, 0) * img.width
        gl.glColor4f(1, 1, 1, 1)


class DigitsActor(object):
    body = None
    name = ''
    def __init__(self, pos, value):
        self.digits = Digits(pos, value, anchor=Digits.ANCHOR_CENTER)
        self.digits.color = self.COLOR
        self.age = 0

    def update(self, dt):
        self.digits.pos += v(0, 15) * dt
        self.age += dt
        if self.age >= 1:
            self.world.destroy(self)
        else:
            self.digits.alpha = int((1 - self.age) * 255 + 0.5)

    def get_shapes(self):
        return []

    def draw(self):
        self.digits.draw()


class DamageActor(DigitsActor):
    COLOR = DAMAGE_COLOR
