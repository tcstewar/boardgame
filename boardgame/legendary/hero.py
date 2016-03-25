import copy

import boardgame as bg

import action
from .core import *
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
    name = 'Iron Man'
    def fill(self):
        self.add(IronManRepulsor, 5)
        self.add(IronManQuantum, 1)
        self.add(IronManEndless, 5)
        self.add(IronManArc, 3)

class IronManArc(Hero):
    name = 'Iron Man: Arc Reactor'
    cost = 5
    tags = [Avenger, Tech]
    power = 3
    extra_power = True
    desc = 'P+1 per other <Tec> played'
    def on_play(self, player):
        player.available_power += player.count_played(tag=Tech, ignore=self)

class IronManEndless(Hero):
    name = 'Iron Man: Endless Intervention'
    cost = 3
    tags = [Avenger, Tech]
    desc = 'Draw a card. <Tec>: Draw another card'
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(1)

class IronManQuantum(Hero):
    name = 'Iron Man: Quantum Breakthrough'
    cost = 7
    tags = [Avenger, Tech]
    desc = 'Draw two cards. <Tec>: Draw two more cards'
    def on_play(self, player):
        player.draw(2)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(2)

class IronManRepulsor(Hero):
    name = 'Iron Man: Repulsor Rays'
    cost = 3
    tags = [Avenger, Ranged]
    power = 2
    extra_power = True
    desc = '<Rng>: P+1'
    def on_play(self, player):
        if player.count_played(tag=Ranged, ignore=self) > 0:
            player.available_power += 1

class SpiderMan(HeroGroup):
    name = 'Spider-Man'
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
            for i in range(len(actions)):
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

class Wolverine2(HeroGroup):
    name = 'Wolverine (X-Force)'
    def fill(self):
        self.add(WolverineAmbush, 5)
        self.add(WolverineAnimal, 5)
        self.add(WolverineReckless, 1)
        self.add(WolverineNoMercy, 3)

class WolverineAmbush(Hero):
    name = 'Wolverine: Sudden Ambush'
    cost = 4
    power = 2
    tags = [XForce, Covert]
    desc = 'If you drew any extra cards this turn, P+2'
    extra_power = True
    def on_play(self, player):
        if player.extra_draw_count > 0:
            player.available_power += 2

class WolverineAnimal(Hero):
    name = 'Wolverine: Animal Instincts'
    cost = 2
    tags = [XForce, Instinct]
    desc = 'Draw a card. <Ins>: P+2'
    extra_power = True
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Instinct, ignore=self) > 0:
            player.available_power += 2

class WolverineReckless(Hero):
    name = 'Wolverine: Reckless Abandon'
    cost = 7
    tags = [XForce, Covert]
    power = 3
    desc = 'Count how many extra cards you have drawn. Draw that many cards.'
    def on_play(self, player):
        count = player.extra_draw_count
        player.draw(count)

class WolverineNoMercy(Hero):
    name = 'Wolverine: No Mercy'
    cost = 4
    tags = [XForce, Strength]
    desc = 'Draw a card. You may KO a card from your hand or discard pile.'
    def on_play(self, player):
        player.draw(1)
        actions = []
        for c in player.hand:
            actions.append(action.KOFrom(c, player.hand))
        for c in player.discard:
            actions.append(action.KOFrom(c, player.discard))
        self.game.choice(actions, allow_do_nothing=True)


class Hawkeye(HeroGroup):
    name = 'Hawkeye'
    def fill(self):
        self.add(HawkeyeCoveringFire, 3)
        self.add(HawkeyeTrick, 1)
        self.add(HawkeyeQuick, 5)
        self.add(HawkeyeTeam, 5)

class HawkeyeCoveringFire(Hero):
    name = 'Hawkeye: Covering Fire'
    cost = 5
    power = 3
    tags = [Avenger, Tech]
    desc = ('<Tec>: Choose one: Each other player draws a card or '
            'each other player discards a card.')
    def on_play(self, player):
        if player.count_played(tag=Tech, ignore=self):
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

