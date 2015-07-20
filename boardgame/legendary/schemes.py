import boardgame as bg

from .core import *
from . import action

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
            "Defeat: [1S] to rescue bystander.")
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
