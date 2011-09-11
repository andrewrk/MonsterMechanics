from __future__ import division, print_function, unicode_literals; range = xrange

import pyglet

import os

def setUpResources():
    # add data folder to pyglet resource path
    _this_py = os.path.abspath(os.path.dirname(__file__))
    _data_dir = os.path.normpath(os.path.join(_this_py, '..', 'data'))
    pyglet.resource.path = [_data_dir, 'data']
    pyglet.resource.reindex()

    # monkey patch pyglet to fix a resource loading bug
    slash_paths = filter(lambda x: x.startswith('/'), pyglet.resource._default_loader._index.keys())
    for path in slash_paths:
        pyglet.resource._default_loader._index[path[1:]] = pyglet.resource._default_loader._index[path]

setUpResources()


def main():
    print("go")