class HawkeyeTeam(Hero):
    name = 'Hawkeye: Team Player'
    cost = 4
    power = 2
    extra_power = True
    tags = [Avenger, Tech]
    desc = '<Avg>: P+1'
    def on_play(self, player):
        if player.count_played(tag=Avenger, ignore=self):
            player.available_power +=1

class HawkeyeQuick(Hero):
    name = 'Hawkeye: Quick Draw'
    cost = 3
    power = 1
    tags = [Avenger, Instinct]
    desc = 'Draw a card'
    def on_play(self, player):
        player.draw(1)


class HawkeyeTrick(Hero):
    name = 'Hawkeye: Impossible Trick Shot'
    cost = 7
    power = 5
    tags = [Avenger, Tech]
    desc = ('Whenever you fight a Villain or Mastermind this turn, '
            'rescue 3 Bystanders')
    def on_play(self, player):
        def on_fight(enemy):
            player.rescue_bystander()
            player.rescue_bystander()
            player.rescue_bystander()
        player.handlers['on_fight'].append(on_fight)


class Cyclops(HeroGroup):
    name = 'Cyclops'
    def fill(self):
        self.add(CyclopsDetermination, 5)
        self.add(CyclopsOptic, 5)
        self.add(CyclopsEnergy, 3)
        self.add(CyclopsUnited, 1)

class CyclopsDetermination(Hero):
    name = 'Cyclops: Determination'
    cost = 2
    star = 3
    tags = [XMen, Strength]
    desc = 'To play this card, you must discard a card.'
    def valid_play(self, player):
        for h in player.hand:
            if h is not self:
                return True
        return False
    def on_play(self, player):
        actions = []
        for h in player.hand:
            if h is not self:
                actions.append(action.DiscardFrom(h, player.hand))
        self.game.choice(actions)

class CyclopsOptic(Hero):
    name = 'Cyclops: Optic Blast'
    cost = 3
    power = 3
    tags = [XMen, Ranged]
    desc = 'To play this card, you must discard a card.'
    def valid_play(self, player):
        for h in player.hand:
            if h is not self:
                return True
        return False
    def on_play(self, player):
        actions = []
        for h in player.hand:
            if h is not self:
                actions.append(action.DiscardFrom(h, player.hand))
        self.game.choice(actions)

class CyclopsEnergy(Hero):
    name = 'Cyclops: Unending Energy'
    cost = 6
    power = 4
    tags = [XMen, Ranged]
    return_from_discard = True
    desc = 'If you discard this card, you may return it to your hand'

class CyclopsUnited(Hero):
    name = 'Cyclops: X-Men United'
    cost = 8
    power = 6
    extra_power = True
    tags = [XMen, Ranged]
    desc = '<XMn> P+2 for each other <XMn> played this turn'
    def on_play(self, player):
        count = player.count_played(tag=XMen, ignore=self)
        player.available_power += 2 * count

class BlackWidow(HeroGroup):
    name = 'Black Widow'
    def fill(self):
        self.add(BlackWidowCovert, 3)
        self.add(BlackWidowRescue, 5)
        self.add(BlackWidowMission, 5)
        self.add(BlackWidowSniper, 1)

class BlackWidowCovert(Hero):
    name = 'Black Widow: Covert Operation'
    cost = 4
    power = 0
    extra_power = True
    tags = [Avenger, Covert]
    desc = 'P+1 for each Bystander in victory pile'
    def on_play(self, player):
        for c in player.victory_pile:
            if isinstance(c, Bystander):
                player.available_power += 1

class BlackWidowRescue(Hero):
    name = 'Black Widow: Dangerous Rescue'
    cost = 3
    power = 2
    tags = [Avenger, Covert]
    desc = ('<Cov> You may KO a card from hand or discard. '
            'If you do, rescue a Bystander')
    def on_play(self, player):
        if player.count_played(tag=Covert, ignore=self) > 0:
            actions = []
            for c in player.hand:
                actions.append(action.KOFrom(c, player.hand))
            for c in player.discard:
                actions.append(action.KOFrom(c, player.discard))
            choice = self.game.choice(actions, allow_do_nothing=True)
            if choice is not None:
                player.rescue_bystander()

