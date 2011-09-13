import pyglet
from pyglet import gl

from vector import v

from .monster import Head, Lung, STYLE_INVALID, STYLE_VALID


ICON_HEIGHT = 64
ICON_HALF = ICON_HEIGHT * 0.5
MARGIN = 10
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
        l = x - ICON_HALF
        r = x + ICON_HALF
        b = y - ICON_HALF
        t = y + ICON_HALF

        return l <= point.x < r and b <= point.y < t


class VirtualPart(object):
    pass


class Shelf(object):
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

    PARTS = {
        'head': Head,
        'lung': Lung
    }
    
    @classmethod
    def load(cls):
        imgs = {}
        for name, path in cls.IMAGES:
            img = pyglet.resource.image(path)
            img.anchor_x = 90 - ICON_HALF
            img.anchor_y = ICON_HALF
            imgs[name] = img
        cls.images = imgs

    def __init__(self, world, monster):
        self.world = world
        self.monster = monster
        self.icons = {}
        self.init_icons()

    def init_icons(self):
        self.batch = pyglet.graphics.Batch()
        x = 853 - ICON_HALF - MARGIN
        y = 400 + ICON_HALF - MARGIN
        for name, path in self.IMAGES:
            s = pyglet.sprite.Sprite(self.images[name], batch=self.batch)
            s.set_position(x, y)
            particon = PartIcon(name, s)
            if name not in self.PARTS:
                particon.set_disabled(True)
            self.icons[name] = particon 
            y -= ICON_HEIGHT + ICON_SEP

        # Mouse handling
        self.draggedicon = None
        self.draggedpart = None

    def get_icon(self, name):
        return self.icons[name]

    def draw(self):
        gl.glLoadIdentity()
        if self.draggedpart:
            self.draggedpart.draw()
        self.batch.draw()

    def icon_for_point(self, x, y):
        point = v(x, y)
        for i in self.icons.values():
            if i.contains(point):
                return i.name

    def on_mouse_press(self, x, y, button, modifiers):
        self.draggedicon = self.icon_for_point(x, y)

    def create_virtual_part(self, name, pos):
        try:
            cls = self.PARTS[name]
        except KeyError:
            return None
        else:
            cls = cls(pos)
            cls.set_style(STYLE_INVALID)
            return cls

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if self.draggedicon and x < (853 - ICON_HEIGHT - MARGIN):
            self.draggedpart = self.create_virtual_part(self.draggedicon, v(x, y))
            self.draggedicon = None

        if self.draggedpart:
            self.draggedpart.set_position(v(x, y))
            attachment = self.monster.attachment_point(self.draggedpart)
            if self.monster.can_attach(self.draggedpart):
                self.draggedpart.set_position(attachment[1])
                self.draggedpart.set_style(STYLE_VALID)
            else:
                self.draggedpart.set_style(STYLE_INVALID)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.draggedpart:
            self.draggedpart.set_position(v(x, y))
            try:
                self.monster.attach_and_grow(self.draggedpart)
            except ValueError:
                pass
        self.draggedpart = None
        self.draggedicon = None
