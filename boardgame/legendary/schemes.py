import boardgame as bg

from .core import *
from . import action
from . import tags
from . import villains

class UnleashCube(Scheme):
    name = 'Unleash the Power of the Cosmic Cube'
    twists = 8
    desc = ('Twists 5, 6: All players gain Wound. '
            'Twist 7: All players gain 3 Wounds. '
            'Twist 8: Evil wins!')
    def twist(self):
        self.twists_done += 1
        if 5 <= self.twists_done <= 6:
            for p in self.game.players:
                p.gain_wound()
        elif self.twists_done == 7:
            for p in self.game.players:
                for i in range(3):
                    p.gain_wound()
        elif self.twists_done == 8:
            self.game.evil_wins()

class WeaveAWebOfLies(Scheme):
    name = 'Weave a Web of Lies'
    twists = 7
    desc = ("Can't fight mastermind unless # Bystanders >= # twists done. "
            "Defeat: [1S] to rescue bystander. 7 twists: evil wins")
    def valid_fight_mastermind(self, player):
        count = len([c for c in player.victory_pile
                       if isinstance(c, Bystander)])
        return count >= self.twists_done
    def on_defeat(self, villain, player):
        if (isinstance(villain, Villain) and
                player.available_star >= 1 and
                len(self.game.bystanders) > 0):
            actions = [
                bg.CustomAction('Rescue a Bystandar for [S1]',
                    func=self.on_defeat_rescue,
                    kwargs=dict(player=player)),
                ]
            self.game.choice(actions, allow_do_nothing=True)
    def on_defeat_rescue(self, player):
        player.available_star -= 1
        b = self.game.bystanders.pop()
        player.victory_pile.append(b)

    def twist(self):
        self.twists_done += 1
        if self.twists_done == 7:
            self.game.evil_wins()

class LegacyVirus(Scheme):
    name = 'The Legacy Virus'
    twists = 8
    desc = ("Twist: each player reveals <Tec> or gains Wound. "
            "Evil wins: the Wound stack (6 per player) runs out")
    def on_start(self):
        count = 6 * len(self.game.players)
        self.game.wounds = [Wound(self.game) for i in range(count)]
    def extra_text(self):
        return ' [Wounds left: %d]' % len(self.game.wounds)
    def twist(self):
        self.twists_done += 1
        for p in self.game.players:
            if p.reveal_tag(tags.Tech) is None:
                p.gain_wound(wounder=self)
    def on_wound_empty(self):
        self.game.evil_wins()

class BankRobbery(Scheme):
    name = 'Midtown Bank Robbery'
    twists = 8
    desc = ("Villains P+1/Bystander. Twist: Villain in Bank captures "
            "2 Bystanders; play Villain. Evil wins if 8 Bystanders escape.")
    count_bystanders = 0
    def adjust_bystander_count(self, count):
        return 12
    def twist(self):
        self.twists_done += 1
        if self.game.city[3] is not None:
            self.game.capture_bystander(index=3)
        if self.game.city[3] is not None:
            self.game.capture_bystander(index=3)
        self.game.play_villain()
    def on_escape(self, card):
        for c in card.captured:
            if isinstance(c, Bystander):
                self.count_bystanders += 1
        if self.count_bystanders >= 8:
            self.game.evil_wins()
    def extra_text(self):
        return ' [%d]' % self.count_bystanders
    def on_capture(self, card, captured):
        if isinstance(card, Villain) and isinstance(captured, Bystander):
            self.game.event('%s gains P+1 for capturing a Bystander' %
                            card.name)
            card.power += 1
    def on_rescue(self, card, captured):
        if isinstance(card, Villain) and isinstance(captured, Bystander):
            card.power -= 1


class PrisonOutbreak(Scheme):
    name = 'Negative Zone Prison Outbreak'
    twists = 8
    desc = ("Add extra Henchman group. Twist: Play 2 Villains. "
            "If 12 Villains escape, evil wins.")
    def adjust_henchman_count(self, count):
        return count + 1
    def twist(self):
        self.twists_done += 1
        self.game.play_villain()
        self.game.play_villain()
    def on_escape(self, card):
        if len(self.game.escaped) >= 12:
            self.game.evil_wins()

class CivilWar(Scheme):
    name = 'Super Hero Civil War'
    allow_solo = False
    desc = "Twist: KO all Heroes in HQ. If Hero pile runs out, Evil wins."
    def __init__(self, game):
        n_players = len(game.players)
        if 2 <= n_players <= 3:
            self.twists = 8
        elif 4 <= n_players <= 5:
            self.twists = 5
        else:
            assert False
        super(CivilWar, self).__init__(game)
    def adjust_hero_count(self, count):
        if len(self.game.players) == 2:
            return 4
        else:
            return count
    def twist(self):
        self.twists_done += 1
        for i, h in enumerate(self.game.hq):
            if h is not None:
                self.game.event('Civil War KOs %s' % h.name)
                self.game.ko.append(h)
                self.game.hq[i] = None
        self.game.fill_hq()
    def on_empty_hero(self):
        self.game.evil_wins()

