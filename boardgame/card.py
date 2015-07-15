import boardgame as bg

class Card(bg.GamePiece):
    def __init__(self, game):
        super(Card, self).__init__(game)
        self._stack = None
        self._attached = None

    @property
    def attached(self):
        if self._attached is None:
            self._attached = bg.Stack(self.game)
        return self._attached

    @property
    def stack(self):
        return self._stack
