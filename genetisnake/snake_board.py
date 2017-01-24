from collections import deque
import string

from .board import Board, Move, CellType, DEFAULT, isdefault, INF

CELL_TYPE_SNAKE = string.ascii_uppercase
CELL_TYPE_EMPTY = ' '
CELL_TYPE_FOOD  = '+'
CELL_TYPE_GOLD  = '*'
CELL_TYPE_WALL  = '#'
CELL_TYPE_CLEAR = CELL_TYPE_EMPTY + CELL_TYPE_FOOD + CELL_TYPE_GOLD

class SnakeCellType(CellType):
    def can_move(self, cell):
        return cell in CELL_TYPE_CLEAR

CellTypeFood = SnakeCellType(CELL_TYPE_FOOD)
CellTypeSnake = SnakeCellType(CELL_TYPE_SNAKE)

class CellTypeEnemy(SnakeCellType):
    def __init__(self, board_id):
        super(CellTypeEnemy, self).__init__(set(CELL_TYPE_SNAKE) - set(board_id))

SnakeMoves = (
    Move("up",     0, -1),
    Move("right",  1,  0),
    Move("down",   0,  1),
    Move("left",  -1,  0),
)

class SnakeBoard(Board):
    def __init__(self, width, height, val=DEFAULT, moves=DEFAULT):
        if isdefault(moves):
            moves = SnakeMoves
        if isdefault(val):
            val = CELL_TYPE_EMPTY
        super(SnakeBoard, self).__init__(width, height, val, moves)
        self.moves_byname = { move.name: move for move in self.moves }

    def move(self, pos, move_name):
        """return a new position after a move"""
        move = self.moves_byname[move_name]
        x, y = self.coords(pos)
        x += move.dx
        y += move.dy
        return self.index(x, y)
        
    def smell_food(self, _board_id):
        return self.smell(CellTypeFood)

    def smell_enemy(self, board_id):
        return self.smell(CellTypeEnemy(board_id))

    def smell_space(self, board_id, pos):
        """find the most moves I can make from pos without bumping into an enemy"""

        # by default, everything is infinite moves away
        smell = self.copy(val=None)

        # start at pos
        self_todo = deque()
        self_todo.append((pos, 0))

        # start all enemies
        enemy_type = CellTypeEnemy(board_id)
        enemy_todo = []
        for pos, val in enumerate(self):
            if enemy_type.matches(val):
                enemy_todo.append((pos, self[pos], 0))

        # fill from my starting pos and my enemies
        max_dist = -INF
        enemy_dist = {}
        while self_todo or enemy_todo:
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
            if self_todo:
                pos, dist = self_todo.popleft()
                if smell[pos] is not None:
                    continue
                smell[pos] = (board_id, dist)
                max_dist = max(max_dist, dist)

                for next_pos, _next_move in self.neighbours(pos):
                    if smell[next_pos] is None and CellTypeSnake.can_move(self[next_pos]):
                        self_todo.append((next_pos, dist+1))

        enemy_dist_vals = enemy_dist.values()
        if not enemy_dist_vals:
            enemy_dist_vals = [INF]
        return smell, max_dist, min(enemy_dist_vals), max(enemy_dist_vals)
