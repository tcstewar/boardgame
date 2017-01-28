import boardgame as bg

class Group(object):
    def __init__(self, game):
        self.group = []
        self.game = game
        self.fill()
    def add(self, card, count):
        for i in range(count):
            c = card(self.game)
            c.group = self.__class__
            self.group.append(c)

class Villain(bg.Card):
    group = None
    bribe = False
    power = 0
    victory = 0
    extra_victory = None
    desc = ''
    original = None
    tags = []
    def __init__(self, game):
        self.game = game
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
        self.game.scheme.on_capture(self, card)
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
        group = ' <%s>' % self.group.name if self.group is not None else ''
        ev = '+' if self.extra_victory else ''
        return '%s%s [P%d V%d%s] %s' % (name, group,
                                        self.power,
                                        self.victory, ev,
                                        self.desc)
    def html(self):
        name = '<strong>%s</strong>' % self.name
        group = ' &lt;%s&gt;' % self.group.name if self.group is not None else ''
        ev = '+' if self.extra_victory else ''
        return '%s%s [P%d V%d%s] %s' % (name, group,
                                        self.power,
                                        self.victory, ev,
                                        self.desc.replace('<','&lt;').replace('>','&gt;'))



class VillainGroup(Group):
    pass
class HeroGroup(Group):
    pass
class Henchman(Villain):
    group = None

def escape(text):
    return text.replace('<','&lt;').replace('>','&gt;')

class Tactic(bg.Card):
    group = None
    extra_victory = None
    def __init__(self, game):
        super(Tactic, self).__init__(game)
    def text(self):
        return '%s: %s' % (self.name, self.desc)

class Mastermind(bg.Card):
    bribe = False
    def __init__(self, game):
        super(Mastermind, self).__init__(game)
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
        self.game.scheme.on_capture(self, card)
    def text(self):
        return '%s [P%d] %s' % (self.name, self.power, self.desc)
    def html(self):
        return '<strong>%s</strong> [P%d] %s' % (self.name, self.power, escape(self.desc))
    def __str__(self):
        return '%s (%d)' % (self.name, self.power)


class Scheme(bg.Card):
    allow_solo = True
    always_leads = None
    def __init__(self, game):
        super(Scheme, self).__init__(game)
        game.add_twists(self.twists)
        self.twists_done = 0
    def __str__(self):
        extra = self.extra_text()
        return '%s (%d/%d) %s%s' % (self.name, self.twists_done, self.twists,
                                    self.desc, extra)
    def html(self):
        extra = self.extra_text()
        return '<strong>%s</strong> (%d/%d) %s%s' % (self.name,
                    self.twists_done, self.twists, escape(self.desc), extra)
    def on_wound_empty(self):
        pass
    def extra_text(self):
        return ''
    def on_start(self):
        pass
    def adjust_bystander_count(self, count):
        return count
    def adjust_henchman_count(self, count):
        return count
    def adjust_hero_count(self, count):
        return count
    def on_capture(self, card, captured):
        pass
    def on_rescue(self, card, captured):
        pass
    def on_escape(self, card):
        pass
    def on_empty_hero(self):
        pass
    def on_empty_villain(self):
        pass

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
    tags = []
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
    grey = False

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
    def html(self):
        name = '<strong>%s</strong>' % self.name
        ep = '+' if self.extra_power else ''
        es = '+' if self.extra_star else ''
        tags = [t.short_name for t in self.tags]
        tags = ' &lt;%s&gt;' % ','.join(tags) if len(tags) > 0 else ' '
        return '%s%s [S%d%s P%d%s] %s' % (name,
                                        tags,
                                        self.star, es,
                                        self.power, ep,
                                        self.desc.replace('<','&lt;').replace('>','&gt;'))


    def __str__(self):
        ep = '+' if self.extra_power else ''
        es = '+' if self.extra_star else ''
        return '[S%d%s P%d%s] %s' % (self.star, es, self.power, ep, self.name)
    def on_play(self, player):
        pass
    def on_discard(self, player):
        pass

class Tag(object):
    def __init__(self, name, short_name):
        self.name = name
        self.short_name = short_name

class Wound(bg.Card):
    name = 'Wound'
    power = 0
    star = 0
    extra_star = False
    extra_power = False
    cost = 0
    tags = []
    grey = False
    return_from_discard = False
    def __str__(self):
        return self.name
    def text(self):
        return self.name
    def html(self):
        return '<strong>Wound</strong>'
    def on_play(self, player):
        pass
    def on_discard(self, player):
        pass

class Handler(object):
    def start(self):
        raise NotImplementedError
    def stop(self):
        raise NotImplementedError
    def update(self):
        raise NotImplementedError

class Adjust(Handler):
    def __init__(self, items):
        self.items_func = items
        self.applied = []
    def items(self, game):
        return self.items_func(game)
    def start(self, game):
        for c in self.items(game):
            if c is not None:
                self.apply(c)
                self.applied.append(c)
    def update(self, game):
        self.stop(game)
        self.start(game)
    def stop(self, game):
        for c in self.applied:
            self.remove(c)
        del self.applied[:]
    def apply(self, item):
        raise NotImplementedError
    def remove(self, item):
        raise NotImplementedError

class AdjustPower(Adjust):
    def __init__(self, items, amount):
        super(AdjustPower, self).__init__(items)
        self.amount = amount

    def apply(self, item):
        item.power += self.amount

    def remove(self, item):
        item.power -= self.amount
