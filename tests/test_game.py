from itertools import repeat
import logging

from genetisnake.game import Game

logging.basicConfig(level=logging.DEBUG)

class IterSnake(object):
    def __init__(self, moves):
        self.moves = moves
        
    def move(self, _game, _board, _self_index):
        return next(self.moves)

class LoopSnake(object):
    MOVES = ["up", "left", "down", "right"]
    def move(self, game, _board, _self_index):
        i = game.turn_count
        return self.MOVES[i/3 % len(self.MOVES)]

def print_board(board):
    print '-' * board.width
    print board.dump()
    print '-' * board.width
        
def assert_board(board, *lines):
    actual = tuple(str(board).split("\n")[:-1])
    assert actual == lines

def assert_killed(game, *killed):
    assert set(snake.killed for snake in game.killed) == set(killed)

def test_wall():
    game = Game(8, 8)
    game.add_snake(IterSnake(repeat("left")))
    for _board in game.run():
        pass
    assert game.turn_count == 7
    assert_killed(game, "Moved out of bounds")
        
def test_collision():
    game = Game(8, 8)
    game.add_snake(IterSnake(repeat("left")))
    game.add_snake(IterSnake(repeat("right")))
    for _board in game.run():
        pass
    assert_killed(game, "Ran into B!", "Ran into A!")

def test_loop():
    game = Game(8, 8)
    game.add_snake(LoopSnake())
    for _board in game.run():
        pass
    assert_killed(game, "Starvation!")
    assert game.turn_count > game.MAX_HEALTH

def test_food():
    class TestGame(Game):
        def start(self, *args, **kwargs):
            super(TestGame, self).start(*args, **kwargs)
            self.food = [ self.snakes[0].body[0] - 1 ]
            self.render()
            return self.board

        def add_stuff(self):
            pass

    game = TestGame(8, 8)
    player1 = game.add_snake(IterSnake(repeat("left")))
    board = None
    for board in game.run():
        
        if game.turn_count == 0:
            assert_board(board,
                         "        ",
                         "        ",
                         "        ",
                         "        ",
                         "     +A ",
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
                         "     Aa ",
                         "        ",
                         "        ",
                         "        ",
                         )
            assert player1.length == game.INITIAL_LENGTH+1
    assert player1.length == game.INITIAL_LENGTH+1
       
    
