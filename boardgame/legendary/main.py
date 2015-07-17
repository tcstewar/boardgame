import argparse


def text_choice(game, actions):
    while True:
        for i, a in enumerate(actions):
            print '%d: %s' % (i + 1, a)
        for i in range(15 - len(actions)):
            print '----------------'
        s = raw_input('Choose: ')
        if s == 'u':
            return 'undo'
        elif s == 'l':
            return 'load autosave.sav'
        try:
            value = int(s) - 1
        except:
            print 'Invalid choice'
        if 0 <= value < len(actions):
            return value

if __name__ == '__main__':

    import boardgame.legendary

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--players', default=2, type=int,
                        help='number of players')
    parser.add_argument('-s', '--seed', default=None, type=int,
                        help='game seed')
    parser.add_argument('-m', '--mastermind', default=None, type=str,
                        help='Mastermind to use')
    parser.add_argument('-v', '--villain', default=None, type=str,
                        help='Villain to use')
    args = parser.parse_args()


    game = boardgame.legendary.Legendary(seed=args.seed,
                                         n_players=args.players,
                                         mastermind=args.mastermind,
                                         villain=args.villain)

    def selector(game, actions):
        print game.text_state()
        if len(game.choices) > 0:
            game.save('autosave.sav')
        return text_choice(game, actions)
    game.run(selector)
    print game.text_state()
