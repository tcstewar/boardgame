import boardgame as bg

import action
from .core import Hero, HeroGroup, Bystander
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
    name = 'Wolverine'
    def fill(self):
        self.add(WolverineAmbush, 5)
        self.add(WolverineAnimal, 5)
        self.add(WolverineReckless, 1)
        self.add(WolverineNoMercy, 3)

class WolverineAmbush(Hero):
    name = 'Wolverine: Sudden Ambush'
    cost = 4
    power = 2
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
        player.handlers[player.on_fight].append(on_fight)


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
        #TODO: ensure at least one of these actions is chosen!
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
        #TODO: ensure at least one of these actions is chosen!
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
            for c in player.hand + player.discard:
                actions.append(bg.CustomAction(
                    name='KO %s to rescue Bystander' % c,
                    valid = lambda game, player: (c in player.hand or
                                                  c in player.discard),
                    func=self.on_ko_rescue,
                    kwargs=dict(card=c, player=player)))
            actions.append(action.DoNothing())
            self.game.choice(actions)

    def on_ko_rescue(self, card, player):
        if card in player.hand:
            player.hand.remove(card)
        elif card in player.discard:
            player.discard.remove(card)
        else:
            #TODO: if action selection is done immediately, this should
            # never happen!
            return
        self.game.ko.append(card)
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
