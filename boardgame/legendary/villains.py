import boardgame as bg

from .core import Villain, VillainGroup
from . import action

class Hydra(VillainGroup):
    name = 'HYDRA'
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
    desc = 'Fight: You may gain a SHIELD Officer'
    def on_fight(self, player):
        if len(self.game.officers) > 0:
            actions = [action.GainFrom(self.game.officers[0],
                                       self.game.officers
                                       ),
                       action.DoNothing()]
        self.game.choice(actions)

class HydraArmies(Villain):
    power = 4
    victory = 3
    group = Hydra
    name = 'Endless Armies of HYDRA'
    desc = 'Fight: Play the top two cards of the Villain deck.'
    def on_fight(self, player):
        self.game.play_villain()
        self.game.play_villain()

class HydraViper(Villain):
    power = 5
    victory = 3
    group = Hydra
    name = 'Viper'
    desc = ('Fight: Each player without other HYDRA in Victory Pile gains'
            ' Wound. Escape: Same effect')
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
    desc = 'V+3 for each other HYDRA in Victory Pile'
    victory = 3
    def extra_victory(self, player):
        pts = 0
        for v in player.victory_pile:
            if v.group is Hydra and v is not self:
                pts += 3
        return pts
