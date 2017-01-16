from itertools import repeat
from battlesnake.game import Game

class IterSnake(object):
    def __init__(self, moves):
        self.moves = moves
        
    def move(self, _game, _board):
        return next(self.moves)

class LoopSnake(object):
    MOVES = ["up", "left", "down", "right"]
    def move(self, game, _board):
        i = game.turn_count
        return self.MOVES[i/3 % len(self.MOVES)]

def print_board(board):
    print '-' * board.width
    print board.dump()
    print '-' * board.width
        
def assert_board(board, *lines):
    actual = tuple(board.dump().split("\n")[:-1])
    assert actual == lines

def test_wall():
    game = Game(8, 8)
    game.add_snake(IterSnake(repeat("left")))
    board = None
    for board in game.run():
        pass
    assert game.turn_count == 7
    assert_board(board,
                 "        ",
                 "        ",
                 "  +   + ",
                 "        ",
                 "aaa     ",
                 "        ",
                 "  +   + ",
                 "        ",
                 )
        
def test_collision():
    game = Game(8, 8)
    game.add_snake(IterSnake(repeat("left")))
    game.add_snake(IterSnake(repeat("right")))
    for _board in game.run():
        pass
    assert not game.snakes
    assert str(game.killed[0]) == "SnakePlayer(id=a name=a killed=Ran into b!)"
    assert str(game.killed[1]) == "SnakePlayer(id=b name=b killed=Ran into a!)"

def test_loop():
    game = Game(8, 8)
    game.add_snake(LoopSnake())
    for _board in game.run():
        pass
    assert game.turn_count > game.MAX_HEALTH
    assert str(game.killed[0]) == "SnakePlayer(id=a name=a killed=Starvation!)"

def test_food():
    class TestGame(Game):
        def start(self, *args, **kwargs):
            super(TestGame, self).start(*args, **kwargs)
            self.food = [ self.snakes[0].body[0] - 1 ]

        def add_stuff(self, _board):
            pass

    game = TestGame(8, 8)
    player1 = game.add_snake(IterSnake(repeat("left")))
    board = None
    for board in game.run():
        print_board(board)
        if game.turn_count == 0:
            assert_board(board,
                         "        ",
                         "        ",
                         "        ",
                         "        ",
                         "     +a ",
                         "        ",
                         "        ",
                         "        ",
                         )
            assert player1.length == game.INITIAL_LENGTH
        elif game.turn_count == 1:
            assert_board(board,
                         "        ",
                         "        ",
                         "        ",
                         "        ",
                         "     aa ",
                         "        ",
                         "        ",
                         "        ",
                         )
            assert player1.length == game.INITIAL_LENGTH+1
    assert_board(board,
                 "        ",
                 "        ",
                 "        ",
                 "        ",
                 "aaaa    ",
                 "        ",
                 "        ",
                 "        ",
                 )
    assert player1.length == game.INITIAL_LENGTH+1
       
    
