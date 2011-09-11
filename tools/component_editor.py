#!/usr/bin/python

import sys
import pygame
import math
import json


def dist(a, b):
    ax, ay = a
    bx, by = b

    return math.sqrt(((ax - bx) ** 2) + ((ay - by) ** 2))


RED = pygame.Color('red')
BLUE = pygame.Color('blue')
GREEN = pygame.Color('#00aa00')



class Handle(object):
    """A draggable component that supports drag callbacks."""

    def __init__(self, pos, listeners=[]):
        self._pos = pos
        self.listeners = listeners[:]
        self.hovered = False
        self.selected = False

    def get_pos(self):
        return self._pos

    def set_pos(self, pos):
        self._pos = pos
        for l in self.listeners:
            l(pos)
        
    pos = property(get_pos, set_pos)

    def move_by(self, dx, dy):
        px, py = self.pos
        self.pos = (px + dx, py + dy)

    def add_move_listener(self, on_move):
        self.listeners.append(on_move)

    def contains(self, pos):
        return dist(pos, self.pos) < 3

    def draw(self, editor):
        color = BLUE if self.hovered else RED
        if self.selected:
            color = GREEN
        screen = editor.rel_to_screen(self.pos)
        pygame.draw.circle(editor.screen, color, screen, 3, 1)


class Circle(object):
    def __init__(self, name, offset, radius):
        self.name = name
        self.offset = offset
        self.radius = radius

        self.handles = [
            Handle(self.offset, listeners=[self.on_centrehandle_move]),
            Handle((self.offset[0] + self.radius, self.offset[1]), listeners=[self.on_radiushandle_move])
        ]

    def on_radiushandle_move(self, pos):
        hx, hy = pos
        hx -= self.offset[0]
        hy -= self.offset[1]
        self.radius = int(math.sqrt(hx * hx + hy * hy) + 0.5)

    def on_centrehandle_move(self, pos):
        ox, oy = self.offset
        ox = pos[0] - ox
        oy = pos[1] - oy
        self.offset = pos
        self.handles[1].move_by(ox, oy)

    def draw(self, editor):
        color = BLUE if any(h.hovered for h in self.handles) else RED
        pygame.draw.circle(editor.screen, color, editor.rel_to_screen(self.offset), self.radius, 1) 

        for h in self.handles:
            h.draw(editor)


class Editor(object):
    def __init__(self, name, radius, offset):
        self.name = name

        self.lastpos = 0, 0
        self.dragging = None

        self.shapes = []
        self.handles = []

        self.add_shape(Circle('base', offset, radius))
        self.selected = None

    def add_shape(self, shape):
        self.shapes.append(shape)
        self.handles += shape.handles

    @staticmethod
    def blank(name):
        return Editor(name, 50, (0, 0))

    @staticmethod
    def load(name, template=None):
        if template is not None:
            sname = template
        else:
            sname = name
        try:
            # load component from file
            with open('data/components/%s.json' % sname) as f:
                dat = json.loads(f.read())
        except (IOError, ValueError):
            return Editor.blank(name)
        else:
            ox, oy = dat.get('offset', (0, 0))
            ed = Editor(name, dat.get('radius', 50), (-ox, -oy))
            for p in dat.get('points', []):
                ed.add_shape(Circle(p['name'], p['offset'], p['radius']))
            return ed
    
    def as_json(self):
        ox, oy = self.shapes[0].offset
        radius = self.shapes[0].radius

        points = []
        for s in self.shapes[1:]:
            points.append({
                'name': s.name,
                'radius': s.radius,
                'offset': s.offset
            })
            
        return {
            'name': 'sprites/%s.png' % self.name,
            'radius': radius,
            'offset': (-ox, -oy),
            'points': points
        }

    def save(self):
        js = self.as_json()
        fname = 'data/components/%s.json' % self.name
        with open(fname, 'w') as f:
            f.write(json.dumps(js))
        print "Wrote", fname

    def show(self):
        pygame.display.init()
        pygame.key.set_repeat(150, 50)
        self.screen = pygame.display.set_mode((800, 480))
        print "Loading..."
        self.image = pygame.image.load("data/sprites/%s.png" % self.name).convert_alpha()
        w, h = self.image.get_size()
        self.img_off = -w // 2, -h // 2
        self.draw()
        while True:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.on_mousedown(event)
            elif event.type == pygame.MOUSEMOTION:
                self.on_mousemove(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.on_mouseup(event)
            elif event.type == pygame.KEYDOWN:
                self.on_keydown(event)

            self.draw()

    def set_selected(self, handle):
        if self.selected is not None:
            self.selected.selected = False
        if handle is not None:
            handle.selected = True
        self.selected = handle

    def on_mousedown(self, event):
        pos = self.screen_to_rel(event.pos)
        handle = self.handle_for_mouse(pos)
        if handle is not None:
            self.dragging = handle
            self.set_selected(handle)
        self.lastpos = pos

    def on_mouseup(self, event):
        self.on_mousemove(event)
        self.dragging = None

    def handle_for_mouse(self, pos):
        handle = None
        for h in self.handles:
            contains = h.contains(pos) 
            h.hovered = contains
            if contains:
                handle = h
        return handle

    def on_mousemove(self, event):
        pos = self.screen_to_rel(event.pos)

        dx = pos[0] - self.lastpos[0]
        dy = pos[1] - self.lastpos[1]

        if self.dragging:
            self.dragging.move_by(dx, dy)
        else:
            self.handle_for_mouse(pos)

        self.lastpos = pos

    def on_keydown(self, event):
        if self.selected:
            if event.key == pygame.K_UP:
                self.selected.move_by(0, -1)
            elif event.key == pygame.K_DOWN:
                self.selected.move_by(0, 1)
            elif event.key == pygame.K_LEFT:
                self.selected.move_by(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.selected.move_by(1, 0)
        elif event.key == pygame.K_a:
            self.add_shape(Circle('rel', (0, 0), 50))
        elif event.key == pygame.K_s:
            self.save()
        elif event.key == pygame.K_ESCAPE:
            sys.exit(0)

    def screen_to_rel(self, coord):
        x, y = coord
        iox, ioy = self.img_off
        return x - 400 - iox, y - 240 - ioy

    def rel_to_screen(self, coord):
        x, y = coord
        iox, ioy = self.img_off
        return x + iox + 400, y + ioy + 240

    def draw(self):
        #ring = BLUE if self.handle_hover else RED
        self.screen.fill(pygame.Color(60, 60, 60))
        self.screen.blit(self.image, self.rel_to_screen((0, 0)))
        #pygame.draw.circle(self.screen, ring, (400, 240), self.radius, 1) 
        #pygame.draw.circle(self.screen, self.RED, (400, 240), 0) 
        #pygame.draw.circle(self.screen, ring, self.rel_to_screen(self.handle), 3, 1)
        for shape in self.shapes:
            shape.draw(self)
        pygame.display.flip()


if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-t', '--template', help='Use TEMPLATE to initialise settings')

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("You must specify a component to edit.")
    
    component = args[0]
    e = Editor.load(component, template=options.template)
    e.show()
