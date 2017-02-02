import inspect

import boardgame as bg

import villains
import masterminds
import schemes
from . import hero as hero_module
from . import action
from .player import Player


from .core import *

class ClassList(object):
    mastermind = dict(inspect.getmembers(masterminds,
        lambda x: inspect.isclass(x) and issubclass(x, Mastermind) and
                   not x is Mastermind))
    villain = dict(inspect.getmembers(villains,
        lambda x: inspect.isclass(x) and issubclass(x, VillainGroup) and
                   not x is VillainGroup))
    henchman = dict(inspect.getmembers(villains,
        lambda x: inspect.isclass(x) and issubclass(x, Henchman) and
                   not x is Henchman))
    hero = dict(inspect.getmembers(hero_module,
        lambda x: inspect.isclass(x) and issubclass(x, HeroGroup) and
                   not x is HeroGroup))
    scheme = dict(inspect.getmembers(schemes,
        lambda x: inspect.isclass(x) and issubclass(x, Scheme) and
                   not x is Scheme))


class Legendary(bg.BoardGame):
    def reset(self, seed=None, n_players=2, mastermind=None, villain=None,
                                            hero=None, scheme=None,
                                            basic=False):
        super(Legendary, self).reset(seed=seed)
        self.villain = []
        self.city = [None, None, None, None, None]
        self.city_names = ['Bridge', 'Street', 'Rooftops', 'Bank', 'Sewers']
        self.hero = []
        self.hq = [None, None, None, None, None]
        self.escaped = []
        self.ko = []
        self.wounds = [Wound(self) for i in range(30)]
        self.bystanders = [Bystander(self) for i in range(30)]
        self.officers = [hero_module.ShieldOfficer(self) for i in range(30)]
        self.players = [Player(self, name='Player %d' % (i+1))
                        for i in range(n_players)]

        self.turn_handlers = {}
        self.turn_handlers['on_choice'] = []
        self.handlers = {}
        self.handlers['on_choice'] = []

        ms = dict(ClassList.mastermind)
        vs = dict(ClassList.villain)
        vhs = dict(ClassList.henchman)
        hs = dict(ClassList.hero)
        ss = dict(ClassList.scheme)


        if mastermind is not None:
            self.mastermind = ms[mastermind](self)
        else:
            self.mastermind = self.rng.choice(ms.values())(self)
        self.event('Mastermind: %s' % self.mastermind.text())

        if scheme is None:
            options = ss.values()
            if n_players == 1 and basic:
                options = [x for x in options if x.allow_solo_basic]
            cls = self.rng.choice(options)
        else:
            if scheme in ss:
                cls = ss[scheme]
            else:
                print 'Unknown Scheme "%s"' % scheme
                print 'Known Schemes: %s' % ss.keys()
                raise ValueError
        self.scheme = cls(self)


        n_vg = {1:1, 2:2, 3:3, 4:3, 5:4}[n_players]
        n_vh = {1:1, 2:1, 3:1, 4:2, 5:2}[n_players]
        n_by = {1:1, 2:2, 3:8, 4:8, 5:12}[n_players]
        n_hg = {1:3, 2:5, 3:5, 4:5, 5:6}[n_players]

        solo = n_players == 1
        if not solo:
            self.solo_basic = False
            self.solo_advanced = False
        else:
            self.solo_basic = basic
            self.solo_advanced = not basic

        n_vh = self.scheme.adjust_henchman_count(n_vh)
        n_hg = self.scheme.adjust_hero_count(n_hg)

        if villain is not None:
            if villain in vs:
                cls = vs[villain]
                for i in range(n_vg + n_vh):
                    self.villain.extend(cls(self).group)
                    self.event('Villain: %s' % cls.name)
            elif villain in vhs:
                cls = vhs[villain]
                for i in range(n_vg + n_vh):
                    for i in range(10):
                        self.villain.append(cls(self))
                    self.event('Henchman: %s' % cls.name)
            else:
                print 'Unknown Villain "%s"' % villain
                print 'Known Villains: %s' % (vs.keys() + vhs.keys())
                raise ValueError
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
            if (self.mastermind.always_leads in vs.values() and
                    (not solo or self.mastermind.force_always_leads)):
                cls = self.mastermind.always_leads
            elif self.scheme.always_leads in vs.values():
                cls = self.scheme.always_leads
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
            elif self.scheme.always_leads in vhs.values():
                cls = self.scheme.always_leads
            else:
                cls = self.rng.choice(vhs.values())
            for k in vhs.keys():
                if vhs[k] is cls:
                    del vhs[k]
                    break
            for j in range(3 if (solo and i == 0) else 10):
                self.villain.append(cls(self))
            self.event('Henchman: %s' % cls.name)


        for i in range(1 if self.solo_basic else 5):
            self.villain.append(MasterStrike(self))

        for i in range(self.scheme.adjust_bystander_count(n_by)):
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
        self.scheme.on_start()
        self.event('Scheme: %s' % self.scheme)

    def fill_hq(self):
        for i in range(5):
            if self.hq[i] is None:
                if len(self.hero) == 0:
                    self.scheme.on_empty_hero()
                    self.tie_game()
                    return
                self.hq[i] = self.hero.pop(0)

    def add_twists(self, count):
        for i in range(count):
            self.villain.append(SchemeTwist(self))

    def start(self):
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


    def play_villain(self, card=None):
        if card is None:
            if len(self.villain) == 0:
                self.scheme.on_empty_villain()
                self.tie_game()
                return
            card = self.villain.pop(0)
        if isinstance(card, Villain):
            self.shift_city()
            self.event('A new Villain enters the city: %s' % card)
            self.city[4] = card
            card.on_ambush()
        elif isinstance(card, SchemeTwist):
            self.event('Scheme Twist!')
            self.scheme_twist()
        elif isinstance(card, MasterStrike):
            self.event('%s makes a master strike' % self.mastermind)
            self.mastermind.strike()
            if self.solo_advanced:
                self.play_villain()
        elif isinstance(card, Bystander):
            card = self.capture_bystander()
        else:
            raise Exception('could not handle %s' % card)

    def scheme_twist(self):
        self.scheme.twist()
        if len(self.players) == 1:
            actions = []
            for c in self.hq:
                if c is not None and c.cost <= 6:
                    if self.solo_advanced:
                        actions.append(action.ReplaceFromHQ(c))
                    else:
                        actions.append(action.KOFromHQ(c))
            if actions:
                self.choice(actions)


    def shift_city(self):
        index = 4
        while self.city[index] is not None:
            index -= 1
            if index < 0:
                self.escaped.append(self.city[0])
                self.on_escape(self.city[0])
                self.city[0].on_escape()
                self.scheme.on_escape(self.city[0])
                self.mastermind.on_escape(self.city[0])
                self.city[0] = None
                index = 0
        for i in range(index, 4):
            self.city[i] = self.city[i + 1]
        self.city[4] = None

    def capture_bystander(self, index=None):
        if len(self.bystanders) == 0:
            return
        if index is None:
            index = 4
            while self.city[index] is None and index >= 0:
                index -= 1
        if index < 0:
            v = self.mastermind
        else:
            v = self.city[index]
        self.event('%s captures a Bystander' % v.name)
        v.capture(self.bystanders.pop(0))
        return v

    def on_escape(self, card):
        self.event('%s escaped!' % card.name)
        actions = []
        for c in self.hq:
            if c is not None and c.cost <= 6:
                actions.append(action.KOFromHQ(c))
        if len(actions) > 0:
            self.choice(actions)

        if len(card.captured) > 0:
            for p in self.players:
                actions = []
                for c in p.hand:
                    actions.append(action.DiscardFrom(c, p.hand))
                if len(actions) > 0:
                    self.choice(actions)

    def find_highest_cost_hero(self):
        index = None
        cost = 0
        for i in range(5):
            if self.hq[i] is not None and cost <= self.hq[i].cost:
                cost = self.hq[i].cost
                index = i
        return index





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
            n_bystanders = len([b for b in p.victory_pile
                                  if isinstance(b, Bystander)])
            if p is self.current_player:
                lines.append('Player %d (current) [S%d P%d V%d B%d]' % (i+1,
                                                      p.available_star,
                                                      p.available_power,
                                                      p.victory_points(),
                                                      n_bystanders))
                for x in p.hand:
                    lines.append('  %s' % x.text())
                for i in range(10-len(p.hand)):
                    lines.append('  ----------------')
            else:
                hand = ', '.join(['%s' % x for x in p.hand])
                lines.append('Player %d [V%d B%d]: %s' % (i+1,
                                                      p.victory_points(),
                                                      n_bystanders,
                                                      hand))
        lines.append('----------------------------------------')
        for event in self.recent_events:
            lines.append(event)
        for i in range(4-len(self.recent_events)):
            lines.append('................')

        return '\n'.join(lines)

    def html_state(self):
        lines = []
        lines.append('''<style>
                div#actions {
                    background: #aa8c39;
                }
                div#actions li:hover {
                    background: #d4b96a;
                    cursor:pointer;
                }
                div#events {
                    background: #8e79ad;
                }
                </style>''')
        lines.append('<ul><li>Mastermind: %s (%d/4)' % (self.mastermind.html(),
                                                len(self.mastermind.tactics)))
        lines.append('<li>Scheme: %s</ul>' % self.scheme.html())
        lines.append('Escaped: %d' % len(self.escaped))
        def text(x):
            return x.html() if x is not None else '-----'
        lines.append('<table>')
        lines.append('<tr><td>Bridge</td><td>%s</td></tr>' % text(self.city[0]))
        lines.append('<tr><td>Streets</td><td>%s</td></tr>' % text(self.city[1]))
        lines.append('<tr><td>Rooftops</td><td>%s</td></tr>' % text(self.city[2]))
        lines.append('<tr><td>Bank</td><td>%s</td></tr>' % text(self.city[3]))
        lines.append('<tr><td>Sewers</td><td>%s</td></tr>' % text(self.city[4]))
        lines.append('</table>')
        lines.append('Villain Pile: %d' % len(self.villain))

        lines.append('<table>')
        for i in range(5):
            if self.hq[i] is None:
                lines.append('<tr><td>HQ %d</td><td>None</td></tr>' % (i + 1))
            else:
                lines.append('<tr><td>HQ %d (%d)</td><td>%s</td></tr>' % (i + 1, self.hq[i].cost,
                                                  self.hq[i].html()))
        lines.append('</table>')
        lines.append('Hero Pile: %d' % len(self.hero))
        for i, p in enumerate(self.players):
            n_bystanders = len([b for b in p.victory_pile
                                  if isinstance(b, Bystander)])
            if p is self.current_player:
                lines.append('<div class="current_player">')
                lines.append('Player %d (current) [S%d P%d V%d B%d]' % (i+1,
                                                      p.available_star,
                                                      p.available_power,
                                                      p.victory_points(),
                                                      n_bystanders))
                lines.append('<ul>')
                for x in p.hand:
                    lines.append('<li>%s' % x.html())
                lines.append('</ul>')
                lines.append('</div>')
            else:
                lines.append('<div class="other_player">')
                hand = ', '.join(['%s' % x for x in p.hand])
                lines.append('Player %d [V%d B%d]: %s' % (i+1,
                                                      p.victory_points(),
                                                      n_bystanders,
                                                      hand))
                lines.append('</div>')
        lines.append('<div id="events"><ul>')
        for event in self.recent_events:
            lines.append('<li>%s</li>' % escape(event))
        lines.append('</ul></div>')

        return '\n'.join(lines)


    def evil_wins(self):
        self.event('Evil Wins!')
        self.result = -1
        raise bg.FinishedException()
    def good_wins(self):
        self.event('Good Wins!')
        self.result = 1
        raise bg.FinishedException()
    def tie_game(self):
        self.event('Tie game!')
        self.result = 0
        raise bg.FinishedException()

    def choice(self, actions, **kwargs):
        self.on_choice()
        c = super(Legendary, self).choice(actions, **kwargs)
        self.on_choice()
        return c

    def on_choice(self):
        for h in self.turn_handlers['on_choice']:
            h.update(self)
        for h in self.handlers['on_choice']:
            h.update(self)

    def add_turn_handler(self, key, handler):
        self.turn_handlers[key].append(handler)
        handler.start(self)
    def add_handler(self, key, handler):
        self.handlers[key].append(handler)
        handler.start(self)

    def clear_turn_handlers(self):
        for v in self.turn_handlers.values():
            while len(v) > 0:
                v.pop().stop(self)
