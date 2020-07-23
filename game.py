from collections import namedtuple
import random
import uuid


class GameException(BaseException):
    pass


class GameOver(GameException):
    pass


class WrongPlayer(GameException):
    pass


class WrongTurn(GameException):
    pass


Player = namedtuple('Player', ('shape', 'pair'))


class Game:
    def __init__(self, p1, p2, field_size=3):
        self.uuid = str(uuid.uuid4())
        self.field = [['' for x in range(field_size)] for y in range(field_size)]
        self.field_size = field_size
        self.shapes = ['x', 'o']

        random.shuffle(self.shapes)

        self.players = {
            p1: Player(self.shapes[0], p2),
            p2: Player(self.shapes[1], p1),
        }

        self.turn = random.choice([p1, p2])
        self.winner = None

    def handle_turn(self, player, *, x, y):
        if self.winner is not None:
            raise GameOver

        if player is not self.turn:
            raise WrongPlayer

        if (x < 0) or (x >= self.field_size) or (y < 0) or (y >= self.field_size) or self.field[y][x] != '':
            raise WrongTurn

        self.field[y][x] = self.players[player].shape

        print('=' * 16)
        for row in self.field:
            print(row)
        print('=' * 16)

        for _x in range(self.field_size):
            if self.field[y][_x] != self.players[player].shape:
                break
        else:
            self.winner = player
            return False

        for _y in range(self.field_size):
            if self.field[_y][x] != self.players[player].shape:
                break
        else:
            self.winner = player
            return False

        for i in range(self.field_size):
            if self.field[i][i] != self.players[player].shape:
                break
        else:
            self.winner = player
            return False

        for i in range(self.field_size):
            if self.field[i][-(i + 1)] != self.players[player].shape:
                break
        else:
            self.winner = player
            return False

        self.turn = self.players[player].pair

        return True
