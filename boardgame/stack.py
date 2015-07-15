import collections

from boardgame.gamepiece import GamePiece
from boardgame.card import Card

class Stack(GamePiece, collections.MutableSequence):
    def __init__(self, game, items=[]):
        super(Stack, self).__init__(game)
        self._list = []
        self.extend(items)

    def __getitem__(self, key):
        return self._list[key]

    def __setitem__(self, key, value):
        self._ensure_valid(value)
        current = self[key]
        if current is value:
            return
        if current is not None:
            current._stack = None
        if value._stack is not None and value._stack is not self:
            value._stack.remove(value)
        value._stack = self
        self._list[key] = value

    def __delitem__(self, key):
        current = self[key]
        if current is not None:
            if isinstance(current, collections.Sequence):
                for x in current:
                    x._stack = None
            else:
                current._stack = None
        del self._list[key]

    def __len__(self):
        return len(self._list)

    def insert(self, key, value):
        self._ensure_valid(value)
        if value._stack is not None and value._stack is not self:
            value._stack.remove(value)
        value._stack = self
        self._list.insert(key, value)

    def _ensure_valid(self, card):
        if not isinstance(card, Card):
            raise ValueError('Items in a Stack must be Cards, not %s' % card)

