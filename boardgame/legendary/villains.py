import boardgame as bg

from .core import *
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
                       ]
        self.game.choice(actions, allow_do_nothing=True)

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

class Sentinel(Henchman):
    name = 'Sentinel'
    power = 3
    victory = 1
    desc = 'Fight: KO one of your Heroes.'
    def on_fight(self, player):
        player.ko_hero_from(player.hand, player.played)

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
        for p in self.game.players:
            actions = []
            for h in heroes:
                if h in self.game.hq:
                    actions.append(action.GainFrom(h, self.game.hq, player=p))
            if len(actions) > 0:
                self.game.choice(actions)

class SkrullQueen(Villain):
    power = 0
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
        if self.stolen_hero is not None:
            self.power = self.stolen_hero.cost
            self.game.event('Skrull Queen Veranke captures %s' %
                            self.stolen_hero)
    def on_fight(self, player):
        if self.stolen_hero is not None:
            self.game.event('Gained %s' % self.stolen_hero)
            player.discard.append(self.stolen_hero)
            self.stolen_hero = None

class SkrullShapeshifter(Villain):
    power = 0
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
                return
        self.stolen_hero = self.game.hq[index]
        self.game.hq[index] = None
        self.game.fill_hq()
        self.power = self.stolen_hero.cost
        self.game.event('Skrull Shapeshifters capture %s' % self.stolen_hero)
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
            if len(p.hand + p.played) > 0:
                p.ko_hero_from(p.hand, p.played)

class HandNinjas(Henchman):
    name = 'Hand Ninjas'
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
            player.ko_hero_from(player.hand, player.played)
            player.ko_hero_from(player.hand, player.played)

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
            if p.reveal_tag(tags.Tech) is None:
                self.game.event('Ultron wounds Player %d' % (i + 1))
                p.gain_wound()

class DoombotLegion(Henchman):
    name = 'Doombot Legion'
    power = 3
    victory = 1
    desc = ('Fight: Reveal the top 2 cards of your deck. '
           'KO one, return the other')
    def on_fight(self, player):
        index = len(player.hand)
        player.draw(2)
        cards = player.hand[index:]
        if len(cards) > 0:
            player.hand = player.hand[:index]
            actions = []
            for act in [action.KOFrom, action.ReturnFrom]:
                for card in cards:
                    actions.append(act(card, cards))
            repeat = len(cards) - 1
            self.game.choice(actions, repeat=repeat, allow_same_type=False)


class SavageLandMutates(Henchman):
    name = 'Savage Land Mutates'
    power = 3
    victory = 1
    desc = ('Fight: When you draw a next hand at the end of your turn, '
            'draw an extra card.')
    def on_fight(self, player):
        player.draw_hand_extra += 1


class EnemiesOfAsgard(VillainGroup):
    name = 'Enemies of Asgard'
    def fill(self):
        self.add(Destroyer, 1)
        self.add(Ymir, 2)
        self.add(FrostGiant, 3)
        self.add(Enchantress, 2)

class Destroyer(Villain):
    name = 'Destroyer'
    power = 7
    victory = 5
    desc = ('Fight: KO all your <Shd> Heros. '
            'Escape: Each player KOs 2 Heros.')
    def on_fight(self, player):
        for c in player.hand[:]:
            if tags.Shield in c.tags:
                player.hand.remove(c)
                self.game.ko.append(c)
                self.game.event('Destroyer KOs %s' % c)
        for c in player.played[:]:
            if tags.Shield in c.tags:
                player.played.remove(c)
                self.game.ko.append(c)
                self.game.event('Destroyer KOs %s' % c)
    def on_escape(self):
        for p in self.game.players:
            p.ko_hero_from(p.hand, p.played)
            p.ko_hero_from(p.hand, p.played)

class Ymir(Villain):
    name = 'Ymir, Frost Giant King'
    power = 6
    victory = 4
    desc = ('Ambush: Each player reveals <Rng> or gains a Wound.'
            'Fight: Choose a player to KO all Wounds from hand and discard.')
    def on_anbush(self):
        for p in self.game.players:
            if p.reveal_tag(tags.Ranged) is None:
                self.game.event('Ymir wounds %s' % p.name)
                p.gain_wound()

    def on_fight(self, player):
        actions = []
        for p in self.game.players:
            actions.append(bg.CustomAction(
                '%s KOs all Wounds' % p.name,
                func=self.on_ko_wounds,
                kwargs=dict(player=p)))
        self.game.choice(actions)
    def on_ko_wounds(self, player):
        for c in player.hand[:]:
            if isinstance(c, Wound):
                self.game.ko.append(c)
                player.hand.remove(c)
        for c in player.discard[:]:
            if isinstance(c, Wound):
                self.game.ko.append(c)
                player.discard.remove(c)

