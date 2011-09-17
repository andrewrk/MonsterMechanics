from __future__ import division, print_function, unicode_literals; range = xrange

import math
import pyglet
import json

import random

from actor import Actor
from geom import *
from vector import v

from projectiles import Thistle, Blood
from .controller import AIController

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
    cost = 200

    def __repr__(self):
        return '<%s %d>' % (self.__class__.__name__, id(self))

    __str__ = __repr__

    def __init__(self, pos, name='player'):
        super(BodyPart, self).__init__(pos, name)
        self.health = self.get_max_health()

    def get_max_health(self):
        return self.MAX_HEALTH

    def add_health(self, h, seen=[]):
        seen = seen[:]
        self.health += h
        maxh = self.get_max_health()
        if self.health > maxh:
            extra = maxh - self.health
            self.health = maxh
            conn = self.get_connected()
            for c in conn:
                if c in seen:
                    continue
                c.add_health(extra / len(conn), seen + [self])

    def get_lung_multiplier(self):
        lungs = len([p for p in self.get_connected() if isinstance(p, Lung)])
        return 1.3 ** lungs
    
    def subparts(self):
        """In nested bodies, return sub-bodies."""
        return [self]

    def get_connected(self):
        connected = []
        if self._parent:
            connected.append(self._parent)
        connected.extend([p for p, j in self._joints])
        return connected

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

    def update(self, dt):
        if self.scale < 1.0:
            newscale = min(1.0, self.scale + dt / 3.0)
            self.set_scale(newscale)

    def can_attach(self, another):
        """Return True if another can be permitted to attach to this part"""
        return True

    def attachment_radius(self, another):
        return None

    def to_json(self):
        return {
            'id': id(self),
            'type': self.__class__.__name__,
            'position': tuple(self.get_position()),
            'angle': self.body.get_rotation(),
            'scale': self.scale
        }

    @classmethod
    def from_json(cls, js, name='player'):
        inst = cls(v(*js['position']), name=name)
        return inst

    def get_bounds(self):
        ang = self.sprite.rotation * math.pi / 180
        bounds = None
        basepos = v(*self.sprite.position)
        for s in self.get_shapes():
            center = v(*s.center)
            center = center.rotated(ang) + basepos
            diag = v(-s.radius, s.radius)
            sbounds = Rect(center + diag, center - diag)
            if bounds is None:
                bounds = sbounds
            else:
                bounds = bounds.union(sbounds)
        return bounds

    _parent = None

    def kill(self):
        for p, j in self._joints:
            p.kill()
        if self._parent is not None:
            self._parent._joints = [(p, j) for p, j in self._parent._joints if p is not self]

        for p, radius in self.get_shapes():
            for i in range(int(radius * radius / 100.0)):
                off = v(random.gauss(0, radius * 0.5), random.gauss(0, radius * 0.5))
                self.world.spawn(Blood(self.get_position() + p + off, name=''))

        self.world.destroy(self)
        self.monster.remove_part(self)
        if self._parent is None:
            self.monster.kill()



def resource_levels(base):
    return {
        'level1': '%s-level1' % base,
        'level2': '%s-level2' % base,
        'level3': '%s-level3' % base,
        'enemy-level1': 'enemy-%s-level1' % base,
        'enemy-level2': 'enemy-%s-level2' % base,
        'enemy-level3': 'enemy-%s-level3' % base,
    }

def single_resource(name):
    return {
        'default': name,
        'enemy-default': 'enemy-' + name
    }
    

class UpgradeablePart(BodyPart):
    DEFAULT_PART = 'level1'

    level = 1

    def upgrade_cost(self):
        return self.cost * 2 ** self.level

    def can_upgrade(self):
        if self.upgrade_cost() > self.monster.mutagen:
            return False
        return self.level < 3 and self.name == 'player'

    def upgrade(self): 
        self.monster.spend_mutagen(self.upgrade_cost())
        self.level += 1
        self.set_part('level%d' % self.level)
        self.health = self.get_max_health() 

    def get_max_health(self):
        return self.MAX_HEALTH[self.level - 1]


class LeafPart(BodyPart):
    """A BodyPart nothing else can attach to."""
    def can_attach(self, another):
        return False


class Head(UpgradeablePart):
    """The head of the monster"""
    RESOURCES = resource_levels('head')

    MAX_HEALTH = 500, 1000, 1500

    cost = 1000

    def can_attach(self, part):
        return not part.ATTACH_CENTER


class Eyeball(LeafPart):
    """An eyeball. Improves accuracy."""
    RESOURCES = single_resource('eyeball')
    DEFAULT_SPRITE = 'default'

    MAX_HEALTH = 30


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

    MAX_HEALTH = 50, 100, 200


