import math
import itertools
from random import randint

from genetisnake.board import Board

class SnakePlayer(object):
    def __init__(self, snake, name, cell_type):
        self.snake = snake
        self.name = name
        self.cell_type = cell_type
        self.killed = None
        self.health = 0
        self.body = []
        self.length = 0

    def move(self, game, board):
        return self.snake.move(game, board)

    def __repr__(self):
        if self.killed:
            state = "killed=%s" % (self.killed,)
        else:
            state = "health=%s length=%s" % (self.health, self.length)
        
        return "%s(id=%s name=%s %s)" % \
               (self.__class__.__name__, self.cell_type, self.name, state)

class SnakeBoard(Board):
    MOVES = { 
        "up":    ( 0, -1),
        "right":  ( 1,  0),
        "down":  ( 0,  1),
        "left": (-1,  0),
        }
    
    def move(self, pos, move_name):
        """return a new position after a move"""
        dx, dy = self.MOVES[move_name]
        x, y = self.coords(pos)
        x += dx
        y += dy
        return self.index(x, y)
        
class Game(object):
    MAX_HEALTH      = 20
    INITIAL_LENGTH  = 3
    CELL_TYPE_EMPTY = ' '
    CELL_TYPE_FOOD  = '+'
    CELL_TYPE_WALL  = '#'

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.turn_count = 0
        self.snakes = []
        self.killed = []
        self.food = []
        self.food_count = 4
        self.walls = []
        self.snake_by_cell = {}

    def add_snake(self, snake, name=None):
        assert len(self.snakes) < 26, "Too many snakes! Max 26"
        cell_type = chr(ord('a') + len(self.snakes))
        if name is None:
            name = cell_type
        player = SnakePlayer(snake, name, cell_type)
        self.snake_by_cell[player.cell_type] = player
        self.snakes.append(player)
        return player

    def load(self, rec):
        pass
    
    def start(self):
        self.turn_count = 0

        board = self.render()
        
        # all snakes start around the center
        for i, snake in enumerate(self.snakes):
            t = 2 * math.pi * i / len(self.snakes) 
            r = board.width/4
            x = int(r * math.cos(t)) + board.width/2
            y = int(r * math.sin(t)) + board.height/2
            pos = board.index(x, y)
            snake.body = [pos]
            snake.health = self.MAX_HEALTH
            snake.length = self.INITIAL_LENGTH

        # 4 foods at the center
        x = int(board.width/2)
        y = int(board.height/2)
        for dx, dy in itertools.product([-2, 2], [-2, 2]):
            pos = board.index(x+dx, y+dy)
            assert board[pos] == self.CELL_TYPE_EMPTY, \
                   "Collision at %s. board too small for snakes and food?" % pos
            self.food.append(pos)
        self.food_count = 4

    def render_list(self, board, pos_list, cell):
        for pos in pos_list:
            assert board[pos] == self.CELL_TYPE_EMPTY, \
                   "Render collision at %s: Can't place '%s' over '%s' at (%s)" % \
                   (pos, cell, board[pos], board.coords(pos))
            board[pos] = cell
        
    def render(self):
        board = SnakeBoard(self.width, self.height, self.CELL_TYPE_EMPTY)
        self.render_list(board, self.food, self.CELL_TYPE_FOOD)
        self.render_list(board, self.walls, self.CELL_TYPE_WALL)
        for snake in self.snakes:
            self.render_list(board, snake.body, snake.cell_type)
        return board

    def add_stuff(self, board):
        # add more food and walls
        while len(self.food) < self.food_count:
            pos = randint(1, len(board))-1
            if board[pos] == self.CELL_TYPE_EMPTY:
                self.food.append(pos)
                board[pos] = self.CELL_TYPE_FOOD
        
    def turn(self):
        self.turn_count += 1

        board = self.render()

        # move snakes
        for snake in self.snakes:
            # ask the snake for its next move name
            try: 
                move_name = snake.move(self, board)
            except Exception as e:
                snake.killed = "Failed to move: %s" % e.message
                continue

            # get the new move's pos on the board
            try:
                pos = board.move(snake.body[0], move_name)
            except ValueError:
                snake.killed = "Invalid move: %s" % move_name
                continue
            except IndexError:
                snake.killed = "Moved out of bounds"
                continue

            snake.body.insert(0, pos)
            for pos in snake.body[snake.length:]:
                board[pos] = self.CELL_TYPE_EMPTY
            del snake.body[snake.length:]

        # place the new heads and detect collisions
        for snake in self.snakes:
            pos = snake.body[0]
            cell = board[pos]
            if cell == self.CELL_TYPE_EMPTY:
                snake.health -= 1
                if snake.health <= 0:
                    snake.killed = "Starvation!"
                board[pos] = snake.cell_type
            elif cell == self.CELL_TYPE_FOOD:
                snake.length += 1
                snake.health = self.MAX_HEALTH
                board[pos] = snake.cell_type
                self.food.remove(pos)
            elif cell == self.CELL_TYPE_WALL:
                snake.killed = "Ran into wall!"
            else:
                other = self.snake_by_cell[cell]
                if other == snake:
                    snake.killed = "Ran into self!"
                else:
                    snake.killed = "Ran into %s!" % other.name
                    if pos == other.body[0]:
                        # head to head, both are dead
                        other.killed = "Ran into %s!" % snake.name
        
        for snake in self.snakes:
            if snake.killed:
                self.killed.append(snake)
                self.snakes.remove(snake)

        return board
                
    def run(self):
        board = self.start()
        yield self.render()
        while self.snakes:
            board = self.turn()
            yield board
