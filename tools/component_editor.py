#!/usr/bin/python

import sys
import pygame
import math
import json


def dist(a, b):
    ax, ay = a
    bx, by = b

    return math.sqrt(((ax - bx) ** 2) + ((ay - by) ** 2))


class Editor(object):
    RED = pygame.Color('red')
    BLUE = pygame.Color('blue')

    def __init__(self, name, radius, offset):
        self.name = name
        self.radius = radius
        self.offset = offset
        self.handle = (radius, 0)

        self.handle_hover = False

        self.lastpos = 0, 0
        self.dragging = None

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
            return Editor(name, dat.get('radius', 50), dat.get('offset', (0, 0)))
    
    def as_json(self):
        return {
            'name': 'data/sprites/%s.png' % self.name,
            'radius': self.radius,
            'offset': self.offset
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
        self.draw()
        while True:
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = self.screen_to_rel(event.pos)
                if dist(pos, self.handle) < 3:
                    self.dragging = 'handle'
                else:
                    self.dragging = 'sprite'
                self.lastpos = pos
            elif event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP]:
                pos = self.screen_to_rel(event.pos)
                self.handle_hover = self.dragging == 'handle' or dist(pos, self.handle) < 3

                dx = pos[0] - self.lastpos[0]
                dy = pos[1] - self.lastpos[1]

                if self.dragging == 'handle':
                    hx, hy = self.handle
                    hx += dx
                    hy += dy
                    self.handle = hx, hy
                    self.radius = int(math.sqrt(self.handle[0] ** 2 + self.handle[1] ** 2) + 0.5)
                elif self.dragging == 'sprite':
                    ox, oy = self.offset
                    ox += pos[0] - self.lastpos[0]
                    oy += pos[1] - self.lastpos[1]
                    self.offset = ox, oy

                self.lastpos = pos
                
                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = None
                    self.dragstart = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.offset = (self.offset[0], self.offset[1] - 1)
                elif event.key == pygame.K_DOWN:
                    self.offset = (self.offset[0], self.offset[1] + 1)
                elif event.key == pygame.K_LEFT:
                    self.offset = (self.offset[0] - 1, self.offset[1])
                elif event.key == pygame.K_RIGHT:
                    self.offset = (self.offset[0] + 1, self.offset[1])
                elif event.key == pygame.K_s:
                    self.save()
                elif event.key == pygame.K_ESCAPE:
                    break

            self.draw()

    def screen_to_rel(self, coord):
        x, y = coord
        return x - 400, y - 240

    def rel_to_screen(self, coord):
        x, y = coord
        return x + 400, y + 240

    def draw(self):
        ring = self.BLUE if self.handle_hover else self.RED
        self.screen.fill(pygame.Color(60, 60, 60))
        self.screen.blit(self.image, self.rel_to_screen(self.offset))
        pygame.draw.circle(self.screen, ring, (400, 240), self.radius, 1) 
        pygame.draw.circle(self.screen, self.RED, (400, 240), 0) 
        pygame.draw.circle(self.screen, ring, self.rel_to_screen(self.handle), 3, 1)
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
