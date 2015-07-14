import boardgame

class Group(object):
    def __init__(self, game):
        self.group = []
        self.game = game
        self.fill()
    def add(self, card, count):
        for i in range(count):
            self.group.append(card(self.game))

class VillainGroup(Group):
    pass
class HenchmenGroup(Group):
    pass
class HeroGroup(Group):
    pass

class Hydra(VillainGroup):
    def fill(self):
        self.add(HydraKidnappers, 3)
        self.add(HydraArmies, 3)
        self.add(HydraViper, 1)
        self.add(HydraSupreme, 1)

class Villain(object):
    power = 0
    victory = 0
    def __init__(self, game):
        self.game = game
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
    def __str__(self):
        return '%s (%d)' % (self.name, self.power)
    def on_fight(self, player):
        pass
    def on_escape(self):
        pass

class HydraKidnappers(Villain):
    power = 3
    victory = 1
    group = Hydra
    name = 'HYDRA Kidnappers'
    def on_fight(self, player):
        actions = [ActionGainCard(self.game, ShieldOfficer(self.game)),
                   ActionDoNothing(self.game)]
        self.game.action_queue.append(boardgame.ActionSet(actions))

class HydraArmies(Villain):
    power = 4
    victory = 3
    group = Hydra
    name = 'Endless Armies of HYDRA'
    def on_fight(self, player):
        self.game.play_villain()
        self.game.play_villain()

class HydraViper(Villain):
    power = 5
    victory = 3
    group = Hydra
    name = 'Viper'
    def on_fight(self, player):
        for p in self.game.players:
            for v in p.victory_pile:
                if v.group is Hydra and v != self:
                    break
            else:
                p.gain_wound()
    def on_escape(self):
        self.on_fight(None)

class HydraSupreme(Villain):
    power = 6
    group = Hydra
    name = 'Supreme HYDRA'
    @property
    def victory(self):
        for p in self.game.players:
            if self in p.victory_pile:
                pts = 0
                for v in p.victory_pile:
                    if v.group is Hydra:
                        pts += 3
                return pts
        return 3



class Tactic(object):
    group = None
    def __init__(self, game):
        self.game = game

class Mastermind(object):
    def __init__(self, game):
        self.game = game
        self.captured = []
    def capture(self, card):
        self.captured.append(card)
    def __str__(self):
        return '%s (%d)' % (self.name, self.power)


class RedSkull(Mastermind):
    name = 'Red Skull'
    def __init__(self, game):
        super(RedSkull, self).__init__(game)
        self.power = 7
        self.always_leads = Hydra
        self.tactics = [RedSkullTactic1(game), RedSkullTactic2(game),
                        RedSkullTactic3(game), RedSkullTactic4(game)]
        self.game.rng.shuffle(self.tactics)
    def strike(self):
        for p in self.game.players:
            actions = []
            for c in p.hand:
                if isinstance(c, Hero):
                    actions.append(ActionKOFrom(self.game, c, p.hand))
            if len(actions) > 0:
                self.game.action_queue.append(boardgame.ActionSet(actions))

class RedSkullTactic1(Tactic):
    victory = 5
    def on_fight(self, player):
        player.available_star += 4

class RedSkullTactic2(Tactic):
    victory = 5
    def on_fight(self, player):
        player.draw(2)
        for c in player.victory_pile:
            if c.group is Hydra:
                player.draw(1)

class RedSkullTactic3(Tactic):
    victory = 5
    def on_fight(self, player):
        player.available_power += 3

class RedSkullTactic4(Tactic):
    victory = 5
    def on_fight(self, player):
        index = len(player.hand)
        player.draw(3)
        cards = player.hand[index:]
        player.hand = player.hand[:index]
        actions = []
        for act in [ActionKOFrom, ActionDiscardFrom, ActionReturnFrom]:
            for card in cards:
                actions.append(act(self.game, card, cards))
        self.game.action_queue.append(boardgame.ActionSet(actions,
                                                    repeat=True,
                                                    allow_same_type=False))

