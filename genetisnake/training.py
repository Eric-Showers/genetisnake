import errno    
import os
import io
import random
import logging
import json
import datetime

import matplotlib
# pylint: disable=wrong-import-position
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import genetic
from .snake import GenetiSnake
from .game import Game

LOG = logging.getLogger(__name__)

def evolve(
    root_dir=None,
    width=20,
    height=20,
    max_gens=None,
    n_players=8, # players per game
    n_games=3, # games per round
    n_rounds=3, # number of games each player will play
    ):

    if root_dir is None:
        now = datetime.datetime.now()
        root_dir = now.strftime("training-%Y%m%d-%H%M%S")
    mkdir_p(root_dir)

    # append to a training log
    training_log_path = os.path.join(root_dir, "training.log")
    def training_log(msg):
        with open(training_log_path, "a") as f:
            f.write(msg)

    # keep a json list of games
    game_list_path = os.path.join(root_dir, "games.json")
    with open(game_list_path, "w") as game_list:
        game_list.write("[\n]\n")

    # graph max turns by generation
    gen_turns = []
    
    solver = genetic.GeneticSolver()
    funcs = solver.population(GenetiSnake.ARITY, n_games * n_players)
    solver.start(maxgens=max_gens)

    while not solver.converged():
        training_log("start generation=%s rounds=%s snakes=%s\n" % (solver.gen_count, n_rounds, len(funcs)))
        
        # play n_rounds games of n_players randomly shuffled
        snakes = [GenetiSnake(func) for func in funcs]
        game_count = 0
        for game_round in range(n_rounds):
            random.shuffle(snakes)
            for start in range(0, len(snakes), n_players):
                game_count += 1

                # write game logs to tmp files
                game_name = "gen%03d-game%02d" % (solver.gen_count, game_count)
                game_log_path_tmp = os.path.join(root_dir, "%s.log.tmp" % game_name)
                game_json_path_tmp = os.path.join(root_dir, "%s.json.tmp" % game_name)
                with open(game_log_path_tmp, 'w') as game_log, \
                     open(game_json_path_tmp, 'w') as game_json :

                    game_log.write("game start generation=%s round=%s game=%s\n" % (solver.gen_count, game_round, game_count))

                    # set up a game with n_players
                    game = Game(width, height)
                    game_hdr = dict(
                        snakes=[],
                        )
                    for snake in snakes[start : start + n_players]:
                        player = game.add_snake(snake)
                        game_log.write("game snake: %s func=%s\n" % (player, snake.move_func.func))
                        game_hdr["snakes"].append(dict(
                            board_id=player.board_id,
                            func=str(snake.move_func.func),
                            ))

                    # print the json header and start a list of turns
                    game_json.write(json.dumps(game_hdr))
                    game_json.seek(-1, io.SEEK_CUR)
                    game_json.write(', "turns": [\n')
                        
                    # play the game
                    for _board in game.run():
                        game_log.write("game turn=%s round=%s generation=%s\n" % (game.turn_count, game_round, solver.gen_count))
                        game_log.write(str(game))
                        game_log.write("\n")
                        if game.turn_count > 0:
                            game_json.write(",\n")
                        game_json.write(json.dumps(game.to_dict()))
                        
                    # sum up the turns each player lasted
                    for player in game.killed:
                        snake = player.snake
                        snake.games += 1
                        snake.turns += player.turns

                    game_log.write("game winners generation=%s round=%s game=%s\n" % (solver.gen_count, game_round, game_count))
                    for player in sorted(game.killed, key=lambda p: p.turns, reverse=True):
                        game_log.write("snake: %s func=%s\n" % (player, player.snake.move_func.func))
                    game_log.write("game finished generation=%s round=%s game=%s\n" % (solver.gen_count, game_round, game_count))

                    game_json.write("\n]}\n")

                # move the tmp logs to their permanent names
                game_name = "gen%03d-game%02d-turns%05d" % (solver.gen_count, game_count, game.turn_count)
                game_log_path = os.path.join(root_dir, "%s.log" % game_name)
                os.rename(game_log_path_tmp, game_log_path)
                game_json_path_rel = "%s.json" % game_name
                game_json_path = os.path.join(root_dir, game_json_path_rel)
                os.rename(game_json_path_tmp, game_json_path)
                
                # update list of games
                with open(game_list_path, "r+") as game_list:
                    game_list.seek(-2, io.SEEK_END)
                    if game_list.tell() > 2:
                        game_list.write(",\n")
                    game_list.write(json.dumps(dict(
                        path=game_json_path_rel,
                        generation=solver.gen_count,
                        game=game_count,
                        round=game_round,
                        turns=game.turn_count,
                        func_size=game.killed[-1].snake.move_func.func.child_count(),
                        #func=str(game.killed[-1].snake.move_func.func),
                        )))
                    game_list.write("]\n")

        # Want to maximize turns, so minimize -turns
        #max_turns = max(snake.turns for snake in snakes)
        #max_size = max(snake.move_func.func.child_count() for snake in snakes)
        for snake in snakes:
            func = snake.move_func
            # -(turns + turns * smallness (1-size/max))
            #func.err = -(snake.turns + snake.turns * 0.1 * (1.0 - float(func.func.child_count()) / max_size))
            func.err = -snake.turns
            func.turns = snake.turns
            assert snake.games == n_rounds

        parents, funcs = solver.generation(funcs)

        # winners for the generation
        training_log("winners generation=%s\n" % (solver.gen_count-1))
        for func in parents:
            training_log("turns=%s func=%s\n" % (-func.err, func))
        training_log("finish generation=%s\n" % (solver.gen_count-1))

        # update the progress graph
        gen_turns.append(-parents[0].err)
        plt.plot(gen_turns)
        plt.ylabel('Max Turns')
        plt.xlabel('Generations')
        plt.savefig(os.path.join(root_dir, 'turns.svg'))

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
