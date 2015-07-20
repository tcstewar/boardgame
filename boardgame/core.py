import json
import random

import numpy as np

class Action(object):
    def valid(self, game, player):
        return True
    def __str__(self):
        return self.name

class CustomAction(Action):
    def __init__(self, name, func, valid=None, args=(), kwargs={}):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.valid_func = valid
    def valid(self, game, player):
        if self.valid_func is not None:
            return self.valid_func(game, player)
        return True
    def perform(self, game, player):
        self.func(*self.args, **self.kwargs)

class DoNothing(Action):
    def __str__(self):
        return 'Do Nothing'
    def perform(self, game, player):
        pass


class UndoException(Exception):
    pass
class LoadException(Exception):
    def __init__(self, filename):
        self.filename = filename
        super(LoadException, self).__init__()
class FinishedException(Exception):
    pass
class NoValidActionException(Exception):
    pass

class BoardGame(object):
    def __init__(self, seed=None, *args, **kwargs):
        if seed is None:
            seed = random.randrange(0x7FFFFFF)
        self.args = args
        self.kwargs = kwargs
        self.reset(seed=seed, *args, **kwargs)

    def reset(self, seed=None):
        self.seed = seed
        self.rng = np.random.RandomState(seed=seed)
        self.player_index = 0
        self.finished = False
        self.events = []
        self.recent_events = []
        self.players = []
        self.choices = []
        self.forced_choices = []

    def event(self, text):
        self.recent_events.append(text)

    @property
    def current_player(self):
        return self.players[self.player_index]

    def next_player(self):
        self.player_index = (self.player_index + 1) % len(self.players)

    def text_state(self):
        raise NotImplementedError

    def get_valid_actions(self, actions, player):
        return [a for a in actions if a.valid(self, player)]

    def choice(self, actions, repeat=False, allow_same_type=True,
               player=None, allow_do_nothing=False):
        while True:
            if player is None:
                p = self.current_player
            else:
                p = player

            valid = self.get_valid_actions(actions, p)

            if len(valid) == 0:
                if allow_do_nothing:
                    return None
                else:
                    raise NoValidActionException()

            if allow_do_nothing:
                valid.append(DoNothing())

            if len(self.forced_choices) > 0:
                choice = self.forced_choices.pop(0)
            else:
                choice = self.selector(self, valid)
            self.choices.append(choice)

            self.events.extend(self.recent_events)
            del self.recent_events[:]

            action = valid[choice]
            action.perform(self, p)

            if self.finished:
                raise FinishedException()

            if not repeat:
                if isinstance(action, DoNothing):
                    return None
                else:
                    return action
            if isinstance(repeat, int):
                repeat -= 1

            if not allow_same_type:
                acts = []
                for a in actions:
                    if a.__class__ is not action.__class__:
                        acts.append(a)
                actions = acts

    def select_action(self):
        self.action_queue.pop(0).select()

    def run(self, selector):
        self.selector = selector

        while True:
            try:
                self.start()
            except UndoException:
                choices = self.choices[:-1]
                self.reset(seed=self.seed, *self.args, **self.kwargs)
                self.forced_choices = choices
            except LoadException as e:
                self.load(e.filename)
            except FinishedException:
                return



    def save(self, filename):
        state = dict(seed=self.seed,
                     choices=self.choices,
                     args=self.args,
                     kwargs=self.kwargs)
        with open(filename, 'w') as f:
            f.write(json.dumps(state))

    def load(self, filename):
        with open(filename) as f:
            state = json.loads(f.read())
        self.reset(seed=state['seed'], *state['args'], **state['kwargs'])
        self.forced_choices = state['choices']



