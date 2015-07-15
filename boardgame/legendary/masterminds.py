import boardgame as bg

from . import villains
from .core import Mastermind, Tactic, Hero
from . import action

class RedSkull(Mastermind):
    name = 'Red Skull'
    def __init__(self, game):
        super(RedSkull, self).__init__(game)
        self.power = 7
        self.always_leads = villains.Hydra
        self.tactics = [RedSkullTactic1(game), RedSkullTactic2(game),
                        RedSkullTactic3(game), RedSkullTactic4(game)]
        self.game.rng.shuffle(self.tactics)
    def strike(self):
        for p in self.game.players:
            actions = []
            for c in p.hand:
                if isinstance(c, Hero):
                    actions.append(action.KOFrom(c, p.hand))
            if len(actions) > 0:
                self.game.choice(actions)

class RedSkullTactic1(Tactic):
    victory = 5
    def on_fight(self, player):
        player.available_star += 4

class RedSkullTactic2(Tactic):
    victory = 5
    def on_fight(self, player):
        player.draw(2)
        for c in player.victory_pile:
            if c.group is villains.Hydra:
                player.draw(1)

class RedSkullTactic3(Tactic):
    victory = 5
    def on_fight(self, player):
        player.available_power += 3

class RedSkullTactic4(Tactic):
    victory = 5
    def on_fight(self, player):
        index = len(player.hand)
        player.draw(3)
        cards = player.hand[index:]
        player.hand = player.hand[:index]
        actions = []
        for act in [action.KOFrom, action.DiscardFrom, action.ReturnFrom]:
            for card in cards:
                actions.append(act(card, cards))
        self.game.choice(actions, repeat=True, allow_same_type=False)
