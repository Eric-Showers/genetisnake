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


    def in_direction(self, pos0, pos1, direction):
        x0, y0 = self.coords(pos0)
        x1, y1 = self.coords(pos1)
        x = x1 - x0
        y = y1 - y0
        y = -y # y goes down on boards

        if y >= x and y >= -x:
            if direction == "up":
                return True

        if y <= x and y <= -x:
            if direction == "down":
                return True

        if y >= x and y <= -x:
            if direction == "left":
                return True

        if y <= x and y >= -x:
            if direction == "right":
                return True

        return False
            
    def smell_space(self, board_id, head_pos, direction):
        """space_all, space_cone, space_map = smell_space(self, board_id, head_pos, move_name)
        
        find the most moves I can make from pos in a direction without bumping into an enemy"""

        # by default, everything is infinite moves away
        smell = self.copy(val=None)
        space_all = 0
        space_cone = 0
        
        # start at pos
        self_todo = []
        smell[head_pos] = board_id
        self_todo.append(head_pos)

        # start all enemies
        enemy_type = CellTypeEnemy(board_id)
        enemy_todo = []
        for pos, val in enumerate(self):
            if enemy_type.matches(val):
                smell[pos] = val
                enemy_todo.append(pos)

        # fill from my starting pos and my enemies
        while self_todo:
            # expand enemies
            next_enemy_todo = []
            for pos in enemy_todo:
                enemy = smell[pos]
                for next_pos, _next_move in self.neighbours(pos):
                    if smell[next_pos] is not None or not enemy_type.can_move(self[next_pos]):
                        continue
                    smell[next_pos] = enemy
                    next_enemy_todo.append(next_pos)
            enemy_todo = next_enemy_todo

            # try myself at the next pos
            next_todo = []
            for pos in self_todo:
                for next_pos, _next_move in self.neighbours(pos):
                    if smell[next_pos] is not None or not enemy_type.can_move(self[next_pos]):
                        continue
                    if self.in_direction(head_pos, next_pos, direction):
                        space_cone += 1
                    elif pos == head_pos:
                        continue
                    space_all += 1
                    smell[next_pos] = board_id
                    next_todo.append(next_pos)
            self_todo = next_todo
            
        return space_all, space_cone, smell