class BlackWidowMission(Hero):
    name = 'Black Widow: Mission Accomplished'
    cost = 2
    tags = [Avenger, Tech]
    desc = 'Draw a card.  <Tec>: Rescue a Bystander'
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.rescue_bystander()

class BlackWidowSniper(Hero):
    name = 'Black Widow: Silent Sniper'
    cost = 7
    power = 4
    tags = [Avenger, Covert]
    desc = 'Defeat a Villain or Mastermind that has a Bystander'
    def on_play(self, player):
        actions = []
        for v in [self.game.mastermind] + self.game.city:
            if v is not None:
                for c in v.captured:
                    if isinstance(c, Bystander):
                        actions.append(bg.CustomAction(
                            'Defeat %s' % v.text(),
                            func=player.defeat,
                            kwargs=dict(villain=v)))
        if len(actions) > 0:
            self.game.choice(actions)

class Hulk(HeroGroup):
    name = 'Hulk'
    def fill(self):
        self.add(HulkUnstoppable, 5)
        self.add(HulkSmash, 1)
        self.add(HulkAnger, 5)
        self.add(HulkRampage, 3)

class HulkRampage(Hero):
    name = 'Hulk: Crazed Rampage'
    cost = 5
    power = 4
    tags = [Avenger, Strength]
    desc = 'Each player gains a Wound'
    def on_play(self, player):
        for p in self.game.players:
            self.game.event('Hulk wounds %s' % p.name)
            p.gain_wound()

class HulkAnger(Hero):
    name = 'Hulk: Growing Anger'
    cost = 3
    power = 2
    extra_power = True
    tags = [Avenger, Strength]
    desc = '<Str> P+1'
    def on_play(self, player):
        if player.count_played(tag=Strength, ignore=self) > 0:
            player.available_power += 1

class HulkSmash(Hero):
    name = 'Hulk: Smash'
    cost = 8
    power = 5
    extra_power = True
    tags = [Avenger, Strength]
    desc = '<Str> P+5'
    def on_play(self, player):
        if player.count_played(tag=Strength, ignore=self) > 0:
            player.available_power += 5

class HulkUnstoppable(Hero):
    name = 'Hulk: Unstoppable'
    cost = 4
    power = 2
    tags = [Avenger, Instinct]
    desc = 'You may KO a Wound from your hand or discard. If you do, P+2.'
    def on_play(self, player):
        actions = []
        for c in player.hand:
            if isinstance(c, Wound):
                actions.append(action.KOFrom(c, player.hand))
                break
        for c in player.discard:
            if isinstance(c, Wound):
                actions.append(action.KOFrom(c, player.discard))
                break
        choice = self.game.choice(actions, allow_do_nothing=True)
        if choice is not None:
            player.available_power += 2

class Wolverine(HeroGroup):
    name = 'Wolverine (X-Men)'
    def fill(self):
        self.add(WolverineSenses, 5)
        self.add(WolverineHealing, 5)
        self.add(WolverineSlashing, 3)
        self.add(WolverineRage, 1)

class WolverineRage(Hero):
    name = 'Wolverine: Berserker Rage'
    cost = 8
    power = 2
    tags = [XMen, Instinct]
    desc = 'Draw 3 cards.  <Ins> You get P+1 for each extra card drawn'
    extra_power = True
    def on_play(self, player):
        player.draw(3)
        player.available_power += player.extra_draw_count

class WolverineSlashing(Hero):
    name = 'Wolverine: Frenzied Slashing'
    cost = 5
    power = 2
    tags = [XMen, Instinct]
    desc = '<Ins> Draw 2 cards'
    def on_play(self, player):
        if player.count_played(tag=Instinct, ignore=self):
            player.draw(2)

