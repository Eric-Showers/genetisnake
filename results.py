#! /usr/bin/env python
import fileinput
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

re_gen   = re.compile(r'^generation=(?P<gen>\d+) done')
re_turns = re.compile(r'^turns=(?P<turns>\d+) func=([-\d.]+) (?P<func>.*)')
re_start = re.compile(r'(?P<game>generation=(?P<gen>\d+) round=\d+ game=\d+)')
re_game_turn = re.compile(r'^turn=(?P<turn>\d+).*')

gen = None

turns = []
max_turns = None
max_turns_func = None
max_turns_gen = None

game_turn = None
max_game_turn = None
max_game_turn_game = None

for line in fileinput.input():
    m = re_gen.match(line)
    if m:
        gen = m.group('gen')
        continue
    
    m = re_turns.match(line)
    if m:
        t = int(m.group('turns'))
        turns.append(t)
        if max_turns is None or t > max_turns:
            max_turns = t
            max_turns_gen = gen
            max_turns_func = m.group('func')
        continue

    m = re_start.match(line)
    if m:
        game = m.group("game")
        if max_game_turn is None or game_turn > max_game_turn:
            max_game_turn = game_turn
            max_game_turn_game = game
        game_turn = 0
        continue

    m = re_game_turn.match(line)
    if m:
        game_turn = int(m.group("turn"))
        
        

plt.plot(turns)
plt.ylabel('Max Turns')
plt.xlabel('Generations')
plt.savefig('turns.svg')

print "Generations: %s" % gen
print "Longest game: %s %s" % (max_game_turn, max_game_turn_game)
print 'Max turns: %s at gen=%s func=%s' % (max_turns, max_turns_gen, max_turns_func)
