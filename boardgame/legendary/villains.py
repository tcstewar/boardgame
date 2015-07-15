import boardgame as bg

from .core import Villain, VillainGroup
from . import action
from . import heroes

class Hydra(VillainGroup):
    def fill(self):
        self.add(HydraKidnappers, 3)
        self.add(HydraArmies, 3)
        self.add(HydraViper, 1)
        self.add(HydraSupreme, 1)

class HydraKidnappers(Villain):
    power = 3
    victory = 1
    group = Hydra
    name = 'HYDRA Kidnappers'
    def on_fight(self, player):
        actions = [action.GainCard(self.game, heroes.ShieldOfficer(self.game)),
                   action.DoNothing(self.game)]
        self.game.choice(actions)

class HydraArmies(Villain):
    power = 4
    victory = 3
    group = Hydra
    name = 'Endless Armies of HYDRA'
    def on_fight(self, player):
        self.game.play_villain()
        self.game.play_villain()

class HydraViper(Villain):
    power = 5
    victory = 3
    group = Hydra
    name = 'Viper'
    def on_fight(self, player):
        for p in self.game.players:
            for v in p.victory_pile:
                if v.group is Hydra and v != self:
                    break
            else:
                p.gain_wound()
    def on_escape(self):
        self.on_fight(None)

class HydraSupreme(Villain):
    power = 6
    group = Hydra
    name = 'Supreme HYDRA'
    @property
    def victory(self):
        for p in self.game.players:
            if self in p.victory_pile:
                pts = 0
                for v in p.victory_pile:
                    if v.group is Hydra:
                        pts += 3
                return pts
        return 3
