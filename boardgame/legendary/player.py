import boardgame as bg

from . import hero
from .core import Hero
from . import action

class Player(object):
    def __init__(self, game, name):
        self.game = game
        self.name = name
        self.stack = []
        self.hand = []
        self.discard = []
        self.played = []
        self.victory_pile = []
        self.return_after_draw = []
        self.available_power = 0
        self.available_star = 0
        self.used_star = 0
        self.has_fought = False
        self.has_recruited = False
        self.has_healed = False
        self.extra_draw_count = 0
        self.take_another_turn = False
        self.can_use_star_as_power = False
        self.draw_target = 6
        self.draw_hand_extra = 0
        for i in range(8):
            self.gain(hero.ShieldAgent(game))
        for i in range(4):
            self.gain(hero.ShieldTrooper(game))
        self.draw_new_hand()
        self.handlers = {}
        self.handlers['on_fight'] = []
        self.handlers['on_ko'] = []

    def clear_handlers(self):
        for v in self.handlers.values():
            del v[:]

    def discard_hand(self):
        self.discard.extend(self.hand)
        del self.hand[:]

    def discard_played(self):
        for c in self.played:
            if c.is_copy:
                if c.original is not None:
                    self.discard.append(c.original)
            else:
                self.discard.append(c)

        del self.played[:]

    def discard_from(self, card, location, allow_return=True):
        if (card.return_from_discard and location is self.hand
            and allow_return):
                #TODO: make this an option
                self.game.event('%s returned to hand' % card)
        else:
            card.on_discard(self)
            self.discard.append(card)
            location.remove(card)

    def draw_new_hand(self):
        self.draw(self.draw_target + self.draw_hand_extra, event_message=False)
        self.draw_hand_extra = 0
        for c in self.return_after_draw:
            if c in self.discard:
                self.discard.remove(c)
                self.hand.append(c)
            elif c in self.stack:
                self.stack.remove(c)
                self.hand.append(c)
            elif c in self.game.ko:
                self.game.ko.remove(c)
                self.hand.append(c)
            else:
                assert c in self.hand
                #TODO: what else chould go wrong here?
        del self.return_after_draw[:]


    def gain(self, card):
        self.discard.append(card)

    def gain_wound(self, wounder=None):
        if len(self.game.wounds) > 0:
            for c in self.hand + self.played:
                if hasattr(c, 'allow_wound'):
                    if not c.allow_wound(self):
                        return
            if wounder is not None:
                self.game.event('%s wounds %s' % (wounder.name, self.name))
            self.gain(self.game.wounds.pop(0))
        if len(self.game.wounds) == 0:
            self.game.scheme.on_wound_empty()

    def reveal(self, count):
        index = len(self.hand)
        self.draw(count, event_message=False, count_draw=False)
        cards = self.hand[index:]
        del self.hand[index:]
        for c in cards:
            self.game.event('Reveal %s' % c)
        return cards

    def return_to_stack(self, card):
        self.stack.insert(0, card)

    def reveal_tag(self, tag, ignore=None):
        for c in self.hand + self.played:
            if tag in c.tags and c is not ignore:
                return c
        return None

    def draw(self, count, put_in_hand=True, event_message=True,
             count_draw=True):
        cards = []
        for i in range(count):
            if len(self.stack) == 0:
                self.stack.extend(self.game.rng.permutation(self.discard))
                del self.discard[:]
            if len(self.stack) > 0:
                if count_draw:
                    self.extra_draw_count += 1
                cards.append(self.stack.pop(0))
            else:
                self.game.event('%s tries to draw but has no cards' %
                                self.name)
        if put_in_hand:
            self.hand.extend(cards)
        if event_message:
            if len(cards) == 0:
                self.game.event('%s draws no cards' % self.name)
            elif len(cards) == 1:
                self.game.event('%s draws a card' % self.name)
            else:
                self.game.event('%s draws %d cards' % (self.name, len(cards)))
        return cards

    def count_played(self, tag, ignore=None):
        return len(self.get_played(tag=tag, ignore=ignore))
    def get_played(self, tag, ignore=None):
        return [c for c in self.played if tag in c.tags and c is not ignore]

    def count_tagged(self, tag):
        return len(self.get_tagged(tag=tag))
    def get_tagged(self, tag):
        cards = []
        for c in self.played:
            if tag in c.tags:
                cards.append(c)
        for c in self.hand:
            if tag in c.tags:
                cards.append(c)
        return cards



    def victory_points(self):
        total = 0
        for c in self.victory_pile:
            total += c.victory
            if c.extra_victory:
                total += c.extra_victory(self)
        for c in self.game.escaped:
            total -= 4 * len(c.captured)
            total -= 1
        total -= self.game.scheme.twists_done * 3
        return total

    def play_from_hand(self, card):
        self.available_power += card.power
        self.available_star += card.star
        self.played.append(card)
        self.hand.remove(card)
        card.on_play(self)

    def play(self, card):
        self.available_power += card.power
        self.available_star += card.star
        self.played.append(card)
        card.on_play(self)

    def rescue_bystander(self, villain=None):
        if villain is None:
            if len(self.game.bystanders) > 0:
                self.victory_pile.append(self.game.bystanders.pop())
                self.game.event('Rescued Bystander')
        else:
            if villain.captured:
                for c in villain.captured:
                    self.game.scheme.on_rescue(villain, c)
                self.victory_pile.extend(villain.captured)
                if len(villain.captured) == 1:
                    self.game.event('Rescued Bystander from %s' % villain.name)
                else:
                    self.game.event('Rescued %d Bystanders from %s' %
                            (len(villain.captured), villain.name))
                del villain.captured[:]



    def on_fight(self, enemy):
        for x in self.handlers['on_fight']:
            x(enemy)
    def on_ko(self, card):
        for x in self.handlers['on_ko']:
            x(card)

    def ko_hero_from(self, *locations):
        actions = []
        for loc in locations:
            for h in loc:
                if isinstance(h, Hero):
                    actions.append(action.KOFrom(h, loc))
        if len(actions) == 0:
            return None
        else:
            return self.game.choice(actions)

    def defeat(self, villain):
        self.rescue_bystander(villain)

        if villain is self.game.mastermind:
            m = villain
            villain = villain.tactics.pop(0)
            self.game.event('Mastermind Tactic: %s' % villain.text())
            if len(m.tactics) == 0:
                self.game.good_wins()
        elif villain in self.game.city:
            index = self.game.city.index(villain)
            self.game.city[index] = None

        if villain.original is None:
            v = villain
        else:
            v = villain.original
        self.victory_pile.append(v)
        villain.on_fight(self)
        self.on_fight(villain)

        if hasattr(self.game.scheme, 'on_defeat'):
            self.game.scheme.on_defeat(villain, self)


    def choose_star_usage(self, minimum, maximum):
        minimum = max(minimum, 0)
        maximum = min(maximum, self.available_star)

        assert maximum >= minimum

        actions = []
        for i in reversed(range(minimum, maximum + 1)):
            actions.append(action.UseStar(i))
        choice = self.game.choice(actions)
        return choice.star

    def other_players(self):
        for p in self.game.players:
            if p is not self or self.game.solo_advanced:
                yield p

    def discard_down_to(self, count):
        while len(self.hand) > count:
            actions = []
            for h in self.hand:
                actions.append(action.DiscardFrom(h, self.hand,
                                                  allow_return=False))
            self.game.choice(actions, player=self)


