#! /usr/bin/env python
import logging
import time
import os
import sys

from flask import Flask, jsonify, request, send_from_directory
import click
from urlparse import urljoin

import genetic
from genetisnake.game import Game
from genetisnake.snake import GenetiSnake

LOG = logging.getLogger(__name__)

application = Flask(__name__)

COLOR = "rgb(144,60,128)"
HEAD = "images/snake_head_nerdy.png"
NAME = "Genetisnake NBK"
TAUNTS = ["taunt"]
MOVES = "up right down left".split()

@application.route('/start', methods=['POST'])
def start():
    LOG.debug("start: request.json=%s", request.json)

    return jsonify({
        "color": COLOR,
        "head_url": urljoin(request.url, HEAD),
        "name": NAME,
        "taunt": TAUNTS[0],
        })

# cat training-20170129-133146/training.log | grep -A 1 '^winners generation' | sed -n -e 's/^turns=\([0-9]*\)/\1 \0/p' | sort -n | tail -20
# winners generation=522
# turns=8311
FUNCSTR = """(add (add (add (add var0 (min var2 var0)) (add (add (neg var1) (min var2 var0)) (add (add 2.50242369095 (min var2 var0)) (min (add (add (neg var1) (min var2 var0)) (min var2 var0)) var0)))) (min (add (add (add (neg var1) (min var2 var0)) (add (add (neg var1) (min var2 var0)) (add (add 2.50242369095 (min var2 var0)) (min (add (add (neg var1) (min var2 var0)) (min var2 var0)) var0)))) var0) var0)) (add (add (add (neg var1) (min var2 var0)) (add (add (neg var1) (min var2 var0)) (add (add 2.50242369095 (min var2 var0)) (min (add (add (neg var1) (min var2 var0)) (min var2 var0)) var0)))) var0))"""
solver = genetic.GeneticSolver()
snake = GenetiSnake(solver.parsefunc(GenetiSnake.ARITY, FUNCSTR))

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

    return func

@application.route('/move', methods=['POST'])
@debug_timing
def move():
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

    if "board" in data:
        del data["board"]

    LOG.debug("move: pid=%s turn=%s content_length=%s",
              os.getpid(), data["turn"],
              request.headers.get('content-length'))

    # convert the Battlesnake server structure into my Game
    width, height = (int(data[x]) for x in ("width", "height"))
    game = Game(width, height)
    game.food = data["food"]
    game.turn_count = int(data["turn"])
    self_index = None
    for idx, data_snake in enumerate(data["snakes"]):
        player = game.add_snake(data_snake, data_snake["id"])
        player.body = data_snake["coords"]
        player.health = data_snake["health_points"]
        if player.name == data["you"]:
            self_index = idx
    board = game.render()
    move_name = snake.move(game, board, self_index)

    LOG.debug("move: move=%s", move_name)

    return jsonify({
        "move": move_name,
        "taunt": move_name,
        })

@application.route('/<path:path>')
def send_html(path):
    LOG.debug("send_from_directory path=%s cwd=%s", path, os.getcwd())
    return send_from_directory(os.path.join(os.getcwd(), 'html'), path)

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
