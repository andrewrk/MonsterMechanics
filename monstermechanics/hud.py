import pyglet
from pyglet import gl

from vector import v


ICON_HEIGHT = 64
ICON_SEP = 5

class PartIcon(object):
    def __init__(self, name, sprite):
        self.name = name
        self.sprite = sprite
        self.disabled = False

    def set_disabled(self, disabled):
        self.disabled = disabled
        if disabled:
            self.sprite.opacity = 128
        else:
            self.sprite.opacity = 255

    def contains(self, point):
        x, y = self.sprite.position
        HALF = ICON_HEIGHT / 2.0
        l = x - HALF
        r = x + HALF
        b = y - HALF
        t = y + HALF

        return l <= point.x < r and b <= point.y < t


class PartsHud(object):
    """A heads-up display that displays icons for the various parts
    that the player can attach to a monster.
    """

    IMAGES = [
        ('armclaw', 'sprites/icon-armclaw.png'),
        ('leg', 'sprites/icon-leg.png'),
        ('scales', 'sprites/icon-scales.png'),
        ('spikes', 'sprites/icon-spikes.png'),
        ('heart', 'sprites/icon-heart.png'),
        ('lung', 'sprites/icon-lung.png'),
        ('wing', 'sprites/icon-wing.png'),
        ('eyeball', 'sprites/icon-eyeball.png'),
        ('thistlegun', 'sprites/icon-thistlegun.png'),
        ('mutagenbladder', 'sprites/icon-mutagenbladder.png'),
        ('eggsack', 'sprites/icon-eggsack.png'),
    ]
    
    @classmethod
    def load(cls):
        imgs = {}
        for name, path in cls.IMAGES:
            img = pyglet.resource.image(path)
            img.anchor_x = 90 - 32
            img.anchor_y = 32
            imgs[name] = img
        cls.images = imgs

    def __init__(self):
        self.icons = {}
        self.batch = pyglet.graphics.Batch()
        x = 853 - 42
        y = 400 + 42
        for name, path in self.IMAGES:
            s = pyglet.sprite.Sprite(self.images[name], batch=self.batch)
            s.set_position(x, y)
            self.icons[name] = PartIcon(name, s)
            y -= ICON_HEIGHT + ICON_SEP

        # Mouse handling
        self.mousedownpos = None
        self.dragging = False

    def get_icon(self, name):
        return self.icons[name]

    def draw(self):
        gl.glLoadIdentity()
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        point = v(x, y)
        for i in self.icons.values():
            if i.contains(point):
                print i.name 
                break
