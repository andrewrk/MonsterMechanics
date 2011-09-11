class Component(object):
    """The base class of monster components, a roughly circular module that can
    be attached to other components."""

    BASE_HEALTH = 100.0

    def __init__(self):
        self.health = self.BASE_HEALTH

    def get_radius(self):
        return self.RADIUS

    def preferred_height(self):
        """Compute the preferred height of the component by assessing how far
        below its subcomponents reach."""

        #TODO: recurse through subcomponents

        return self.get_radius()


class Head(Component):
    SPRITES = {
        'level1': 'head-level1.png',
        'level2': 'head-level2.png',
        'level3': 'head-level3.png',
    }
    RADIUS = 42
    def __init__(self, level=1):
        self.level = level


class Hip(Component):
    """A component that joins onto legs and knows how to articulate them."""
    SPRITES = {
        'hip': 'hip.png',
    }
    RADIUS = 39


class Lung(Component):
    MIN_RADIUS = 50
    MAX_RADIUS = 70

    SPRITES = {
        'lung': 'lung.png'
    }

    def __init__(self):
        super(Lung, self).__init__()
        self.breathing_phase = 0.0
        self.breathing_speed = 1.0
    
    def get_radius(self):
        r = math.sin(self.breathing_phase)
        r = r * r

        return r * self.MIN_RADIUS + (1 - r) * self.MAX_RADIUS


