import boardgame as bg

from .core import Scheme

class UnleashCube(Scheme):
    name = 'Unleash the Power of the Cosmic Cube'
    def __init__(self, game):
        super(UnleashCube, self).__init__(game, twists=8)
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
