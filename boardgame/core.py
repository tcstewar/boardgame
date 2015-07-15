import numpy as np

class Action(object):
    def __init__(self, game):
        self.game = game
    def valid(self):
        return True
    def __str__(self):
        return self.name

class ActionSet(object):
    def __init__(self, actions, repeat=False, allow_same_type=True):
        self.actions = actions
        self.repeat = repeat
        self.allow_same_type = allow_same_type

    def get_valid_actions(self):
        return [a for a in self.actions if a.valid()]

    def text_choice(self):
        actions = self.get_valid_actions()
        while True:
            for i, a in enumerate(actions):
                print '%d: %s' % (i + 1, a)
            for i in range(15 - len(actions)):
                print '----------------'
            s = raw_input('Choose: ')
            try:
                return actions[int(s) - 1]
            except:
                print 'Invalid choice'

    def select(self, action):
        acts = self.get_valid_actions()
        assert action in acts

        if self.repeat:
            if not self.allow_same_type:
                acts = []
                for a in self.actions:
                    if a.__class__ is not action.__class__:
                        acts.append(a)
                self.actions = acts
            for a in self.actions:
                if a.valid():
                    a.game.action_queue.insert(0, self)
                    break

        action.perform()

class BoardGame(object):
    def __init__(self, seed=None):
        self.seed = seed
        self.rng = np.random.RandomState(seed=seed)
        self.player_index = 0
        self.finished = False
        self.events = []
        self.recent_events = []
        self.action_queue = []
        self.players = []

    def event(self, text):
        self.recent_events.append(text)

    @property
    def current_player(self):
        return self.players[self.player_index]

    def next_player(self):
        self.player_index = (self.player_index + 1) % len(self.players)

    def text_state(self):
        raise NotImplementedError

    def choice(self, actions, **kwargs):
        if len(actions) > 0:
            self.action_queue.insert(0, ActionSet(actions, **kwargs))

    def select_action(self):
        self.action_queue.pop(0).select()

    def run(self, selector):
        while not self.finished:
            actions = self.action_queue.pop(0)
            valid = actions.get_valid_actions()
            if len(valid) > 0:
                selector(self, actions)

