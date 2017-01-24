#! /usr/bin/env python

from genetisnake.snake_board import SnakeBoard

def test_snake_board_smell_space():
    board = SnakeBoard.load(
        "    # ",
        " A*   ",
        "Ca  Bb",
        "c     ",
        )

    assert board.smell_space('A', 7) == ([
        ('C', 2), ('A', 1), ('B', 4), ('B', 3),     None, ('B', 3),
        ('C', 1), ('A', 0), ('A', 1), ('B', 2), ('B', 1), ('B', 2),
        ('C', 0),     None, ('B', 2), ('B', 1), ('B', 0),     None,
            None, ('B', 4), ('B', 3), ('B', 2), ('B', 1), ('B', 2)
        ], 1, 2, 4)

def test_snake_board_smell_game():
    board = SnakeBoard.load(
        "        ",
        "      F ",
        "   G    ",
        "    *   ",
        " A    * ",
        "        ",
        )
    _food_smell, _food_max = board.smell_food('A')
    #assert food_smell == []
    
    _enemy_smell, _enemy_max = board.smell_enemy('A')
    #assert enemy_smell == []

    move_pos = board.index(2, 5)
    _space, _space_self, _space_enemy_min, _space_enemy_max = board.smell_space('A', move_pos)
    #assert space == []
