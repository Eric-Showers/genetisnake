from collections import namedtuple, deque

INF = float('inf')

Move = namedtuple('Move', ['name', 'dx', 'dy'])

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

class DEFAULT():
    pass

def isdefault(v):
    return v is DEFAULT

class CellType(object):
    def __init__(self, values):
        self.values = values
        
    def matches(self, cell):
        return cell in self.values

    def can_move(self, cell):
        return cell in (None, ' ')

class Board(list):
    """A 2-d array of values, stored in a list"""
    neighbours_cache = {}

    def __init__(self, width, height, val=DEFAULT, moves=DEFAULT):
        self.width = width
        self.height = height

        if isdefault(moves):
            moves = ManhattanMoves
        self.moves = moves

        self.neighbours_cache_key = (self.width, self.height, self.moves)

        if isdefault(val):
            val = None

        if callable(val):
            for y in range(height):
                for x in range(width):
                    self.append(val(x, y))
        else:
            super(Board, self).__init__([val]*(width * height))

    @classmethod
    def load(cls, *strs):
        """load from an array of arrays"""
        width = len(strs[0]) 
        height = len(strs)
        return cls(width, height, val=lambda x, y: strs[y][x])

    def put_list(self, pos_list, cell_type):
        for pos in pos_list:
            self[pos] = cell_type

    def index(self, x, y):
        """convert (x,y) coordinates to an integer index in my array"""
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError("coordinates (%s, %s) are outside (%s, %s)"
                             % (x, y, self.width, self.height))
        return y * self.width + x

    def coords(self, index):
        """return the x, y coordinates of index"""
        try:
            return index % self.width, index / self.width
        except TypeError:
            return index

    def neighbours(self, pos):
        """return all (x, y, move) adjacent to index.  moves is an array of obects that define dx and dy"""

        key = self.neighbours_cache_key
        if key not in self.neighbours_cache:
            neighs = []
            neigh_pos = 0
            for y in range(self.height):
                for x in range(self.width):
                    neigh_moves = []
                    for move in self.moves:
                        x1 = x + move.dx
                        y1 = y + move.dy
                        if x1 >= 0 and x1 < self.width and y1 >= 0 and y1 < self.height:
                            neigh_moves.append((self.index(x1, y1), move))
                    neighs.append(neigh_moves)
                    neigh_pos += 1
            self.neighbours_cache[key] = neighs
        return self.neighbours_cache[key][pos]

    def copy(self, val=DEFAULT):
        return self.__class__(self.width, self.height, val, moves=self.moves)

    def remap_none(self, val=INF):
        for i, x in enumerate(self):
            if x is None:
                self[i] = val
        
    def smell(self, cell_type):
        """make a board where the values are the least number of moves from
        each cell to the nearest cell_type"""

        # by default, everything is infinite moves away
        smell = self.copy(val=None)

        # start with all cells in cell_type
        todo = deque()
        for pos, val in enumerate(self):
            if cell_type.matches(val):
                todo.append((pos, 0))

        # keep adding neighbours at increasing distance
        max_dist = 0
        while todo:
            pos, dist = todo.popleft()
            
            # stop if this cell is already hit or is opaque
            if smell[pos] is not None:
                continue

            smell[pos] = dist
            if dist > max_dist:
                max_dist = dist
            for next_pos, _next_move in self.neighbours(pos):
                if smell[next_pos] is None and cell_type.can_move(self[next_pos]):
                    todo.append((next_pos, dist+1))

        smell.remap_none()
        return smell, max_dist

    def __str__(self):
        return self.fmt()
        
    def fmt(self, sep=""):
        width = max(len(str(cell)) for cell in self)
        s = ""
        for i, val in enumerate(self):
            if i>0 and (i % self.width)==0:
                s += "\n"
            s += '{0: >{1}}{2}'.format(val, width, sep)
        s += "\n"
        return s
