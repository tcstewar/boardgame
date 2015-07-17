import boardgame as bg

from .core import Villain, VillainGroup, HenchmenGroup, Hero
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
        self.game.capture_bystander()

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


class Skrulls(VillainGroup):
    name = 'Skrulls'
    def fill(self):
        self.add(SuperSkrull, 3)
        self.add(SkrullShapeshifter, 3)
        self.add(SkrullQueen, 1)
        self.add(PowerSkrull, 1)

class PowerSkrull(Villain):
    power = 8
    group = Skrulls
    name = 'Paibok the Power Skrull'
    desc = "Fight: Each player gains a Hero from the HQ."
    victory = 3
    def on_fight(self, player):
        heroes = [h for h in self.game.hq if isinstance(h, Hero)]
        actions = []
        for p in self.game.players:
            for h in heroes:
                actions.append(action.GainFrom(h, self.game.hq, player=p))
            self.game.choice(actions)

class SkrullQueen(Villain):
    power = None
    group = Skrulls
    name = 'Skrull Queen Veranke'
    desc = ("Ambush: Capture the highest-cost Hero from HQ. P is Hero's C. "
            "Fight: Gain that Hero.")
    victory = 4
    def on_ambush(self):
        costs = [h.cost if h is not None else -1 for h in self.game.hq]
        index = costs.index(max(costs))
        self.stolen_hero = self.game.hq[index]
        self.game.hq[index] = None
        self.game.fill_hq()
        self.power = self.stolen_hero.cost
    def on_fight(self, player):
        self.game.event('Gained %s' % self.stolen_hero)
        player.discard.append(self.stolen_hero)

class SkrullShapeshifter(Villain):
    power = None
    group = Skrulls
    name = 'Skrull Shapeshifters'
    desc = ("Ambush: Capture the right-most Hero from HQ. P is Hero's C. "
            "Fight: Gain that Hero.")
    victory = 2
    def on_ambush(self):
        index = 4
        while not isinstance(self.game.hq[index], Hero):
            index -= 1
            if index < 0:
                self.stolen_hero = None
                self.power = 0
                return
        self.stolen_hero = self.game.hq[index]
        self.game.hq[index] = None
        self.game.fill_hq()
        self.power = self.stolen_hero.cost
    def on_fight(self, player):
        if self.stolen_hero is not None:
            self.game.event('Gained %s' % self.stolen_hero)
            player.discard.append(self.stolen_hero)

class SuperSkrull(Villain):
    name = 'Super-Skrull'
    group = Skrulls
    power = 4
    victory = 2
    desc = 'Fight: Each player KOs one of their Heroes.'
    def on_fight(self, player):
        for p in self.game.players:
            p.ko_from(p.hand, p.played)

class HandNinjaGroup(HenchmenGroup):
    name = 'Hand Ninjas'
    def fill(self):
        self.add(HandNinjas, 10)

class HandNinjas(Villain):
    name = 'Hand Ninjas'
    group = HandNinjaGroup
    power = 3
    victory = 1
    desc = 'Fight: You get S+1.'
    def on_fight(self, player):
        player.available_star += 1

class MastersOfEvil(VillainGroup):
    name = 'Masters of Evil'
    def fill(self):
        self.add(Ultron, 2)
        self.add(Whirlwind, 2)
        self.add(Melter, 2)
        self.add(BaronZemo, 2)

class BaronZemo(Villain):
    name = 'Baron Zemo'
    group = MastersOfEvil
    power = 6
    victory = 4
    desc = 'Fight: For each <Avg>, rescue a Bystander.'
    def on_fight(self, player):
        for i in range(player.count_played(tag=tags.Avenger)):
            player.rescue_bystander()

class Melter(Villain):
    name = 'Melter'
    group = MastersOfEvil
    power = 5
    victory = 3
    desc = ('Fight: Each player reveals top card of deck. '
            'You choose to KO or return it.')
    def on_fight(self, player):
        for p in self.game.players:
            cards = p.reveal(1)
            if len(cards) > 0:
                actions = [
                    action.KOFrom(cards[0], cards),
                    action.ReturnFrom(cards[0], cards)
                    ]
                self.game.choice(actions)

class Whirlwind(Villain):
    name = 'Whirlwind'
    group = MastersOfEvil
    power = 4
    victory = 2
    desc = 'Fight: If you fight on the Rooftops or Bridge, KO two heros.'
    def on_pre_fight(self, player):
        if self is self.game.city[0] or self is self.game.city[2]:
            player.ko_from(player.hand, player.played)
            player.ko_from(player.hand, player.played)

class Ultron(Villain):
    name = 'Ultron'
    group = MastersOfEvil
    power = 6
    victory = 2
    desc = ('V+1 for each <Tec> you own. '
            'Escape: Each player reveals <Tec> or gains a Wound.')
    def extra_victory(self, player):
        total = 0
        for c in player.hand + player.discard + player.played + player.stack:
            if tags.Tech in c.tags:
                total += 1
        return total
    def on_escape(self):
        for i, p in enumerate(self.game.players):
            for c in p.hand + p.played:
                if tags.Tech in c.tags:
                    break
            else:
                self.game.event('Ultron wounds Player %d' % (i + 1))
                p.gain_wound()

