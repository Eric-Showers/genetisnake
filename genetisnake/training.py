import errno    
import os
import io
import random
import logging
import json
import datetime
import re

import click
import matplotlib
# pylint: disable=wrong-import-position
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathos.multiprocessing import Pool

import genetic
from .snake import GenetiSnake
from .game import Game

LOG = logging.getLogger(__name__)


RE_GAME = re.compile(r'(?P<basename>gen\d+-game\d+-turns\d+)\.(json|log)(?:\..*)?')
MAX_WINNERS = 20

def evolve(
    root_dir=None,
    width=20,
    height=20,
    max_gens=None,
    n_players=6, # players per game
    n_games=3, # games per round
    n_rounds=5, # number of games each player will play
    ):

    if not root_dir:
        now = datetime.datetime.now()
        root_dir = now.strftime("training-%Y%m%d-%H%M%S")
    mkdir_p(root_dir)

    # list of all winners
    winners = []
    gen_start = 0
    winners_path = os.path.join(root_dir, "winners.json")
    if os.path.exists(winners_path):
        with open(winners_path) as f:
            winners = json.load(f)
            gen_start = max(w["gen"] for w in winners)
        
    # append to a training log
    training_log_path = os.path.join(root_dir, "training.log")
    def training_log(msg):
        with open(training_log_path, "a") as f:
            f.write(msg)

    # keep a json list of games
    game_list_path = os.path.join(root_dir, "games.json")
    games = []
    if os.path.exists(game_list_path):
        with open(game_list_path) as f:
            games = json.load(f)

    # graph max turns by generation
    gen_turns = []

    # genetic solver and initial population
    solver = genetic.GeneticSolver()
    funcs = []
    if winners:
        funcs = [genetic.FuncWithErr(solver.parsefunc(GenetiSnake.ARITY, w["func"])) for w in winners]
    n = n_games * n_players
    funcs = funcs[:n]
    if n > len(funcs):
        funcs += solver.population(GenetiSnake.ARITY, n-len(funcs))

    # I need to train to beat worthy adversaries
    extra_snakes = []
    for funcstr in (
        "(neg var1)",
        "(neg var1)",
        ):
        snake = GenetiSnake(genetic.FuncWithErr(solver.parsefunc(GenetiSnake.ARITY, funcstr)))
        extra_snakes.append(snake)
    
    solver.start(maxgens = max_gens)
    solver.gen_count = gen_start
    winners = []
    
    while not solver.converged():
        gen_count = solver.gen_count+1
        training_log("start generation=%s rounds=%s snakes=%s\n" % (solver.gen_count, n_rounds, len(funcs)))
        
        # play n_rounds games of n_players randomly shuffled
        snakes = {}
        for func in funcs:
            func.err = 0
            func.games = []
            snake = GenetiSnake(func)
            snake.err = 0
            snake.games = []
            snake.snake_id = id(snake)
            snakes[snake.snake_id] = snake

        game_count = 0
        game_infos = []
        for game_round in range(n_rounds):
            # pick groups of n snakes, and add in a few greedy snakes to beat
            snake_ids = snakes.keys()
            random.shuffle(snakes.keys())
            start = 0
            while start < len(snake_ids):
                snake_group = [snakes[snake_id] for snake_id in snake_ids[start : start + n_players]]
                start += n_players

                # add a couple of greedy snakes to the game for competition
                snake_group += extra_snakes
                    
                game_count += 1
                game_infos.append(dict(
                    root_dir = root_dir,
                    width = width,
                    height = height,
                    game_count = game_count,
                    game_round = game_round,
                    gen_count = gen_count,
                    snakes = snake_group,
                    ))
            
        pool = Pool()
        for result in pool.map(play_game, game_infos):
            for snake_id, snake_result in result['snakes'].items():
                snake = snakes[snake_id]
                # TODO - merge results into snake
                snake.games.append(snake_result['game'])
                snake.turns += snake_result['turns']
                snake.err += snake_result['err']
                
            # update list of games
            games.append(dict(
                path = result['game_json'],
                generation = result['gen_count'],
                game = result['game_count'],
                round = result['game_round'],
                turns = result['turn_count'],
                func_size = result['func_size'], # game.killed[-1].snake.move_func.func.child_count(),
                func = result['func'], # func=str(game.killed[-1].snake.move_func.func),
                ))

        # Evaluate snakes: miximize turns and killed_order
        for snake in snakes.values():
            func = snake.move_func
            func.err = -snake.err
            func.turns = snake.turns
            func.games = snake.games
            assert len(func.games) == n_rounds

        # the solver makes the next generation based on func.err
        parents, funcs = solver.generation(funcs)

        # winners for the generation
        training_log("winners generation=%s\n" % (solver.gen_count-1))
        winner_func = None
        for func in parents:
            if hasattr(func, 'turns'):
                training_log("turns=%s func=%s\n" % (func.turns, func))
                if not winner_func:
                    winner_func = func
        training_log("finish generation=%s\n" % (solver.gen_count-1))

        # update the progress graph
        gen_turns.append(-parents[0].err)
        plt.plot(gen_turns)
        plt.ylabel('Max Turns')
        plt.xlabel('Generations')
        plt.savefig(os.path.join(root_dir, 'turns.svg'))

        # keep only the games for the top 100 winners
        if winner_func:
            winner = dict(
                err=winner_func.err,
                func=str(winner_func.func),
                turns=winner_func.turns,
                games=winner_func.games,
                gen=solver.gen_count,
                )
            training_log("game generation=%s winner=%s\n" % (solver.gen_count, winner))
            winners.append(winner)

        # only keep the last few winners
        winners = sorted(winners, key=lambda w: w['err'])[:MAX_WINNERS]
        winners = winners[:MAX_WINNERS]
        winner_games = set()
        for w in winners:
            for g in w['games']:
                m = RE_GAME.match(g['path'])
                assert m
                winner_games.add(m.group('basename'))

        # delete game files not in winner_games
        for path in os.listdir(root_dir):
            m = RE_GAME.match(path)
            if m and m.group('basename') not in winner_games:
                p = os.path.join(root_dir, path)
                os.unlink(p)

        # delete games not in winner_games
        games_keep = []
        for game in games:
            m = RE_GAME.match(game['path'])
            assert m
            if m.group('basename') in winner_games:
                games_keep.append(game)
        games = games_keep
        game_list_path_t = game_list_path + '.t'
        with open(game_list_path_t, "w") as f:
            json.dump(games, f, indent=2)
        os.rename(game_list_path_t, game_list_path)

        # write winners
        winners_path_t = winners_path + ".t"
        with open(winners_path_t, "w") as f:
            json.dump(winners, f, sort_keys=True, indent=2)
        os.rename(winners_path_t, winners_path)

