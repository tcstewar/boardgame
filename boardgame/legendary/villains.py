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
                p.gain_wound(wounder=self)
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
            for p in player.other_players():
                p.gain_wound(wounder=self)

class Venom(Villain):
    power = 5
    group = SpiderFoes
    name = 'Venom'
    desc = ("You can't defeat Venom unless you have <Cov>. "
            "Escape: each player gains a Wound.")
    victory = 3
    def on_escape(self):
        for p in self.game.players:
            p.gain_wound(wounder=self)
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
                p.gain_wound(wounder=self)

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
                p.gain_wound(wounder=self)

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
                p.gain_wound(wounder=self)
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
                p.gain_wound(wounder=self)
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
                p.gain_wound(wounder=self)
    def on_escape(self):
        for p in self.game.players:
            p.gain_wound(wounder=self)

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

class Radiation(VillainGroup):
    name = 'Radiation'
    def fill(self):
        self.add(Maestro, 2)
        self.add(Abomination, 2)
        self.add(Zzzax, 2)
        self.add(TheLeader, 2)

class Maestro(Villain):
    name = 'Maestro'
    power = 6
    victory = 4
    desc = "Fight: For each of your <Str> Heroes, KO one of your Heroes."
    def on_fight(self, player):
        for i in range(player.count_tagged(tags.Strength)):
            player.ko_hero_from(player.hand, player.played)

class Abomination(Villain):
    name = 'Abomination'
    power = 5
    victory = 3
    desc = "Fight: If you fight on Streets or Bridge, rescue 3 Bystanders."
    def on_pre_fight(self, player):
        if self is self.game.city[0] or self is self.game.city[1]:
            player.rescue_bystander()
            player.rescue_bystander()
            player.rescue_bystander()

class Zzzax(Villain):
    name = 'Zzzax'
    power = 5
    victory = 3
    desc = ("Fight: Each player reveals <Str> or gains a Wound. "
            "Escape: same effect.")
    def on_fight(self, player):
        for p in self.game.players:
            if p.reveal_tag(tags.Strength) is None:
                p.gain_wound(wounder=self)
    def on_escape(self):
        self.on_fight(None)

class TheLeader(Villain):
    name = 'The Leader'
    power = 4
    victory = 2
    desc = "Ambush: Play the top Villain card."
    def on_ambush(self):
        self.game.play_villain()

class FourHorsemen(VillainGroup):
    name = 'Four Horsemen'
    def fill(self):
        self.add(Death, 2)
        self.add(War, 2)
        self.add(Pestilence, 2)
        self.add(Famine, 2)

class Death(Villain):
    name = 'Death'
    power = 7
    victory = 5
    desc = ("Fight: Each other player KOs a hero of cost 1 or more. "
            "Escape: Each player does the same.")
    def on_fight(self, player):
        for p in player.other_players():
            self.punish(p)
    def on_escape(self):
        for p in self.game.players:
            self.punish(p)
    def punish(self, p):
        actions = []
        for c in p.hand:
            if c.cost >= 1:
                actions.append(action.KOFrom(c, p.hand))
        if len(actions) > 0:
            self.game.choice(actions)

class War(Villain):
    name = 'War'
    power = 6
    victory = 4
    desc = ("Fight: Each other player reveals <Ins> or gains Wound. "
            "Escape: Each player does the same.")
    def on_fight(self, player):
        for p in player.other_players():
            self.punish(p)
    def on_escape(self):
        for p in self.game.players:
            self.punish(p)
    def punish(self, p):
        actions = []
        if p.reveal_tag(tags.Instinct) is None:
            p.gain_wound(wounder=self)

class Pestilence(Villain):
    name = 'Pestilence'
    power = 5
    victory = 3
    desc = ("Fight: Each other player reveals top 3 cards, discards C>0, puts "
            "rest back in any order. Escape: Each player does the same.")
    def on_fight(self, player):
        for p in player.other_players():
            self.punish(p)
    def on_escape(self):
        for p in self.game.players:
            self.punish(p)
    def punish(self, p):
        cards = p.reveal(3)
        for c in cards:
            if c.cost > 0:
                p.discard_from(c, cards)
        while len(cards) > 0:
            actions = [action.ReturnFrom(c, cards) for c in cards]
            self.game.choice(actions)

class Famine(Villain):
    name = 'Famine'
    power = 4
    victory = 2
    desc = ("Fight: Each other player reveals <Ins> or discards a card. "
            "Escape: Each player does the same.")
    def on_fight(self, player):
        for p in player.other_players():
            self.punish(p)
    def on_escape(self):
        for p in self.game.players:
            self.punish(p)
    def punish(self, p):
        actions = []
        if p.reveal_tag(tags.Instinct) == 0:
            actions = [action.DiscardFrom(c, p.hand) for c in p.hand]
            self.game.choice(actions)

class MaggiaGoons(Henchman):
    name = 'Maggia Goons'
    power = 4
    victory = 1
    bribe = True
    desc = 'Bribe. Fight: KO one of your Heroes.'
    def on_fight(self, player):
        player.ko_hero_from(player.hand, player.played)

class StreetsOfNewYork(VillainGroup):
    name = 'Streets of New York'
    def fill(self):
        self.add(Jigsaw, 2)
        self.add(Tombstone, 2)
        self.add(Bullseye, 2)
        self.add(Hammerhead, 2)

class Jigsaw(Villain):
    name = 'Jigsaw'
    power = 11
    victory = 5
    bribe = True
    desc = ("Bribe. Ambush: Each player discards 3 cards, then draws 2 cards.")
    def on_ambush(self):
        for p in self.game.players:
            for i in range(3):
                if len(p.hand) > 0:
                    actions = [action.DiscardFrom(c, p.hand) for c in p.hand]
                    self.game.choice(actions)
            p.draw(2)

class Tombstone(Villain):
    name = 'Tombstone'
    power = 8
    victory = 4
    bribe = True
    desc = ("Bribe. Escape: Each player reveals <Str> or gains a Wound.")
    def on_escape(self):
        for p in self.game.players:
            if p.reveal_tag(tags.Strength) is None:
                p.gain_wound(wounder=self)

class Bullseye(Villain):
    name = 'Bullseye'
    power = 6
    victory = 4
    desc = ("Fight: KO one Hero with S icon and one Hero with P icon.")
    def on_fight(self, player):
        actions = []
        for c in player.hand:
            if c.star > 0 or c.extra_star:
                actions.append(action.KOFrom(c, player.hand))
        for c in player.played:
            if c.star > 0 or c.extra_star:
                actions.append(action.KOFrom(c, player.played))
        if len(actions) > 0:
            self.game.choice(actions)
        actions = []
        for c in player.hand:
            if c.power > 0 or c.extra_power:
                actions.append(action.KOFrom(c, player.hand))
        for c in player.played:
            if c.power > 0 or c.extra_power:
                actions.append(action.KOFrom(c, player.played))
        if len(actions) > 0:
            self.game.choice(actions)

class Hammerhead(Villain):
    name = 'Hammerhead'
    power = 5
    victory = 2
    bribe = True
    desc = ("Bribe. Fight: KO one Hero with S icon.")
    def on_fight(self, player):
        actions = []
        for c in player.hand:
            if c.star > 0 or c.extra_star:
                actions.append(action.KOFrom(c, player.hand))
        for c in player.played:
            if c.star > 0 or c.extra_star:
                actions.append(action.KOFrom(c, player.played))
        if len(actions) > 0:
            self.game.choice(actions)
