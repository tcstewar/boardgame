import boardgame as bg

from . import villains
from .core import *
from . import action
from . import tags

class RedSkull(Mastermind):
    name = 'Red Skull'
    desc = 'Master Strike: Each player KOs a Hero from their hand.'
    always_leads = villains.Hydra
    power = 7
    def __init__(self, game):
        super(RedSkull, self).__init__(game)
        self.tactics = [RedSkullTactic1(game), RedSkullTactic2(game),
                        RedSkullTactic3(game), RedSkullTactic4(game)]
        self.game.rng.shuffle(self.tactics)
    def strike(self):
        for p in self.game.players:
            actions = []
            for c in p.hand:
                if isinstance(c, Hero):
                    actions.append(action.KOFrom(c, p.hand))
            if len(actions) > 0:
                self.game.choice(actions)

class RedSkullTactic1(Tactic):
    name = 'Endless Resources'
    desc = 'S+4'
    victory = 5
    def on_fight(self, player):
        player.available_star += 4

class RedSkullTactic2(Tactic):
    name = 'HYDRA Conspiracy'
    desc = 'Draw 2 cards. Draw another per HYDRA Villain in Victory Pile'
    victory = 5
    def on_fight(self, player):
        player.draw(2)
        for c in player.victory_pile:
            if c.group is villains.Hydra:
                player.draw(1)

class RedSkullTactic3(Tactic):
    name = 'Negablast Grenades'
    desc = 'P+3'
    victory = 5
    def on_fight(self, player):
        player.available_power += 3

class RedSkullTactic4(Tactic):
    name = 'Ruthless Dictator'
    desc = 'Reveal top 3 cards. KO one, discard one, return one.'
    victory = 5
    def on_fight(self, player):
        index = len(player.hand)
        player.draw(3)
        cards = player.hand[index:]
        player.hand = player.hand[:index]
        actions = []
        for act in [action.KOFrom, action.DiscardFrom, action.ReturnFrom]:
            for card in cards:
                actions.append(act(card, cards))
        if len(cards) > 0:
            repeat = len(cards) - 1
            self.game.choice(actions, repeat=repeat, allow_same_type=False)


