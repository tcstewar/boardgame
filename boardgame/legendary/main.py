
if __name__ == '__main__':

    import boardgame.legendary

    game = boardgame.legendary.Legendary(seed=1)
    while not game.finished:
        print game.text_state()
        game.select_action()
    print game.text_state()
