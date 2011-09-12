from __future__ import division, print_function, unicode_literals; range = xrange

import pyglet
from vec2d import Vec2d

from monster import Monster, BodyPart

import math
import json

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
        self.size = Vec2d(width, height)
        self.show_fps = show_fps

        self.next_group_num = 0

        self.controls = {
            pyglet.window.key.LEFT: Control.MoveLeft,
            pyglet.window.key.RIGHT: Control.MoveRight,
            pyglet.window.key.UP: Control.MoveUp,
            pyglet.window.key.DOWN: Control.MoveDown,

            pyglet.window.key._1: Control.Rotate1,
            pyglet.window.key._2: Control.Rotate2,
            pyglet.window.key._3: Control.Rotate3,
            pyglet.window.key._4: Control.Rotate4,
            pyglet.window.key._5: Control.Rotate5,
            pyglet.window.key._6: Control.Rotate6,
        }

        self.control_state = [False] * (len(dir(Control)) - 2)

        self.part_definitions = {}

        self.scroll = Vec2d(0,0)

    def makeBodyPart(self, name):
        try:
            definition = self.part_definitions[name]
        except KeyError:
            with pyglet.resource.file('components/%s.json' % name) as f:
                definition = json.loads(f.read())

            # add image to it
            img = pyglet.resource.image(definition['name'])
            # <mauve> [offset is] the amount you have to translate the image
            # <mauve> So -1 * the position of the centre in the image
            # also we have to flip the y axis because this is pyglet
            img.anchor_x = -definition['offset'][0]
            img.anchor_y = img.height+definition['offset'][1]
            definition['img'] = img

            # cache it
            self.part_definitions[name] = definition
        
        sprite = pyglet.sprite.Sprite(definition['img'])
        return BodyPart(sprite)

    def buildMonster(self):
        head = self.makeBodyPart('head-level1')
        leg = self.makeBodyPart('leg-level1')
        leg.rotation = math.pi /2
        claw = self.makeBodyPart('claws-level1')

        head.attach_part(leg, 50, math.pi * 3 / 2)
        leg.attach_part(claw, 120, math.pi * 3 / 2)

        self.monster = Monster(head)
        self.monster.pos = Vec2d(200, 300)

        self.leg = leg
        self.claw = claw

    def getNextGroupNum(self):
        val = self.next_group_num
        self.next_group_num += 1
        return val

    def update(self, dt):
        if self.control_state[Control.MoveLeft]:
            self.monster.pos.x -= 50 * dt
        if self.control_state[Control.MoveRight]:
            self.monster.pos.x += 50 * dt
        if self.control_state[Control.MoveUp]:
            self.monster.pos.y += 50 * dt
        if self.control_state[Control.MoveDown]:
            self.monster.pos.y -= 50 * dt
        if self.control_state[Control.Rotate1]:
            self.leg.rotation += math.pi * .5 * dt
        if self.control_state[Control.Rotate2]:
            self.leg.rotation -= math.pi * .5 * dt
        if self.control_state[Control.Rotate3]:
            self.claw.rotation += math.pi * .5 * dt
        if self.control_state[Control.Rotate4]:
            self.claw.rotation -= math.pi * .5 * dt
        if self.control_state[Control.Rotate5]:
            self.scroll.x += 100 * dt
        if self.control_state[Control.Rotate6]:
            self.scroll.x -= 100 * dt

    def on_draw(self):
        self.window.clear()

        # far bg
        far_bgpos = Vec2d(-((self.scroll.x * 0.25) % self.sprite_bg2_left.width), -(self.scroll.y * 0.10))
        if far_bgpos.y > 0:
            far_bgpos.y = 0
        if far_bgpos.y + self.sprite_bg2_left.height < self.window.height:
            far_bgpos.y = self.window.height - self.sprite_bg2_left.height
        far_bgpos.do(int)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(far_bgpos.x, far_bgpos.y, 0.0)
        self.batch_bg2.draw()

        # close bg
        close_bgpos = Vec2d(-((self.scroll.x * 0.5) % self.sprite_bg_left.width), -(self.scroll.y * 0.20))
        if close_bgpos.y > 0:
            close_bgpos.y = 0
        close_bgpos.do(int)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(close_bgpos.x, close_bgpos.y, 0.0)
        self.batch_bg1.draw()

        # level
        floored_scroll = -self.scroll.done(int)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(floored_scroll.x, floored_scroll.y, 0.0)
        self.batch_level.draw()
        self.monster.draw()

        # hud
        pyglet.gl.glLoadIdentity()
        self.batch_static.draw()
        if self.show_fps:
            self.fps_display.draw()
        
    def start(self):
        self.window = pyglet.window.Window(width=self.size.x, height=self.size.y, caption=name)

        # create batches
        self.batch_bg2 = pyglet.graphics.Batch()
        self.batch_bg1 = pyglet.graphics.Batch()
        self.batch_level = pyglet.graphics.Batch()
        self.batch_static = pyglet.graphics.Batch()

        # create groups

        # create background
        img = pyglet.resource.image('cloudsbg.png')
        self.sprite_bg_left = pyglet.sprite.Sprite(img, batch=self.batch_bg1)
        self.sprite_bg_right = pyglet.sprite.Sprite(img, batch=self.batch_bg1)
        self.sprite_bg_left.set_position(0, 300)
        self.sprite_bg_right.set_position(self.sprite_bg_left.width, 300)

        img = pyglet.resource.image('bg.png')
        self.sprite_bg2_left = pyglet.sprite.Sprite(img, batch=self.batch_bg2)
        self.sprite_bg2_right = pyglet.sprite.Sprite(img, batch=self.batch_bg2)
        self.sprite_bg2_left.set_position(0, 0)
        self.sprite_bg2_left.set_position(self.sprite_bg2_left.width, 0)

        # create level
        img = pyglet.resource.image('fg.png')
        self.sprite_level_left = pyglet.sprite.Sprite(img, batch=self.batch_level)
        self.sprite_level_right = pyglet.sprite.Sprite(img, batch=self.batch_level)
        self.sprite_level_left.set_position(0, 0)
        self.sprite_level_left.set_position(self.sprite_level_left.width, 0)

        self.buildMonster()

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
