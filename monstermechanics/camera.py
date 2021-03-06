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
        hlimit = self.viewport_height * 0.5 / self.scale
        self.center = v(self.center.x, hlimit)

    def screen_to_world(self, s):
        return self.center + (s - self.viewport_offset) / self.scale

    def world_to_screen(self, w):
        return (w - self.center) * self.scale + self.viewport_offset

    def get_viewport(self):
        tl = v(0, self.viewport_height)
        br = v(self.viewport_width, 0)
        return Rect(self.screen_to_world(tl), self.screen_to_world(br))

    def set_matrix(self):
        gl.glLoadIdentity()
        gl.glTranslatef(self.viewport_offset.x, self.viewport_offset.y, 0)
        x, y = self.center
        gl.glScalef(self.scale, self.scale, 1)
        gl.glTranslatef(int(-x + 0.5), int(-y + 0.5), 0)