class WolverineHealing(Hero):
    name = 'Wolverine: Healing Factor'
    cost = 3
    power = 2
    tags = [XMen, Instinct]
    desc = 'You may KO a Wound from hand or discard. If you do, draw a card.'
    def on_play(self, player):
        actions = []
        for c in player.hand:
            if isinstance(c, Wound):
                actions.append(action.KOFrom(c, player.hand))
        for c in player.discard:
            if isinstance(c, Wound):
                actions.append(action.KOFrom(c, player.discard))
        if len(actions) > 0:
            choice = self.game.choice(actions, allow_do_nothing=True)
            if choice is not None:
                player.draw(1)

class WolverineSenses(Hero):
    name = 'Wolverine: Keen Senses'
    cost = 2
    power = 1
    tags = [XMen, Instinct]
    desc = '<Ins> Draw a card'
    def on_play(self, player):
        if player.count_played(tag=Instinct, ignore=self) > 0:
            player.draw(1)

class CaptainAmerica(HeroGroup):
    name = 'Captain America'
    def fill(self):
        self.add(CapTeamwork, 5)
        self.add(CapBlock, 3)
        self.add(CapDay, 1)
        self.add(CapAssemble, 5)

class CapAssemble(Hero):
    name = 'Captain America: Avengers Assemble'
    cost = 3
    star = 0
    extra_star = True
    tags = [Avenger, Instinct]
    desc = 'S+1 for each color of Hero you have'
    def on_play(self, player):
        cards = player.hand + player.played
        for tag in [Tech, Ranged, Strength, Instinct, Covert, Shield]:
            for c in cards:
                if tag in c.tags:
                    player.available_star +=1
                    break

class CapDay(Hero):
    name = 'Captain America: A Day Unlike Any Other'
    cost = 7
    power = 3
    extra_power = True
    tags = [Avenger, Covert]
    desc = '<Avg> P+3 for every other Avg played'
    def on_play(self, player):
        count = player.count_played(tag=Avenger, ignore=self)
        player.available_power += count * 3

class CapBlock(Hero):
    name = 'Captain America: Diving Block'
    cost = 6
    power = 4
    tags = [Avenger, Tech]
    desc = 'If you would gain a Wound, reveal this and draw a card instead'
    def allow_wound(self, player):
        choice = self.game.choice([
            bg.CustomAction('Have Captain America block the Wound')
            ], allow_do_nothing=True)
        if choice is not None:
            player.draw(1)
            return False
        else:
            return True

class CapTeamwork(Hero):
    name = 'Captain America: Perfect Teamwork'
    cost = 4
    extra_power = True
    tags = [Avenger, Strength]
    desc = 'P+1 for each color of Hero you have'
    def on_play(self, player):
        cards = player.hand + player.played
        for tag in [Tech, Ranged, Strength, Instinct, Covert, Shield]:
            for c in cards:
                if tag in c.tags:
                    player.available_power +=1
                    break

class Thor(HeroGroup):
    name = 'Thor'
    def fill(self):
        self.add(ThorPower, 5)
        self.add(ThorOdinson, 5)
        self.add(ThorThunder, 1)
        self.add(ThorLightning, 3)

class ThorLightning(Hero):
    name = 'Thor: Call Lightning'
    cost = 6
    power = 3
    extra_power = True
    tags = [Avenger, Ranged]
    desc = '<Rng> P+3'
    def on_play(self, player):
        if player.count_played(tag=Ranged, ignore=self) > 0:
            player.available_power += 3

class ThorOdinson(Hero):
    name = 'Thor: Odinson'
    cost = 3
    star = 2
    extra_star = True
    tags = [Avenger, Strength]
    desc = '<Str> S+2'
    def on_play(self, player):
        if player.count_played(tag=Strength, ignore=self) > 0:
            player.available_star += 2

class ThorPower(Hero):
    name = 'Thor: Surge of Power'
    cost = 4
    star = 2
    extra_star = True
    tags = [Avenger, Ranged]
    desc = 'If you made 8 or more S, P+3'
    def on_play(self, player):
        if player.available_star + player.used_star >= 8:
            player.available_power += 3

