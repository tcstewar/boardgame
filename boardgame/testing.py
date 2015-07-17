import numpy as np

class RandomPlay(object):
    def __init__(self, seed):
        self.rng = np.random.RandomState(seed=seed)
        self.choices = []
    def selector(self, game, actions):
        c = self.rng.randint(len(actions))
        self.choices.append(c)
        return c

class FirstPlay(object):
    def __init__(self):
        self.n_choices = 0
    def selector(self, game, actions):
        self.n_choices += 1
        return 0
