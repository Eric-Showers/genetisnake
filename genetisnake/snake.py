from collections import deque
import string
import logging
import random

import genetic

from .board import Board, Move, CellType
from .game import Game

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

INF = float('inf')

CELL_TYPE_SELF  = 'A'
CELL_TYPE_ENEMY = set(string.ascii_uppercase) - set(CELL_TYPE_SELF)
CELL_TYPE_SPACE = ' '
CELL_TYPE_FOOD  = '*'
CELL_TYPE_GOLD  = '+'
CELL_TYPE_WALL  = '#'
CELL_TYPE_CLEAR = set([CELL_TYPE_SPACE, CELL_TYPE_FOOD, CELL_TYPE_GOLD])

class SnakeCellType(CellType):
    def can_move(self, cell):
        return cell in CELL_TYPE_CLEAR

CellTypeFood = SnakeCellType(CELL_TYPE_FOOD)
CellTypeEnemy = SnakeCellType(CELL_TYPE_ENEMY)
CellTypeSelf = SnakeCellType(CELL_TYPE_SELF)

SnakeMoves = (
    Move("up",     0, -1),
    Move("left",   1,  0),
    Move("down",   0,  1),
    Move("right", -1,  0),
)

class SnakeBoard(Board):
    def __init__(self, width, height, val=None, moves=None):
        if moves is None:
            moves = SnakeMoves
        super(SnakeBoard, self).__init__(width, height, val, moves)

    def smell_food(self):
        return self.smell(CellTypeFood)

    def smell_enemy(self):
        return self.smell(CellTypeEnemy)

    def smell_space(self, pos):
        """find the most moves I can make from pos without bumping into an enemy"""

        # by default, everything is infinite moves away
        smell = self.copy()

        # start at pos
        self_todo = deque()
        self_todo.append((pos, 0))

        # start all enemies
        enemy_type = CellTypeEnemy
        enemy_todo = []
        for pos, val in enumerate(self):
            if enemy_type.matches(val):
                enemy_todo.append((pos, self[pos], 0))

        # fill from my starting pos and my enemies
        max_dist = -INF
        enemy_dist = {}
        while self_todo:
            # expand enemies
            next_enemy_todo = []
            for pos, enemy, dist in enemy_todo:
                if smell[pos] is not None:
                    continue
                smell[pos] = (enemy, dist)
                enemy_dist[enemy] = dist
                for next_pos, _next_move in self.neighbours(pos):
                    if smell[next_pos] is None and enemy_type.can_move(self[next_pos]):
                        next_enemy_todo.append((next_pos, enemy, dist+1))
            enemy_todo = next_enemy_todo

            # try myself at the next pos
            pos, dist = self_todo.popleft()
            if smell[pos] is not None:
                continue
            smell[pos] = (CELL_TYPE_SELF, dist)
            max_dist = max(max_dist, dist)
                
            for next_pos, _next_move in self.neighbours(pos):
                if smell[next_pos] is None and CellTypeSelf.can_move(self[next_pos]):
                    self_todo.append((next_pos, dist+1))

        return smell, max_dist, min(enemy_dist.values()), max(enemy_dist.values())
        

class GenetiSnake(object):
    ARITY = 6 # number of arguments my decision function takes
    
    def __init__(self, move_func):
        self.move_func = move_func
        self.games = 0
        self.turns = 0

    def move(self, game, self_index):
        board = SnakeBoard(game.width, game.height)
        board.put_list(game.food, CELL_TYPE_FOOD)
        board.put_list(game.walls, CELL_TYPE_WALL)
        enemy_ids = iter(CELL_TYPE_ENEMY)
        for i, snake in enumerate(game.snakes):
            if i == self_index:
                body_id = CELL_TYPE_SELF
            else:
                body_id = next(enemy_ids)
            board.put_list(snake.body, body_id.lower())
            board[snake.body[0]] = body_id
        
        self_head = game.snakes[self_index].body[0]
        self_health = game.snakes[self_index].health

        food_smell,   _food_max = board.smell_food()
        enemy_smell, _enemy_max = board.smell_enemy()

        max_move = board.moves[0]
        max_score = None
        for move_pos, move in board.neighbours(self_head):
            if not CellTypeSelf.can_move(board[move_pos]):
                continue
            _space, space_self, space_enemy_min, space_enemy_max = board.smell_space(move_pos)
            # the number of arguments here is self.ARITY
            score = self.move_func(
                self_health,
                food_smell[move_pos],
                enemy_smell[move_pos],
                space_self,
                space_enemy_min,
                space_enemy_max,
                )
            if max_score is None or score > max_score:
                max_score = score
                max_move = move
        return max_move.name
        
def training():
    WIDTH=20
    HEIGHT=20
    N_ROUNDS = 5
    N_PLAYERS = 8

    solver = genetic.GeneticSolver()
    funcs = solver.population(GenetiSnake.ARITY, N_ROUNDS * N_PLAYERS)
    solver.start()
    while not solver.converged:
        # play N_ROUNDS games of N_PLAYERS randomly shuffled
        snakes = [GenetiSnake(func) for func in funcs]
        random.shuffle(snakes)
        for start in range(0, len(snakes), N_PLAYERS):
            # set up a game with N_PLAYERS
            game = Game(WIDTH, HEIGHT)
            for snake in snakes[start : start + N_PLAYERS]:
                game.add(snake)

            # play it
            for _board in game.run():
                pass

            # sum up the turns each player lasted
            for player in game.killed:
                snake = player.snake
                snake.games += 1
                snake.turns += player.turns

        # Want to maximize turns, so minimize -turns
        for snake in snakes:
            snake.func.err = -snake.turns
            assert snake.games == N_ROUNDS

        funcs = solver.generation(funcs)
                
