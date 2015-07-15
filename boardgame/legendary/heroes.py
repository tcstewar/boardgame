import boardgame as bg

import action
from .core import Hero, HeroGroup
from .tags import *

class ShieldAgent(Hero):
    name = 'SHIELD Agent'
    star = 1

class ShieldTrooper(Hero):
    name = 'SHIELD Trooper'
    power = 1

class ShieldOfficer(Hero):
    name = 'SHIELD Officer'
    star = 2
    cost = 3

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
    @property
    def power(self):
        return 3 + self.game.current_player.count_played(tag=Tech)

class IronManEndless(Hero):
    name = 'Iron Man: Endless Intervention'
    cost = 3
    tags = [Tech, Avenger]
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(1)

class IronManQuantum(Hero):
    name = 'Iron Man: Quantum Breakthrough'
    cost = 7
    tags = [Tech, Avenger]
    def on_play(self, player):
        player.draw(2)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(2)

class IronManRepulsor(Hero):
    name = 'Iron Man: Repulsor Rays'
    cost = 3
    tags = [Ranged, Avenger]
    @property
    def power(self):
        if self.game.current_player.count_played(tag=Ranged, ignore=self) > 0:
            return 3
        else:
            return 2

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
    def on_play(self, player):
        player.rescue_bystander()
        cards = player.reveal(1)
        for c in cards:
            if c.cost <= 2:
                self.game.event('Spider-Man draws %s' % c)
                player.hand.append(c)
            else:
                player.stack.insert(0, c)

