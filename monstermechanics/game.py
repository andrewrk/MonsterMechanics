from __future__ import division, print_function, unicode_literals; range = xrange

import pyglet
from pyglet.window import key
from pyglet import gl
from vector import v
from .physics import get_physics

from .camera import Camera
from .hud import Shelf
from .monster import Monster, LEFT, RIGHT
from .background import Background
from .world import World

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
    Attack = 10


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
            key.SPACE: Control.Attack,

            key._1: Control.Rotate1,
            key._2: Control.Rotate2,
            key._3: Control.Rotate3,
            key._4: Control.Rotate4,
            key._5: Control.Rotate5,
            key._6: Control.Rotate6,
        }

        self.control_state = [False] * (len(dir(Control)) - 2)
        self.scroll = v(0,0)
        self.filename = None
        self.enemy = None
        self.camera = None


    def getNextGroupNum(self):
        val = self.next_group_num
        self.next_group_num += 1
        return val

    def update(self, dt):
        if self.control_state[Control.MoveLeft]:
            self.monster.moving = LEFT
        elif self.control_state[Control.MoveRight]:
            self.monster.moving = RIGHT
        else:
            self.monster.moving = 0

        if self.control_state[Control.Attack]:
            self.monster.attack()

        self.monster.update(dt)
        self.world.update(dt)
        self.hud.update(dt)
        self.camera.track_bounds(self.world.get_monster_bounds())
        self.camera.update(dt)

    def on_draw(self):
        self.window.clear()
        self.camera.set_matrix()
        self.background.draw()
        self.world.draw()

        # hud
        self.hud.draw()
        if self.show_fps:
            self.fps_display.draw()
        
    def start(self):
        Monster.load_all()
        self.window = pyglet.window.Window(width=self.size.x, height=self.size.y, caption=name)
        self.camera = Camera(v(self.size.x, self.size.y) * 0.5, self.size.x, self.size.y)

        Background.load()
        self.background = Background(self.window)

        self.world = World()
        self.monster = Monster.create_initial(self.world, v(400, 80))
        self.world.add_monster(self.monster)

        if self.filename is not None:
            self.world.add_monster(Monster.enemy_from_json(self.world, self.filename))

        Shelf.load()
        self.hud = Shelf(self.world, self.monster, self.camera)

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

    def save(self):
        import json
        import datetime
        import pprint
        from .screenshot import take_screenshot
        fname = datetime.datetime.now().strftime('mutants/mutant-%Y-%m-%d_%H:%M:%S.%f')
        take_screenshot(self.window, filename=fname + '.jpg')
        pprint.pprint(self.monster.to_json())
        with open(fname + '.json', 'w') as f:
            f.write(json.dumps(self.monster.to_json(), indent=2))

    def on_key_press(self, symbol, modifiers):
        if symbol == key.F12: 
            from .screenshot import take_screenshot
            take_screenshot(self.window)
            return
        elif symbol == key.F2: 
            self.save()
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
