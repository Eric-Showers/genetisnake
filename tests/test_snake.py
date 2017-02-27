#! /usr/bin/env python

from genetisnake.snake_board import SnakeBoard

def test_snake_board_direction():
    board = SnakeBoard(20, 20)

    def direction_set(p0, p1):
        return set([move.name for move in board.moves if board.in_direction(board.index(*p0), board.index(*p1), move.name)])
    
    assert direction_set((5, 5), (8, 5)) == set(('right',))
    assert direction_set((5, 5), (3, 4)) == set(('left',))
    assert direction_set((5, 5), (6, 6)) == set(('right', 'down'))
    assert direction_set((5, 5), (4, 4)) == set(('up', 'left'))
    assert direction_set((5, 5), (4, 7)) == set(('down',))
    assert direction_set((5, 5), (7, 0)) == set(('up',))
    assert direction_set((5, 5), (1, 3)) == set(('left',))

def test_snake_board_smell_space():
    board = SnakeBoard.load(
        "    # ",
        " A*   ",
        " a   B",
        "Cc   b",
        )

    assert board.smell_space('A', 7, 'left' )[1] == 2
    assert board.smell_space('A', 7, 'up'   )[1] == 3
    assert board.smell_space('A', 7, 'down' )[1] == 0

    actual = board.smell_space('A', 7, 'right')
    assert actual == (7, 5, [
        'C', 'A', 'A', 'A',     None, 'B',
        'C', 'A', 'A', 'A', 'B', 'B',
        'C',     None, 'A', 'B', 'B', 'B',
        'C',     None, 'A', 'B', 'B',     None,
        ]), "unexpected actual board:\n%s" % actual[2].fmt(", ")

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
    assert board.smell_space('A', 35, 'up' )[1] == 3

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
    space_all, space_cone, _space_smell_cone = board.smell_space(board_id, self_head, move_name)
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
    space_all_up, space_cone_up, _space_smell_cone_up = board.smell_space(board_id, self_head, move_name)

    move_name = 'down'
    space_all_down, space_cone_down, _space_smell_cone_down = board.smell_space(board_id, self_head, move_name)

    assert space_cone_down < space_cone_up
    assert space_cone_down + space_all_down > space_cone_up + space_all_up
