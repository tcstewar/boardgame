import inspect

import boardgame as bg

import villains
import masterminds
import schemes
from . import hero as hero_module
from . import action
from .player import Player


from .core import *

class Legendary(bg.BoardGame):
    def reset(self, seed=None, n_players=2, mastermind=None, villain=None,
                                            hero=None):
        super(Legendary, self).reset(seed=seed)
        self.villain = []
        self.city = [None, None, None, None, None]
        self.hero = []
        self.hq = [None, None, None, None, None]
        self.escaped = []
        self.ko = []
        self.wounds = [Wound(self) for i in range(30)]
        self.bystanders = [Bystander(self) for i in range(30)]
        self.officers = [hero_module.ShieldOfficer(self) for i in range(30)]
        self.players = [Player(self) for i in range(n_players)]

        self.state = BeginTurn
        self.choice([action.StartTurn(),
                     action.PlayAll(),
                     action.PlayFromHand(),
                     action.Heal(),
                     action.Recruit(),
                     action.Fight(),
                     action.EndTurn(),
                    ],
                    repeat=True)

        ms = dict(inspect.getmembers(masterminds,
            lambda x: inspect.isclass(x) and issubclass(x, Mastermind) and
                       not x is Mastermind))
        vs = dict(inspect.getmembers(villains,
            lambda x: inspect.isclass(x) and issubclass(x, VillainGroup) and
                       not x is VillainGroup))
        vhs = dict(inspect.getmembers(villains,
            lambda x: inspect.isclass(x) and issubclass(x, HenchmenGroup) and
                       not x is HenchmenGroup))
        hs = dict(inspect.getmembers(hero_module,
            lambda x: inspect.isclass(x) and issubclass(x, HeroGroup) and
                       not x is HeroGroup))

        if mastermind is not None:
            self.mastermind = ms[mastermind](self)
        else:
            self.mastermind = self.rng.choice(ms.values())(self)

        n_vg = {1:1, 2:2, 3:3, 4:3, 5:4}[n_players]
        n_vh = {1:1, 2:1, 3:1, 4:2, 5:2}[n_players]
        n_by = {1:1, 2:2, 3:8, 4:8, 5:12}[n_players]
        n_hg = {1:3, 2:5, 3:5, 4:5, 5:6}[n_players]

        solo = n_players == 1

        if villain is not None:
            if villain in vs:
                cls = vs[villain]
            elif villain in vhs:
                cls = vhs[villain]
            else:
                print 'Unknown Villain "%s"' % villain
                print 'Known Villains: %s' % (vs.keys() + vhs.keys())
                raise ValueError
            for i in range(n_vg + n_vh):
                self.villain.extend(cls(self).group)
                self.event('Villain: %s' % cls.name)
            n_vg = 0
            n_vh = 0
        if hero is not None:
            if hero in hs:
                cls = hs[hero]
            else:
                print 'Unknown Hero "%s"' % hero
                print 'Known Heroes: %s' % hs.keys()
                raise ValueError
            for i in range(n_hg):
                self.hero.extend(cls(self).group)
                self.event('Hero: %s' % cls.name)
            n_hg = 0

        for i in range(n_vg):
            if self.mastermind.always_leads in vs.values() and not solo:
                cls = self.mastermind.always_leads
            else:
                cls = self.rng.choice(vs.values())
            for k in vs.keys():
                if vs[k] is cls:
                    del vs[k]
                    break
            self.villain.extend(cls(self).group)
            self.event('Villain: %s' % cls.name)
        for i in range(n_vh):
            if self.mastermind.always_leads in vhs.values() and not solo:
                cls = self.mastermind.always_leads
            else:
                cls = self.rng.choice(vhs.values())
            for k in vhs.keys():
                if vhs[k] is cls:
                    del vhs[k]
                    break
            if solo:
                self.villain.extend(cls(self).group[:3])
            else:
                self.villain.extend(cls(self).group)
            self.event('Henchmen: %s' % cls.name)


        self.scheme = schemes.UnleashCube(self)

        for i in range(5 if not solo else 1):
            self.villain.append(MasterStrike(self))

        for i in range(n_by):
            self.villain.append(self.bystanders.pop(0))
        self.rng.shuffle(self.villain)

        for i in range(n_hg):
            cls = self.rng.choice(hs.values())
            for k in hs.keys():
                if hs[k] is cls:
                    del hs[k]
                    break
            self.hero.extend(cls(self).group)
            self.event('Hero: %s' % cls.name)
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
            self.shift_city()
            self.city[4] = card
            card.on_ambush()
            self.event('A new Villain enters the city: %s' % card)
        elif isinstance(card, SchemeTwist):
            self.event('Scheme Twist!')
            self.scheme.twist()
            if len(self.players) == 1:
                actions = []
                for c in self.hq:
                    if c is not None and c.cost <= 6:
                        actions.append(action.KOFromHQ(c))
                self.choice(actions)

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
            if c is not None and c.cost <= 6:
                actions.append(action.KOFromHQ(c))
        self.choice(actions)

        if len(card.captured) > 0:
            for p in self.players:
                actions = []
                for c in p.hand:
                    actions.append(action.DiscardFrom(c, p.hand))
                self.choice(actions)





    def text_state(self):
        lines = []
        for i in range(10):
            lines.append('.................')

        lines.append('LEGENDARY  (Game seed=%d)' % self.seed)
        lines.append('----------------------------------------')
        lines.append('Mastermind: %s (%d/4)' % (self.mastermind.text(),
                                                len(self.mastermind.tactics)))
        lines.append('Scheme: %s' % self.scheme)
        lines.append('Escaped: %d' % len(self.escaped))
        def text(x):
            return x.text() if x is not None else '-----'
        lines.append('    Bridge: %s' % text(self.city[0]))
        lines.append('   Streets: %s' % text(self.city[1]))
        lines.append('  Rooftops: %s' % text(self.city[2]))
        lines.append('      Bank: %s' % text(self.city[3]))
        lines.append('    Sewers: %s' % text(self.city[4]))
        lines.append('Villain Pile: %d' % len(self.villain))
        for i in range(5):
            if self.hq[i] is None:
                lines.append('  HQ %d: None' % (i + 1))
            else:
                lines.append(' HQ %d (%d): %s' % (i + 1, self.hq[i].cost,
                                                  self.hq[i].text()))
        lines.append('Hero Pile: %d' % len(self.hero))
        lines.append('----------------------------------------')
        for i, p in enumerate(self.players):
            if p is self.current_player:
                lines.append('Player %d (current) [S%d P%d V%d]' % (i+1,
                                                      p.available_star,
                                                      p.available_power,
                                                      p.victory_points()))
                for x in p.hand:
                    lines.append('  %s' % x.text())
                for i in range(10-len(p.hand)):
                    lines.append('  ----------------')
            else:
                hand = ', '.join(['%s' % x for x in p.hand])
                lines.append('Player %d [V%d]: %s' % (i+1,
                                                      p.victory_points(),
                                                      hand))
        lines.append('----------------------------------------')
        for event in self.recent_events:
            lines.append(event)
        for i in range(4-len(self.recent_events)):
            lines.append('................')

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
