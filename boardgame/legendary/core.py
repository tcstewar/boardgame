import boardgame as bg

class Group(object):
    def __init__(self, game):
        self.group = []
        self.game = game
        self.fill()
    def add(self, card, count):
        for i in range(count):
            self.group.append(card(self.game))

class Villain(object):
    power = 0
    victory = 0
    extra_victory = None
    def __init__(self, game):
        self.game = game
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
    def __str__(self):
        ev = '+' if self.extra_victory else ''
        return '%s [P%d V%d%s]' % (self.name, self.power, self.victory, ev)
    def on_fight(self, player):
        pass
    def on_pre_fight(self, player):
        pass
    def can_fight(self, player):
        return True
    def on_escape(self):
        pass
    def on_ambush(self):
        pass
    def text(self):
        name = '%40s' % self.name
        group = self.group.name if self.group is not None else ''
        ev = '+' if self.extra_victory else ''
        return '%s <%s> [P%d V%d%s] %s' % (name, group,
                                           self.power,
                                           self.victory, ev,
                                           self.desc)


class VillainGroup(Group):
    pass
class HeroGroup(Group):
    pass
class Henchman(Villain):
    group = None


class Tactic(bg.Card):
    group = None
    extra_victory = None
    def __init__(self, game):
        super(Tactic, self).__init__(game)
    def text(self):
        return '%s: %s' % (self.name, self.desc)

class Mastermind(bg.Card):
    def __init__(self, game):
        super(Mastermind, self).__init__(game)
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
    def text(self):
        return '%s [P%d] %s' % (self.name, self.power, self.desc)
    def __str__(self):
        return '%s (%d)' % (self.name, self.power)


class Scheme(bg.Card):
    def __init__(self, game, twists):
        super(Scheme, self).__init__(game)
        game.add_twists(twists)
        self.twists_done = 0
        self.twists_total = twists
    def __str__(self):
        return '%s (%d/%d)' % (self.name, self.twists_done, self.twists_total)

class SchemeTwist(bg.Card):
    def __str__(self):
        return 'Scheme Twist'
class MasterStrike(bg.Card):
    def __str__(self):
        return 'Master Strike'
class Bystander(bg.Card):
    victory = 1
    extra_victory = False
    group = None
    def __str__(self):
        return 'Bystander'


class GameState(object):
    def __init__(self, name):
        self.name = name

BeginTurn = GameState('Begin Turn')
DuringTurn = GameState('During Turn')


class Hero(bg.Card):
    group = None
    power = 0
    star = 0
    cost = 0
    extra_power = False
    extra_star = False
    tags = []
    desc = ''
    return_from_discard = False

    def text(self):
        name = '%35s' % self.name
        ep = '+' if self.extra_power else ''
        es = '+' if self.extra_star else ''
        tags = [t.short_name for t in self.tags]
        tags = ' <%s>' % ','.join(tags) if len(tags) > 0 else ' '
        return '%s%s [S%d%s P%d%s] %s' % (name,
                                        tags,
                                        self.star, es,
                                        self.power, ep,
                                        self.desc)

    def __str__(self):
        ep = '+' if self.extra_power else ''
        es = '+' if self.extra_star else ''
        return '[S%d%s P%d%s] %s' % (self.star, es, self.power, ep, self.name)
    def on_play(self, player):
        pass

class Tag(object):
    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name

class Wound(bg.Card):
    power = 0
    star = 0
    cost = 0
    tags = []
    return_from_discard = False
    def __str__(self):
        return 'Wound'
    def text(self):
        return 'Wound'

