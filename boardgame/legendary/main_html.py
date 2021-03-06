import json
import threading
import time
import random

import boardgame as bg

class GameRunner(threading.Thread):
    def __init__(self, game):
        super(GameRunner, self).__init__()
        self.game = game
        self.latest_state = None
        self.latest_state_event = threading.Event()
        self.latest_actions = None
        self.action_choice_made = threading.Event()
        self.action_choice = None

    def set_state(self, state, actions):
        self.latest_state = state
        self.latest_actions = actions
        self.latest_state_event.set()

    def get_action_html(self):
        if self.latest_actions is None:
            x = []
        else:
            x = ['<li onclick="do_action(%d);">%s</li>' % (i, str(a).replace('<', '&lt;').replace('>', '&gt;')) for i, a in enumerate(self.latest_actions)]
            x.append('''<li onclick="do_action('u');">Undo</li>''')
            #x.append('''<li onclick="do_action('r');">Reset</li>''')
        return '<ul>%s</ul>' % ''.join(x)

    def run(self):
        self.game.run(self.selector)
        self.set_state(self.game.html_state(), None)

    def selector(self, game, actions):
        self.set_state(game.html_state(), actions)
        self.action_choice_made.wait()
        self.action_choice_made.clear()
        if self.action_choice == 'u':
            raise bg.UndoException()
        elif self.action_choice == 'r':
            raise bg.ResetException()
        return int(self.action_choice)

    def choose_action(self, choice):
        self.action_choice = choice
        self.action_choice_made.set()

import boardgame.swi
import boardgame.legendary
import boardgame.testing
from boardgame.legendary.game import ClassList
class Server(boardgame.swi.SimpleWebInterface):
    games = {}
    def swi(self):
        return '''<ul><li><a href="newgame">Start new game</a>
                      <li><a href="configure">Configure a game</a></ul>'''

    def swi_configure(self, seed=None, n_players=1, scheme=None,
                          mastermind=None, villain=None, hero=None):
        if seed is None:
            seed = random.randrange(0x7FFFFFFF)
        else:
            seed = int(seed)
        n_players = int(n_players)

        text = '''
        <a href="configure?seed=%(next_seed)d">randomize</a>
        <ul>
          <li>Mastermind: %(mastermind)s
          <li>Scheme: %(scheme)s
          <li>Results: %(mean_result)1.3f %(results)s
          <li>Scores: %(mean_score)1.3f %(scores)s
        </ul>

        <a href="newgame?seed=%(seed)d">start game</a>
        '''

        scores = []
        results = []
        for i in range(50):
            game = boardgame.legendary.Legendary(seed=seed,
                n_players=n_players,
                scheme=scheme,
                mastermind=mastermind,
                villain=villain,
                hero=hero
                )
            random.shuffle(game.hero)
            random.shuffle(game.villain)
            rand = boardgame.testing.FirstPlay()
            game.run(rand.selector)
            scores.append(sum(p.victory_points() for p in game.players))
            results.append(game.result)

        mean_score = sum(scores) / float(len(scores))
        mean_result = sum(results) / float(len(results))


        scheme = game.scheme.html()
        mastermind = game.mastermind.html()
        next_seed = random.randrange(0x7FFFFFFF)

        return text % locals()





    def swi_newgame(self, seed=None, n_players=1, scheme=None,
                          mastermind=None, villain=None, hero=None):
        if seed is not None:
            seed = int(seed)
        n_players = int(n_players)
        game = boardgame.legendary.Legendary(
                seed=seed,
                n_players=n_players,
                scheme=scheme,
                mastermind=mastermind,
                villain=villain,
                hero=hero
                )
        runner = GameRunner(game)
        runner.start()
        Server.games[id(game)] = runner

        return '''<meta http-equiv="refresh" content="0; url=/game/%d" />''' % id(game)

    def swi_game(self, gameid):
        code = '''<script type="text/javascript">
            var statediv = document.getElementById('state');
            var actionsdiv = document.getElementById('actions');
            var parser = document.createElement('a');
            parser.href = document.URL;
            var ws_url = 'ws://' + parser.host + '/gameupdate?gameid=%d';
            var ws = new WebSocket(ws_url);
            var ws2_url = 'ws://' + parser.host + '/gameaction?gameid=%d';
            var ws2 = new WebSocket(ws2_url);
            ws.onmessage = function(event) {
                var d = JSON.parse(event.data);
                statediv.innerHTML = d.state;
                actionsdiv.innerHTML = d.actions
            }
            function do_action(number) {
                ws2.send(number);
            }
            </script>
        ''' % (int(gameid), int(gameid))

        return '<div id="state"></div> <div id="actions"></div>%s' % code

    def ws_gameupdate(self, client, gameid):
        game = Server.games[int(gameid)]

        while True:
            game.latest_state_event.wait()
            game.latest_state_event.clear()
            msg = json.dumps(dict(state=game.latest_state,
                                         actions=game.get_action_html()))
            client.write(msg)

    def ws_gameaction(self, client, gameid):
        game = Server.games[int(gameid)]

        while True:
            x = client.read()
            if x is None:
                time.sleep(0.01)
            else:
                game.choose_action(x)




if __name__ == '__main__':
    Server.start(port=8080, browser=True)
    1/0

    game = boardgame.legendary.Legendary(seed=args.seed,
                                         n_players=args.players,
                                         mastermind=args.mastermind,
                                         hero=args.hero,
                                         scheme=args.scheme,
                                         basic=args.basic,
                                         villain=args.villain)

    def selector(game, actions):
        print game.text_state()
        if len(game.choices) > 0:
            game.save('autosave.sav')
        return text_choice(game, actions)
    game.run(selector)
    print game.text_state()