class Scheme(object):
    def __init__(self, game, twists):
        game.add_twists(twists)
        self.game = game
        self.twists_done = 0
        self.twists_total = 8
    def __str__(self):
        return '%s (%d/%d)' % (self.name, self.twists_done, self.twists_total)

class UnleashCube(Scheme):
    name = 'Unleash the Power of the Cosmic Cube'
    def __init__(self, game):
        super(UnleashCube, self).__init__(game, twists=8)
    def twist(self):
        self.twists_done += 1
        if 5 <= self.twists_done <= 6:
            for p in self.game.players:
                p.gain_wound()
        elif self.twists_done == 7:
            for p in self.game.players:
                for i in range(3):
                    p.gain_wound()
        elif self.twists_done == 8:
            self.game.evil_wins()

class SchemeTwist(object):
    def __init__(self, game):
        self.game = game
    def __str__(self):
        return 'Scheme Twist'
class MasterStrike(object):
    def __init__(self, game):
        self.game = game
    def __str__(self):
        return 'Master Strike'
class Bystander(object):
    def __init__(self, game):
        self.game = game
    def __str__(self):
        return 'Bystander'


class GameState(object):
    def __init__(self, name):
        self.name = name
BeginTurn = GameState('Begin Turn')
DuringTurn = GameState('During Turn')

class ActionStartTurn(boardgame.Action):
    name = 'Start turn'
    def valid(self):
        return self.game.state is BeginTurn
    def perform(self):
        self.game.play_villain()
        self.game.state = DuringTurn

class ActionEndTurn(boardgame.Action):
    name = 'End turn'
    def valid(self):
        return self.game.state is DuringTurn
    def perform(self):
        self.game.current_player.available_star = 0
        self.game.current_player.available_power = 0
        self.game.current_player.discard_hand()
        self.game.current_player.discard_played()
        self.game.current_player.draw_new_hand()
        self.game.state = BeginTurn
        self.game.next_player()


class ActionPlayFromHand(boardgame.Action):
    name = 'Play Hero from hand'
    def valid(self):
        if self.game.state is DuringTurn:
            cards = [h for h in self.game.current_player.hand
                       if isinstance(h, Hero)]
            return len(cards) > 0
        return False
    def perform(self):
        actions = []
        for h in self.game.current_player.hand:
            if isinstance(h, Hero):
                actions.append(ActionPlay(self.game, h))
        self.game.action_queue.append(boardgame.ActionSet(actions))

class ActionRecruit(boardgame.Action):
    name = 'Recruit Hero'
    def valid(self):
        if self.game.state is not DuringTurn:
            return False
        if self.game.current_player.available_star >= ShieldOfficer.cost:
            return True
        cards = [h for h in self.game.hq
                   if h.cost <= self.game.current_player.available_star]
        return len(cards) > 0
    def perform(self):
        actions = []
        for h in self.game.hq:
            if h.cost <= self.game.current_player.available_star:
                actions.append(ActionRecruitHero(self.game, h))
        if self.game.current_player.available_star >= ShieldOfficer.cost:
            actions.append(ActionRecruitHero(self.game,
                                             ShieldOfficer(self.game)))

        self.game.action_queue.append(boardgame.ActionSet(actions))


class ActionFight(boardgame.Action):
    name = 'Fight'
    def valid(self):
        if self.game.state is not DuringTurn:
            return False
        if (self.game.current_player.available_power >=
                           self.game.mastermind.power):
            return True
        cards = [h for h in self.game.city
                   if h is not None and
                      h.power <= self.game.current_player.available_power]
        return len(cards) > 0
    def perform(self):
        actions = []

        if (self.game.current_player.available_power >=
                self.game.mastermind.power):
            actions.append(ActionFightMastermind(self.game))
        for h in self.game.city:
            if (h is not None and
                    h.power <= self.game.current_player.available_power):
                actions.append(ActionFightVillain(self.game, h))
        self.game.action_queue.append(boardgame.ActionSet(actions))


