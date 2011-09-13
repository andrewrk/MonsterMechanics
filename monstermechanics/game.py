from __future__ import division, print_function, unicode_literals; range = xrange

import pyglet
from pyglet.window import key
from pyglet import gl
from vector import v
from .physics import get_physics

from .hud import Shelf
from .monster import Monster
from .background import Background

import math


name = "Monster Mechanics"
target_fps = 60


class Control:
    MoveLeft = 0
    MoveRight = 1
    MoveUp = 2
    MoveDown = 3
    Rotate1 = 4
    Rotate2 = 5
    Rotate3 = 6
    Rotate4 = 7
    Rotate5 = 8
    Rotate6 = 9


class Game(object):
    def __init__(self, width=853, height=480, show_fps=True):
        self.size = v(width, height)
        self.show_fps = show_fps

        self.next_group_num = 0

        self.controls = {
            key.LEFT: Control.MoveLeft,
            key.RIGHT: Control.MoveRight,
            key.UP: Control.MoveUp,
            key.DOWN: Control.MoveDown,

            key._1: Control.Rotate1,
            key._2: Control.Rotate2,
            key._3: Control.Rotate3,
            key._4: Control.Rotate4,
            key._5: Control.Rotate5,
            key._6: Control.Rotate6,
        }

        self.control_state = [False] * (len(dir(Control)) - 2)
        self.scroll = v(0,0)


    def buildMonster(self):
        head = self.makeBodyPart('head-level1')
        leg = self.makeBodyPart('leg-level1')
        leg.rotation = math.pi /2
        claw = self.makeBodyPart('claws-level1')

        head.attach_part(leg, 50, math.pi * 3 / 2)
        leg.attach_part(claw, 120, math.pi * 3 / 2)

        self.monster = Monster(head)
        self.monster.pos = v(200, 300)

        self.monster.cacheBoundingBox()
        img = pyglet.resource.image('debugbox.png')
        self.test = [pyglet.sprite.Sprite(img, batch=self.batch_level) for x in range(4)]

        self.leg = leg
        self.claw = claw

    def getNextGroupNum(self):
        val = self.next_group_num
        self.next_group_num += 1
        return val

    def update(self, dt):
        self.monster.update(dt)
        self.world.update(dt)
        self.hud.update(dt)

    def on_draw(self):
        self.window.clear()
        self.background.draw()
        self.monster.draw()

        # hud
        gl.glLoadIdentity()
        self.hud.draw()
        if self.show_fps:
            self.fps_display.draw()
        
    def start(self):
        self.window = pyglet.window.Window(width=self.size.x, height=self.size.y, caption=name)

        Background.load()
        self.background = Background(self.window)

        #self.buildMonster()
        physics = get_physics()
        self.world = physics.create_world(gravity=v(0, -500))
        self.world.create_ground(20)
        self.monster = Monster.create_initial(self.world, v(50, 200))

        Shelf.load()
        self.hud = Shelf(self.world, self.monster)

        self.fps_display = pyglet.clock.ClockDisplay()

        pyglet.clock.schedule_interval(self.update, 1/target_fps)
        self.window.set_handlers(
            on_draw=self.on_draw,
            on_key_press=self.on_key_press,
            on_key_release=self.on_key_release,
            on_mouse_press=self.hud.on_mouse_press,
            on_mouse_release=self.hud.on_mouse_release,
            on_mouse_drag=self.hud.on_mouse_drag,
            on_mouse_scroll=self.hud.on_mouse_scroll,
        )

        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F12: 
            from .screenshot import take_screenshot
            take_screenshot(self.window)
            return
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
