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
    def __init__(self, game):
        self.game = game
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
    def __str__(self):
        return '%s (%d)' % (self.name, self.power)
    def on_fight(self, player):
        pass
    def on_escape(self):
        pass

class VillainGroup(Group):
    pass
class HenchmenGroup(Group):
    pass
class HeroGroup(Group):
    pass


class Tactic(bg.Card):
    group = None
    def __init__(self, game):
        super(Tactic, self).__init__(game)

class Mastermind(bg.Card):
    def __init__(self, game):
        super(Mastermind, self).__init__(game)
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
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
    tags = []
    def __str__(self):
        return '%s (%d/%d)' % (self.name, self.star, self.power)
    def on_play(self, player):
        pass

class Tag(object):
    def __init__(self, name):
        self.name = name

class Wound(bg.Card):
    power = 0
    star = 0
    def __str__(self):
        return 'Wound'

