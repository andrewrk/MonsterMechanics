from pyglet.gl import gl

from .vector import v
from .geom import Rect


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
    
    def update(self, dt):
        self.scale = self.target_scale + (self.scale - self.target_scale) * 0.2 ** dt
        self.center = self.target + (self.center - self.target) * 0.2 ** dt

    def screen_to_world(self, s):
        s /= self.scale
        s += self.center - self.viewport_offset
        return s

    def set_matrix(self):
        gl.glLoadIdentity()
        x, y = self.center - self.viewport_offset
        gl.glTranslatef(int(-x + 0.5), int(-y + 0.5), 0)
        gl.glScalef(self.scale, self.scale, 1)