class Spikes(UpgradeablePart, OutFacingPart, LeafPart):
    RESOURCES = resource_levels('spikes')

    MAX_HEALTH = 150, 200, 300
    DAMAGE = 10, 25, 50

    hit_time = 0

    def get_damage(self):
        return self.DAMAGE[self.level - 1]

    def update(self, dt):
        super(Spikes, self).update(dt)
        if self.hit_time > 0:
            self.hit_time = max(0, self.hit_time - dt)
        else:
            for enemy in self.world.get_enemies_for_name(self.name):
                p = enemy.colliding(self, allowance=3)
                if p is None:
                    continue
                damage = self.get_damage()
                self.world.damage_part(p, self.name, damage)
                self.hit_time = 0.3

        


class Scales(UpgradeablePart, OutFacingPart, LeafPart):
    RESOURCES = resource_levels('scales')

    MAX_HEALTH = 250, 400, 750


class Lung(PulsingBodyPart):
    """Lungs that supply energy to connected parts"""
    RESOURCES = single_resource('lung')
    DEFAULT_PART = 'default'
    MAX_HEALTH = 300


class Heart(UpgradeablePart, PulsingBodyPart):
    """Hearts heal nearby tissue"""
    RESOURCES = resource_levels('heart')
    pulse_rate = 3
    pulse_amount = 0.3

    MAX_HEALTH = 200, 300, 400
    HEAL_RATE = 1, 2, 4

    def update(self, dt):
        super(Heart, self).update(dt)
        lung_boost = self.get_lung_multiplier()
        for c in self.get_connected():
            c.add_health(lung_boost * self.HEAL_RATE[self.level - 1] * dt, seen=[self])


class MutagenBladder(UpgradeablePart, PulsingBodyPart):
    """Mutagen bladders add to the monster's mutagen storage capacity."""
    RESOURCES = resource_levels('mutagenbladder')
    pulse_rate = 0.01
    pulse_amount = 0.05

    MAX_HEALTH = 100, 150, 200

    def get_mutagen_capacity(self):
        return 100 * 2 ** self.level


class ThistleGun(UpgradeablePart):
    RESOURCES = resource_levels('thistlegun')
    ATTACK_INTERVAL = 2

    MUZZLE = {
        'left': v(-25, 20),
        'right': v(25, 20),
    }
    MUZZLE_IMPULSE = {
        'left': v(-1, 0.2) * 0.0001,
        'right': v(1, 0.2) * 0.0001,
    }

    attack_ready = True
    attack_timer = 0
    
    PROJECTILE = Thistle
    MAX_HEALTH = 100, 200, 300

    def get_dir(self):
        return {
            'player': 'left',
            'enemy': 'right'
        }[self.name]

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
        dir = self.get_dir()
        vel = self.MUZZLE_IMPULSE[dir]
        pos = self.get_position() + self.MUZZLE[dir]
        projectile = self.PROJECTILE(pos, self.name)
        self.world.spawn(projectile)
        projectile.set_level(self.level)
        projectile.multiplier = self.get_lung_multiplier()
        projectile.body.apply_impulse(vel, pos)
        self.body.apply_impulse(-5 * vel, pos)


class Claw(UpgradeablePart):
    RESOURCES = resource_levels('claws')

    MAX_HEALTH = 200, 300, 500

    def can_attach(self, part):
        return isinstance(part, Eyeball)


class Leg(UpgradeablePart):
    RESOURCES = resource_levels('leg')

    MAX_HEALTH = 300, 450, 600

    def update(self, dt):
        super(Leg, self).update(dt)
        #FIXME: only apply torque if the leg is touching the ground
        rot = self.body.get_rotation()
        gain = -0.0003
        self.body.apply_torque(rot * gain)


class LowerArm(BodyPart):
    type = 'arm'
    RESOURCES = single_resource('lower-arm')

class UpperArm(BodyPart):
    type = 'arm'
    RESOURCES = single_resource('upper-arm')


class Arm(BodyPart):
    ATTACH_CENTER = True

    MAX_HEALTH = 200, 300, 500

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
}