class ActionKOFrom(boardgame.Action):
    def __str__(self):
        return 'KO %s' % self.card
    def __init__(self, game, card, location):
        super(ActionKOFrom, self).__init__(game)
        self.card = card
        self.location = location
    def valid(self):
        return self.card in self.location
    def perform(self):
        self.game.ko.append(self.card)
        self.location.remove(self.card)

class ActionDiscardFrom(boardgame.Action):
    def __str__(self):
        return 'Discard %s' % self.card
    def __init__(self, game, card, location):
        super(ActionDiscardFrom, self).__init__(game)
        self.card = card
        self.location = location
    def valid(self):
        return self.card in self.location
    def perform(self):
        self.game.current_player.discard.append(self.card)
        self.location.remove(self.card)

class ActionReturnFrom(boardgame.Action):
    def __str__(self):
        return 'Return %s' % self.card
    def __init__(self, game, card, location):
        super(ActionReturnFrom, self).__init__(game)
        self.card = card
        self.location = location
    def valid(self):
        return self.card in self.location
    def perform(self):
        self.game.current_player.stack.insert(0, self.card)
        self.location.remove(self.card)

class ActionPlay(boardgame.Action):
    def __str__(self):
        return 'Play %s' % self.card
    def __init__(self, game, card):
        super(ActionPlay, self).__init__(game)
        self.card = card
    def valid(self):
        return self.card in self.game.current_player.hand
    def perform(self):
        self.game.current_player.available_power += self.card.power
        self.game.current_player.available_star += self.card.star
        self.card.on_play(self.game.current_player)
        self.game.current_player.played.append(self.card)
        self.game.current_player.hand.remove(self.card)

class ActionRecruitHero(boardgame.Action):
    def __str__(self):
        return 'Recruit %s' % self.card
    def __init__(self, game, card):
        super(ActionRecruitHero, self).__init__(game)
        self.card = card
    def valid(self):
        if (self.card not in self.game.hq and
            not isinstance(self.card, ShieldOfficer)):
                return False
        if self.card.cost > self.game.current_player.available_star:
            return False
        return True
    def perform(self):
        self.game.current_player.gain(self.card)
        self.game.current_player.available_star -= self.card.cost
        if not isinstance(self.card, ShieldOfficer):
            index = self.game.hq.index(self.card)
            self.game.hq[index] = None
            self.game.fill_hq()

class ActionGainCard(boardgame.Action):
    def __str__(self):
        return 'Gain %s' % self.card
    def __init__(self, game, card):
        super(ActionGainCard, self).__init__(game)
        self.card = card
    def perform(self):
        self.game.current_player.gain(self.card)

class ActionDoNothing(boardgame.Action):
    def __str__(self):
        return 'Do Nothing'
    def __init__(self, game):
        super(ActionDoNothing, self).__init__(game)
    def perform(self):
        pass


class ActionFightVillain(boardgame.Action):
    def __str__(self):
        return 'Fight %s' % self.card
    def __init__(self, game, card):
        super(ActionFightVillain, self).__init__(game)
        self.card = card
    def valid(self):
        return self.game.current_player.available_power >= self.card.power
    def perform(self):
        self.game.current_player.available_power -= self.card.power
        self.card.on_fight(self.game.current_player)
        index = self.game.city.index(self.card)
        self.game.city[index] = None
        self.game.current_player.victory_pile.append(self.card)

class ActionFightMastermind(boardgame.Action):
    def __str__(self):
        return 'Fight %s' % self.game.mastermind
    def __init__(self, game):
        super(ActionFightMastermind, self).__init__(game)
    def valid(self):
        return (self.game.current_player.available_power >=
                  self.game.mastermind.power)
    def perform(self):
        self.game.current_player.available_power -= self.game.mastermind.power
        tactic = self.game.mastermind.tactics.pop(0)
        tactic.on_fight(self.game.current_player)
        self.game.current_player.victory_pile.append(tactic)
        if len(self.game.mastermind.tactics) == 0:
            self.game.good_wins()



