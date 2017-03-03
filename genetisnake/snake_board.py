import string
from collections import namedtuple
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

    def smell_death(self, self_id, direction):
        """space_all, space_cone, space_map, death_prob = smell_death(self, head_pos, move_name)

        If I moved in direction, how much space is there, and what's the likelihood of me or an enemy dying
        try to figure out 
        
        find the most moves I can make from pos in a direction without bumping into an enemy"""

        smell = self.copy(val=None)
        space_all = 0
        space_cone = 0
        head_pos = None
        turn = 0
        
        # find myself and all enemies
        snake_ids = []
        snake_todos = {}
        for pos, snake_id in enumerate(self):
            if CellTypeSnake.matches(snake_id):
                assert snake_id not in snake_todos, "snake_id=%s appears more than once on the board!" % snake_id
                todo = PosProb(pos, 1, snake_id, turn)
                snake_todos[snake_id] = [todo]
                smell[pos] = todo
                if snake_id == self_id:
                    head_pos = pos
                else:
                    snake_ids.append(snake_id)
        assert head_pos is not None, "couldn't find self_id=%s in self:\n%s\n" % (self_id, str(self))
        snake_ids.append(self_id)

        # record the probability of each snake's death
        death_prob = {snake_id: [0] for snake_id in snake_ids}
        
        # pylint: disable=too-many-nested-blocks
        # fill from my starting pos and my enemies
        while snake_todos:
            turn += 1
            
            for snake_id in snake_ids:
                death_prob[snake_id].append(death_prob[snake_id][turn-1])
                assert len(death_prob[snake_id]) == turn+1
                
                if snake_id not in snake_todos:
                    continue
                
                # expand snake
                next_todos = []
                for todo in snake_todos[snake_id]:
                    has_move = False
                    for next_pos, _next_move in self.neighbours(todo.pos):
                        if not CellTypeSnake.can_move(self[next_pos]):
                            continue

                        next_todo = smell[next_pos]
                        if next_todo and next_todo.turn != turn:
                            # can't move on to another snake
                            continue

                        if next_todo is None:
                            if snake_id == self_id:
                                # count the total number of moves following direction
                                if self.in_direction(head_pos, next_pos, direction):
                                    space_cone += 1
                                elif todo.pos == head_pos:
                                    # if I'm at the head, I can only move in direction
                                    continue
                                space_all += 1

                            next_todo = PosProb(next_pos, 0, snake_id, turn)
                            next_todos.append(next_todo)
                            smell[next_pos] = next_todo
                            has_move = True
                            
                        if next_todo.turn == turn:
                            next_todo.prob += todo.prob

                    if not has_move:
                        # this move is terminal. The probability of death is:
                        # 1. the probablility of getting here * the probability of dying
                        # 2. dying = sum(probability neighbour is occupied) / sum(neighbours)
                        p = 0.0
                        n = 0
                        for next_pos, _next_move in self.neighbours(todo.pos):
                            next_todo = smell[next_pos]
                            if not next_todo or not CellTypeSnake.can_move(self[next_pos]):
                                continue
                            p += next_todo.prob
                            n += 1
                        if n == 0:
                            p = 1.0
                        else:
                            p /= n
                        death_prob[snake_id][turn] += todo.prob * p
                        
                        
                            

                if not next_todos:
                    del snake_todos[snake_id]
                else:
                    snake_todos[snake_id] = PosProb.normalize(next_todos)
            
        return DeathSmell(space_all, space_cone, smell, death_prob)

    def death_by_move(self, board_id, head_pos=None):
        if head_pos is None:
            for pos, val in enumerate(self):
                if val == board_id:
                    head_pos = pos
                    break
        assert head_pos is not None, "Couldn't find board_id=%s in board:\n%s\n" % (board_id, self)
            
        # find out which direction causes the most death
        death_smell = {}
        for move_pos, move in self.neighbours(head_pos):
            if CellTypeSnake.can_move(self[move_pos]):
                death_smell[move.name] = self.smell_death(board_id, move.name)

        if not death_smell:
            return None, None, None

        # look at most 4 turns in the future
        lookahead = min(4, len(death_smell.values()[0].death_prob.values()[0])-1)

        # find the maximum difference, per enemy, between their least probability of death and the prob of death at this move
        # probability of death for each snake and move, lookahead turns in the future
        death_prob = {}
        for snake_id in death_smell.values()[0].death_prob.keys():
            death_prob[snake_id] = {}
            for move_name in death_smell:
                death_prob[snake_id][move_name] = death_smell[move_name].death_prob[snake_id][lookahead]

        # min probability of death for each snake
        death_min = {}
        for snake_id, probs in death_prob.items():
            death_min[snake_id] = min(probs.values())

        # max increase in probability of death for all enemies by move
        death_max = {}
        for move_name in death_smell:
            death_max[move_name] = max(death_smell[move_name].death_prob[snake_id][lookahead] - death_min[snake_id]
                                       for snake_id in death_min.keys()
                                        if snake_id != board_id)
            
        return death_smell, death_prob, death_max
        

DeathSmell = namedtuple('DeathSmell', 'space_all space_cone board death_prob'.split())

class PosProb(object):
    def __init__(self, pos, prob, snake_id, turn):
        self.pos = pos
        self.prob = prob
        self.snake_id = snake_id
        self.turn = turn
        
    def __str__(self):
        return "%s@%d:%.3f" % (self.snake_id, self.turn, self.prob)

    @staticmethod
    def normalize(probs):
        for prob in probs:
            prob.prob = float(prob.prob)/len(probs)
        return probs
