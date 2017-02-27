import logging

from genetisnake.game import Game
from genetisnake.snake import GenetiSnake

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def mock_func(argidx):
    def arity_func(*args):
        assert len(args) == GenetiSnake.ARITY
        return args[argidx]
    return arity_func

def move_food(*args):
    assert len(args) == GenetiSnake.ARITY
    return -args[1]
    
def print_board(board):
    print '-' * board.width
    print board.dump()
    print '-' * board.width

def assert_killed(game, **killed):
    assert set((snake.board_id, snake.killed) for snake in game.killed) == set(killed.items())

def test_game():
    game = Game(20, 20)
    game.add_snake(GenetiSnake(move_food))
    game.add_snake(GenetiSnake(move_food))
    for _board in game.run():
        if game.turn > game.MAX_HEALTH:
            break
    assert game.turn > game.MAX_HEALTH

def test_collision():
    game = Game(8, 8)
    game.add_snake(GenetiSnake(move_food))
    game.add_snake(GenetiSnake(move_food))
    for board in game.run():
        if game.turn_count == 0:
            game.food = [board.index(4, 4)]
            game.food_count = 1
            game.snakes[0].body = [board.index(4, 3)]
            game.snakes[1].body = [board.index(4, 5)]
    assert_killed(game, A="Ran into B!", B="Ran into A!")

def test_collision_3():
    game = Game(8, 8)
    game.add_snake(GenetiSnake(move_food))
    game.add_snake(GenetiSnake(move_food))
    game.add_snake(GenetiSnake(move_food))
    for board in game.run():
        if game.turn_count == 0:
            game.food = [board.index(4, 4)]
            game.food_count = 1
            game.snakes[0].body = [board.index(4, 3)]
            game.snakes[1].body = [board.index(4, 5)]
            game.snakes[2].body = [board.index(3, 4)]
    assert_killed(game, A="Ran into B!", B="Ran into A!", C="Ran into A!")
    
def move_space(*args):
    assert len(args) == GenetiSnake.ARITY
    LOG.debug("move_space: args=%s", args)
    return -args[1] if args[0] < 0.5 else args[3] + args[4]

def test_game_greedy():
    game = Game(20, 20)
    game.add_snake(GenetiSnake(move_space))
    game.add_snake(GenetiSnake(move_food))
    for board in game.run():
        if game.turn > game.MAX_HEALTH:
            break
    assert game.turn > game.MAX_HEALTH
    
if __name__ == '__main__':
    game = Game(20, 20)
    game.add_snake(GenetiSnake(move_space))
    game.add_snake(GenetiSnake(move_food))
    for board in game.run():
        print "game.run: turn=%s" % game.turn
        print board