class ThorThunder(Hero):
    name = 'Thor: God of Thunder'
    cost = 8
    star = 5
    extra_power = True
    tags = [Avenger, Ranged]
    desc = 'You can use S as P this turn'
    def on_play(self, player):
        player.can_use_star_as_power = True

class Rogue(HeroGroup):
    name = 'Rogue'
    def fill(self):
        self.add(RogueBrawn, 5)
        self.add(RogueEnergy, 5)
        self.add(RogueSteal, 1)
        self.add(RogueCopy, 3)

class RogueBrawn(Hero):
    name = 'Rogue: Stolen Brawn'
    cost = 4
    power = 1
    extra_power = True
    tags = [XMen, Strength]
    desc = '<Str>: P+3'
    def on_play(self, player):
        if player.count_played(tag=Strength, ignore=self):
            player.available_power += 3

class RogueSteal(Hero):
    name = 'Rogue: Steal Abilities'
    cost = 8
    power = 4
    tags = [XMen, Strength]
    desc = ('Each player discards the top card of their deck. '
            'Play a copy of each card.')
    def on_play(self, player):
        for p in self.game.players:
            cards = p.draw(1, put_in_hand=False)
            if len(cards) > 0:
                card = cards[0]
                p.discard.append(card)

                self.game.event('Rogue steals: %s' % card.text())
                copied = card.copy()
                try:
                    player.play(copied)
                except bg.NoValidActionException:
                    self.game.event("Rogue's copy of %s skipped requirements")

class RogueCopy(Hero):
    name = 'Rogue: Copy Powers'
    cost = 5
    tags = [XMen, Covert]
    desc = ('Play this as a copy of another Hero you played this turn. '
            'This card <Cov> in addition')
    def valid_play(self, player):
        for c in player.played:
            if not hasattr(c, 'valid_play') or c.valid_play(player):
                return True
        return False

    def on_play(self, player):
        player.played.remove(self)
        actions = []
        for c in player.played:
            if not hasattr(c, 'valid_play') or c.valid_play(player):
                actions.append(bg.CustomAction(
                    'Copy %s' % c.text(),
                    func=self.on_copy,
                    kwargs=dict(player=player, card=c)))
        self.game.choice(actions)

    def on_copy(self, player, card):
        copied = card.copy()
        if Covert not in copied.tags:
            copied.tags = [Covert] + copied.tags
        copied.original = self
        player.play(copied)

class RogueEnergy(Hero):
    name = 'Rogue: Energy Drain'
    cost = 3
    star = 2
    extra_star = True
    tags = [XMen, Covert]
    desc = '<Cov>: You may KO a card from hand or discard. If you do, S+1.'
    def on_play(self, player):
        if player.count_played(tag=Covert, ignore=self):
            actions = []
            for c in player.hand:
                actions.append(action.KOFrom(c, player.hand))
            for c in player.discard:
                actions.append(action.KOFrom(c, player.discard))
            if len(actions) > 0:
                choice = self.game.choice(actions, allow_do_nothing=True)
                if choice is not None:
                    player.available_star += 1

class Deadpool(HeroGroup):
    name = 'Deadpool'
    def fill(self):
        self.add(DeadpoolUnkind, 1)
        self.add(DeadpoolDoOver, 3)
        self.add(DeadpoolOddball, 5)
        self.add(DeadpoolHoldThis, 5)