class DrDoom(Mastermind):
    name = 'Dr. Doom'
    desc = ('Master Strike: Each player with exactly 6 card in hand reveals '
            '<Tec> or returns 2 cards from hand to deck.')

    always_leads = villains.DoombotLegion
    power = 9

    def __init__(self, game):
        super(DrDoom, self).__init__(game)
        self.tactics = [DrDoomTactic1(game), DrDoomTactic2(game),
                        DrDoomTactic3(game), DrDoomTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            if len(p.hand) == 6:
                if p.reveal_tag(tags.Tech) is None:
                    actions = []
                    for c in p.hand:
                        actions.append(action.ReturnFrom(c, p.hand))
                    self.game.choice(actions, player=p)
                    self.game.choice(actions, player=p)

class DrDoomTactic1(Tactic):
    name = 'Dark Technology'
    desc = 'You may recruit a <Tec> or <Rng> hero for free'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in self.game.hq:
            if c is not None and (tags.Tech in c.tags or
                                  tags.Ranged in c.tags):
                actions.append(action.GainFrom(c, self.game.hq))
        if len(actions) > 0:
            self.game.choice(actions, allow_do_nothing=True)

class DrDoomTactic2(Tactic):
    name = "Monarch's Decree"
    desc = ('Choose one: each other player discards a card or '
            'each other player draws a card.')
    victory = 5
    def on_fight(self, player):
        actions = [
            bg.CustomAction('Each other player draws a card',
                      self.on_choose_draw, kwargs=dict(player=player)),
            bg.CustomAction('Each other player discards a card',
                      self.on_choose_discard, kwargs=dict(player=player)),
            ]
        self.game.choice(actions)

    def on_choose_draw(self, player):
        for p in player.other_players():
            p.draw(1)

    def on_choose_discard(self, player):
        for p in player.other_players():
            actions = []
            for h in p.hand:
                actions.append(action.DiscardFrom(h, p.hand))
            self.game.choice(actions, player=p)

class DrDoomTactic3(Tactic):
    name = 'Secrets of Time Travel'
    desc = 'Take another turn after this one'
    victory = 5
    def on_fight(self, player):
        player.take_another_turn = True

class DrDoomTactic4(Tactic):
    name = 'Treasures of Latveria'
    desc = 'When you draw a new hand at the end of your turn, draw 3 extra.'
    victory = 5
    def on_fight(self, player):
        player.draw_hand_extra += 3


class Loki(Mastermind):
    name = 'Loki'
    desc = 'Master Strike: Each player reveals a <Str> or gains a Wound.'

    always_leads = villains.EnemiesOfAsgard
    power = 10

    def __init__(self, game):
        super(Loki, self).__init__(game)
        self.tactics = [LokiTactic1(game), LokiTactic2(game),
                        LokiTactic3(game), LokiTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            if p.reveal_tag(tags.Strength) is None:
                p.gain_wound(wounder=self)

class LokiTactic1(Tactic):
    name = 'Whispers and Lies'
    desc = 'Each other player KOs 2 Bystanders from victory pile'
    victory = 5
    def on_fight(self, player):
        for p in player.other_players():
            count = 2
            for c in p.victory_pile[:]:
                if isinstance(c, Bystander):
                    p.victory_pile.remove(c)
                    self.game.ko.append(c)
                    count -= 1
                    if count == 0:
                        break

class LokiTactic2(Tactic):
    name = 'Vanishing Illusions'
    desc = 'Each other player KOs a Villain from their victory pile.'
    victory = 5
    def on_fight(self, player):
        for p in player.other_players():
            actions = []
            for c in p.victory_pile:
                if isinstance(c, Villain):
                    actions.append(action.KOFrom(c, p.victory_pile))
            if len(actions) > 0:
                self.game.choice(actions)

class LokiTactic3(Tactic):
    name = 'Maniacal Tyrant'
    desc = 'KO up to 4 cards from your discard pile'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in player.discard:
            actions.append(action.KOFrom(c, player.discard))
        for i in range(4):
            choice = self.game.choice(actions, allow_do_nothing=True)
            if choice is None:
                break

class LokiTactic4(Tactic):
    name = 'Cruel Ruler'
    desc = 'Defeat a Villain in the city for free'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in self.game.city:
            if c is not None:
                actions.append(bg.CustomAction(
                    'Defeat %s' % c.text(),
                    func=player.defeat,
                    kwargs=dict(villain=c)))
        if len(actions) > 0:
            self.game.choice(actions, allow_do_nothing=True)

class Magneto(Mastermind):
    name = 'Magneto'
    desc = 'Master Strike: Each player reveals <Xmn> or discards down to 4.'

    always_leads = villains.Brotherhood
    power = 8

    def __init__(self, game):
        super(Magneto, self).__init__(game)
        self.tactics = [MagnetoTactic1(game), MagnetoTactic2(game),
                        MagnetoTactic3(game), MagnetoTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            if p.reveal_tag(tags.XMen) is None:
                while len(p.hand) > 4:
                    actions = []
                    for c in p.hand:
                        if not c.return_from_discard:
                            actions.append(action.DiscardFrom(c, p.hand))
                    if len(actions) == 0:
                        break
                    self.game.choice(actions)

class MagnetoTactic1(Tactic):
    name = "Xavier's Nemesis"
    desc = 'For each <XMn>, rescue a Bystander'
    victory = 5
    def on_fight(self, player):
        for i in range(player.count_tagged(tags.XMen)):
            player.rescue_bystander()

class MagnetoTactic2(Tactic):
    name = "Crushing Shockwave"
    desc = 'Each other player reveals <XMn> or gains 2 Wounds.'
    victory = 5
    def on_fight(self, player):
        for p in player.other_players():
            if p.count_tagged(tags.XMen) == 0:
                p.gain_wound(wounder=self)
                p.gain_wound(wounder=self)

class MagnetoTactic3(Tactic):
    name = "Electromagnetic Bubble"
    desc = 'Choose an <XMn>. Add it to your hand after you draw your new hand.'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in player.get_tagged(tags.XMen):
            if c.is_copy:
                if c.original is None:
                    continue
                else:
                    c = c.original
            actions.append(bg.CustomAction(
                'Return %s' % c.text(),
                self.on_return,
                kwargs=dict(player=player, card=c)))
        if len(actions) > 0:
            self.game.choice(actions)

    def on_return(self, player, card):
        player.return_after_draw.append(card)

class MagnetoTactic4(Tactic):
    name = "Biter Captor"
    desc = 'Recruit an <Xmn> from HQ for free.'
    victory = 5
    def on_fight(self, player):
        actions = []
        for c in self.game.hq:
            if c is not None and tags.XMen in c.tags:
                actions.append(action.GainFrom(c, self.game.hq))
        if len(actions) > 0:
            self.game.choice(actions)

class Kingpin(Mastermind):
    name = 'Kingpin'
    desc = ('Bribe. Master Strike: Each player reveals <MKn> or '
            'discards hand and draws 5')

    always_leads = villains.StreetsOfNewYork
    power = 13
    bribe = True

    def __init__(self, game):
        super(Kingpin, self).__init__(game)
        self.tactics = [KingpinTactic1(game), KingpinTactic2(game),
                        KingpinTactic3(game), KingpinTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            if p.reveal_tag(tags.MKnight) is None:
                for c in p.hand[:]:
                    p.discard_from(c, p.hand)
                p.draw(5)

class KingpinTactic1(Tactic):
    name = "Call a Hit"
    desc = "Choose a Hero from each player's discard pile and KO it."
    victory = 6
    def on_fight(self, player):
        for p in self.game.players:
            actions = []
            for c in p.discard:
                if isinstance(c, Hero):
                    actions.append(action.KOFrom(c, p.discard))
            if len(actions) > 0:
                self.game.choice(actions, player=player)

class KingpinTactic2(Tactic):
    name = "Criminal Empire"
    desc = ("If not last tactic, reveal top 3 cards in Villain deck. "
            "Play all Villains revealed and return others in random order.")
    victory = 6
    def on_fight(self, player):
        if len(self.game.mastermind.tactics) > 0:
            cards = []
            for i in range(3):
                if len(self.game.villain) == 0:
                    self.game.play_villain()  # trigger game end
                card = self.game.villain.pop(0)
                if isinstance(card, Villain):
                    self.game.play_villain(card)
                else:
                    self.game.event('Revealed %s' % card)
                    cards.append(card)
            self.game.rng.shuffle(cards)
            for c in cards:
                self.game.villain.insert(0, c)

class KingpinTactic3(Tactic):
    name = "Dirty Cops"
    desc = ("Put a 0 cost Hero from the KO pile on top of each other "
            "player's deck.")
    victory = 6
    def on_fight(self, player):
        for p in player.other_players():
            #TODO: allow choice of order for doing this
            actions = []
            for c in self.game.ko:
                if isinstance(c, Hero) and c.cost == 0:
                    actions.append(bg.CustomAction(
                                        "Put %s on %s's deck" % (c, p.name),
                                        func=self.dirty_cop,
                                        args=(c, p)))
            if len(actions) > 0:
                self.game.choice(actions)

    def dirty_cop(self, card, player):
        self.game.ko.remove(card)
        player.stack.insert(0, card)

class KingpinTactic4(Tactic):
    name = "Mob War"
    desc = ("Each other player plays a Henchman from their Victory pile "
            "as if playing it fro the Villain deck.")
    victory = 6
    def on_fight(self, player):
        for p in player.other_players():
            #TODO: allow choice of order for doing this
            actions = []
            for c in p.victory_pile:
                if isinstance(c, Henchman):
                    actions.append(bg.CustomAction("Play Henchman %s" % c,
                                                   func=self.mob_war,
                                                   args=(c, p)))
            if len(actions) > 0:
                self.game.choice(actions, player=p)

    def mob_war(self, card, player):
        player.victory_pile.remove(card)
        self.game.play_villain(card)

class Apocalypse(Mastermind):
    name = 'Apocalypse'
    desc = ('Master Strike: Each player puts all C>1 Heros in hand on top of '
            'deck.  Evil Wins if Famine, Pestilence, War, and Death escape.')

    always_leads = villains.FourHorsemen
    force_always_leads = True
    power = 12

    horsemen = (villains.Death, villains.War,
                villains.Pestilence, villains.Famine)

    def __init__(self, game):
        super(Apocalypse, self).__init__(game)
        self.tactics = [ApocalypseTactic1(game), ApocalypseTactic2(game),
                        ApocalypseTactic3(game), ApocalypseTactic4(game)]
        self.game.rng.shuffle(self.tactics)

    def strike(self):
        for p in self.game.players:
            for c in p.hand[:]:
                if isinstance(c, Hero) and c.cost > 1:
                    p.hand.remove(c)
                    p.return_to_stack(c)

    def on_escape(self, card):
        for v in Apocalypse.horsemen:
            for c in self.game.escaped:
                if isinstance(c, v):
                    break
            else:
                return
        self.game.evil_wins()


class ApocalypseTactic1(Tactic):
    name = "Horsemen Are Drawing Nearer"
    desc = "Each other player plays a Four Horsemen from their Victory Pile."
    victory = 6
    def on_fight(self, player):
        for p in player.other_players():
            actions = []
            for c in p.victory_pile:
                if isinstance(c, Apocalypse.horsemen):
                    actions.append(bg.CustomAction('Play %s' % c,
                                                   self.draw_near,
                                                   args=(p,c)))
            if len(actions) > 0:
                self.game.choice(actions, player=p)

    def draw_near(self, player, card):
        player.victory_pile.remove(card)
        self.game.play_villain(card)


class ApocalypseTactic2(Tactic):
    name = "Immortal and Undefeated"
    desc = ("If not last tactic, rescue 6 Bystanders and shuffle this "
            "back into the tactics deck.")

    victory = 6
    def on_fight(self, player):
        if len(self.game.mastermind.tactics) > 0:
            for i in range(6):
                player.rescue_bystander()
            self.game.mastermind.tactics.append(self)
            self.game.rng.shuffle(self.game.mastermind.tactics)

class ApocalypseTactic3(Tactic):
    name = "The End of All Things"
    desc = ("Each other player reveals top 3 cards of deck, KOs C>=1, puts"
            " rest back in any order")
    victory = 6
    def on_fight(self, player):
        for p in player.other_players():
            cards = p.reveal(3)
            for c in cards[:]:
                if c.cost >= 1:
                    action.KOFrom(c, cards).perform(self.game, player)
            while len(cards) > 0:
                actions = []
                for c in cards:
                    actions.append(action.ReturnFrom(c, cards))
                self.game.choice(actions)

class ApocalypseTactic4(Tactic):
    name = "Apocalyptic Destruction"
    desc = ("Each other player KOs 2 Heros from discard that cost 1 or more")
    victory = 6
    def on_fight(self, player):
        for p in player.other_players():
            for i in range(2):
                actions = []
                for c in p.discard:
                    if isinstance(c, Hero) and c.cost >=1:
                        actions.append(action.KOFrom(c, p.discard))
                if len(actions) > 0:
                    self.game.choice(actions)
