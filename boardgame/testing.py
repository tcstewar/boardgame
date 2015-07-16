import numpy as np

class RandomPlay(object):
    def __init__(self, seed):
        self.rng = np.random.RandomState(seed=seed)
    def selector(self, game, actions):
        return self.rng.randint(len(actions))

class FirstPlay(object):
    def selector(self, game, actions):
        return 0
