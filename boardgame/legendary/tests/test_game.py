import pytest

import boardgame.testing
from boardgame.legendary import Legendary

def test_game_random():
    for i in range(10):
        for j in range(10):
            game = Legendary(seed=i)
            rand = boardgame.testing.RandomPlay(seed=j)
            game.run(rand.selector)


def test_game_first():
    for i in range(100):
        game = Legendary(seed=i)
        rand = boardgame.testing.FirstPlay()
        game.run(rand.selector)

