import random
import logging

import genetic
from .snake import GenetiSnake
from .game import Game

LOG = logging.getLogger(__name__)

def evolve(
    width=20,
    height=20,
    max_gens=None,
    n_players=8, # players per game
    n_games=3, # games per round
    n_rounds=3, # number of games each player will play
    ):

    solver = genetic.GeneticSolver()
    funcs = solver.population(GenetiSnake.ARITY, n_games * n_players)
    solver.start(maxgens=max_gens)
    while not solver.converged():
        # play n_rounds games of n_players randomly shuffled
        snakes = [GenetiSnake(func) for func in funcs]
        for game_round in range(n_rounds):
            random.shuffle(snakes)
            game_count = 0
            for start in range(0, len(snakes), n_players):
                game_count += 1
                print "game=%s round=%s generation=%s" % (solver.gen_count, game_round, game_count)
                
                # set up a game with n_players
                game = Game(width, height)
                for snake in snakes[start : start + n_players]:
                    player = game.add_snake(snake)
                    print "snake: board_id=%s func=%s" % (player.board_id, snake.move_func.func)
                
                # play it
                for _board in game.run():
                    print "turn=%s round=%s generation=%s" % (game.turn_count, game_round, solver.gen_count)
                    print str(game)

                # sum up the turns each player lasted
                for player in game.killed:
                    snake = player.snake
                    snake.games += 1
                    snake.turns += player.turns

        # Want to maximize turns, so minimize -turns
        for snake in snakes:
            snake.move_func.err = -snake.turns
            assert snake.games == n_rounds

        parents, funcs = solver.generation(funcs)
        
        print "-" * width
        print "generation=%s done" % (solver.gen_count)
        for func in parents:
            print "turns=%s func=%s" % (-func.err, func)
                