class DeadpoolUnkind(Hero):
    name = 'Deadpool: Random Acts of Unkindness'
    cost = 7
    power = 6
    tags = [Instinct]
    desc = ('You may gain Wound to your hand. '
           'Each player passes a card to their left.')
    def on_play(self, player):
        if len(self.game.wounds) > 0:
            actions = [bg.CustomAction(
                'Gain a Wound to your hand',
                func=self.on_gain_wound,
                kwargs=dict(player=player))]
            self.game.choice(actions, allow_do_nothing=True)

        if len(self.game.players) > 1:
            all_actions = []
            for i, p in enumerate(self.game.players):
                p2 = self.game.players[(i + 1) % len(self.game.players)]
                actions = []
                for c in p.hand:
                    actions.append(bg.CustomAction(
                        'Pass %s to %s' % (c, p2.name),
                        func=self.on_pass,
                        kwargs=dict(card=c, player=p, player2=p2)))
                all_actions.append(actions)
            for i, p in enumerate(self.game.players):
                if all_actions[i]:
                    self.game.choice(all_actions[i], player=p)

    def on_gain_wound(self, player):
        player.hand.append(self.game.wounds.pop(0))

    def on_pass(self, card, player, player2):
        self.game.event('%s gives %s to %s' % (player.name, card.name,
                                               player2.name))
        player.hand.remove(card)
        player2.hand.append(card)

class DeadpoolDoOver(Hero):
    name = 'Deadpool: Hey, can I get a Do Over?'
    cost = 3
    power = 2
    tags = [Instinct]
    desc = ('If this is the first Hero played, you may discard the rest of '
            'your hand and draw four cards.')
    def on_play(self, player):
        if len(player.played) == 1:
            actions = [bg.CustomAction(
                'Get a Do Over',
                func=self.on_do_over,
                kwargs=dict(player=player))]
            self.game.choice(actions, allow_do_nothing=True)
    def on_do_over(self, player):
        for c in player.hand[:]:
            player.discard_from(c, player.hand)
        player.draw(4)

class DeadpoolOddball(Hero):
    name = 'Deadpool: Oddball'
    cost = 5
    power = 2
    extra_power = True
    tags = [Covert]
    desc = ('P+1 for each other Hero played with odd C.')
    def on_play(self, player):
        for c in player.played:
            if c is not self and (c.cost % 2) == 1:
                player.available_power += 1

class DeadpoolHoldThis(Hero):
    name = 'Deadpool: Here, Hold This for a Second'
    cost = 3
    star = 2
    tags = [Tech]
    desc = ('A Villain of your choice captures a Bystander.')
    def on_play(self, player):
        if self.game.bystanders:
            actions = []
            for v in self.game.city:
                if v is not None:
                    actions.append(bg.CustomAction(
                        '%s captures Bystander' % v.name,
                        func=self.on_capture,
                        kwargs=dict(villain=v)))
            if actions:
                self.game.choice(actions)
    def on_capture(self, villain):
        villain.capture(self.game.bystanders.pop(0))

class EmmaFrost(HeroGroup):
    name = 'Emma Frost'
    def fill(self):
        self.add(EmmaFrostDiamond, 1)
        self.add(EmmaFrostPsychic, 3)
        self.add(EmmaFrostThoughts, 5)
        self.add(EmmaFrostMental, 5)

class EmmaFrostDiamond(Hero):
    name = 'Emma Frost: Diamond Form'
    cost = 7
    power = 5
    tags = [XMen, Strength]
    desc = ('Whenever you defeat a Villain or Mastermind this turn, S+3.')
    def on_play(self, player):
        def on_fight(enemy):
            player.available_star += 3
        player.handlers['on_fight'].append(on_fight)

class EmmaFrostPsychic(Hero):
    name = 'Emma Frost: Psychic Link'
    cost = 5
    power = 3
    tags = [XMen, Instinct]
    desc = 'Each player who reveals another <XMn> draws a card.'
    def on_play(self, player):
        for p in self.game.players:
            if p.reveal_tag(XMen, ignore=self) is not None:
                p.draw(1)

class EmmaFrostThoughts(Hero):
    name = 'Emma Frost: Shadowed Thoughts'
    cost = 4
    power = 2
    tags = [XMen, Covert]
    desc = ('You may play a Villain. If you do, P+3.')
    def on_play(self, player):
        if self.game.villain:
            actions = [bg.CustomAction(
                'Play Villain',
                func=self.on_play_villain,
                kwargs=dict(player=player))]
            self.game.choice(actions, allow_do_nothing=True)
    def on_play_villain(self, player):
        self.game.play_villain()
        player.available_power += 3

