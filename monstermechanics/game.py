from __future__ import division, print_function, unicode_literals; range = xrange

import pyglet
from vec2d import Vec2d

name = "Monster Mechanics"
target_fps = 60

class Control:
    MoveLeft = 0
    MoveRight = 1
    MoveUp = 2
    MoveDown = 3

class Game(object):
    def __init__(self, width=853, height=480, show_fps=True):
        self.size = Vec2d(width, height)
        self.show_fps = show_fps

        self.next_group_num = 0

        self.controls = {
            pyglet.window.key.LEFT: Control.MoveLeft,
            pyglet.window.key.RIGHT: Control.MoveRight,
            pyglet.window.key.UP: Control.MoveUp,
            pyglet.window.key.DOWN: Control.MoveDown,
        }

        self.control_state = [False] * (len(dir(Control)) - 2)

    def getNextGroupNum(self):
        val = self.next_group_num
        self.next_group_num += 1
        return val

    def update(self, dt):
        if self.control_state[Control.MoveLeft]:
            self.circle_pos.x -= 50 * dt
        if self.control_state[Control.MoveRight]:
            self.circle_pos.x += 50 * dt
        if self.control_state[Control.MoveUp]:
            self.circle_pos.y += 50 * dt
        if self.control_state[Control.MoveDown]:
            self.circle_pos.y -= 50 * dt

        self.circle_sprite.set_position(*self.circle_pos)

    def on_draw(self):
        self.window.clear()

        self.batch_main.draw()

        if self.show_fps:
            self.fps_display.draw()
        
    def start(self):
        self.window = pyglet.window.Window(width=self.size.x, height=self.size.y, caption=name)

        self.img_circle = pyglet.resource.image('monster.png')

        self.batch_main = pyglet.graphics.Batch()
        self.group_main = pyglet.graphics.OrderedGroup(self.getNextGroupNum())

        self.circle_pos = Vec2d(100, 100)
        self.circle_sprite = pyglet.sprite.Sprite(self.img_circle, group=self.group_main, batch=self.batch_main, x=self.circle_pos.x, y=self.circle_pos.y)

        self.fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self.update, 1/target_fps)
        self.window.set_handler('on_draw', self.on_draw)
        self.window.set_handler('on_key_press', self.on_key_press)
        self.window.set_handler('on_key_release', self.on_key_release)

        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        try:
            control = self.controls[symbol]
            self.control_state[control] = True
        except KeyError:
            return

    def on_key_release(self, symbol, modifiers):
        try:
            control = self.controls[symbol]
            self.control_state[control] = False
        except KeyError:
            return
