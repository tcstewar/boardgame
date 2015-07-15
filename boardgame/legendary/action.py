import boardgame as bg

from .core import *
from . import heroes

class StartTurn(bg.Action):
    name = 'Start turn'
    def valid(self):
        return self.game.state is BeginTurn
    def perform(self):
        self.game.play_villain()
        self.game.state = DuringTurn

class EndTurn(bg.Action):
    name = 'End turn'
    def valid(self):
        return self.game.state is DuringTurn
    def perform(self):
        self.game.current_player.available_star = 0
        self.game.current_player.available_power = 0
        self.game.current_player.discard_hand()
        self.game.current_player.discard_played()
        self.game.current_player.draw_new_hand()
        self.game.state = BeginTurn
        self.game.next_player()


class PlayFromHand(bg.Action):
    name = 'Play Hero from hand'
    def valid(self):
        if self.game.state is DuringTurn:
            cards = [h for h in self.game.current_player.hand
                       if isinstance(h, Hero)]
            return len(cards) > 0
        return False
    def perform(self):
        actions = []
        for h in self.game.current_player.hand:
            if isinstance(h, Hero):
                actions.append(Play(self.game, h))
        self.game.choice(actions)

class Recruit(bg.Action):
    name = 'Recruit Hero'
    def valid(self):
        if self.game.state is not DuringTurn:
            return False
        if self.game.current_player.available_star >= heroes.ShieldOfficer.cost:
            return True
        cards = [h for h in self.game.hq
                   if h.cost <= self.game.current_player.available_star]
        return len(cards) > 0
    def perform(self):
        actions = []
        for h in self.game.hq:
            if h.cost <= self.game.current_player.available_star:
                actions.append(RecruitHero(self.game, h))
        if self.game.current_player.available_star >= heroes.ShieldOfficer.cost:
            actions.append(RecruitHero(self.game,
                                             heroes.ShieldOfficer(self.game)))

        self.game.choice(actions)


class Fight(bg.Action):
    name = 'Fight'
    def valid(self):
        if self.game.state is not DuringTurn:
            return False
        if (self.game.current_player.available_power >=
                           self.game.mastermind.power):
            return True
        cards = [h for h in self.game.city
                   if h is not None and
                      h.power <= self.game.current_player.available_power]
        return len(cards) > 0
    def perform(self):
        actions = []

        if (self.game.current_player.available_power >=
                self.game.mastermind.power):
            actions.append(FightMastermind(self.game))
        for h in self.game.city:
            if (h is not None and
                    h.power <= self.game.current_player.available_power):
                actions.append(FightVillain(self.game, h))
        self.game.choice(actions)


class KOFrom(bg.Action):
    def __str__(self):
        return 'KO %s' % self.card
    def __init__(self, game, card, location):
        super(KOFrom, self).__init__(game)
        self.card = card
        self.location = location
    def valid(self):
        return self.card in self.location
    def perform(self):
        self.game.ko.append(self.card)
        self.location.remove(self.card)

class KOFromHQ(bg.Action):
    def __str__(self):
        return 'KO %s from HQ' % self.card
    def __init__(self, game, card):
        super(KOFromHQ, self).__init__(game)
        self.card = card
    def valid(self):
        return self.card in self.game.hq
    def perform(self):
        index = self.game.hq.index(self.card)
        self.game.ko.append(self.card)
        self.game.hq[index] = None
        self.game.fill_hq()

class DiscardFrom(bg.Action):
    def __str__(self):
        return 'Discard %s' % self.card
    def __init__(self, game, card, location):
        super(DiscardFrom, self).__init__(game)
        self.card = card
        self.location = location
    def valid(self):
        return self.card in self.location
    def perform(self):
        self.game.current_player.discard.append(self.card)
        self.location.remove(self.card)

class ReturnFrom(bg.Action):
    def __str__(self):
        return 'Return %s' % self.card
    def __init__(self, game, card, location):
        super(ReturnFrom, self).__init__(game)
        self.card = card
        self.location = location
    def valid(self):
        return self.card in self.location
    def perform(self):
        self.game.current_player.stack.insert(0, self.card)
        self.location.remove(self.card)

class Play(bg.Action):
    def __str__(self):
        return 'Play %s' % self.card
    def __init__(self, game, card):
        super(Play, self).__init__(game)
        self.card = card
    def valid(self):
        return self.card in self.game.current_player.hand
    def perform(self):
        self.game.current_player.available_power += self.card.power
        self.game.current_player.available_star += self.card.star
        self.card.on_play(self.game.current_player)
        self.game.current_player.played.append(self.card)
        self.game.current_player.hand.remove(self.card)

class RecruitHero(bg.Action):
    def __str__(self):
        return 'Recruit %s' % self.card
    def __init__(self, game, card):
        super(RecruitHero, self).__init__(game)
        self.card = card
    def valid(self):
        if (self.card not in self.game.hq and
            not isinstance(self.card, heroes.ShieldOfficer)):
                return False
        if self.card.cost > self.game.current_player.available_star:
            return False
        return True
    def perform(self):
        self.game.current_player.gain(self.card)
        self.game.current_player.available_star -= self.card.cost
        if not isinstance(self.card, heroes.ShieldOfficer):
            index = self.game.hq.index(self.card)
            self.game.hq[index] = None
            self.game.fill_hq()

class GainCard(bg.Action):
    def __str__(self):
        return 'Gain %s' % self.card
    def __init__(self, game, card):
        super(GainCard, self).__init__(game)
        self.card = card
    def perform(self):
        self.game.current_player.gain(self.card)

class DoNothing(bg.Action):
    def __str__(self):
        return 'Do Nothing'
    def __init__(self, game):
        super(DoNothing, self).__init__(game)
    def perform(self):
        pass


class FightVillain(bg.Action):
    def __str__(self):
        return 'Fight %s' % self.card
    def __init__(self, game, card):
        super(FightVillain, self).__init__(game)
        self.card = card
    def valid(self):
        return self.game.current_player.available_power >= self.card.power
    def perform(self):
        self.game.current_player.available_power -= self.card.power
        self.card.on_fight(self.game.current_player)
        if self.card in self.game.city:
            index = self.game.city.index(self.card)
            self.game.city[index] = None
        self.game.current_player.victory_pile.append(self.card)
        self.game.current_player.victory_pile.extend(self.card.captured)
        del self.card.captured[:]

class FightMastermind(bg.Action):
    def __str__(self):
        return 'Fight %s' % self.game.mastermind
    def __init__(self, game):
        super(FightMastermind, self).__init__(game)
    def valid(self):
        return (self.game.current_player.available_power >=
                  self.game.mastermind.power)
    def perform(self):
        self.game.current_player.available_power -= self.game.mastermind.power
        tactic = self.game.mastermind.tactics.pop(0)
        tactic.on_fight(self.game.current_player)
        self.game.current_player.victory_pile.append(tactic)
        self.game.current_player.victory_pile.extend(self.game.mastermind.captured)
        del self.game.mastermind.captured[:]
        if len(self.game.mastermind.tactics) == 0:
            self.game.good_wins()
