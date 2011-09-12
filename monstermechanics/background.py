import pyglet
from pyglet.gl import gl

from vector import v


class Background(object):
    @classmethod
    def load(cls):
        # create background
        cls.clouds = pyglet.resource.image('cloudsbg.png')
        cls.bg = pyglet.resource.image('bg.png')
        cls.fg = pyglet.resource.image('fg.png')

    def __init__(self, window):
        self.window = window
        self.scroll = v(0, 0)
        # create batches
        self.batch_bg2 = pyglet.graphics.Batch()
        self.batch_bg1 = pyglet.graphics.Batch()
        self.batch_level = pyglet.graphics.Batch()

        # create groups
        img = self.clouds
        self.sprite_bg_left = pyglet.sprite.Sprite(img, batch=self.batch_bg1)
        self.sprite_bg_right = pyglet.sprite.Sprite(img, batch=self.batch_bg1)
        self.sprite_bg_left.set_position(0, 300)
        self.sprite_bg_right.set_position(self.sprite_bg_left.width, 300)

        img = self.bg
        self.sprite_bg2_left = pyglet.sprite.Sprite(img, batch=self.batch_bg2)
        self.sprite_bg2_right = pyglet.sprite.Sprite(img, batch=self.batch_bg2)
        self.sprite_bg2_left.set_position(0, 0)
        self.sprite_bg2_left.set_position(self.sprite_bg2_left.width, 0)

        # create level
        img = self.fg
        self.sprite_level_left = pyglet.sprite.Sprite(img, batch=self.batch_level)
        self.sprite_level_right = pyglet.sprite.Sprite(img, batch=self.batch_level)
        self.sprite_level_left.set_position(0, 0)
        self.sprite_level_left.set_position(self.sprite_level_left.width, 0)

    def set_scroll(self, v):
        self.scroll = v 

    def draw(self):
        # far bg
        far_bgpos = v(-((self.scroll.x * 0.25) % self.sprite_bg2_left.width), -(self.scroll.y * 0.10))
        if far_bgpos.y > 0:
            far_bgpos.y = 0
        if far_bgpos.y + self.sprite_bg2_left.height < self.window.height:
            far_bgpos.y = self.window.height - self.sprite_bg2_left.height
        far_bgpos = v(int(far_bgpos.x), int(far_bgpos.y))
        gl.glLoadIdentity()
        gl.glTranslatef(far_bgpos.x, far_bgpos.y, 0.0)
        self.batch_bg2.draw()

        # close bg
        close_bgpos = v(-((self.scroll.x * 0.5) % self.sprite_bg_left.width), -(self.scroll.y * 0.20))
        if close_bgpos.y > 0:
            close_bgpos.y = 0
        close_bgpos = v(int(far_bgpos.x), int(far_bgpos.y))
        gl.glLoadIdentity()
        gl.glTranslatef(close_bgpos.x, close_bgpos.y, 0.0)
        self.batch_bg1.draw()

        # level
        floored_scroll = -v(int(self.scroll.x), int(self.scroll.y))
        gl.glLoadIdentity()
        gl.glTranslatef(floored_scroll.x, floored_scroll.y, 0.0)
        self.batch_level.draw()