class NegativeZone(Scheme):
    name = 'Negative Zone Prison Breakout'
    allow_solo = False
    desc = ("Twist: Play top 2 Villains. If 12 Villains escape, evil wins.")
    twists = 8
    def adjust_henchman_count(self, count):
        return count + 1
    def twist(self):
        self.twists_done += 1
        self.game.play_villain()
        self.game.play_villain()
    def on_escape(self, card):
        if len(self.game.escaped) >= 12:
            self.game.evil_wins()


class Killbot(Villain):
    name = 'Killbot'
    power = 3
    victory = 1

class ReplaceLeaders(Scheme):
    name = "Replace Earth's Leaders with Killbots"
    twists = 5
    desc = ("Killbots have P3+ the number of twists. If 5 escape, evil wins.")
    def adjust_bystander_count(self, count):
        return 18
    def on_start(self):
        self.killbots = []
        for i, card in enumerate(self.game.villain):
            if isinstance(card, Bystander):
                killbot = Killbot(self.game)
                killbot.original = card
                self.game.villain[i] = killbot
                self.killbots.append(killbot)
    def twist(self):
        self.twists_done += 1
        for k in self.killbots:
            k.power += 1

class Skrull(Villain):
    name = 'Skrull'
    def __init__(self, game, hero):
        super(Skrull, self).__init__(game)
        self.hero = hero
        self.power = 2 + hero.cost
    def on_fight(self, player):
        self.game.event('%s gains %s' % (player.name, self.hero))
        player.discard.append(self.hero)

class SecretInvasion(Scheme):
    name = "Secret Invasion of the Skrull Shapeshifters"
    twists = 8
    desc = ("Twist: Highest cost Hero from HQ become Skrull Villain. "
            "If 6 Skrull Villains escape, evil wins.")
    always_leads = villains.Skrulls
    def adjust_hero_count(self, count):
        return 6
    def on_start(self):
        for i in range(12):
            hero = self.game.hero.pop(0)
            skrull = Skrull(self.game, hero)
            self.game.villain.append(skrull)
    def twist(self):
        self.twists_done += 1
        index = self.game.find_highest_cost_hero()
        if index is not None:
            skrull = Skrull(self.game, self.game.hq[index])
            self.game.hq[index] = None
            self.game.fill_hq()
            self.game.villain.insert(0, skrull)
            self.game.play_villain()
    def count_escaped(self):
        count = 0
        for card in self.game.escaped:
            if isinstance(card, Skrull):
                count += 1
        return count
    def on_escape(self, card):
        if self.count_escaped() >= 6:
            self.game.evil_wins()
    def extra_text(self):
        return '[%d]' % self.count_escaped()

class DarkPortals(Scheme):
    name = "Portals to the Dark Dimension"
    twists = 7
    desc = ("Twist 1: Mastermind gets P+1. Twists 2-6: City space gets P+1."
            "Twist 7: Evil wins!")
    def twist(self):
        self.twists_done += 1
        if self.twists_done == 1:
            self.game.mastermind.power += 1
        elif self.twists_done == 7:
            self.game.evil_wins()
        else:
            index = self.twists_done - 2
            adjust = AdjustPower(
                items=lambda game: [game.city[index]],
                amount=1)
            self.game.add_handler('on_choice', adjust)

class CloneSaga(Scheme):
    name = "The Clone Saga"
    twists = 8
    desc = ("Twist: reveal 2 non-grey heros with same name or discard to 3. "
            "Evil wins: 2 same name Villains Escape or Villain deck runs out.")
    def twist(self):
        self.twists_done += 1
        for p in self.game.players:
            safe = False
            names = []
            for c in p.hand:
                if not isinstance(c, Hero) or c.grey:
                    continue
                if c.name in names:
                    safe = True
                    self.game.event('Protected by %s clones' % c.name)
                    break
                else:
                    names.append(c.name)
            if not safe:
                while len(p.hand) > 3:
                    actions = []
                    for h in p.hand:
                        actions.append(action.DiscardFrom(h, p.hand))
                    self.game.choice(actions, player=p)
    def on_escape(self, card):
        for c in self.game.escaped:
            if (c is not card) and (c.name == card.name):
                self.game.evil_wins()
    def on_empty_villain(self):
        self.game.evil_wins()















