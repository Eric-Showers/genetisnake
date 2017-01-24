#! /usr/bin/env python

from genetisnake.training import evolve

def test_training():
    return evolve(
        width=20,
        height=20,
        n_rounds=1,
        n_players=4,
        n_games=1,
        max_gens=2,
        )
