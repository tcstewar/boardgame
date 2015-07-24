import boardgame as bg

from .core import *
from . import action
from . import tags

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





