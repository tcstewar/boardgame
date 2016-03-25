import json
import threading
import time

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
        x = ['<li onclick="do_action(%d);">%s</li>' % (i, str(a).replace('<', '&lt;').replace('>', '&gt;')) for i, a in enumerate(self.latest_actions)]
        x.append('''<li onclick="do_action('u');">Undo</li>''')
        #x.append('''<li onclick="do_action('r');">Reset</li>''')
        return '<ul>%s</ul>' % ''.join(x)

    def run(self):
        self.game.run(self.selector)

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
class Server(boardgame.swi.SimpleWebInterface):
    games = {}
    def swi(self):
        return '<a href="newgame">Start new game</a>'

    def swi_newgame(self, seed=None, n_players=1):
        game = boardgame.legendary.Legendary(
                seed=seed,
                n_players=n_players,
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
                console.log(d);
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
