from collections import namedtuple
from vector import v


Circle = namedtuple('Circle', 'center radius')


class Rect(object):
    def __init__(self, tl, br):
        self.tl = tl
        self.br = br

    def union(self, ano):
        l, t = self.tl
        al, at = ano.tl

        r, b = self.br
        ar, ab = ano.br

        return Rect(v(min(l, al), max(t, at)), v(max(r, ar), min(b, ab)))
        
    def __repr__(self):
        return 'Rect(%r, %r)' % (self.tl, self.br)
    __str__ = __repr__
