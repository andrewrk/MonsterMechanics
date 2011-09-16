from __future__ import division, print_function, unicode_literals; range = xrange

import math
import pyglet
import json

from actor import Actor
from geom import Circle
from vector import v

from projectiles import Thistle

STYLE_NORMAL = 0
STYLE_VALID = 1
STYLE_INVALID = 2

LEFT = -1
RIGHT = 1




class BodyPart(Actor):
    """Base class of all body parts.
    
    Parts support tangible physics, but are created in a ghost mode that shows
    where they would be inserted if the player releases the mouse. There is also
    the ability to display the part with a visual effect to indicate whether it
    can be created in its current position.
    
    To create a physics controller for the BodyPart (ie. make it non-virtual),
    use .create_body().

    """

    ATTACH_CENTER = False
    DEFAULT_PART = 'default'
    type = 'body'
    attack_ready = False

    def subparts(self):
        """In nested bodies, return sub-bodies."""
        return [self]

    def position_to_joint(self, joint):
        """Default implementation does nothing."""

    def set_style(self, style):
        """Set a display style for the part.""" 
        if style == STYLE_VALID:
            self.sprite.color = (0, 160, 0)
            self.sprite.opacity = 80
        elif style == STYLE_INVALID:
            self.sprite.color = (200, 0, 0)
            self.sprite.opacity = 80
        else:
            self.sprite.color = (255, 255, 255)
            self.sprite.opacity = 255
    
    def get_base_shape(self):
        return self.get_shapes()[0]

    def update(self, dt):
        if self.scale < 1.0:
            newscale = min(1.0, self.scale + dt / 3.0)
            self.set_scale(newscale)

    def can_attach(self, another):
        """Return True if another can be permitted to attach to this part"""
        return True

    def attachment_radius(self, another):
        return None



def resource_levels(base):
    return {
        'level1': '%s-level1' % base,
        'level2': '%s-level2' % base,
        'level3': '%s-level3' % base,
    }
    

class UpgradeablePart(BodyPart):
    DEFAULT_PART = 'level1'

    level = 1


class LeafPart(BodyPart):
    """A BodyPart nothing else can attach to."""
    def can_attach(self, another):
        return False


class Head(UpgradeablePart):
    """The head of the monster"""
    RESOURCES = resource_levels('head')

    def can_attach(self, part):
        return not part.ATTACH_CENTER


class Eyeball(LeafPart):
    """An eyeball. Improves accuracy."""


class OutFacingPart(BodyPart):
    """A part that always attaches facing outwards from the part it attaches to"""
    def position_to_joint(self, joint_vector):
        a = joint_vector.angle
        self.sprite.rotation = 180 - a
        if self.body:
            self.body.set_rotation(-self.sprite.rotation * math.pi / 180.0)


class PulsingBodyPart(BodyPart):
    """A part that grows and shrinks in size, sinusoidally."""
    phase = 0
    pulse_rate = 1
    pulse_amount = 0.1

    def update(self, dt):
        self.phase += dt * self.pulse_rate
        s = self.pulse_amount * math.cos(self.phase) + 1 - self.pulse_amount
        self.set_scale(self.scale * 0.97 + s * 0.03)


class Wing(UpgradeablePart):
    RESOURCES = resource_levels('wing')
    ATTACH_CENTER = True


class Spikes(UpgradeablePart, OutFacingPart, LeafPart):
    RESOURCES = resource_levels('spikes')


class Scales(UpgradeablePart, OutFacingPart, LeafPart):
    RESOURCES = resource_levels('scales')


class Lung(PulsingBodyPart):
    """Lungs that supply energy to connected parts"""
    RESOURCES = {
        'lung': 'lung'
    }
    DEFAULT_PART = 'lung'


class Heart(UpgradeablePart, PulsingBodyPart):
    """Hearts heal nearby tissue"""
    RESOURCES = resource_levels('heart')
    pulse_rate = 3
    pulse_amount = 0.3


