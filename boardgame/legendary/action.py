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
        player.used_star = 0
        player.has_fought = False
        player.has_recruited = False
        player.has_healed = False
        player.discard_hand()
        player.discard_played()
        player.draw_new_hand()
        player.extra_draw_count = 0
        player.draw_target = 6
        player.can_use_star_as_power = False
        player.clear_handlers()
        game.clear_turn_handlers()
        game.state = BeginTurn
        if player.take_another_turn:
            player.take_another_turn = False
        else:
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
            if (isinstance(h, Hero) and
                     not hasattr(h, 'valid_play') and
                     h in player.hand):
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
        power = player.available_power
        max_bribe = player.available_star if game.mastermind.bribe else 0
        if player.can_use_star_as_power:
            power += player.available_star
            max_bribe = 0
        if (power + max_bribe >= game.mastermind.power):
            if hasattr(game.scheme, 'valid_fight_mastermind'):
                if game.scheme.valid_fight_mastermind(player):
                    return True
            else:
                return True
        cards = []
        for h in game.city:
            if h is not None:
                if player.can_use_star_as_power:
                    max_bribe = 0
                else:
                    max_bribe = player.available_star if h.bribe else 0
                if h.power <= power + max_bribe and h.can_fight(player):
                    cards.append(h)
        return len(cards) > 0
    def perform(self, game, player):
        actions = []

        power = player.available_power
        max_bribe = player.available_star if game.mastermind.bribe else 0
        if player.can_use_star_as_power:
            power += player.available_star
            max_bribe = 0

        if (power + max_bribe >= game.mastermind.power):
            if hasattr(game.scheme, 'valid_fight_mastermind'):
                if game.scheme.valid_fight_mastermind(player):
                    actions.append(FightMastermind(game.mastermind))
            else:
                actions.append(FightMastermind(game.mastermind))
        for h in game.city:
            if h is not None:
                if player.can_use_star_as_power:
                    max_bribe = 0
                else:
                    max_bribe = player.available_star if h.bribe else 0
                if h.power <= power + max_bribe and h.can_fight(player):
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
        player.on_ko(self.card)
        game.scheme.on_ko(self.card)
        if self.location is game.hq:
            game.hq[game.hq.index(self.card)] = None
            game.fill_hq()
        else:
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
        player.on_ko(self.card)
        game.scheme.on_ko(self.card)
        game.hq[index] = None
        game.fill_hq()

class ReplaceFromHQ(bg.Action):
    def __str__(self):
        return 'Replace from HQ: %s' % self.card.text()
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        return self.card in game.hq
    def perform(self, game, player):
        index = game.hq.index(self.card)
        game.hero.append(self.card)
        game.hq[index] = None
        game.fill_hq()


class DiscardFrom(bg.Action):
    def __str__(self):
        extra = ''
        if self.show_cost:
            extra = extra + ' (cost:%d)' % self.card.cost
        return 'Discard %s%s' % (self.card, extra)
    def __init__(self, card, location, player=None, show_cost=False,
                 allow_return=True):
        self.card = card
        self.show_cost = show_cost
        self.player = player
        self.location = location
        self.allow_return = allow_return
    def valid(self, game, player):
        return self.card in self.location
    def perform(self, game, player):
        if self.player is not None:
            player = self.player
        player.discard_from(self.card, self.location,
                            allow_return=self.allow_return)

class GainFrom(bg.Action):
    def __str__(self):
        return 'Gain %s' % self.card
    def __init__(self, card, location, player=None, to_hand=False):
        self.card = card
        self.location = location
        self.player = player
        self.to_hand = to_hand
    def valid(self, game, player):
        return self.card in self.location
    def perform(self, game, player):
        if self.player is not None:
            player = self.player
        if self.to_hand:
            player.hand.append(self.card)
        else:
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
        return 'Play %s' % self.card.text()
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
        player.used_star += self.card.cost
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

class UseStar(bg.Action):
    def __str__(self):
        return 'Use %d Star as Power' % self.star
    def __init__(self, star):
        self.star = star
    def perform(self, game, player):
        player.available_star -= self.star

class FightVillain(bg.Action):
    def __str__(self):
        return 'Fight %s' % self.card
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        power = player.available_power
        if player.can_use_star_as_power or self.card.bribe:
            power += player.available_star
        return (power >= self.card.power and
                self.card.can_fight(player))
    def perform(self, game, player):
        if player.can_use_star_as_power or self.card.bribe:
            minimum = self.card.power - player.available_power
            maximum = self.card.power
            star = player.choose_star_usage(minimum, maximum)
        else:
            star = 0
        self.card.on_pre_fight(player)
        player.has_fought = True
        player.available_power -= (self.card.power - star)
        player.defeat(self.card)


class FightMastermind(bg.Action):
    def __str__(self):
        return 'Fight %s' % self.card
    def __init__(self, card):
        self.card = card
    def valid(self, game, player):
        if hasattr(game.scheme, 'valid_fight_mastermind'):
            if not game.scheme.valid_fight_mastermind(player):
                return False
        power = player.available_power
        if player.can_use_star_as_power or self.card.bribe:
            power += player.available_star
        return power >= self.card.power
    def perform(self, game, player):
        if player.can_use_star_as_power or self.card.bribe:
            minimum = self.card.power - player.available_power
            maximum = self.card.power
            star = player.choose_star_usage(minimum, maximum)
        else:
            star = 0

        player.has_fought = True
        player.available_power -= (self.card.power - star)
        player.defeat(self.card)