class Legendary(boardgame.BoardGame):
    def __init__(self, seed=None):
        super(Legendary, self).__init__(seed=seed)
        self.villain = []
        self.city = [None, None, None, None, None]
        self.hero = []
        self.hq = [None, None, None, None, None]
        self.escaped = []
        self.ko = []
        self.initialize()
        self.state = BeginTurn
        self.finished = False
        self.actions = boardgame.ActionSet([ActionStartTurn(self),
                                            ActionPlayFromHand(self),
                                            ActionRecruit(self),
                                            ActionFight(self),
                                            ActionEndTurn(self),
                                            ])
        self.action_queue = []

    def initialize(self):
        self.players = [Player(self) for i in range(2)]
        self.mastermind = RedSkull(self)
        self.scheme = UnleashCube(self)
        for i in range(5):
            self.villain.append(MasterStrike(self))
        self.villain.extend(Hydra(self).group)
        self.villain.extend(Hydra(self).group)
        self.villain.extend(Hydra(self).group)
        self.villain.extend([Bystander(self) for i in range(2)])
        self.rng.shuffle(self.villain)

        self.hero.extend(IronMan(self).group)
        self.hero.extend(IronMan(self).group)
        self.hero.extend(IronMan(self).group)
        self.hero.extend(IronMan(self).group)
        self.hero.extend(IronMan(self).group)
        self.rng.shuffle(self.hero)

        self.fill_hq()

    def fill_hq(self):
        for i in range(5):
            if self.hq[i] is None and len(self.hero) > 0:
                self.hq[i] = self.hero.pop(0)


    def add_twists(self, count):
        for i in range(count):
            self.villain.append(SchemeTwist(self))

    def play_villain(self):
        card = self.villain.pop(0)
        if isinstance(card, Villain):
            self.shift_city()
            self.city[4] = card
        elif isinstance(card, SchemeTwist):
            self.scheme.twist()
        elif isinstance(card, MasterStrike):
            self.mastermind.strike()
        elif isinstance(card, Bystander):
            self.capture_bystander()
        else:
            raise Exception('could not handle %s' % card)

    def shift_city(self):
        index = 4
        while self.city[index] is not None:
            index -= 1
            if index < 0:
                self.escaped.append(self.city[0])
                self.city[0].on_escape()
                self.city[0] = None
                index = 0
        for i in range(index, 4):
            self.city[i] = self.city[i + 1]
        self.city[4] = None

    def capture_bystander(self):
        index = 4
        while self.city[index] is None and index >= 0:
            index -= 1
        if index < 0:
            v = self.mastermind
        else:
            v = self.city[index]
        v.capture(Bystander(self))




    def text_state(self):
        lines = []
        lines.append('Mastermind: %s' % self.mastermind)
        lines.append('Scheme: %s' % self.scheme)
        lines.append('Escaped: %d' % len(self.escaped))
        lines.append('    Bridge: %s' % self.city[0])
        lines.append('   Streets: %s' % self.city[1])
        lines.append('  Rooftops: %s' % self.city[2])
        lines.append('      Bank: %s' % self.city[3])
        lines.append('    Sewers: %s' % self.city[4])
        lines.append('Villain Pile: %d' % len(self.villain))
        for i in range(5):
            lines.append(' HQ %d (%d): %s' % (i + 1, self.hq[i].cost,
                                               self.hq[i]))
        for i, p in enumerate(self.players):
            hand = ', '.join(['%s' % x for x in p.hand])
            lines.append('  P%d: %s' % (i+1, hand))

        lines.append('Current Player %d: (%d/%d)' % (self.player_index+1,
                                        self.current_player.available_star,
                                        self.current_player.available_power))
        return '\n'.join(lines)

    def evil_wins(self):
        self.finished = True
    def good_wins(self):
        self.finished = True


