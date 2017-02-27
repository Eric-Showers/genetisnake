import pytest
from genetisnake.board import Board, CompassMoves, ManhattanMoves, CellType, INF

def test_board():
    board = Board(3,5)
    board_lines = (
        "123456",
        "abcdef",
        "ABCDEF",
        )
    board = Board.load(*board_lines)
    assert board.width == 6
    assert board.height == 3
    assert str(board) == "123456\nabcdef\nABCDEF\n"
    assert list(enumerate("".join(board_lines))) == list(enumerate(board))
    assert board[board.index(3,1)] == 'd'

def test_neighbours():
    for x, y, compass, manhattan in (
        (0, 0, "S E SE", "S E"),
        (5, 2, "N W NW", "N W"),
        (2, 1, "N S W E NE NW SE SW", "N S W E"),
        ):

        board = Board(6, 3, moves=CompassMoves)
        neighs = board.neighbours(board.index(x, y))
        assert set(compass.split()) == set([move.name for _pos, move in neighs])

        board = Board(6, 3, moves=ManhattanMoves)
        neighs = board.neighbours(board.index(x, y))
        assert set(manhattan.split()) == set([move.name for _pos, move in neighs])

def test_index_error():
    board = Board(3, 5)
    for x, y in (
        (-1, 0),
        (0, -1),
        (board.width, 0),
        (0, board.height)
        ):
        with pytest.raises(IndexError):
            board.index(x, y)
        
class MyCellType(CellType):
    def can_move(self, cell):
        return cell in '* '

def test_smell_food():
    board = Board.load(
        "    # ",
        " A*   ",
        " a  Bb",
        "       ",
        )

    assert board.smell(MyCellType('*')) == ([
        3,    2, 1, 2,  INF,    4,
        4,  INF, 0, 1,    2,    3,
        5,  INF, 1, 2,  INF,  INF,
        4,    3, 2, 3,    4,    5], 5)

def test_smell_enemy():
    board = Board.load(
        "    # ",
        " A*   ",
        "Ca  Bb",
        "c      ",
        )

    assert board.smell(MyCellType('BC')) == ([
           2,    3, 4, 3,  INF,    3,
           1,  INF, 3, 2,    1,    2,
           0,  INF, 2, 1,    0,  INF,
         INF,    4, 3, 2,    1,    2], 4)

def test_smell_space():
    board = Board.load(
        "    # ",
        " A*   ",
        "Ca  Bb",
        "c      ",
        )

    assert board.smell(MyCellType('BC')) == ([
           2,    3, 4, 3,  INF,    3,
           1,  INF, 3, 2,    1,    2,
           0,  INF, 2, 1,    0,  INF,
         INF,    4, 3, 2,    1,    2], 4)
