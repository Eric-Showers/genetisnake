import pytest
from battlesnake.board import Board, CompassMoves, ManhattanMoves

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
    assert board.dump() == "123456\nabcdef\nABCDEF\n"
    assert list(enumerate("".join(board_lines))) == list(enumerate(board))

    assert board[board.index(3,1)] == 'd'

    for x, y, compass, manhattan in (
        (0, 0, "S E SE", "S E"),
        (5, 2, "N W NW", "N W"),
        (2, 1, "N S W E NE NW SE SW", "N S W E"),
        ):
        assert set(compass.split()) == set([move.name for _pos, move in board.neighbours(board.index(x, y), CompassMoves)])
        assert set(manhattan.split()) == set([move.name for _pos, move in board.neighbours(board.index(x, y), ManhattanMoves)])

    for x, y in (
        (-1, 0),
        (0, -1),
        (board.width, 0),
        (0, board.height)
        ):
        with pytest.raises(IndexError):
            board.neighbours(board.index(x, y), CompassMoves)
        with pytest.raises(IndexError):
            board.index(board.index(x, y))
        
