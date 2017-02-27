import string

from .board import Board, Move, CellType, DEFAULT, isdefault

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


    def move_direction(self, pos0, pos1):
        x0, y0 = self.coords(pos0)
        x1, y1 = self.coords(pos1)
        x = x1 - x0
        y = y1 - y0
        y = -y # y goes down on boards
        s = set()
        if y >= x and y >= -x:
            s.add("up")

        if y <= x and y <= -x:
            s.add("down")

        if y >= x and y <= -x:
            s.add("left")

        if y <= x and y >= -x:
            s.add("right")

        return s
            
    def smell_space_cone(self, board_id, head_pos, direction):
        return self._smell_space(board_id, head_pos, lambda next_pos: direction in self.move_direction(head_pos, next_pos))
                            
    def smell_space_all(self, board_id, move_pos):
        return self._smell_space(board_id, move_pos)
        
    def _smell_space(self, board_id, head_pos, constraint=None):
        """find the most moves I can make from pos in a direction without bumping into an enemy"""

        # by default, everything is infinite moves away
        smell = self.copy(val=None)
        total = 0
        
        # start at pos
        self_todo = []
        smell[head_pos] = (board_id, 0)
        self_todo.append((head_pos, 0))

        # start all enemies
        enemy_type = CellTypeEnemy(board_id)
        enemy_todo = []
        for pos, val in enumerate(self):
            if enemy_type.matches(val):
                smell[pos] = (val, 0)
                enemy_todo.append((pos, self[pos], 0))

        # fill from my starting pos and my enemies
        while self_todo:
            # expand enemies
            next_enemy_todo = []
            for pos, enemy, dist in enemy_todo:
                for next_pos, _next_move in self.neighbours(pos):
                    if smell[next_pos] is not None or not enemy_type.can_move(self[next_pos]):
                        continue
                    smell[next_pos] = (enemy, dist+1)
                    next_enemy_todo.append((next_pos, enemy, dist+1))
            enemy_todo = next_enemy_todo

            # try myself at the next pos
            next_todo = []
            for pos, dist in self_todo:
                for next_pos, _next_move in self.neighbours(pos):
                    if smell[next_pos] is not None or not enemy_type.can_move(self[next_pos]):
                        continue
                    if constraint and not constraint(next_pos):
                        continue
                    total += 1
                    smell[next_pos] = (board_id, dist+1)
                    next_todo.append((next_pos, dist+1))
            self_todo = next_todo
            
        return total, smell
