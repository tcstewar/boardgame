import pytest

import boardgame.testing
from boardgame.legendary import Legendary

def test_game_random():
    for p in range(2, 6):
        for i in range(5):
            for j in range(5):
                game = Legendary(seed=i + 30 * p + 300 * j, n_players=p)
                rand = boardgame.testing.RandomPlay(seed=j + 30 * p)
                game.run(rand.selector)


def test_game_first():
    for p in range(2, 6):
        for i in range(100):
            game = Legendary(seed=i + 30 * p, n_players=p)
            rand = boardgame.testing.FirstPlay()
            game.run(rand.selector)