def play_game(game_info):
    # set up a game with n_players
    game = Game(game_info['width'], game_info['height'])
    game_hdr = dict(
        snakes=[],
        )

    gen_count = game_info['gen_count']
    game_round = game_info['game_round']
    game_count = game_info['game_count']
    root_dir = game_info['root_dir']
    
    # write game logs to tmp files
    game_name = "gen%03d-game%02d" % (gen_count, game_count)
    game_log_path_tmp = os.path.join(root_dir, "%s.log.tmp" % game_name)
    game_json_path_tmp = os.path.join(root_dir, "%s.json.tmp" % game_name)
    with open(game_log_path_tmp, 'w') as game_log, \
         open(game_json_path_tmp, 'w') as game_json :

        game_log.write("game start generation=%s round=%s game=%s pid=%s\n" % (gen_count, game_round, game_count, os.getpid()))

        for snake in game_info['snakes']:
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
            if game.turn_count > 0:
                game_json.write(",\n")
            game_json.write(json.dumps(game.to_dict()))
            
            # end the game when all but 1 are dead
            if len(game.snakes) <= 1:
                break

        game.killed += game.snakes
        
        game_log.write("game winners generation=%s round=%s game=%s\n" % (gen_count, game_round, game_count))
        for player in sorted(game.killed, key=lambda p: p.turns, reverse=True):
            game_log.write("snake: %s func=%s\n" % (player, player.snake.move_func.func))
        game_log.write("game finished generation=%s round=%s game=%s\n" % (gen_count, game_round, game_count))

        game_json.write("\n]}\n")

    # move the tmp logs to their permanent names
    game_name = "gen%03d-game%02d-turns%05d" % (gen_count, game_count, game.turn_count)
    game_log_path = os.path.join(root_dir, "%s.log" % game_name)
    assert RE_GAME.match(os.path.basename(game_log_path))
    os.rename(game_log_path_tmp, game_log_path)
    game_json_path_rel = "%s.json" % game_name
    game_json_path = os.path.join(root_dir, game_json_path_rel)
    assert RE_GAME.match(os.path.basename(game_json_path))
    os.rename(game_json_path_tmp, game_json_path)

    # sum up the turns each player lasted
    result_snakes = {}
    for killed_order, player in enumerate(game.killed):
        snake_id = getattr(player.snake, 'snake_id', None)
        if not snake_id:
            continue
        
        result_snakes[snake_id] = dict(
            game = dict(
                game_turns = game.turn_count,
                player_turns = player.turns,
                killed_order = killed_order+1,
                path=os.path.basename(game_json_path),
            ),
            turns = player.turns,
            err = player.turns * killed_order,
            )
            
    # return a map of snake_id => game stats
    result = dict(
        game_json = game_json_path_rel,
        gen_count = gen_count,
        game_count = game_count,
        game_round = game_round,
        turn_count = game.turn_count,
        func_size = game.killed[-1].snake.move_func.func.child_count(),
        func = str(game.killed[-1].snake.move_func.func),
        snakes = result_snakes,
        )
    return result
            
    

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

@click.command()
@click.option('--root_dir', '-r', default='')
@click.option('--width', '-w', default=20)
@click.option('--height', '-h', default=20)
@click.option('--players', '-p', default=6)
@click.option('--games', '-g', default=3)
@click.option('--rounds', '-n', default=5)
@click.option('--max_gens', default=0)
def cli(root_dir, width, height, players, games, rounds, max_gens):
    evolve(
        root_dir=root_dir,
        width=width,
        height=height,
        n_players=players, # players per game
        n_games=games, # games per round
        n_rounds=rounds, # number of games each player will play
        max_gens=max_gens,
        )
    
if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli(auto_envvar_prefix='TRAINING')
