import pyglet
from pyglet import gl


ICON_HEIGHT = 64
ICON_SEP = 5

class PartIcon(object):
    def __init__(self, sprite):
        self.sprite = sprite
        self.disabled = False

    def set_disabled(self, disabled):
        self.disabled = disabled
        if disabled:
            self.sprite.opacity = 128
        else:
            self.sprite.opacity = 255


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
            imgs[name] = img
        cls.images = imgs

    def __init__(self):
        self.icons = {}
        self.batch = pyglet.graphics.Batch()
        y = 0
        for name, path in self.IMAGES:
            s = pyglet.sprite.Sprite(self.images[name], batch=self.batch)
            s.set_position(0, y)
            self.icons[name] = PartIcon(s)
            y -= ICON_HEIGHT + ICON_SEP

    def get_icon(self, name):
        return self.icons[name]

    def draw(self):
        gl.glPushMatrix(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(750, 400, 0.0)
        self.batch.draw()
        gl.glPopMatrix(gl.GL_MODELVIEW)