class Enchantress(Villain):
    name = 'Enchantress'
    power = 6
    victory = 4
    desc = 'Fight: Draw 3 cards.'
    def on_fight(self, player):
        player.draw(3)

class FrostGiant(Villain):
    name = 'Frost Giant'
    power = 4
    victory = 2
    desc = ('Fight: Each player reveals <Rng> or gains a Wound.'
            ' Escape: same effect.')
    def on_fight(self, player):
        for p in self.game.players:
            if p.reveal_tag(tags.Ranged) is None:
                self.game.event('Frost Giant wounds %s' % p.name)
                p.gain_wound()
    def on_escape(self):
        self.on_fight(None)

class Brotherhood(VillainGroup):
    name = 'Brotherhood'
    def fill(self):
        self.add(Juggernaut, 2)
        self.add(Sabretooth, 2)
        self.add(Mystique, 2)
        self.add(Blob, 2)

class Juggernaut(Villain):
    name = 'Juggernaut'
    power = 6
    victory = 4
    desc = ('Ambush: Each player KOs 2 Heroes from their discard pile.'
            ' Escape: Each player KOs 2 Heroes from their hand.')
    def on_ambush(self):
        self.game.event('Juggernaut ambushes!')
        for p in self.game.players:
            p.ko_hero_from(p.discard)
            p.ko_hero_from(p.discard)
    def on_escape(self):
        for p in self.game.players:
            p.ko_hero_from(p.hand)
            p.ko_hero_from(p.hand)

class Sabretooth(Villain):
    name = 'Sabretooth'
    power = 5
    victory = 3
    desc = ('Fight: Each player reveals <XMn> or gains a Wound.'
            ' Escape: Same effect.')
    def on_fight(self, player):
        for p in self.game.players:
            if p.reveal_tag(tags.XMen) is None:
                self.game.event('Sabretooth wounds %s' % p.name)
                p.gain_wound()
    def on_escape(self):
        self.on_fight(None)

class Mystique(Villain):
    name = 'Mystique'
    power = 5
    victory = 3
    desc = ('Escape: Mystique becomes a Scheme Twist that takes effect'
            ' immediately.')
    def on_escape(self):
        self.game.event('Mystique causes a Scheme Twist')
        self.game.scheme_twist()

class Blob(Villain):
    name = 'Blob'
    power = 4
    victory = 2
    desc = "You can't defeat Blob unless you have <XMn>"
    def can_fight(self, player):
        return player.count_played(tag=tags.XMen) > 0

class EmissariesOfEvil(VillainGroup):
    name = 'Emissaries of Evil'
    def fill(self):
        self.add(Electro, 2)
        self.add(Rhino, 2)
        self.add(Gladiator, 2)
        self.add(Egghead, 2)

class Electro(Villain):
    name = 'Electro'
    power = 6
    victory = 4
    desc = ("Ambush: If top Villain card is a Scheme Twist, play it.")
    def on_ambush(self):
        if len(self.game.villain) == 0:
            return
        card = self.game.villain[0]
        self.game.event('Electro reveals %s' % card.text())
        if isinstance(card, SchemeTwist):
            self.game.play_villain()

class Rhino(Villain):
    name = 'Rhino'
    power = 5
    victory = 3
    desc = ("Ambush: If top Villain card is Master Strike, each "
            "player gains Wound. Escape: Each player gains Wound.")
    def on_ambush(self):
        if len(self.game.villain) == 0:
            return
        card = self.game.villain[0]
        self.game.event('Rhino reveals %s' % card.text())
        if isinstance(card, MasterStrike):
            for p in self.game.players:
                self.game.event('Rhino wounds %s' % p.name)
                p.gain_wound()
    def on_escape(self):
        for p in self.game.players:
            self.game.event('Rhino wounds %s' % p.name)
            p.gain_wound()

class Gladiator(Villain):
    name = 'Gladiator'
    power = 5
    victory = 3
    desc = ("Ambush: If top Villain card is a Bystander, "
            "Gladiator captures it.")
    def on_ambush(self):
        if len(self.game.villain) == 0:
            return
        card = self.game.villain[0]
        self.game.event('Gladiator reveals %s' % card.text())
        if isinstance(card, Bystander):
            self.game.play_villain()

class Egghead(Villain):
    name = 'Egghead'
    power = 4
    victory = 2
    desc = ("Ambush: If top Villain card is a Villain, play it.")
    def on_ambush(self):
        if len(self.game.villain) == 0:
            return
        card = self.game.villain[0]
        self.game.event('Egghead reveals %s' % card.text())
        if isinstance(card, Villain):
            self.game.play_villain()
