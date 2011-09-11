from .components import *


class Monster(object):
    def __init__(self, head=None):
        self.head = head or Head()
        self.head.pos = (0, head.preferred_height())
