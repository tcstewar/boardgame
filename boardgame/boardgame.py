import numpy as np

class Action(object):
    def __init__(self, game):
        self.game = game
    def valid(self):
        return True
    def __str__(self):
        return self.name

class ActionSet(object):
    def __init__(self, actions):
        self.actions = actions
    def select(self):
        acts = [a for a in self.actions if a.valid()]
        for i, a in enumerate(acts):
            print '%d: %s' % (i + 1, a)
        s = raw_input('Choose: ')
        try:
            act = acts[int(s) - 1]
        except:
            print 'Invalid choice'
            select()
        act.perform()


class BoardGame(object):
    def __init__(self, seed=None):
        self.rng = np.random.RandomState(seed=seed)
        self.player_index = 0

    @property
    def current_player(self):
        return self.players[self.player_index]

    def next_player(self):
        self.player_index = (self.player_index + 1) % len(self.players)

    def text_state(self):
        raise NotImplementedError

    def select_action(self):
        if len(self.action_queue) > 0:
            self.action_queue.pop(0).select()
        else:
            self.actions.select()