class Hero(object):
    group = None
    power = 0
    star = 0
    cost = 0
    tags = []
    def __init__(self, game):
        self.game = game
    def __str__(self):
        return '%s (%d/%d)' % (self.name, self.star, self.power)
    def on_play(self, player):
        pass

class ShieldAgent(Hero):
    name = 'SHIELD Agent'
    star = 1
    def __init__(self, game):
        super(ShieldAgent, self).__init__(game)
class ShieldTrooper(Hero):
    name = 'SHIELD Trooper'
    power = 1
    def __init__(self, game):
        super(ShieldTrooper, self).__init__(game)
class ShieldOfficer(Hero):
    name = 'SHIELD Officer'
    star = 2
    cost = 3
    def __init__(self, game):
        super(ShieldOfficer, self).__init__(game)


class Tag(object):
    def __init__(self, name):
        self.name = name

Tech = Tag('Tech')
Avenger = Tag('Avenger')
Ranged = Tag('Ranged')

class IronMan(HeroGroup):
    def fill(self):
        self.add(IronManRepulsor, 5)
        self.add(IronManQuantum, 1)
        self.add(IronManEndless, 5)
        self.add(IronManArc, 3)

class IronManArc(Hero):
    name = 'Iron Man: Arc Reactor'
    cost = 5
    tags = [Tech, Avenger]
    @property
    def power(self):
        return 3 + self.game.current_player.count_played(tag=Tech)

class IronManEndless(Hero):
    name = 'Iron Man: Endless Intervention'
    cost = 3
    tags = [Tech, Avenger]
    def on_play(self, player):
        player.draw(1)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(1)

class IronManQuantum(Hero):
    name = 'Iron Man: Quantum Breakthrough'
    cost = 7
    tags = [Tech, Avenger]
    def on_play(self, player):
        player.draw(2)
        if player.count_played(tag=Tech, ignore=self) > 0:
            player.draw(2)

class IronManRepulsor(Hero):
    name = 'Iron Man: Repulsor Rays'
    cost = 3
    tags = [Ranged, Avenger]
    @property
    def power(self):
        if self.game.current_player.count_played(tag=Ranged, ignore=self) > 0:
            return 3
        else:
            return 2


class Wound(object):
    def __init__(self, game):
        self.game = game
        self.power = 0
        self.star = 0
    def __str__(self):
        return 'Wound'



class Player(object):
    def __init__(self, game):
        self.game = game
        self.stack = []
        self.hand = []
        self.discard = []
        self.played = []
        self.victory_pile = []
        self.available_power = 0
        self.available_star = 0
        for i in range(8):
            self.gain(ShieldAgent(game))
        for i in range(4):
            self.gain(ShieldTrooper(game))
        self.draw_new_hand()

    def discard_hand(self):
        self.discard.extend(self.hand)
        del self.hand[:]

    def discard_played(self):
        self.discard.extend(self.played)
        del self.played[:]

    def draw_new_hand(self):
        self.draw(6)

    def gain(self, card):
        self.discard.append(card)

    def gain_wound(self):
        self.gain(Wound(self.game))

    def draw(self, count):
        for i in range(count):
            if len(self.stack) == 0:
                self.stack.extend(self.game.rng.permutation(self.discard))
                del self.discard[:]
            if len(self.stack) > 0:
                self.hand.append(self.stack.pop(0))

    def count_played(self, tag, ignore=None):
        return len(self.get_played(tag=tag, ignore=ignore))
    def get_played(self, tag, ignore=None):
        return [c for c in self.played if tag in c.tags and c is not ignore]






if __name__ == '__main__':
    game = Legendary(seed=1)
    while not game.finished:
        print game.text_state()
        game.select_action()
    print game.text_state()
