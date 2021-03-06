from collections import namedtuple
import pyglet
from pyglet import gl

from vector import v
from geom import Rect

from .monster import *
from .digits import Digits


ICON_HEIGHT = 64
ICON_HALF = ICON_HEIGHT * 0.5
MARGIN = 10
ICON_SEP = 5

 


class PartIcon(object):
    def __init__(self, name, sprite, cost=100):
        self.name = name
        self.sprite = sprite
        self.disabled = False
        self.cost = cost

    def set_disabled(self, disabled):
        self.disabled = disabled
        if disabled:
            self.sprite.opacity = 128
        else:
            self.sprite.opacity = 255

    def contains(self, point):
        x, y = self.sprite.position
        l = x - ICON_HALF
        r = x + ICON_HALF
        b = y - ICON_HALF
        t = y + ICON_HALF

        return l <= point.x < r and b <= point.y < t


class PartHud(object):
    @classmethod
    def load(cls):
        cls.healthbar_full = pyglet.resource.image('ui/healthbar-full.png')
        cls.healthbar_empty = pyglet.resource.image('ui/healthbar-empty.png')
        cls.star = pyglet.resource.image('ui/upgrade-star.png')
        cls.upgrade_button = pyglet.resource.image('ui/upgrade-button.png')

    def __init__(self, part):
        self.part = part
        self.locked = False # whether to destroy it on mouseout
        self.upgrade_button_rect = None

    def dead(self):
        return self.part not in self.part.monster.parts

    def draw(self, camera):
        frac = min(1, float(self.part.health) / self.part.get_max_health())

        pos = self.part.get_position() + v(0, self.part.get_base_shape().radius)
        pos = camera.world_to_screen(pos)
        pos = v(int(pos.x + 0.5), int(pos.y + 0.5))
        
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        w = self.healthbar_empty.width
        h = self.healthbar_empty.height

        p = pos - v(w/2, 0)
        self.healthbar_empty.blit(*p)

        fillw = frac * w
        fill = self.healthbar_full.get_region(0, 0, fillw, h)
        fill.blit(*p)
        if hasattr(self.part, 'level'):
            self.draw_level(p + v(0, 20))

    def draw_level(self, pos):
        p = pos
        for i in range(self.part.level):
            self.star.blit(*p)
            p += v(self.star.width, 0)
        if self.part.can_upgrade():
            p = pos + v(self.healthbar_empty.width - self.upgrade_button.width, 0)
            self.upgrade_button.blit(*p)
            self.upgrade_button_rect = Rect(p + v(0, self.upgrade_button.height), p + v(self.upgrade_button.width, 0))


IconDef = namedtuple('IconDef', 'name sprite cost')


ICONS = [
    #IconDef('arm', 'sprites/icon-arm.png', 500),
    #IconDef('claw', 'sprites/icon-claw.png', 300),
    IconDef('thistlegun', 'sprites/icon-thistlegun.png', 250),
    IconDef('scales', 'sprites/icon-scales.png', 25),
    IconDef('spikes', 'sprites/icon-spikes.png', 25),
    IconDef('leg', 'sprites/icon-leg.png', 500),
    IconDef('heart', 'sprites/icon-heart.png', 125),
    IconDef('lung', 'sprites/icon-lung.png', 200),
    IconDef('mutagenbladder', 'sprites/icon-mutagenbladder.png', 75),
    IconDef('wing', 'sprites/icon-wing.png', 75),
    IconDef('eyeball', 'sprites/icon-eyeball.png', 5),
]


