import boardgame as bg

import villains
import masterminds
import schemes
from . import heroes
from . import action
from .player import Player


from .core import *

class Legendary(bg.BoardGame):
    def __init__(self, seed=None):
        super(Legendary, self).__init__(seed=seed)
        self.villain = []
        self.city = [None, None, None, None, None]
        self.hero = []
        self.hq = [None, None, None, None, None]
        self.escaped = []
        self.ko = []
        self.wounds = [Wound(self) for i in range(30)]
        self.bystanders = [Bystander(self) for i in range(30)]
        self.officers = [heroes.ShieldOfficer(self) for i in range(30)]

        self.initialize()
        self.state = BeginTurn
        self.choice([action.StartTurn(self),
                     action.PlayFromHand(self),
                     action.Recruit(self),
                     action.Fight(self),
                     action.EndTurn(self),
                    ],
                    repeat=True)

    def initialize(self):
        self.players = [Player(self) for i in range(2)]
        self.mastermind = masterminds.RedSkull(self)
        self.scheme = schemes.UnleashCube(self)
        for i in range(5):
            self.villain.append(MasterStrike(self))
        self.villain.extend(villains.Hydra(self).group)
        self.villain.extend(villains.Hydra(self).group)
        self.villain.extend(villains.Hydra(self).group)
        for i in range(2):
            self.villain.append(self.bystanders.pop(0))
        self.rng.shuffle(self.villain)

        self.hero.extend(heroes.IronMan(self).group)
        self.hero.extend(heroes.IronMan(self).group)
        self.hero.extend(heroes.IronMan(self).group)
        self.hero.extend(heroes.IronMan(self).group)
        self.hero.extend(heroes.IronMan(self).group)
        self.rng.shuffle(self.hero)

        self.fill_hq()

    def fill_hq(self):
        for i in range(5):
            if self.hq[i] is None and len(self.hero) > 0:
                if len(self.hero) == 0:
                    self.tie_game()
                    return
                self.hq[i] = self.hero.pop(0)


    def add_twists(self, count):
        for i in range(count):
            self.villain.append(SchemeTwist(self))

    def play_villain(self):
        if len(self.villain) == 0:
            self.tie_game()
            return
        card = self.villain.pop(0)
        if isinstance(card, Villain):
            self.event('A new Villain enters the city: %s' % card)
            self.shift_city()
            self.city[4] = card
            card.on_ambush()
        elif isinstance(card, SchemeTwist):
            self.event('Scheme Twist!')
            self.scheme.twist()
        elif isinstance(card, MasterStrike):
            self.event('%s makes a master strike' % self.mastermind)
            self.mastermind.strike()
        elif isinstance(card, Bystander):
            card = self.capture_bystander()
            self.event('%s captures a Bystander' % card)
        else:
            raise Exception('could not handle %s' % card)

    def shift_city(self):
        index = 4
        while self.city[index] is not None:
            index -= 1
            if index < 0:
                self.escaped.append(self.city[0])
                self.on_escape(self.city[0])
                self.city[0].on_escape()
                self.city[0] = None
                index = 0
        for i in range(index, 4):
            self.city[i] = self.city[i + 1]
        self.city[4] = None

    def capture_bystander(self):
        if len(self.bystanders) == 0:
            return
        index = 4
        while self.city[index] is None and index >= 0:
            index -= 1
        if index < 0:
            v = self.mastermind
        else:
            v = self.city[index]
        v.capture(self.bystanders.pop(0))
        return v

    def on_escape(self, card):
        actions = []
        for c in self.hq:
            if c.cost <= 6:
                actions.append(action.KOFromHQ(self, c))
        self.choice(actions)

        if len(card.captured) > 0:
            for p in self.players:
                actions = []
                for c in p.hand:
                    actions.append(action.DiscardFrom(self, c, p.hand))
                self.choice(actions)





    def text_state(self):
        lines = []
        for i in range(10):
            lines.append('.................')

        lines.append('LEGENDARY  (Game seed=%d)' % self.seed)
        lines.append('----------------------------------------')
        lines.append('Mastermind: %s' % self.mastermind)
        lines.append('Scheme: %s' % self.scheme)
        lines.append('Escaped: %d' % len(self.escaped))
        lines.append('    Bridge: %s' % self.city[0])
        lines.append('   Streets: %s' % self.city[1])
        lines.append('  Rooftops: %s' % self.city[2])
        lines.append('      Bank: %s' % self.city[3])
        lines.append('    Sewers: %s' % self.city[4])
        lines.append('Villain Pile: %d' % len(self.villain))
        for i in range(5):
            lines.append(' HQ %d (%d): %s' % (i + 1, self.hq[i].cost,
                                               self.hq[i]))
        lines.append('----------------------------------------')
        for i, p in enumerate(self.players):
            if p is self.current_player:
                lines.append('Player %d (current) [S%d P%d]' % (i+1,
                                                      p.available_star,
                                                      p.available_power))
                for x in p.hand:
                    lines.append('  %s' % x)
                for i in range(10-len(p.hand)):
                    lines.append('  ----------------')
            else:
                hand = ', '.join(['%s' % x for x in p.hand])
                lines.append('Player %d: %s' % (i+1, hand))
        lines.append('----------------------------------------')
        for event in self.recent_events:
            lines.append(event)
        for i in range(4-len(self.recent_events)):
            lines.append('................')
        self.events.extend(self.recent_events)
        del self.recent_events[:]

        return '\n'.join(lines)

    def evil_wins(self):
        print 'evil wins'
        self.finished = True
    def good_wins(self):
        print 'good wins'
        self.finished = True
    def tie_game(self):
        print 'tie game'
        self.finished = True
