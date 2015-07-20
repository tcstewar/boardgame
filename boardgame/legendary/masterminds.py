import boardgame as bg

from . import villains
from .core import *
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
        if len(cards) > 0:
            repeat = len(cards) - 1
            self.game.choice(actions, repeat=repeat, allow_same_type=False)


class DrDoom(Mastermind):
    name = 'Dr. Doom'
    desc = ('Master Strike: Each player with exactly 6 card in hand reveals '
            '<Tec> or returns 2 cards from hand to deck.')

    always_leads = villains.DoombotLegion
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


class Loki(Mastermind):
    name = 'Loki'
    desc = 'Master Strike: Each player reveals a <Str> or gains a Wound.'

    always_leads = villains.EnemiesOfAsgard
    power = 10

    def __init__(self, game):
        super(Loki, self).__init__(game)
        self.tactics = [LokiTactic1(game), LokiTactic2(game),
                        LokiTactic3(game), LokiTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            if p.count_played(tag=tags.Strength) == 0:
                self.game.event('Loki wounds %s' % p.name)
                p.gain_wound()

class LokiTactic1(Tactic):
    name = 'Whispers and Lies'
    desc = 'Each other player KOs 2 Bystanders from victory pile'
    victory = 5
    def on_fight(self, player):
        for p in self.game.players:
            if p is not player:
                count = 2
                for c in p.victory_pile[:]:
                    if isinstance(c, Bystander):
                        p.victory_pile.remove(c)
                        self.game.ko.append(c)
                        count -= 1
                        if count == 0:
                            break

class LokiTactic2(Tactic):
    name = 'Vanishing Illusions'
    desc = 'Each other player KOs a Villain from their victory pile.'
    victory = 5
    def on_fight(self, player):
        for p in self.game.players:
            if p is player:
                continue
            actions = []
            for c in p.victory_pile:
                if isinstance(c, Villain):
                    actions.append(action.KOFrom(c, p.victory_pile))
            if len(actions) > 0:
                self.game.choice(actions)

class LokiTactic3(Tactic):
    name = 'Maniacal Tyrant'
    desc = 'KO up to 4 cards from your discard pile'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in player.discard:
            actions.append(action.KOFrom(c, player.discard))
        for i in range(4):
            choice = self.game.choice(actions, allow_do_nothing=True)
            if choice is None:
                break

class LokiTactic4(Tactic):
    name = 'Cruel Ruler'
    desc = 'Defeat a Villain in the city for free'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in self.game.city:
            if c is not None:
                actions.append(bg.CustomAction(
                    'Defeat %s' % c.text(),
                    func=player.defeat,
                    kwargs=dict(villain=c)))
        if len(actions) > 0:
            self.game.choice(actions)
