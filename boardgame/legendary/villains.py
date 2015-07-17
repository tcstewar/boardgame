import boardgame as bg

from .core import Villain, VillainGroup, HenchmenGroup
from . import action
from . import tags

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

class SentinelGroup(HenchmenGroup):
    name = 'Sentinel'
    def fill(self):
        self.add(Sentinel, 10)

class Sentinel(Villain):
    name = 'Sentinel'
    group = SentinelGroup
    power = 3
    victory = 1
    desc = 'Fight: KO one of your Heroes.'
    def on_fight(self, player):
        player.ko_from(player.hand, player.played)

class SpiderFoes(VillainGroup):
    name = 'Spider Foes'
    def fill(self):
        self.add(Venom, 2)
        self.add(Lizard, 2)
        self.add(GreenGoblin, 2)
        self.add(DoctorOctopus, 2)

class DoctorOctopus(Villain):
    power = 4
    group = SpiderFoes
    name = 'Doctor Octopus'
    desc = 'When you draw at the end of this turn, draw 8 instead of 6'
    victory = 2
    def on_fight(self, player):
        player.draw_target = 8

class GreenGoblin(Villain):
    power = 6
    group = SpiderFoes
    name = 'Green Goblin'
    desc = 'Ambush: Green Goblin captures a Bystander'
    victory = 4
    def on_ambush(self):
        card = self.game.capture_bystander()
        assert card is self

class Lizard(Villain):
    power = 3
    group = SpiderFoes
    name = 'The Lizard'
    desc = ('If you fight The Lizard in the Sewers,'
            ' each other player gains a Wound.')
    victory = 2
    def on_pre_fight(self, player):
        if self is self.game.city[4]:
            self.game.event('The Lizard causes Wounds.')
            for p in self.game.players:
                if p is not player:
                    p.gain_wound()

class Venom(Villain):
    power = 5
    group = SpiderFoes
    name = 'Venom'
    desc = ("You can't defeat Venom unless you have <Cov>. "
            "Escape: each player gains a Wound.")
    victory = 3
    def on_escape(self):
        for p in self.game.players:
            p.gain_wound()
    def can_fight(self, player):
        return player.count_played(tag=tags.Covert) > 0


