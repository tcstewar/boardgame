import copy

class GamePiece(object):
    def __init__(self, game):
        self.game = game
        self.is_copy = False
        self.original = None

    def copy(self):
        clone = copy.copy(self)
        clone.is_copy = True
        return clone

    def text(self):
        return str(self)