class MutagenBladder(UpgradeablePart, PulsingBodyPart):
    """Mutagen bladders add to the monster's mutagen storage capacity."""
    RESOURCES = resource_levels('mutagenbladder')
    pulse_rate = 0.01
    pulse_amount = 0.05

    def get_mutagen_capacity(self):
        return 100 * 2 ** self.level


class ThistleGun(UpgradeablePart):
    RESOURCES = resource_levels('thistlegun')
    ATTACK_INTERVAL = 2
    attack_ready = True
    attack_timer = 0

    PROJECTILE = Thistle

    def update(self, dt):
        super(ThistleGun, self).update(dt)
        if self.attack_timer > 0:
            self.attack_timer = max(0, self.attack_timer - dt) 
        else:
            self.attack_ready = True

    def draw(self):
        """Don't rotate the thistlegun as we want it to always fire in the same direction."""
        if self.body:
            self.sprite.set_position(*self.body.get_position())
        self.sprite.draw()

    def attack(self):
        self.attack_timer = self.ATTACK_INTERVAL
        self.attack_ready = False
        vel = v(-1, 0.5) * 0.0001
        pos = self.get_position() + v(-25, 20)
        projectile = self.PROJECTILE(pos, self.name)
        self.world.spawn(projectile)
        projectile.body.apply_impulse(vel, pos)
        self.body.apply_impulse(-5 * vel, pos)



class EggSack(BodyPart):
    RESOURCES = {
        'default': 'egg-sack'
    }


class Claw(UpgradeablePart):
    RESOURCES = resource_levels('claws')

    def can_attach(self, part):
        return isinstance(part, Eyeball)


class Leg(UpgradeablePart):
    RESOURCES = resource_levels('leg')

    def update(self, dt):
        super(Leg, self).update(dt)
        #FIXME: only apply torque if the leg is touching the ground
        rot = self.body.get_rotation()
        gain = -0.0005
        self.body.apply_torque(rot * gain)


class LowerArm(BodyPart):
    type = 'arm'
    RESOURCES = {
        'default': 'lower-arm'
    }

class UpperArm(BodyPart):
    type = 'arm'
    RESOURCES = {
        'default': 'upper-arm'
    }


class Arm(BodyPart):
    ATTACH_CENTER = True

    @classmethod
    def load(cls):
        UpperArm.load()
        LowerArm.load()

    @property
    def body(self):
        return self.upper.body

    def update(self, dt):
        self.upper.update(dt)
        self.lower.update(dt)

    def subparts(self):
        return [self.upper, self.lower]

    def __init__(self, pos, name='player'):
        self.upper = UpperArm(pos, name=name)
        self.lower = LowerArm(pos + self.upper.get_shapes()[1].center, name=name)

    def set_scale(self, scale):
        self.upper.set_scale(scale)
        self.lower.set_scale(scale)

    def set_style(self, style):
        self.upper.set_style(style)
        self.lower.set_style(style)

    def create_body(self, world):
        self.upper.create_body(world)
        self.lower.create_body(world)
        self.joint = self.upper.body.attach(self.lower.body, self.lower.get_position())

    def get_shapes(self):
        return self.upper.get_shapes() + self.lower.get_shapes()[1:]

    def set_position(self, pos):
        """Move the part."""
        if self.upper.body:
            delta = pos - self.upper.get_position()
            self.upper.set_position(pos)
            self.lower.set_position(self.lower.get_position() + delta)
        else:
            self.upper.set_position(pos)
            self.lower.set_position(self.upper.get_position() + self.upper.get_shapes()[1].center)

    def get_position(self):
        return self.upper.get_position()

    def draw(self):
        self.upper.draw()
        self.lower.draw()
        


