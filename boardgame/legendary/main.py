
if __name__ == '__main__':

    import boardgame.legendary

    game = boardgame.legendary.Legendary(seed=1)

    def selector(game, actions):
        print game.text_state()
        action = actions.text_choice()
        actions.select(action)
    game.run(selector)
    print game.text_state()
