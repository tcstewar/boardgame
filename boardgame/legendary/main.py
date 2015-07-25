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
        elif s == 'l':
            raise bg.LoadException('autosave.sav')
        try:
            value = int(s) - 1
            if 0 <= value < len(actions):
                return value
        except:
            print 'Invalid choice'

if __name__ == '__main__':

    import boardgame.legendary

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--players', default=1, type=int,
                        help='number of players')
    parser.add_argument('-s', '--seed', default=None, type=int,
                        help='game seed')
    parser.add_argument('-m', '--mastermind', default=None, type=str,
                        help='Mastermind to use')
    parser.add_argument('-v', '--villain', default=None, type=str,
                        help='Villain to use')
    parser.add_argument('--hero', default=None, type=str,
                        help='Hero to use')
    parser.add_argument('--scheme', default=None, type=str,
                        help='Evil scheme')
    parser.add_argument('--basic', action='store_true',
                        help='Use basic solo mode')
    args = parser.parse_args()


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
