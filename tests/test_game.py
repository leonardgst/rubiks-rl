"""Tests des règles du jeu au clavier (rubiks.game), sans aucune fenêtre."""

import numpy as np
import pytest

from rubiks.cube import MOVES, Cube
from rubiks.game import SCRAMBLE_LENGTH, Game, key_to_move

FACES = ["U", "D", "L", "R", "F", "B"]


# --------------------------------------------------------------------------
# Touches -> mouvements
# --------------------------------------------------------------------------


@pytest.mark.parametrize("face", FACES)
def test_letter_key_gives_clockwise_move(face):
    """La touche d'une face (en minuscule, comme pygame la nomme) donne son
    quart de tour horaire."""
    assert key_to_move(face.lower(), shift=False) == face


@pytest.mark.parametrize("face", FACES)
def test_shift_letter_key_gives_inverse_move(face):
    """Avec Maj, la même touche donne le mouvement inverse."""
    assert key_to_move(face.lower(), shift=True) == face + "'"


@pytest.mark.parametrize("shift", [False, True])
@pytest.mark.parametrize(
    "key_name", ["x", "a", "space", "escape", "backspace", "return", "1", ""]
)
def test_other_keys_give_no_move(key_name, shift):
    """Une touche qui n'est pas une face ne donne aucun mouvement."""
    assert key_to_move(key_name, shift) is None


@pytest.mark.parametrize("key_name", list("udlrfb"))
@pytest.mark.parametrize("shift", [False, True])
def test_every_key_move_is_a_valid_move(key_name, shift):
    """Chaque mouvement donné par le clavier fait partie des 18 de cube.py."""
    assert key_to_move(key_name, shift) in MOVES


# --------------------------------------------------------------------------
# Une partie
# --------------------------------------------------------------------------


def test_new_game_is_solved_but_not_won():
    """Au lancement, le cube est neuf : résolu, mais pas gagné."""
    game = Game()

    assert game.cube.is_solved()
    assert not game.is_won()
    assert game.scramble_moves == []


def test_letter_keys_play_moves():
    """Les touches jouent les mêmes mouvements que cube.apply."""
    game = Game()
    reference = Cube()

    for key_name, shift in [("r", False), ("u", False), ("r", True), ("u", True)]:
        game.press(key_name, shift)
    reference.apply("R U R' U'")

    assert np.array_equal(game.cube.state, reference.state)
    assert game.moves_played == 4


def test_unknown_key_does_nothing():
    """Une touche inconnue ne change ni le cube ni le compteur."""
    game = Game()

    game.press("x")

    assert game.cube.is_solved()
    assert game.moves_played == 0


def test_space_scrambles_the_cube():
    """Espace mélange le cube, et retient la suite du mélange."""
    game = Game()

    game.press("space")

    assert len(game.scramble_moves) == SCRAMBLE_LENGTH
    assert not game.cube.is_solved()
    assert not game.is_won()


def test_scramble_starts_from_a_new_cube():
    """Un mélange repart d'un cube neuf : la suite affichée suffit à le refaire."""
    game = Game()
    game.press("r")
    game.press("f")

    game.scramble(seed=3)
    reference = Cube()
    reference.apply(" ".join(game.scramble_moves))

    assert np.array_equal(game.cube.state, reference.state)
    assert game.moves_played == 0


def test_backspace_resets_everything():
    """Retour arrière remet un cube neuf, et oublie le mélange et les coups."""
    game = Game()
    game.press("space")
    game.press("r")

    game.press("backspace")

    assert game.cube.is_solved()
    assert game.scramble_moves == []
    assert game.moves_played == 0
    assert not game.is_won()


@pytest.mark.parametrize("seed", range(5))
def test_solving_after_scramble_wins(seed):
    """Mélanger, puis jouer au clavier la suite inverse : la partie est gagnée.

    C'est le critère de fin de la phase 2, joué par un test.
    """
    game = Game()
    game.scramble(seed=seed)
    assert not game.is_won()

    for move in game.cube.inverse_sequence(game.scramble_moves):
        # « R' » se tape Maj + r ; « R2 » se tape r deux fois
        if move.endswith("2"):
            game.press(move[0].lower())
            game.press(move[0].lower())
        else:
            game.press(move[0].lower(), shift=move.endswith("'"))

    assert game.is_won()


def test_scramble_never_gives_a_solved_cube(monkeypatch):
    """Si les coups du mélange s'annulent tous, on mélange à nouveau.

    On force le premier mélange à être « R R' » (le cube redevient résolu) en
    remplaçant temporairement Cube.scramble (monkeypatch le remet ensuite).
    """
    real_scramble = Cube.scramble
    calls = []

    def fake_scramble(cube, n, seed=None):
        calls.append(seed)
        if len(calls) == 1:
            cube.apply("R R'")
            return ["R", "R'"]
        return real_scramble(cube, n, seed=seed)

    monkeypatch.setattr(Cube, "scramble", fake_scramble)
    game = Game()

    game.scramble(seed=0)

    assert len(calls) == 2  # un second mélange a eu lieu
    assert not game.cube.is_solved()
    assert not game.is_won()
