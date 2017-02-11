#! /usr/bin/env python
import logging

from flask import Flask, jsonify, request

import genetic
from genetisnake.game import Game
from genetisnake.snake import GenetiSnake

LOG = logging.getLogger(__name__)

app = Flask(__name__)

# spec at https://stembolthq.github.io/battle_snake/

COLOR = "#FF0000"
HEAD_URL = "http://placecage.com/c/100/100"
NAME = "Genetisnake NBK"
TAUNTS = ["taunt"]
MOVES = "up right down left".split()

@app.route('/start', methods=['POST'])
def start():
    LOG.debug("start: request.json=%s", request.json)
    return jsonify({
        "color": COLOR,
        "head_url": HEAD_URL,
        "name": NAME,
        "taunt": TAUNTS[0],
        })

# from training-20170129-133146/training.log
# winners generation=613
# turns=7725
FUNCSTR = """(add (add (add (min var2 var0) (exp -3.51617647341)) (add -3.26129321449 (add (add (neg var1) (min var2 var0)) (add (add 2.50242369095 (min var2 var0)) (min (add (add (neg var1) (min var2 var0)) (min var2 var0)) var0))))) (sin (exp -3.51617647341)))"""
solver = genetic.GeneticSolver()
func = solver.parsefunc(GenetiSnake.ARITY, FUNCSTR)
snake = GenetiSnake(func)


@app.route('/move', methods=['POST'])
def move():
    LOG.debug("move: request=%s", request)

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
    data = request.json

    if "board" in data:
        del data["board"]

    LOG.debug("move: data=%s", data)

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

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN)

    args=dict(
        host='0.0.0.0',
        )
    if args.get('debug'):
        LOG.setLevel(logging.DEBUG)
        
    app.run(**args)
    
