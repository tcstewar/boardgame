def text_choice(game, actions):
    while True:
        for i, a in enumerate(actions):
            print '%d: %s' % (i + 1, a)
        for i in range(15 - len(actions)):
            print '----------------'
        s = raw_input('Choose: ')
        if s == 'u':
            return 'undo'
        try:
            value = int(s) - 1
        except:
            print 'Invalid choice'
        if 0 <= value < len(actions):
            return value

if __name__ == '__main__':

    import boardgame.legendary

    game = boardgame.legendary.Legendary(seed=1)

    def selector(game, actions):
        print game.text_state()
        return text_choice(game, actions)
    game.run(selector)
    print game.text_state()
