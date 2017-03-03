import logging

from . import snake_board

LOG = logging.getLogger(__name__)

class GenetiSnake(object):
    ARITY = 7 # number of arguments my decision function takes
    
    def __init__(self, move_func):
        self.move_func = move_func
        self.games = 0
        self.turns = 0

    def move(self, game, board, self_index):
        board_id = game.snakes[self_index].board_id
        self_head = game.snakes[self_index].body[0]
        self_health = game.snakes[self_index].health
        
        food_smell,   _food_max = board.smell_food(board_id)
        enemy_smell, _enemy_max = board.smell_enemy(board_id)

        LOG.debug("snake.move board_id=%s head=%s health=%s", board_id, board.coords(self_head), self_health)

        max_move = board.moves[0]
        max_score = None

        max_moves = float(board.width + board.height)
        max_space = float(board.width * board.height)

        death_smell, death_prob, death_max = board.death_by_move(board_id)
        if death_smell is None:
            return board.moves[0].name
        
        for move_pos, move in board.neighbours(self_head):
            if not snake_board.CellTypeSnake.can_move(board[move_pos]):
                continue
            death = death_smell[move.name]

            # the number of arguments here is self.ARITY
            score = self.move_func(
                float(self_health) / game.MAX_HEALTH,     # var0 - my health
                float(food_smell[move_pos]) / max_moves,  # var1 - min distance to food
                float(enemy_smell[move_pos]) / max_moves, # var2 - min distance to an enemy
                float(death.space_cone) / max_space,      # var3 - moves I could make in a cone
                float(death.space_all) / max_space,       # var4 - moves I could make anywhere
                death_max[move.name],                     # var5 - prob of killing an enemy
                death_prob[board_id][move.name],          # var6 - prob of dying myself
                )

            LOG.debug("snake.move board_id=%s pos=%s move=%s score=%s"
                      " food=%s enemy=%s",
                      board_id, board.coords(move_pos), move.name, score,
                      food_smell[move_pos], enemy_smell[move_pos])

            if max_score is None or score > max_score:
                max_score = score
                max_move = move
                
        LOG.debug("snake.move self_index=%s best move=%s score=%s", self_index, max_move.name, max_score)
        return max_move.name
        
