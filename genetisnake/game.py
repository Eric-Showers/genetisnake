import math
import itertools
from random import randint
import logging

from . import snake_board

LOG = logging.getLogger(__name__)

class SnakePlayer(object):
    def __init__(self, game, snake, name, board_id):
        self.game = game
        self.snake = snake
        self.name = name
        self.board_id = board_id
        self.killed = None
        self.health = 0
        self.body = []
        self.length = 0
        self.last_move = None
        self.turns = 0

    def move(self, game, board, index):
        return self.snake.move(game, board, index)

    def __str__(self):
        if self.killed:
            state = "turns=%s last_move=%s killed=%s" % (self.turns, self.last_move, self.killed,)
        else:
            state = "health=%s length=%s" % (self.health, self.length)
        
        return "%s(board_id=%s name=%s %s)" % \
               (self.__class__.__name__, self.board_id, self.name, state)

    def to_dict(self):
        return dict(
            name = self.name,
            board_id = self.board_id,
            killed = self.killed,
            body = [self.coords(pos) for pos in self.body],
            turns = self.turns,
            health = self.health,
            )

class Game(object):
    MAX_HEALTH      = 100
    INITIAL_LENGTH  = 3

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
        self.board = None

    def coords(self, index):
        return (index % self.width, index / self.width)
        
    def add_snake(self, snake, name=None):
        snake_index = len(self.snakes)
        board_id = snake_board.CELL_TYPE_SNAKE[snake_index]
        if name is None:
            name = board_id
        player = SnakePlayer(self, snake, name, board_id)
        self.snake_by_cell[player.board_id] = player
        self.snakes.append(player)
        return player

    def render(self):
        self.board = snake_board.SnakeBoard(self.width, self.height)
        self.board.put_list(self.food, snake_board.CELL_TYPE_FOOD)
        self.board.put_list(self.walls, snake_board.CELL_TYPE_WALL)
        for snake in self.snakes:
            self.board.put_list(snake.body, snake.board_id.lower())
            if snake.body:
                self.board[snake.body[0]] = snake.board_id
        return self.board

    def start(self):
        self.turn_count = 0

        self.render()
        
        # all snakes start around the center
        for i, snake in enumerate(self.snakes):
            t = 2 * math.pi * i / len(self.snakes) 
            r = self.board.width/4
            x = int(r * math.cos(t)) + self.board.width/2
            y = int(r * math.sin(t)) + self.board.height/2
            pos = self.board.index(x, y)
            snake.body = [pos]
            snake.health = self.MAX_HEALTH
            snake.length = self.INITIAL_LENGTH

        # 4 foods at the center
        x = int(self.board.width/2)
        y = int(self.board.height/2)
        for dx, dy in itertools.product([-2, 2], [-2, 2]):
            pos = self.board.index(x+dx, y+dy)
            assert self.board[pos] == snake_board.CELL_TYPE_EMPTY, \
                   "Collision at %s. board too small for snakes and food?" % pos
            self.food.append(pos)
        self.food_count = 4

        self.render()
        return self.board

    def add_stuff(self):
        # add more food and walls
        while len(self.food) < self.food_count:
            pos = randint(1, len(self.board))-1
            if self.board[pos] == snake_board.CELL_TYPE_EMPTY:
                self.food.append(pos)
                self.board[pos] = snake_board.CELL_TYPE_FOOD
        
    def turn(self):
        self.turn_count += 1

        self.board = self.render()

        LOG.debug("Game.turn: turn_count=%s board=\n%s\n", self.turn_count, self.board)

        killed = set()
        def kill(snake, reason):
            if not snake.killed:
                snake.killed = reason
                snake.turns = self.turn_count
                LOG.debug("game.turn killed snake %s", snake)
                self.killed.append(snake)
                killed.add(snake)
        
        # query all snakes for their move
        for i, snake in enumerate(self.snakes):
            try: 
                # ask the snake for its next move name
                snake.last_move = snake.move(self, self.board, i)
            except Exception as e:
                kill(snake, "Failed to move: %s" % e.message)
                continue

            # get the new move's pos on the board
            try:
                pos = self.board.move(snake.body[0], snake.last_move)
            except ValueError:
                kill(snake, "Invalid move: %s" % snake.last_move)
                continue
            except IndexError:
                kill(snake, "Moved out of bounds")
                continue

        # move snakes
        for i, snake in enumerate(self.snakes):
            if snake.killed:
                continue
            pos = self.board.move(snake.body[0], snake.last_move)
            snake.body.insert(0, pos)
            for pos in snake.body[snake.length:]:
                self.board[pos] = snake_board.CELL_TYPE_EMPTY
            del snake.body[snake.length:]

        # place the new heads and detect collisions
        for snake in self.snakes:
            if snake.killed:
                continue
            pos = snake.body[0]
            cell = self.board[pos]
            if cell == snake_board.CELL_TYPE_EMPTY:
                snake.health -= 1
                if snake.health <= 0:
                    kill(snake, "Starvation!")
                self.board[pos] = snake.board_id
            elif cell == snake_board.CELL_TYPE_FOOD:
                snake.length += 1
                snake.health = self.MAX_HEALTH
                self.board[pos] = snake.board_id
                self.food.remove(pos)
            elif cell == snake_board.CELL_TYPE_WALL:
                kill(snake, "Ran into wall!")
            else:
                other = self.snake_by_cell[cell.upper()]
                if other == snake:
                    kill(snake, "Ran into self!")
                else:
                    kill(snake, "Ran into %s!" % other.name)
                    if pos == other.body[0]:
                        # head to head, both are dead
                        kill(other, "Ran into %s!" % snake.name)

        # remove killed snakes and maybe rerender board
        if killed:
            self.snakes = [ snake for snake in self.snakes if not snake.killed ]

        self.board = self.render()

        # add more walls and food
        self.add_stuff()
        
        return self.board

    def to_dict(self):
        return dict(
            width = self.width,
            height = self.height,
            turn = self.turn_count,
            snakes = [ snake.to_dict() for snake in self.snakes ],
            killed = [ snake.to_dict() for snake in self.killed ],
            food = [ self.coords(pos) for pos in self.food ],
            walls = [ self.coords(pos) for pos in self.walls ],
            )

    def __str__(self):
        board_lines = str(self.board).split('\n')
        snake_lines = [ str(snake) for snake in itertools.chain(self.snakes, self.killed) ]
        fmt = '|{0:<%d}| {1}' % (self.width,)
        return "\n".join(fmt.format(*l)
                         for l in itertools.izip_longest(board_lines, snake_lines, fillvalue=''))
        
    def run(self):
        yield self.start()
        while self.snakes:
            yield self.turn()
