import boardgame as bg

from .core import *

class StartTurn(bg.Action):
    name = 'Start turn'
    def valid(self, game, player):
        return game.state is BeginTurn
    def perform(self, game, player):
        game.play_villain()
        game.state = DuringTurn

class EndTurn(bg.Action):
    name = 'End turn'
    def valid(self, game, player):
        return game.state is DuringTurn
    def perform(self, game, player):
        player.available_star = 0
        player.available_power = 0
        player.has_fought = False
        player.has_recruited = False
        player.has_healed = False
        player.discard_hand()
        player.discard_played()
        player.draw_new_hand()
        player.extra_draw_count = 0
        player.draw_target = 6
        player.clear_handlers()
        game.state = BeginTurn
        game.next_player()

class Heal(bg.Action):
    name = 'Heal Wounds'
    def valid(self, game, player):
        if not game.state is DuringTurn:
            return False
        if player.has_fought or player.has_recruited:
            return False
        for card in player.hand:
            if isinstance(card, Wound):
                return True
        return False
    def perform(self, game, player):
        wounds = [card for card in player.hand if isinstance(card, Wound)]
        for w in wounds:
            player.hand.remove(w)
            game.event('Player healed a Wound')
            game.ko.append(w)
        player.has_healed = True

class PlayFromHand(bg.Action):
    name = 'Play Hero from hand'
    def valid(self, game, player):
        if game.state is DuringTurn:
            cards = []
            for h in player.hand:
                if isinstance(h, Hero):
                    if hasattr(h, 'valid_play') and not h.valid_play(player):
                        continue
                    cards.append(h)
            return len(cards) > 0
        return False
    def perform(self, game, player):
        actions = []
        for h in player.hand:
            if isinstance(h, Hero):
                actions.append(Play(h))
        game.choice(actions)

class PlayAll(bg.Action):
    name = 'Play all Heroes'
    def valid(self, game, player):
        if game.state is DuringTurn:
            cards = [h for h in player.hand
                       if isinstance(h, Hero) and not hasattr(h, 'valid_play')]
            return len(cards) > 0
        return False
    def perform(self, game, player):
        for h in player.hand[:]:
            if isinstance(h, Hero) and not hasattr(h, 'valid_play'):
                player.play_from_hand(h)

class Recruit(bg.Action):
    name = 'Recruit Hero'
    def valid(self, game, player):
        if player.has_healed:
            return False
        if game.state is not DuringTurn:
            return False
        if (len(game.officers) > 0 and
            player.available_star >= game.officers[0].cost):
                    return True
        for h in game.hq:
            if h is not None:
                if h.cost <= player.available_star:
                    return True
        return False
    def perform(self, game, player):
        actions = []
        for h in game.hq:
            if (h is not None and
                    h.cost <= player.available_star):
                actions.append(RecruitHero(h))
        if (len(game.officers) > 0 and
            player.available_star >=
                  game.officers[0].cost):
            actions.append(RecruitHero(game.officers[0]))

        game.choice(actions)


class Fight(bg.Action):
    name = 'Fight'
    def valid(self, game, player):
        if player.has_healed:
            return False
        if game.state is not DuringTurn:
            return False
        if (player.available_power >= game.mastermind.power):
            return True
        cards = [h for h in game.city
                   if h is not None and
                      h.power <= player.available_power and
                      h.can_fight(player)]
        return len(cards) > 0
    def perform(self, game, player):
        actions = []

        if (player.available_power >=
                game.mastermind.power):
            actions.append(FightMastermind(game.mastermind))
        for h in game.city:
            if (h is not None and
                    h.power <= player.available_power and
                    h.can_fight(player)):
                actions.append(FightVillain(h))
        game.choice(actions)


class KOFrom(bg.Action):
    def __str__(self):
        return 'KO: %s' % self.card.text()
    def __init__(self, card, location):
        self.card = card
        self.location = location
    def valid(self, game, player):
        return self.card in self.location
    def perform(self, game, player):
        game.ko.append(self.card)
        self.location.remove(self.card)

