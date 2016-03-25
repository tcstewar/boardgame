import argparse

import boardgame as bg


def text_choice(game, actions):
    while True:
        for i, a in enumerate(actions):
            print '%d: %s' % (i + 1, a)
        for i in range(15 - len(actions)):
            print '----------------'
        s = raw_input('Choose: ')
        if s == 'u':
            raise bg.UndoException()
        elif s == 'r':
            raise bg.ResetException()
        elif s == 'l':
            raise bg.LoadException('autosave.sav')
        try:
            value = int(s) - 1
            if 0 <= value < len(actions):
                return value
        except:
            print 'Invalid choice'

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
        Server.games[id(game)] = game

        return '''<meta http-equiv="refresh" content="0; url=/game/%d" />''' % id(game)

    def swi_game(self, gameid):
        game = Server.games[int(gameid)]

        return game.html_state()





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