class EmmaFrostMental(Hero):
    name = 'Emma Frost: Mental Discipline'
    cost = 3
    star = 1
    tags = [XMen, Ranged]
    desc = ('Draw a card.')
    def on_play(self, player):
        player.draw(1)

class Gambit(HeroGroup):
    name = 'Gambit'
    def fill(self):
        self.add(GambitJackpot, 1)
        self.add(GambitCharm, 3)
        self.add(GambitCardShark, 5)
        self.add(GambitStackDeck, 5)

class GambitJackpot(Hero):
    name = 'Gambit: High Stakes Jackpot'
    cost = 7
    power = 4
    extra_power = True
    tags = [XMen, Instinct]
    desc = ("Reveal top card of deck. P+ that card's C.")
    def on_play(self, player):
        cards = player.reveal(1)
        if len(cards) > 0:
            card = cards[0]
            player.available_power += card.cost
            player.stack.insert(0, card)

class GambitCharm(Hero):
    name = 'Gambit: Hypnotic Charm'
    cost = 3
    star = 2
    tags = [XMen, Instinct]
    desc = ("Reveal top card of deck. Discard it or put it back."
            " <Ins>: do the same to each other player's deck.")
    def on_play(self, player):
        cards = player.reveal(1)
        if cards:
            self.game.choice([action.DiscardFrom(cards[0], cards),
                              action.ReturnFrom(cards[0], cards)])
        if player.count_played(tag=Instinct, ignore=self):
            for p in self.game.players:
                if p is not player:
                    cards = p.reveal(1)
                    if cards:
                        self.game.choice([action.DiscardFrom(cards[0],
                                                             cards, p),
                                          action.ReturnFrom(cards[0],
                                                            cards, p)])

class GambitCardShark(Hero):
    name = 'Gambit: Card Shark'
    cost = 4
    power = 2
    tags = [XMen, Ranged]
    desc = ("Reveal top card of deck. If it is <XMn>, draw it.")
    def on_play(self, player):
        cards = player.reveal(1)
        if cards:
            player.return_to_stack(cards[0])
            if XMen in cards[0].tags:
                player.draw(1)

class GambitStackDeck(Hero):
    name = 'Gambit: Stack the Deck'
    cost = 2
    tags = [XMen, Covert]
    desc = ("Draw 2 cards. Put a card from your hand on top of the deck.")
    def on_play(self, player):
        player.draw(2)
        actions = []
        for c in player.hand:
            actions.append(action.ReturnFrom(c, player.hand))
        if actions:
            self.game.choice(actions)

class NickFury(HeroGroup):
    name = 'Nick Fury'
    def fill(self):
        self.add(NickFuryPure, 1)
        self.add(NickFuryCommander, 3)
        self.add(NickFuryPromotion, 5)
        self.add(NickFuryWeaponry, 5)

class NickFuryPure(Hero):
    name = 'Nick Fury: Pure Fury'
    cost = 8
    tags = [Shield, Tech]
    desc = ("Defeat any Villain or Mastermind whose P is less than the"
            " number of SHIELD Heroes in the KO pile.")
    def on_play(self, player):
        count = 0
        for c in self.game.ko:
            if Shield in c.tags:
                count += 1
        actions = []
        for v in self.game.city:
            if v is not None and v.power < count:
                actions.append(bg.CustomAction('Defeat %s' % v.text(),
                    func=player.defeat,
                    kwargs=dict(villain=v)))
        if self.game.mastermind.power < count:
            v = self.game.mastermind
            actions.append(bg.CustomAction('Defeat %s' % v.text(),
                func=player.defeat,
                kwargs=dict(villain=v)))
        self.game.choice(actions)

