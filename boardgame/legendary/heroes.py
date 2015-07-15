import boardgame as bg

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