class Monster(object):
    @staticmethod
    def load_all():
        for cls in PART_CLASSES.values():
            cls.load() 
        Thistle.load()
        Blood.load()

    @classmethod
    def create_initial(cls, world, pos, name='player'):
        head = Head(pos, name=name)
        world.spawn(head)
        return cls(world, [head], name=name)

    def __init__(self, world, parts, name='player'):
        self.world = world
        self.parts = parts
        for p in self.parts:
            p.monster = self
        self.name = name
        self.leg_count = len([p for p in self.parts if isinstance(p, Leg)])
        self.moving = 0
        self.mutagen = 500
        self.death_listeners = []
        self.controller = None
        self.dead = False

    def set_controller(self, controller):
        self.controller = controller

    def set_mutagen(self, value):
        self.mutagen = value

    def get_position(self):
        try:
            return self.parts[0].get_position()
        except IndexError:
            return v(0,0) # FIXME

    def add_mutagen(self, value):
        cap = self.get_mutagen_capacity()
        self.mutagen = min(cap, self.mutagen + value)

    def spend_mutagen(self, value):
        self.mutagen = max(0, self.mutagen - value)

    def get_bounds(self):
        bounds = None
        for p in self.parts:
            if bounds is None:
                bounds = p.get_bounds()
            else:
                bounds = bounds.union(p.get_bounds())
        return bounds

    def get_mutagen_capacity(self):
        s = 1000
        for p in self.parts:
            try:
                m = p.get_mutagen_capacity()
            except AttributeError:
                continue
            s += m
        return s

    def left(self):
        self.moving = LEFT

    def right(self):
        self.moving = RIGHT

    def attack(self):
        for p in self.parts:
            if p.attack_ready:
                p.attack()

    def add_part(self, part):
        part.monster = self
        if isinstance(part, Leg):
            self.leg_count += 1
            self.parts.insert(0, part)
        else:
            self.parts.append(part)

    def remove_part(self, part):
        self.parts.remove(part)
        if isinstance(part, Leg):
            self.leg_count -= 1

    def colliding(self, actor, allowance=0):
        """Find an actor is colliding with this monster."""
        partpos = actor.get_position()
        baseshape = actor.get_base_shape()
        partpos += baseshape.center
        partradius = baseshape.radius
        for currentpart in self.parts:
            for p in currentpart.subparts():
                ppos = p.get_position()
                for centre, radius in p.get_shapes():
                    # FIXME: rotation
                    c = centre + ppos
                    vec = (partpos - c)
                    if vec.length2 < (radius + partradius + allowance) * (radius + partradius + allowance):
                        return currentpart
        return None

    def colliding_point(self, point):
        """Find an actor is colliding with this monster."""
        for currentpart in self.parts:
            for p in currentpart.subparts():
                ppos = p.get_position()
                for centre, radius in p.get_shapes():
                    # FIXME: take into account rotation
                    c = centre + ppos
                    vec = (point - c)
                    if vec.length < radius:
                        return currentpart
        return None

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
        if self.controller:
            self.controller.update(dt)
        if self.moving in [LEFT, RIGHT]:
            self.phase += self.moving * dt * 2
            for p in self.parts:
                if not isinstance(p, Leg):
                    continue
                ppos = p.get_position()
                step = math.sin(ppos.x / 50.0 + self.phase)
                f = step * 0.5 + 0.5
                p.set_position(ppos + v(self.moving * 200 * f * dt, 10 * f * dt))
                rot = p.body.get_rotation()
                p.body.set_rotation(rot + self.moving * step * dt) 
        self.moving = 0

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
        self.do_attach(destpart, part, jointpos)

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
        self.do_attach(destpart, part, jointpos)

    def do_attach(self, target, part, jointpos):
        assert part is not target
        j = target.body.attach(part.body, jointpos)
        target._joints.append((part, j))
        part._parent = target

    def to_json(self):
        parts = []
        joints = []

        for p in self.parts:
            parts.append(p.to_json())
            for p2, j in p._joints:
                d = j.to_json()
                d['body1'] = id(p) 
                d['body2'] = id(p2)
                joints.append(d)

        return {
            'parts': parts,
            'joints': joints
        }

    def add_death_listener(self, l):
        self.death_listeners.append(l)
    
    def kill(self):
        self.dead = True
        self.world.remove_monster(self)
        for l in self.death_listeners:
            l(self)

    @staticmethod
    def from_json(world, json, name):

        classes = {}
        for n, cls in PART_CLASSES.items():
            classes[cls.__name__] = cls

        part_map = {}
        parts = []
        for p in json['parts']:
            cls = classes[p['type']]
            part = cls.from_json(p, name)
            parts.append(part)
            part_map[p['id']] = part
            world.spawn(part)

        # re-attach parts with joints
        for j in json['joints']:
            body1 = part_map[j['body1']]
            body2 = part_map[j['body2']]
            body1._joints.append((body2, body1.body.restore_joint(body2.body, j)))
            body2._parent = body1
        return Monster(world, parts, name=name)

    @staticmethod
    def player_from_json(world, fname):
        with open(fname, 'r') as f:
            mutant = json.load(f)
        return Monster.from_json(world, mutant, 'player')

    @staticmethod
    def enemy_from_json(world, fname):
        with open(fname, 'r') as f:
            mutant = json.load(f)
        player = world.get_player()
        x = player.get_bounds().tl.x
        mxpos = mutant['parts'][0]['position'][0]
        trans = x - mxpos + 400
        def refl(pos):
            x, y = pos
            return v(-x, y)
        def refl_and_move(pos):
            x, y = pos
            return v(trans - x, y)
        def rot(angle):
            return math.pi - angle

        for p in mutant['parts']:
            p['position'] = refl_and_move(p['position'])
            p['angle'] = rot(p['angle']) 
        for j in mutant['joints']:
            j['anchor1'] = refl(j['anchor1'])
            j['anchor2'] = refl(j['anchor2'])
            j['angle'] = rot(j['angle']) 
            j['refAngle'] = -j['refAngle']

        m = Monster.from_json(world, mutant, 'enemy')
        m.set_controller(AIController(world, m, 'enemy'))
        return m
