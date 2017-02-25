#! /usr/bin/env python
import datetime
import json
import freezegun
import os
import py

from genetisnake.training import evolve
@freezegun.freeze_time("2012-01-01 00:01:02")
def test_training(tmpdir):
    py.path.local(__file__).dirpath().join("data/winners.json").copy(tmpdir)
    assert(tmpdir.join('winners.json').exists())
    
    tmpdir.chdir()

    now = datetime.datetime.now()
    evolve(
        width=20,
        height=20,
        n_rounds=1,
        n_players=4,
        n_games=1,
        max_gens=2,
        )

    root_dir = tmpdir.join(now.strftime("training-%Y%m%d-%H%M%S"))
    games = json.loads(root_dir.join("games.json").read())
    for game in games:
        _turns = json.loads(root_dir.join(game["path"]).read())
    _turns_svg = root_dir.join("turns.svg").read()