class Shelf(object):
    """A heads-up display that displays icons for the various parts
    that the player can attach to a monster.
    """

    @classmethod
    def load(cls):
        PartHud.load()
        Digits.load()
        imgs = {}
        for icon in ICONS:
            img = pyglet.resource.image(icon.sprite)
            img.anchor_x = 90 - ICON_HALF
            img.anchor_y = ICON_HALF
            imgs[icon.name] = img

        cls.mutagen_label = pyglet.sprite.Sprite(pyglet.resource.image('ui/mutagen.png'))
        cls.cost_label = pyglet.sprite.Sprite(pyglet.resource.image('ui/cost.png'))
        cls.mutagen_label.position = v(20, 440)
        cls.cost_label.position = v(200, 443)
        cls.images = imgs

    def __init__(self, world, monster, camera):
        self.world = world
        self.monster = monster
        self.camera = camera
        self.icons = {}
        self.init_icons()
        self.scroll_y = 0
        self.mousedown = False
        self.parthud = None

        self.mutagen_count = Digits(v(20, 410), anchor=Digits.ANCHOR_LEFT)
        self.cost_display = Digits(v(200, 410), anchor=Digits.ANCHOR_LEFT)
        self.cost_value = None

    def init_icons(self):
        self.batch = pyglet.graphics.Batch()
        x = 853 - ICON_HALF - MARGIN
        y = 400 + ICON_HALF - MARGIN
        for icon in ICONS:
            s = pyglet.sprite.Sprite(self.images[icon.name], batch=self.batch)
            s.set_position(x, y)
            particon = PartIcon(icon.name, s, cost=icon.cost)
            if icon.name not in PART_CLASSES:
                particon.set_disabled(True)
            self.icons[icon.name] = particon 
            y -= ICON_HEIGHT + ICON_SEP

        self.height = ICON_SEP - y

        # Mouse handling
        self.draggedicon = None
        self.draggedpart = None

    def update(self, dt):
        if not self.mousedown:
            if self.scroll_y < 0:
                self.scroll_y *= 0.001 ** dt
            max_scroll = self.height - 30
            if self.scroll_y > max_scroll:
                self.scroll_y = max_scroll + (self.scroll_y - max_scroll) * 0.001 ** dt

        v = self.monster.mutagen
        for i in self.icons.values():
            i.set_disabled(i.cost > v)
        self.mutagen_count.value = v
        self.mutagen_count.update(dt)

    def get_icon(self, name):
        return self.icons[name]

    def draw(self):
        if self.draggedpart:
            self.draggedpart.draw()
        gl.glLoadIdentity()
        if self.parthud:
            if self.parthud.dead():
                self.parthud = None
            else:
                self.parthud.draw(self.camera)
        gl.glTranslatef(0, self.scroll_y, 0)
        self.batch.draw()
        gl.glLoadIdentity()
        self.mutagen_label.draw()
        self.mutagen_count.draw()
        if self.cost_value:
            self.cost_label.draw()
            self.cost_display.value = self.cost_value
            self.cost_display.display_value = self.cost_value
            self.cost_display.draw()

    def icon_for_point(self, x, y):
        point = v(x, y) - v(0, self.scroll_y)
        for i in self.icons.values():
            if i.contains(point) and not i.disabled:
                return i.name

    def on_mouse_press(self, x, y, button, modifiers):
        self.draggedicon = self.icon_for_point(x, y)
        if self.parthud:
            s = v(x, y)
            if self.parthud.upgrade_button_rect and self.parthud.upgrade_button_rect.contains(s):
                self.parthud.part.upgrade()
            else:
                wpos = self.camera.screen_to_world(s)
                for m in self.world.monsters:
                    part = m.colliding_point(wpos)
                    if part and part is self.parthud.part:
                        break
                else:
                    self.parthud = None
        self.mousedown = True

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if x > (853 - ICON_HEIGHT - MARGIN):
            if scroll_y > 0:
                if self.scroll_y > 0:
                    self.scroll_y = max(0, self.scroll_y - scroll_y * 30)
            else:
                max_scroll = self.height - 30
                if self.scroll_y < max_scroll:
                    self.scroll_y = min(max_scroll, self.scroll_y - scroll_y * 30)

    def on_mouse_motion(self, x, y, dx, dy):
        icon = self.icon_for_point(x, y)
        if icon:
            self.cost_value = self.icons[icon].cost
        else:
            self.cost_value = None
        if self.parthud:
            s = v(x, y)
            if self.parthud.upgrade_button_rect and self.parthud.upgrade_button_rect.contains(s):
                self.cost_value = self.parthud.part.upgrade_cost()
            if self.parthud.locked:
                return
        wpos = self.camera.screen_to_world(v(x, y))
        for m in self.world.monsters:
            part = m.colliding_point(wpos)
            if part:
                break
        else:
            if self.parthud and not self.parthud.locked:
                self.parthud = None
            return
    
        if self.parthud is None or part is not self.parthud.part:
            self.parthud = PartHud(part)

    def create_virtual_part(self, name, pos):
        try:
            cls = PART_CLASSES[name]
        except KeyError:
            return None
        else:
            cls = cls(pos)
            cls.cost = self.icons[name].cost
            cls.set_style(STYLE_INVALID)
            return cls

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if x > (853 - ICON_HEIGHT - MARGIN) and not self.draggedpart:
            self.scroll_y += dy

        wpos = self.camera.screen_to_world(v(x, y))
        if self.draggedicon and x < (853 - ICON_HEIGHT - MARGIN):
            self.draggedpart = self.create_virtual_part(self.draggedicon, wpos)
            self.draggedicon = None

        if self.draggedpart:
            self.draggedpart.set_position(wpos)
            attachment = self.monster.attachment_point(self.draggedpart)
            if attachment is not None:
                self.draggedpart.position_to_joint(attachment[1] - attachment[2])
                self.draggedpart.set_position(attachment[1])
                self.draggedpart.set_style(STYLE_VALID)
            else:
                self.draggedpart.set_style(STYLE_INVALID)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.draggedpart:
            wpos = self.camera.screen_to_world(v(x, y))
            self.draggedpart.set_position(wpos)
            try:
                self.monster.attach_and_grow(self.draggedpart)
            except ValueError:
                pass
            else:
                self.monster.spend_mutagen(self.draggedpart.cost)
        elif self.parthud:
            self.parthud.locked = True
        self.draggedpart = None
        self.draggedicon = None
        self.mousedown = False
