#! /usr/bin/env python

from genetisnake.snake import SnakeBoard

def test_snake_board():
    board = SnakeBoard.load(
        "    # ",
        " A*   ",
        "Ca  Bb",
        "c     ",
        )

    assert board.smell_space(7) == ([
        ('C', 2), ('A', 1), ('B', 4), ('B', 3),     None, ('B', 3),
        ('C', 1), ('A', 0), ('A', 1), ('B', 2), ('B', 1), ('B', 2),
        ('C', 0),     None, ('B', 2), ('B', 1), ('B', 0),     None,
            None, ('B', 4), ('B', 3), ('B', 2), ('B', 1), ('B', 2)
        ], 1, 2, 4)
