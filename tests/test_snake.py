#! /usr/bin/env python
import re
import logging

from genetisnake.snake_board import SnakeBoard

LOG = logging.getLogger(__name__)

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

def nospace(s):
    return re.sub(r'(?m)\s+', '', s)

def assert_board(board, expect):
    actual = board.fmt(", ")
    assert nospace(actual) == nospace(expect), "actual:\n%s\nexpect:\n%s\n" % (actual, expect)

def test_smell_death():
    board = SnakeBoard.load(
        "    # ",
        " A*   ",
        " a   B",
        "Cc   b",
        )
    
    death_smell, death_prob, death_max = board.death_by_move('A')

    assert death_max['left'] == 1.0 - 0.5555555555555556

    smell = death_smell['left']
    assert_board(smell.board, """
A@2:1.000, A@3:1.000, A@4:1.000, B@4:0.042,      None, B@2:0.125, 
A@1:1.000, A@0:1.000, B@4:0.056, B@3:0.125, B@2:0.250, B@1:0.500, 
C@1:1.000,      None, B@3:0.042, B@2:0.125, B@1:0.500, B@0:1.000, 
C@0:1.000,      None, B@4:0.042, B@3:0.083, B@2:0.125,      None,
""")
    assert smell.space_all == 4
    assert smell.space_cone == 2
    assert smell.death_prob == {
        'A': [0, 0, 0, 0, 0, 0.36574074074074076],
        'B': [0, 0, 0, 0.0625, 0.06828703703703703, 0.11593364197530864],
        'C': [0, 0, 1.0, 1.0, 1.0, 1.0],
        }

    smell = death_smell['right']
    assert_board(smell.board, """
C@3:1.000, A@3:0.111, A@2:0.333, A@3:0.222,      None, B@2:0.125, 
C@2:1.000, A@0:1.000, A@1:1.000, A@2:0.333, B@2:0.250, B@1:0.500, 
C@1:1.000,      None, A@2:0.333, B@2:0.125, B@1:0.500, B@0:1.000, 
C@0:1.000,      None, A@3:0.111, B@3:0.250, B@2:0.125,      None, 
""")
    assert smell.space_all == 7
    assert smell.space_cone == 5
    assert smell.death_prob == {
        'A': [0, 0, 0, 0.17013888888888887, 0.35069444444444436],
        'B': [0, 0, 0, 0.21788194444444442, 0.247974537037037],
        'C': [0, 0, 0, 0, 0.5555555555555556],
        }
    
    smell = death_smell['up']
    assert_board(smell.board, """
A@2:0.500, A@1:1.000, A@2:0.500, A@3:0.250,      None, B@2:0.125, 
C@2:1.000, A@0:1.000, A@3:0.250, B@3:0.125, B@2:0.250, B@1:0.500, 
C@1:1.000,      None, B@3:0.042, B@2:0.125, B@1:0.500, B@0:1.000, 
C@0:1.000,      None, B@4:0.125, B@3:0.083, B@2:0.125,      None, 
""")
    assert smell.space_all == 5
    assert smell.space_cone == 3
    assert smell.death_prob == {
        'A': [0, 0, 0, 0.5, 0.6336805555555556, 0.6336805555555556],
        'B': [0, 0, 0, 0.0625, 0.09678819444444445, 0.10460069444444445],
        'C': [0, 0, 0, 0.75, 0.75, 0.75],
        }

    space_all, space_cone, board, death_prob = board.smell_death('A', 'down')
    assert_board(board, """
C@3:1.000, C@4:1.000, B@5:1.097, B@4:0.042,      None, B@2:0.125, 
C@2:1.000, A@0:1.000, B@4:0.056, B@3:0.125, B@2:0.250, B@1:0.500, 
C@1:1.000,      None, B@3:0.042, B@2:0.125, B@1:0.500, B@0:1.000, 
C@0:1.000,      None, B@4:0.042, B@3:0.083, B@2:0.125,      None, 
""")
    assert space_all == 0
    assert space_cone == 0
    assert death_prob == {
        'A': [0, 1, 1, 1, 1, 1, 1],
        'B': [0, 0, 0, 0.0625, 0.06828703703703703, 0.07577803497942387, 0.4770769032921811],
        'C': [0, 0, 0, 0, 0, 1.0486111111111112, 1.0486111111111112],
        }

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

def test_smell_death_2():
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
        "a   baaaaa    +     ", 
        "aa  Baaaaa          ", 
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

    smell_right = board.smell_death('A', 'right')
    smell_down = board.smell_death('A', 'down')
    assert smell_right.death_prob['B'][4] > 2 * smell_down.death_prob['B'][4]
