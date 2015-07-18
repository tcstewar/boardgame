import boardgame as bg

from . import villains
from .core import Mastermind, Tactic, Hero
from . import action
from . import tags

class RedSkull(Mastermind):
    name = 'Red Skull'
    desc = 'Master Strike: Each player KOs a Hero from their hand.'
    always_leads = villains.Hydra
    power = 7
    def __init__(self, game):
        super(RedSkull, self).__init__(game)
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
    name = 'Endless Resources'
    desc = 'S+4'
    victory = 5
    def on_fight(self, player):
        player.available_star += 4

class RedSkullTactic2(Tactic):
    name = 'HYDRA Conspiracy'
    desc = 'Draw 2 cards. Draw another per HYDRA Villain in Victory Pile'
    victory = 5
    def on_fight(self, player):
        player.draw(2)
        for c in player.victory_pile:
            if c.group is villains.Hydra:
                player.draw(1)

class RedSkullTactic3(Tactic):
    name = 'Negablast Grenades'
    desc = 'P+3'
    victory = 5
    def on_fight(self, player):
        player.available_power += 3

class RedSkullTactic4(Tactic):
    name = 'Ruthless Dictator'
    desc = 'Reveal top 3 cards. KO one, discard one, return one.'
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


class DrDoom(Mastermind):
    name = 'Dr. Doom'
    desc = ('Master Strike: Each player with exactly 6 card in hand reveals '
            '<Tec> or returns 2 cards from hand to deck.')

    always_leads = villains.DoombotGroup
    power = 9

    def __init__(self, game):
        super(DrDoom, self).__init__(game)
        self.tactics = [DrDoomTactic1(game), DrDoomTactic2(game),
                        DrDoomTactic3(game), DrDoomTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            if len(p.hand) == 6:
                actions = []
                for c in p.hand:
                    actions.append(action.ReturnFrom(c, p.hand))
                self.game.choice(actions, player=p)
                self.game.choice(actions, player=p)

class DrDoomTactic1(Tactic):
    name = 'Dark Technology'
    desc = 'You may recruit a <Tec> or <Rng> hero for free'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in self.game.hq:
            if c is not None and (tags.Tech in c.tags or
                                  tags.Ranged in c.tags):
                actions.append(action.GainFrom(c, self.game.hq))
        if len(actions) > 0:
            self.game.choice(actions)

class DrDoomTactic2(Tactic):
    name = "Monarch's Decree"
    desc = ('Choose one: each other player discards a card or '
            'each other player draws a card.')
    victory = 5
    def on_fight(self, player):
        actions = [
            bg.CustomAction('Each other player draws a card',
                      self.on_choose_draw, kwargs=dict(player=player)),
            bg.CustomAction('Each other player discards a card',
                      self.on_choose_discard, kwargs=dict(player=player)),
            ]
        self.game.choice(actions)

    def on_choose_draw(self, player):
        for p in self.game.players:
            if p is not player:
                p.draw(1)

    def on_choose_discard(self, player):
        for p in self.game.players:
            if p is not player:
                actions = []
                for h in p.hand:
                    actions.append(action.DiscardFrom(h, p.hand))
                self.game.choice(actions, player=p)

class DrDoomTactic3(Tactic):
    name = 'Secrets of Time Travel'
    desc = 'Take another turn after this one'
    victory = 5
    def on_fight(self, player):
        player.take_another_turn = True

class DrDoomTactic4(Tactic):
    name = 'Treasures of Latveria'
    desc = 'When you draw a new hand at the end of your turn, draw 3 extra.'
    victory = 5
    def on_fight(self, player):
        player.draw_hand_extra += 3
