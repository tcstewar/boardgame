import boardgame as bg

from . import heroes

class Player(object):
    def __init__(self, game):
        self.game = game
        self.stack = []
        self.hand = []
        self.discard = []
        self.played = []
        self.victory_pile = []
        self.available_power = 0
        self.available_star = 0
        for i in range(8):
            self.gain(heroes.ShieldAgent(game))
        for i in range(4):
            self.gain(heroes.ShieldTrooper(game))
        self.draw_new_hand()

    def discard_hand(self):
        self.discard.extend(self.hand)
        del self.hand[:]

    def discard_played(self):
        self.discard.extend(self.played)
        del self.played[:]

    def draw_new_hand(self):
        self.draw(6)

    def gain(self, card):
        self.discard.append(card)

    def gain_wound(self):
        if len(self.game.wounds) > 0:
            self.gain(self.game.wounds.pop(0))

    def draw(self, count):
        for i in range(count):
            if len(self.stack) == 0:
                self.stack.extend(self.game.rng.permutation(self.discard))
                del self.discard[:]
            if len(self.stack) > 0:
                self.hand.append(self.stack.pop(0))

    def count_played(self, tag, ignore=None):
        return len(self.get_played(tag=tag, ignore=ignore))
    def get_played(self, tag, ignore=None):
        return [c for c in self.played if tag in c.tags and c is not ignore]




