import pyglet
from pyglet.gl import gl

from vector import v


class Background(object):
    @classmethod
    def load(cls):
        # create background
        cls.clouds = pyglet.resource.image('cloudsbg.png')
        cls.fg = pyglet.resource.image('fg.png')

    def __init__(self, window):
        self.window = window

    def set_scroll(self, v):
        self.scroll = v 

    def draw(self, viewport):
        gl.glClearColor(183 / 255.0, 196 / 255.0, 200 / 255.0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        x1 = viewport.tl.x
        x2 = viewport.br.x

        backgrounds = [
            (self.clouds, self.clouds.width), 
            (self.fg, self.fg.width), 
        ]

        for img, w in backgrounds:
            cx = x1 - x1 % w - w
            while cx < x2:
                img.blit(cx, 0)
                cx += w
