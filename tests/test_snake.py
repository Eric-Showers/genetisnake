#! /usr/bin/env python

from genetisnake.snake_board import SnakeBoard

def test_snake_board_direction():
    board = SnakeBoard(20, 20)
    assert board.move_direction(board.index(5, 5), board.index(8, 5)) == set(('right',))
    assert board.move_direction(board.index(5, 5), board.index(3, 4)) == set(('left',))
    assert board.move_direction(board.index(5, 5), board.index(6, 6)) == set(('right', 'down'))
    assert board.move_direction(board.index(5, 5), board.index(4, 4)) == set(('up', 'left'))
    assert board.move_direction(board.index(5, 5), board.index(4, 7)) == set(('down',))
    assert board.move_direction(board.index(5, 5), board.index(7, 0)) == set(('up',))
    assert board.move_direction(board.index(5, 5), board.index(1, 3)) == set(('left',))

def test_snake_board_smell_space():
    board = SnakeBoard.load(
        "    # ",
        " A*   ",
        " a   B",
        "Cc   b",
        )

    assert board.smell_space_cone('A', 7, 'left' )[0] == 2
    assert board.smell_space_cone('A', 7, 'up'   )[0] == 3
    assert board.smell_space_cone('A', 7, 'down' )[0] == 0

    actual = board.smell_space_cone('A', 7, 'right')
    assert actual == (5, [
        ('C', 3), ('C', 4), ('A', 2), ('A', 3),     None, ('B', 2),
        ('C', 2), ('A', 0), ('A', 1), ('A', 2), ('B', 2), ('B', 1),
        ('C', 1),     None, ('A', 2), ('B', 2), ('B', 1), ('B', 0),
        ('C', 0),     None, ('B', 4), ('B', 3), ('B', 2),     None,
        ]), "unexpected board:\n%s" % actual[1].fmt(", ")

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

def test_smell_space():
    board = SnakeBoard.load(
        "                    ", 
        "               A    ", 
        "               a    ", 
        "               a    ", 
        "                    ", 
        "                    ", 
        "                    ", 
        "                    ", 
        "         bbbB       ", 
        "                    ", 
        "                    ", 
        "                +   ", 
        "        +   +       ", 
        "                    ", 
        "     +              ", 
        "                    ", 
        "                    ", 
        "                    ", 
        "                    ", 
        "                    ", 
        )
    assert board.smell_space_cone('A', 35, 'up' )[0] == 3

def test_smell_space_2():
    board = SnakeBoard.load(
        "                    ", 
        "aaaaaaaaa           ", 
        "a       a           ", 
        "a       a           ", 
        "a       a           ", 
        "a       a           ", 
        "a    aaaa           ", 
        "a    aaa            ", 
        "a    aaa            ", 
        "a    aaaaa    +     ", 
        "aa   aaaaa          ", 
        " aa  aaaaaa         ", 
        "  aa aaa            ", 
        "   A aaaa           ", 
        "      aaaa          ", 
        "       aaa          ", 
        "                    ", 
        "                    ", 
        "   +     +          ", 
        "                 +  ", 
        )
    board_id = 'A'
    self_head = board.index(3,13)
    move_name = 'right'
    move_pos = board.index(4,13)
    space_cone, _space_smell_cone = board.smell_space_cone(board_id, self_head, move_name)
    space_all, _space_smell_all = board.smell_space_all(board_id, move_pos)
    assert space_all >= space_cone

def test_smell_space_3():
    board = SnakeBoard.load(
        "                    ", 
        "aaaaaaaaa           ", 
        "a       a           ", 
        "a       a           ", 
        "a       a           ", 
        "a       a           ", 
        "a    aaaa           ", 
        "a    aaa            ", 
        "a    aaa            ", 
        "a    aaaaa    +     ", 
        "aa   aaaaa          ", 
        " aa  aaaaaa         ", 
        "  aa aaa            ", 
        "   aAaaaa           ", 
        "      aaaa          ", 
        "       aaa          ", 
        "                    ", 
        "                    ", 
        "   +     +          ", 
        "                 +  ", 
        )
    board_id = 'A'
    self_head = board.index(4,13)
    
    move_name = 'up'
    move_pos = board.index(4,12)
    space_cone_up, _space_smell_cone_up = board.smell_space_cone(board_id, self_head, move_name)
    space_all_up, _space_smell_all_up = board.smell_space_all(board_id, move_pos)

    move_name = 'down'
    move_pos = board.index(4,14)
    space_cone_down, _space_smell_cone_down = board.smell_space_cone(board_id, self_head, move_name)
    space_all_down, _space_smell_all_down = board.smell_space_all(board_id, move_pos)

    assert space_cone_down < space_cone_up
    assert space_cone_down + space_all_down > space_cone_up + space_all_up

