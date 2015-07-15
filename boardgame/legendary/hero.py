import boardgame as bg

import action
from .core import Hero, HeroGroup
from .tags import *

class ShieldAgent(Hero):
    name = 'SHIELD Agent'
    star = 1
    tags = [Shield]

class ShieldTrooper(Hero):
    name = 'SHIELD Trooper'
    power = 1
    tags = [Shield]

class ShieldOfficer(Hero):
    name = 'SHIELD Officer'
    star = 2
    cost = 3
    tags = [Shield]

class IronMan(HeroGroup):
    def fill(self):
        self.add(IronManRepulsor, 5)
        self.add(IronManQuantum, 1)
        self.add(IronManEndless, 5)
        self.add(IronManArc, 3)

class IronManArc(Hero):
    name = 'Iron Man: Arc Reactor'
    cost = 5
    tags = [Tech, Avenger]
    power = 3
    extra_power = True
    desc = 'P+1 per other <Tec> played'
    def on_play(self, player):
        player.available_power += player.count_played(tag=Tech)

class IronManEndless(Hero):
    name = 'Iron Man: Endless Intervention'
    cost = 3
    tags = [Tech, Avenger]
    desc = 'Draw a card. <Tec>: Draw another card'
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(1)

class IronManQuantum(Hero):
    name = 'Iron Man: Quantum Breakthrough'
    cost = 7
    tags = [Tech, Avenger]
    desc = 'Draw two cards. <Tec>: Draw two more cards'
    def on_play(self, player):
        player.draw(2)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(2)

class IronManRepulsor(Hero):
    name = 'Iron Man: Repulsor Rays'
    cost = 3
    tags = [Ranged, Avenger]
    power = 2
    extra_power = True
    desc = '<Rng>: P+1'
    def on_play(self, player):
        if player.count_played(tag=Ranged, ignore=self) > 0:
            player.available_power += 1

class SpiderMan(HeroGroup):
    def fill(self):
        self.add(SpiderManStrength, 5)
        self.add(SpiderManAmazing, 1)
        self.add(SpiderManResponsibility, 5)
        self.add(SpiderManWeb, 3)

class SpiderManStrength(Hero):
    name = 'Spider-Man: Astonishing Strength'
    cost = 2
    star = 1
    tags = [Spider, Strength]
    desc = 'Reveal top card. If C<=2, draw it.'
    def on_play(self, player):
        cards = player.reveal(1)
        for c in cards:
            if c.cost <= 2:
                self.game.event('Spider-Man draws %s' % c)
                player.hand.append(c)
            else:
                player.stack.insert(0, c)

class SpiderManAmazing(Hero):
    name = 'Spider-Man: The Amazing Spider-Man'
    cost = 2
    tags = [Spider, Covert]
    desc = 'Reveal top 3 cards. Draw any with C<=2. Return others in any order.'
    def on_play(self, player):
        cards = player.reveal(3)
        actions = []
        for c in cards:
            if c.cost <= 2:
                self.game.event('Spider-Man draws %s' % c)
                player.hand.append(c)
            else:
                actions.append(action.ReturnFrom(c, cards))
        if len(actions) <= 1:
            for a in actions:
                player.stack.insert(0, a.card)
        else:
            self.game.choice(actions)

class SpiderManResponsibility(Hero):
    name = 'Spider-Man: Great Responsibility'
    cost = 2
    power = 1
    tags = [Spider, Instinct]
    desc = 'Reveal top card. If C<=2, draw it.'
    def on_play(self, player):
        cards = player.reveal(1)
        for c in cards:
            if c.cost <= 2:
                self.game.event('Spider-Man draws %s' % c)
                player.hand.append(c)
            else:
                player.stack.insert(0, c)


class SpiderManWeb(Hero):
    name = 'Spider-Man: Web Shooters'
    cost = 2
    tags = [Spider, Tech]
    desc = 'Rescue Bystander. Reveal top card. If C<=2, draw it.'
    def on_play(self, player):
        player.rescue_bystander()
        cards = player.reveal(1)
        for c in cards:
            if c.cost <= 2:
                self.game.event('Spider-Man draws %s' % c)
                player.hand.append(c)
            else:
                player.stack.insert(0, c)

class Wolverine(HeroGroup):
    def fill(self):
        self.add(WolverineAmbush, 5)
        self.add(WolverineAnimal, 5)
        self.add(WolverineReckless, 1)
        self.add(WolverineNoMercy, 3)

class WolverineAmbush(Hero):
    name = 'Wolverine: Sudden Ambush'
    cost = 4
    tags = [XMen, Covert]
    desc = 'If you drew any extra cards this turn, P+2'
    extra_power = True
    def on_play(self, player):
        if player.extra_draw_count > 0:
            player.available_power += 2

class WolverineAnimal(Hero):
    name = 'Wolverine: Animal Instincts'
    cost = 2
    tags = [XMen, Instinct]
    desc = 'Draw a card. <Ins>: P+2'
    extra_power = True
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Instinct, ignore=self) > 0:
            player.available_power += 2

class WolverineReckless(Hero):
    name = 'Wolverine: Reckless Abandon'
    cost = 7
    tags = [XMen, Covert]
    power = 3
    desc = 'Count how many extra cards you have drawn. Draw that many cards.'
    def on_play(self, player):
        count = player.extra_draw_count
        player.draw(count)

class WolverineNoMercy(Hero):
    name = 'Wolverine: No Mercy'
    cost = 4
    tags = [XMen, Strength]
    desc = 'Draw a card. You may KO a card from your hand or discard pile.'
    def on_play(self, player):
        player.draw(1)
        actions = []
        for c in player.hand:
            actions.append(action.KOFrom(c, player.hand))
        for c in player.discard:
            actions.append(action.KOFrom(c, player.discard))
        actions.append(action.DoNothing())
        self.game.choice(actions)



