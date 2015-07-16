import numpy as np

class Action(object):
    def valid(self, game, player):
        return True
    def __str__(self):
        return self.name

class CustomAction(Action):
    def __init__(self, name, func, args=(), kwargs={}):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def perform(self, game, player):
        self.func(*self.args, **self.kwargs)

class ActionSet(object):
    def __init__(self, actions, repeat=False, allow_same_type=True,
                                player=None):
        self.actions = actions
        self.repeat = repeat
        self.player = player
        self.allow_same_type = allow_same_type

    def get_valid_actions(self, game):
        player = game.current_player if self.player is None else self.player
        return [a for a in self.actions if a.valid(game, player)]

    def select(self, game, action):
        acts = self.get_valid_actions(game)
        assert action in acts
        player = game.current_player if self.player is None else self.player

        if self.repeat:
            if not self.allow_same_type:
                acts = []
                for a in self.actions:
                    if a.__class__ is not action.__class__:
                        acts.append(a)
                self.actions = acts
            for a in self.actions:
                if a.valid(game, player):
                    game.action_queue.insert(0, self)
                    break

        action.perform(game, player)

class BoardGame(object):
    def __init__(self, seed=None, filename='game.sav'):
        self.reset(seed=seed, filename=filename)

    def reset(self, seed=None, filename='game.sav'):
        self.seed = seed
        self.rng = np.random.RandomState(seed=seed)
        self.player_index = 0
        self.finished = False
        self.events = []
        self.recent_events = []
        self.action_queue = []
        self.players = []
        self.choices = []
        self.filename = filename

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

    def run(self, selector, steps=None):
        while not self.finished:
            if steps is not None:
                if steps <= 0:
                    return
                steps -= 1
            actions = self.action_queue.pop(0)
            valid = actions.get_valid_actions(self)
            if len(valid) > 0:
                choice = selector(self, valid)
                self.events.extend(self.recent_events)
                del self.recent_events[:]
                if choice == 'undo':
                    self.undo()
                else:
                    actions.select(self, valid[choice])
                    self.choices.append(choice)

    def undo(self):
        choices = self.choices[:-1]
        self.reset(seed=self.seed, filename=self.filename)

        def selector(game, actions):
            return choices.pop(0)

        self.run(selector, steps=len(choices))
        return
        for c in choices:
            actions = self.action_queue.pop(0)
            valid = actions.get_valid_actions(self)
            if len(valid) > 0:
                actions.select(self, valid[c])
                self.choices.append(c)
