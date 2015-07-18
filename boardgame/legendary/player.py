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
        self.available_power = 0
        self.available_star = 0
        self.has_fought = False
        self.has_recruited = False
        self.has_healed = False
        self.extra_draw_count = 0
        self.take_another_turn = False
        self.draw_target = 6
        self.draw_hand_extra = 0
        for i in range(8):
            self.gain(hero.ShieldAgent(game))
        for i in range(4):
            self.gain(hero.ShieldTrooper(game))
        self.draw_new_hand()
        self.handlers = {}
        self.handlers[self.on_fight] = []

    def clear_handlers(self):
        for v in self.handlers.values():
            del v[:]

    def discard_hand(self):
        self.discard.extend(self.hand)
        del self.hand[:]

    def discard_played(self):
        self.discard.extend(self.played)
        del self.played[:]

    def draw_new_hand(self):
        self.draw(self.draw_target + self.draw_hand_extra)
        self.draw_hand_extra = 0

    def gain(self, card):
        self.discard.append(card)

    def gain_wound(self):
        if len(self.game.wounds) > 0:
            self.gain(self.game.wounds.pop(0))

    def reveal(self, count):
        index = len(self.hand)
        self.draw(count)
        cards = self.hand[index:]
        del self.hand[index:]
        for c in cards:
            self.game.event('Reveal %s' % c)
        return cards

    def draw(self, count):
        for i in range(count):
            if len(self.stack) == 0:
                self.stack.extend(self.game.rng.permutation(self.discard))
                del self.discard[:]
            if len(self.stack) > 0:
                self.extra_draw_count += 1
                self.hand.append(self.stack.pop(0))
            else:
                self.game.event('%s tries to draw but has no cards' %
                                self.name)

    def count_played(self, tag, ignore=None):
        return len(self.get_played(tag=tag, ignore=ignore))
    def get_played(self, tag, ignore=None):
        return [c for c in self.played if tag in c.tags and c is not ignore]

    def victory_points(self):
        total = 0
        for c in self.victory_pile:
            total += c.victory
            if c.extra_victory:
                total += c.extra_victory(self)
        return total

    def play_from_hand(self, card):
        self.available_power += card.power
        self.available_star += card.star
        card.on_play(self)
        self.played.append(card)
        self.hand.remove(card)

    def rescue_bystander(self):
        if len(self.game.bystanders) > 0:
            self.victory_pile.append(self.game.bystanders.pop())
            self.game.event('Rescued Bystander')


    def on_fight(self, enemy):
        for x in self.handlers[on_fight]:
            x(enemy)

    def ko_from(self, *locations):
        actions = []
        for loc in locations:
            for h in loc:
                if isinstance(h, Hero):
                    actions.append(action.KOFrom(h, loc))
        self.game.choice(actions)

    def defeat(self, villain):
        self.victory_pile.extend(villain.captured)
        del villain.captured[:]

        if villain is self.game.mastermind:
            villain = villain.tactics.pop(0)
            self.game.event('Mastermind Tactic: %s' % villain.text())
        elif villain in self.game.city:
            index = self.game.city.index(villain)
            self.game.city[index] = None

        self.victory_pile.append(villain)
        villain.on_fight(self)



