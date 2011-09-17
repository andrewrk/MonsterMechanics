from pyglet.gl import gl

from .vector import v
from .geom import Rect

MARGIN = 120

class Camera(object):
    def __init__(self, center, viewport_width, viewport_height):
        self.center = center
        self.viewport_offset = v(viewport_width, viewport_height) * 0.5
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.scale = 1
        self.target = None 
        self.target_scale = 1

    def track_bounds(self, bounds):
        br = v(bounds.br.x, 0)
        self.target = (bounds.tl + br) * 0.5 
        self.target = v(self.target.x, self.viewport_height * 0.5)
        self.target_scale = min(1, (self.viewport_width - MARGIN * 2) / bounds.width(), (self.viewport_height - MARGIN) / bounds.height())

    def update(self, dt):
        self.scale = self.target_scale + (self.scale - self.target_scale) * 0.2 ** dt
        self.center = self.target + (self.center - self.target) * 0.2 ** dt
        if self.center.y > self.viewport_height * 0.5 / self.scale:
            self.center = v(self.center.x, self.viewport_height * 0.5 / self.scale)

    def screen_to_world(self, s):
        s += self.center - self.viewport_offset
        s /= self.scale
        return s

    def set_matrix(self):
        gl.glLoadIdentity()
        gl.glTranslatef(self.viewport_offset.x, self.viewport_offset.y, 0)
        x, y = self.center
        gl.glScalef(self.scale, self.scale, 1)
        gl.glTranslatef(int(-x + 0.5), int(-y + 0.5), 0)
