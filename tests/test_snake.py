#! /usr/bin/env python

from genetisnake.snake import Board, Cell, INF

def test_snake():

    board = Board(20, 20)

    assert board.index(0, 0) == 0
    assert board.index(2, 1) == 22
    assert board.index(1, 2) == 41

    assert list(board.neighbours(board.index(0, 0))) == [
        Cell(board.index(1, 0), 'right'),
        Cell(board.index(0, 1), 'down')
        ]

    assert list(board.neighbours(board.index(board.xmax-1, board.ymax-1))) == [
        Cell(board.index(board.xmax-2, board.ymax-1), 'left'),
        Cell(board.index(board.xmax-1, board.ymax-2), 'up')]

    assert Board(2, 3) == [
        None, None,
        None, None,
        None, None,
        ]

    board = Board(2, 3, lambda x, y: (x, y))
    assert board == [
        (0, 0), (1, 0),
        (0, 1), (1, 1),
        (0, 2), (1, 2),
        ]

    board = Board(2, 3, lambda x, y: (x, y))
    assert list(board) == [
        Cell(0, (0, 0)),
        Cell(1, (1, 0)),
        Cell(2, (0, 1)),
        Cell(3, (1, 1)),
        Cell(4, (0, 2)),
        Cell(5, (1, 2)),
        ]


    board = Board.load_strs("123", "456")
    assert board == [
        '1', '2', '3',
        '4', '5', '6'
        ]
    assert board.xmax == 3
    assert board.ymax == 2

    board = Board.load_strs(
        "    # ",
        " A*   ",
        " a  Bb",
        "      ",
        )

    assert board.smell_food() == ([
        3,   2,   1,   2, INF,   4,
        2,   1,   0,   1,   2,   3,
        3, INF,   1,   2, INF, INF,
        4,   3,   2,   3,   4,   5,
        ], 5)

    assert board.smell_enemy() == ([
        6,   5,   4,   3, INF,   3,
        5,   4,   3,   2,   1,   2,
        6, INF,   2,   1,   0, INF,
        5,   4,   3,   2,   1,   2,
        ], 6)

    assert board.smell_self() == ([
        2,   1,   2,   3, INF,   5,
        1,   0,   1,   2,   3,   4,
        2, INF,   2,   3, INF, INF,
        3,   4,   3,   4,   5,   6,
        ], 6)

    space_by_move, space_max, space_map = board.smell_space()
    assert space_map == [
        'left',   'up',    'up',    'up',   None,  'right',
        'left', 'left', 'right', 'right', 'right', 'right',
        'left',   None, 'right', 'right',    None,    None,
        'left', 'left', 'right', 'right', 'right', 'right',
        ]
    assert space_by_move == {
        'left': 6,
        'right': 11,
        'up': 3,
        }
    assert space_max == 11

    assert board.move() == 'right'

    board = Board.load_strs(
        " *  # ",
        " A    ",
        " aBb  ",
        "      ",
        )
    assert board.move() == 'left'
    board.ttl = 1
    assert board.move() == 'up'

    board = Board.load_strs(
        " *  #*",
        "    BA",
        "      ",
        "      ",
        )
    assert board.move() == 'down'

    assert board.dump() == (
        '| *  #*|\n'
        '|    BA|\n'
        '|      |\n'
        '|      |\n'
        )
