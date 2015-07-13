import numpy as np

class BoardGame(object):
    def __init__(self, seed=None):
        self.undo = []
        self.redo = []
        self.rng = np.random.RandomState(seed=seed)

    def text_state(self):
        raise NotImplementedError