PART_CLASSES = {
    'head': Head,
    'arm': Arm,
    'claw': Claw,
    'leg': Leg,
    'heart': Heart,
    'lung': Lung,
    'eyeball': Eyeball,
    'spikes': Spikes,
    'scales': Scales,
    'wing': Wing,
    'mutagenbladder': MutagenBladder,
    'thistlegun': ThistleGun,
    'eggsack': EggSack,
}

class Monster(object):
    @staticmethod
    def load_all():
        for cls in PART_CLASSES.values():
            cls.load() 
        Thistle.load()

    @classmethod
    def create_initial(cls, world, pos, name='player'):
        Monster.load_all()
        head = Head(pos, name=name)
        world.spawn(head)
        return cls(world, [head])

    def __init__(self, world, parts, name='player'):
        self.world = world
        self.parts = parts
        self.name = name
        self.leg_count = len([p for p in parts if isinstance(p, Leg)])
        self.moving = 0

    def get_mutagen_capacity(self):
        s = 1000
        for p in self.parts:
            try:
                m = p.get_mutagen_capacity()
            except AttributeError:
                continue
            s += m
        return s

    def attack(self):
        for p in self.parts:
            if p.attack_ready:
                p.attack()

    def add_part(self, part):
        if isinstance(part, Leg):
            self.leg_count += 1
            self.parts.insert(0, part)
        else:
            self.parts.append(part)

    def remove_part(self, part):
        self.parts.remove(part)
        part.body.destroy()
        if isinstance(part, Leg):
            self.leg_count -= 1

    def attachment_point(self, part):
        """Find an attachment point for part to any of the parts in this monster.
        
        Returns None if no suitable attachment point exists.

        """
        partpos = part.get_position()
        baseshape = part.get_base_shape()
        partpos += baseshape.center
        partradius = baseshape.radius
        for currentpart in self.parts:
            for p in currentpart.subparts():
                if not p.can_attach(part):
                    continue
                ppos = p.get_position()
                for centre, radius in p.get_shapes():
                    c = centre + ppos
                    vec = (partpos - c)
                    if vec.length2 < (radius + partradius) * (radius + partradius):
                        if part.ATTACH_CENTER:
                            return p, c, c
                        else:
                            return p, c + vec.scaled_to(radius + partradius), c + vec.scaled_to(radius)

    def can_attach(self, part):
       return self.attachment_point(part) is not None 

    phase = 0

    def update(self, dt):
        for p in self.parts:
            p.update(dt)
        if self.moving in [LEFT, RIGHT]:
            self.phase += self.moving * dt * 6
            for p in self.parts:
                if not isinstance(p, Leg):
                    continue
                ppos = p.get_position()
                step = math.sin(ppos.x / 50.0 + self.phase)
                f = step * 0.5 + 0.5
                p.set_position(ppos + v(self.moving * 200 * f * dt, 10 * f * dt))
                rot = p.body.get_rotation()
                p.body.set_rotation(rot + self.moving * step * dt) 

    def attach(self, part):
        attachment = self.attachment_point(part)
        if attachment is None:
            raise ValueError("Cannot attach part to this monster.")

        destpart, partpos, jointpos = attachment
        part.set_position(partpos)
        part.position_to_joint(partpos - jointpos)
        self.world.spawn(part)
        part.set_style(STYLE_NORMAL)
        self.add_part(part)
        destpart.body.attach(part.body, jointpos)

    def attach_and_grow(self, part, initial_scale=0.1):
        attachment = self.attachment_point(part)
        if attachment is None:
            raise ValueError("Cannot attach part to this monster.")

        destpart, partpos, jointpos = attachment

        baseshape = part.get_base_shape()
        partradius = baseshape.radius

        partpos = jointpos + (partpos - jointpos) * initial_scale
        
        self.world.spawn(part)
        part.set_scale(initial_scale)
        part.set_position(partpos)
        part.position_to_joint(partpos - jointpos)
        part.set_style(STYLE_NORMAL)
        self.add_part(part)
        destpart.body.attach(part.body, jointpos)
