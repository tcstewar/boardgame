import numpy as np

class RandomPlay(object):
    def __init__(self, seed):
        self.rng = np.random.RandomState(seed=seed)
    def selector(self, game, actions):
        action = self.rng.choice(actions.get_valid_actions(game))
        actions.select(game, action)

class FirstPlay(object):
    def __init__(self, keep_state=False):
        self.keep_state = keep_state

    def selector(self, game, actions):
        if self.keep_state:
            state = game.text_state()
        try:
            action = actions.get_valid_actions(game)[0]
            actions.select(game, action)
        except:
            if self.keep_state:
                print state
            raise
