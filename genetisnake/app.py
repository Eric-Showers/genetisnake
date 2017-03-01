#! /usr/bin/env python
import logging
import time
import os
import sys
from urlparse import urljoin

from flask import Flask, jsonify, request, send_from_directory, redirect
import click

import genetic
from genetisnake.game import Game
from genetisnake.snake import GenetiSnake

LOG = logging.getLogger(__name__)

application = Flask(__name__)

solver = genetic.GeneticSolver()

# sed -n -e 's/^turns=\([0-9]*\) /\1 \0/p' training-20170124.out | sort -n | tail -100
BEST_FUNCSTR = "(if_neg (add var0 (neg 0.4)) (neg var1) (add var3 var4))"
BEST_SNAKE = GenetiSnake(solver.parsefunc(GenetiSnake.ARITY, BEST_FUNCSTR))

COLOR = "rgb(144,60,128)"
HEAD = "/images/snake_head_nerdy.png"
NAME = "Genetisnake NBK"
TAUNTS = ["taunt"]
MOVES = "up right down left".split()

def debug_timing(f):
    def func(*args, **kwargs):
        dt = time.clock()
        try:
            return f(*args, **kwargs)
        finally:
            dt = (time.clock()-dt)*1000
            LOG.debug("debug_timing(%s) dt=%sms", f.__name__, dt)
            if dt > 400:
                LOG.debug("long delay! content=%s", request.data)
    func.func_name = f.func_name
    return func

def crossorigin(f):
    def func(*args, **kwargs):
        resp = f(*args, **kwargs)
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp
    func.func_name = f.func_name
    return func
    
#---------------------------------------------------------------------
# best snake

@application.route('/start', methods=['POST'])
@crossorigin
def start():
    LOG.debug("start: request.json=%s", request.json)

    return jsonify({
        "color": COLOR,
        "head_url": urljoin(request.url, '/images/snake_head.png'),
        "name": NAME,
        "taunt": "Evolved for battle",
        })

@application.route('/move', methods=['POST'])
@debug_timing
@crossorigin
def move(snake=None):
    #LOG.debug("move: request=%s", request)

    # See https://stembolthq.github.io/battle_snake/
    # board	Array<Array<BoardCell>>	Two dimensional representation of the board
    # food	Array<Point>	Array of all food currently on the board
    # game_id	UUID
    # height	integer
    # width	integer
    # snakes	Array<Snake>	Array of all living snakes in the game
    #   coords	 	Array<Point>
    #   health_points	 	0..100
    #   id	 	UUID
    #   name	 	string
    #   taunt	 	string
    # turn	integer	The current turn.
    # you	UUID	A reference to your snake's id, the snake object can be found in snakes.
    request.get_data() # get all request data and cache it
    data = request.json

    if not snake:
        snake=BEST_SNAKE
    
    if "board" in data:
        del data["board"]

    LOG.debug("move: pid=%s turn=%s content_length=%s",
              os.getpid(), data["turn"],
              request.headers.get('content-length'))

    # convert the Battlesnake server structure into my Game
    width, height = (int(data[x]) for x in ("width", "height"))
    game = Game(width, height)
    board = game.render()
    game.food = [board.index(*xy) for xy in data["food"]]
    game.turn_count = int(data["turn"])
    self_index = None
    for idx, data_snake in enumerate(data["snakes"]):
        player = game.add_snake(data_snake, data_snake["id"])
        player.body = [board.index(*xy) for xy in data_snake["coords"]]
        player.health = data_snake["health_points"]
        if player.name == data["you"]:
            self_index = idx
    board = game.render()
    move_name = snake.move(game, board, self_index)

    LOG.debug("move: move=%s", move_name)

    return jsonify({
        "move": move_name,
        "taunt": "%s@%s" % (move_name, game.turn_count),
        })


#--------------------------------------------------------------------
# ok snake: recent trainee

# cat training-20170129-133146/training.log | grep -A 1 '^winners generation' | sed -n -e 's/^turns=\([0-9]*\)/\1 \0/p' | sort -n | tail -20
# winners generation=522
# turns=8311
TRAINEE_FUNCSTR = """(add (add (add -0.956064389076 (square var4)) (add (min (mul var5 var0) (square -2.76973052056)) (square (square (square (add (add (add (if_neg var1 1.79267619074 (add (square var3) (exp (cos2pi (min var2 -0.48064695733))))) (square var3)) 1.88411201432) (square (mul (exp (sin2pi -1.67536141169)) 3.55149852287)))))))) (add (add (add (if_neg var1 1.79267619074 (add (square var3) (exp (cos2pi (min var2 -0.48064695733))))) (square var3)) 1.88411201432) (add (add -0.956064389076 (square var4)) (add (min (mul var5 var0) (square -2.76973052056)) (square (square (square (add (add (add (if_neg var1 1.79267619074 (add (square var3) (exp (cos2pi (min var2 -0.48064695733))))) (square var3)) 1.88411201432) (square (mul (exp (sin2pi -1.67536141169)) 3.55149852287))))))))))"""
TRAINEE_SNAKE = GenetiSnake(solver.parsefunc(GenetiSnake.ARITY, TRAINEE_FUNCSTR))

@application.route('/trainee/start', methods=['POST'])
@crossorigin
def trainee_start():
    return jsonify({
        "color": 'green',
        "head_url": urljoin(request.url, '/images/trainee.png'),
        "name": 'GenetiRookie',
        "taunt": 'Keen and green',
        })

@application.route('/trainee/move', methods=['POST'])
@crossorigin
def trainee_move():
    return move(snake=TRAINEE_SNAKE)

#--------------------------------------------------------------------
# greedy snake: always go for food

GREEDY_FUNCSTR = "(neg var1)"
GREEDY_SNAKE = GenetiSnake(solver.parsefunc(GenetiSnake.ARITY, GREEDY_FUNCSTR))

@application.route('/greedy/start', methods=['POST'])
@crossorigin
def greedy_start():
    return jsonify({
        "color": 'yellow',
        "head_url": urljoin(request.url, '/images/greedy.png'),
        "name": 'GenetiGreedy',
        "taunt": 'hungry hungry snake',
        })

@application.route('/greedy/move', methods=['POST'])
@crossorigin
def greedy_move():
    return move(snake=GREEDY_SNAKE)

#---------------------------------------------------------------------
# static files

@application.route('/<path:path>')
@crossorigin
def send_html(path):
    LOG.debug("send_from_directory path=%s cwd=%s", path, os.getcwd())
    return send_from_directory(os.path.join(os.getcwd(), 'html'), path)

@application.route('/')
@crossorigin
def index():
    return redirect("/snake.html")

#---------------------------------------------------------------------
# cli

@click.command()
@click.option('--host', '-h', default='0.0.0.0')
@click.option('--port', '-p', default=5000)
@click.option('--debug/--no-debug', '-d', default=False)
@click.option('--name', '-n', default=NAME)
@click.option('--color', '-c', default=COLOR)
@click.option('--head', default=HEAD)
def cli(host, port, debug, name, color, head):
    logging.basicConfig(level=logging.WARN)
    # pylint: disable=global-statement
    global COLOR, HEAD, NAME
    COLOR = color
    HEAD = head
    NAME = name
    
    args=dict(
        host=host,
        port=port,
        debug=debug,
        )
    if args.get('debug'):
        LOG.setLevel(logging.DEBUG)

    sys.stderr.write("cli: %s pid=%s args=%s\n" % (__name__, os.getpid(), args))
    LOG.debug("application.run(args=%s)", args)

    application.run(**args)



if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli(auto_envvar_prefix='GENETISNAKE')
