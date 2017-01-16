from collections import namedtuple

Move = namedtuple('Move', ['name', 'dx', 'dy'], verbose=True)

ManhattanMoves = (
    Move("N",  0, -1),
    Move("E",  1,  0),
    Move("S",  0,  1),
    Move("W", -1,  0),
)

CompassMoves = (
    Move("N",  0, -1),
    Move("NE",  1, -1),
    Move("E",  1,  0),
    Move("SE",  1,  1),
    Move("S",  0,  1),
    Move("SW", -1,  1),
    Move("W", -1,  0),
    Move("NW", -1, -1),
)

class Board(list):
    """A 2-d array of values, stored in a list"""

    def __init__(self, width, height, val=None):
        super(Board, self).__init__()

        self.width = width
        self.height = height
        if not callable(val):
            f = lambda x, y: val
        else:
            f = val

        for y in range(height):
            for x in range(width):
                self.append(f(x, y))

    @classmethod
    def load(cls, *strs):
        """load from an array of arrays"""
        width = len(strs[0]) 
        height = len(strs)
        return Board(width, height, lambda x, y: strs[y][x])

    def index(self, x, y):
        """convert (x,y) coordinates to an integer index in my array"""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError("coordinates (%s, %s) are outside (%s, %s)"
                             % (x, y, self.width, self.height))
        return y * self.width + x

    def coords(self, index):
        """return the x, y coordinates of index"""
        return index % self.width, index / self.width

    def neighbours(self, pos, moves):
        """return all (x, y, move) adjacent to index.  moves is an array of obects that define dx and dy"""
        x, y = self.coords(pos)
        for move in moves:
            x1 = x + move.dx
            y1 = y + move.dy
            if x1 >= 0 and x1 < self.width and y1 >= 0 and y1 < self.height:
                yield self.index(x1, y1), move
    
    def dump(self):
        s = ""
        for i, val in enumerate(self):
            if i>0 and (i % self.width)==0:
                s += "\n"
            s += str(val)
        s += "\n"
        return s
