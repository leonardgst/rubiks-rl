"""Tests des mélanges aléatoires (rubiks.scramble)."""

import pytest

from rubiks.moves import MOVES
from rubiks.scramble import random_moves


@pytest.mark.parametrize("n", [0, 1, 25, 200])
def test_scramble_has_n_valid_moves(n):
    """n coups, tous parmi les 18 mouvements de faces."""
    moves = random_moves(n, seed=0)

    assert len(moves) == n
    assert all(move in MOVES for move in moves)


@pytest.mark.parametrize("seed", range(10))
def test_never_the_same_face_twice_in_a_row(seed):
    """Deux coups de suite sur la même face seraient gaspillés (R R' ou R R2)."""
    moves = random_moves(200, seed=seed)

    for previous, current in zip(moves, moves[1:], strict=False):
        assert previous[0] != current[0]


def test_same_seed_same_scramble():
    """La graine rend le mélange reproductible."""
    assert random_moves(30, seed=5) == random_moves(30, seed=5)
    assert random_moves(30, seed=5) != random_moves(30, seed=6)


def test_all_moves_eventually_appear():
    """Sur un long mélange, les 18 mouvements sortent tous (aucun n'est oublié)."""
    assert set(random_moves(2000, seed=0)) == set(MOVES)