class NickFuryCommander(Hero):
    name = 'Nick Fury: Legendary Commander'
    cost = 6
    power = 1
    extra_power = True
    tags = [Shield, Strength]
    desc = ("P+1 for each other <Shd> played this turn.")
    def on_play(self, player):
        count = player.count_played(Shield, ignore=self)
        player.available_power += count

class NickFuryPromotion(Hero):
    name = 'Nick Fury: Battlefield Promotion'
    cost = 4
    tags = [Shield, Covert]
    desc = ("You may KO a <Shd> Hero from hand or discard pile. "
            "If you do, gain a SHIELD Officer to your hand")
    def on_play(self, player):
        actions = []
        for c in player.hand:
            if Shield in c.tags:
                actions.append(action.KOFrom(c, player.hand))
        for c in player.discard:
            if Shield in c.tags:
                actions.append(action.KOFrom(c, player.discard))
        choice = self.game.choice(actions, allow_do_nothing=True)
        if choice is not None and self.game.officers:
            player.hand.append(self.game.officers.pop())

class NickFuryWeaponry(Hero):
    name = 'Nick Fury: High Tech Weaponry'
    cost = 3
    power = 2
    extra_power = True
    tags = [Shield, Tech]
    desc = ("<Tec>: P+1")
    def on_play(self, player):
        if player.count_played(Tech, ignore=self):
            player.available_power += 1

class Storm(HeroGroup):
    name = 'Storm'
    def fill(self):
        self.add(StormTidalWave, 1)
        self.add(StormCyclone, 3)
        self.add(StormLightning, 5)
        self.add(StormGathering, 5)

class StormTidalWave(Hero):
    name = 'Storm: Tidal Wave'
    cost = 7
    power = 5
    tags = [XMen, Ranged]
    desc = ("Villains on Bridge get P-2. <Rng>: Mastermind gets P-2.")
    def on_play(self, player):

        adjust_bridge = AdjustPower(
            items=lambda game: [game.city[0]],
            amount=-2)
        self.game.add_turn_handler('on_choice', adjust_bridge)
        if player.count_played(Ranged, ignore=self):
            adjust_mastermind = AdjustPower(
                items=lambda game: [game.mastermind],
                amount=-2)
            self.game.add_turn_handler('on_choice', adjust_mastermind)

class StormCyclone(Hero):
    name = 'Storm: Spinning Cyclone'
    cost = 6
    power = 4
    tags = [XMen, Covert]
    desc = ("You may move Villain to new space. Rescue "
            "Bystanders captured by Villain. If space full, swap.")
    def on_play(self, player):
        actions = []
        for v in self.game.city:
            if v is not None:
                actions.append(bg.CustomAction(
                    'Move %s' % v.text(),
                    func=self.on_move,
                    kwargs=dict(villain=v, player=player)))
        if actions:
            self.game.choice(actions, allow_do_nothing=True)
    def on_move(self, villain, player):
        actions = []
        for i in range(5):
            if self.game.city[i] is not villain:
                actions.append(bg.CustomAction(
                    'Move %s to %s' % (villain.name, self.game.city_names[i]),
                    func=self.on_move_to,
                    kwargs=dict(villain=villain, target=i, player=player)))
        self.game.choice(actions)

    def on_move_to(self, villain, target, player):
        player.rescue_bystander(villain)

        index = self.game.city.index(villain)
        self.game.city[index] = self.game.city[target]
        self.game.city[target] = villain

class StormLightning(Hero):
    name = 'Storm: Lightning Bolt'
    cost = 4
    power = 2
    tags = [XMen, Ranged]
    desc = ("Villains on Rooftops get P-2.")
    def on_play(self, player):
        adjust_roof = AdjustPower(
            items=lambda game: [game.city[2]],
            amount=-2)
        self.game.add_turn_handler('on_choice', adjust_roof)

class StormGathering(Hero):
    name = 'Storm: Gathering Stormclouds'
    cost = 3
    star = 2
    tags = [XMen, Ranged]
    desc = ("<Rng>: Draw a card")
    def on_play(self, player):
        if player.count_played(Ranged, ignore=self):
            player.draw(1)