class KOFromHQ(bg.Action):
    def __str__(self):
        return 'KO from HQ: %s' % self.card.text()
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        return self.card in game.hq
    def perform(self, game, player):
        index = game.hq.index(self.card)
        game.ko.append(self.card)
        game.hq[index] = None
        game.fill_hq()

class DiscardFrom(bg.Action):
    def __str__(self):
        return 'Discard %s' % self.card
    def __init__(self, card, location):
        self.card = card
        self.location = location
    def valid(self, game, player):
        return self.card in self.location
    def perform(self, game, player):
        if self.card.return_from_discard:
            #TODO: make this an option
            game.event('%s returned to hand' % self.card)
        else:
            player.discard.append(self.card)
            self.location.remove(self.card)

class GainFrom(bg.Action):
    def __str__(self):
        return 'Gain %s' % self.card
    def __init__(self, card, location, player=None):
        self.card = card
        self.location = location
        self.player = player
    def valid(self, game, player):
        return self.card in self.location
    def perform(self, game, player):
        if self.player is not None:
            player = self.player
        player.discard.append(self.card)
        if self.location is game.hq:
            game.hq[game.hq.index(self.card)] = None
            game.fill_hq()
        else:
            self.location.remove(self.card)

class ReturnFrom(bg.Action):
    def __str__(self):
        return 'Return %s' % self.card
    def __init__(self, card, location, player=None):
        self.card = card
        self.location = location
        self.player = player
    def valid(self, game, player):
        return self.card in self.location
    def perform(self, game, player):
        if self.player is not None:
            player = self.player
        player.stack.insert(0, self.card)
        self.location.remove(self.card)

class Play(bg.Action):
    def __str__(self):
        return 'Play %s' % self.card
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        if hasattr(self.card, 'valid_play'):
            if not self.card.valid_play(player):
                return False
        return self.card in player.hand
    def perform(self, game, player):
        player.play_from_hand(self.card)


class RecruitHero(bg.Action):
    def __str__(self):
        return '[C%d] Recruit %s' % (self.card.cost, self.card.text())
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        if (self.card not in game.hq and
            self.card not in game.officers):
                return False
        if self.card.cost > player.available_star:
            return False
        return True
    def perform(self, game, player):
        player.has_recruited = True
        player.gain(self.card)
        player.available_star -= self.card.cost
        if self.card in game.hq:
            index = game.hq.index(self.card)
            game.hq[index] = None
            game.fill_hq()
        else:
            game.officers.remove(self.card)

class GainCard(bg.Action):
    def __str__(self):
        return 'Gain %s' % self.card
    def __init__(self, card):
        self.card = card
    def perform(self, game, player):
        self.game.current_player.gain(self.card)

class DoNothing(bg.Action):
    def __str__(self):
        return 'Do Nothing'
    def perform(self, game, player):
        pass


class FightVillain(bg.Action):
    def __str__(self):
        return 'Fight %s' % self.card
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        return (player.available_power >= self.card.power and
                self.card.can_fight(player))
    def perform(self, game, player):
        self.card.on_pre_fight(player)
        player.has_fought = True
        player.available_power -= self.card.power
        if self.card in game.city:
            index = game.city.index(self.card)
            game.city[index] = None
        player.victory_pile.append(self.card)
        player.victory_pile.extend(self.card.captured)
        del self.card.captured[:]
        self.card.on_fight(player)

class FightMastermind(bg.Action):
    def __str__(self):
        return 'Fight %s' % self.card
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        return player.available_power >= self.card.power
    def perform(self, game, player):
        player.has_fought = True
        player.available_power -= self.card.power
        tactic = self.card.tactics.pop(0)
        game.event('Mastermind Tactic: %s' % tactic.text())
        tactic.on_fight(player)
        player.victory_pile.append(tactic)
        player.victory_pile.extend(self.card.captured)
        del self.card.captured[:]
        if len(self.card.tactics) == 0:
            game.good_wins()