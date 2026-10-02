"""Tests de la disposition du patron dans la fenêtre 2D.

Aucun de ces tests n'ouvre de fenêtre : ils ne testent que des calculs
(sticker_position et les constantes de view2d).
"""

import pytest

from rubiks.cube import MOVES
from rubiks.render.view2d import (
    COLORS,
    STICKER_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    key_to_move,
    sticker_position,
)

# Les faces, avec les numéros de cube.py
U, R, F, D, L, B = range(6)

ALL_STICKERS = [
    (face, row, col) for face in range(6) for row in range(3) for col in range(3)
]


def test_all_54_positions_are_different():
    """Deux cases ne sont jamais dessinées au même endroit."""
    positions = {sticker_position(*sticker) for sticker in ALL_STICKERS}

    assert len(positions) == 54


@pytest.mark.parametrize("sticker", ALL_STICKERS)
def test_every_sticker_fits_in_the_window(sticker):
    """Chaque case est entièrement dans la fenêtre."""
    x, y = sticker_position(*sticker)

    assert 0 <= x and x + STICKER_SIZE <= WINDOW_WIDTH
    assert 0 <= y and y + STICKER_SIZE <= WINDOW_HEIGHT


def test_there_is_one_color_per_face():
    """6 couleurs, toutes différentes."""
    assert len(COLORS) == 6
    assert len(set(COLORS)) == 6


@pytest.mark.parametrize(
    ("first", "second", "dx", "dy"),
    [
        # U6 U7 U8 touchent F0 F1 F2 (U est vue de dessus, F en bas)
        ((U, 2, 0), (F, 0, 0), 0, 1),
        ((U, 2, 2), (F, 0, 2), 0, 1),
        # F6 F7 F8 touchent D0 D1 D2 (D est vue de dessous, F en haut)
        ((F, 2, 0), (D, 0, 0), 0, 1),
        ((F, 2, 2), (D, 0, 2), 0, 1),
        # Sur la ligne du milieu : L, F, R, B côte à côte, dans cet ordre
        ((L, 0, 2), (F, 0, 0), 1, 0),
        ((F, 0, 2), (R, 0, 0), 1, 0),
        ((R, 0, 2), (B, 0, 0), 1, 0),
        ((L, 2, 2), (F, 2, 0), 1, 0),
    ],
    ids=["U6/F0", "U8/F2", "F6/D0", "F8/D2", "L2/F0", "F2/R0", "R2/B0", "L8/F6"],
)
def test_neighbouring_stickers_touch(first, second, dx, dy):
    """Les jonctions du patron respectent l'orientation décrite dans cube.py.

    (dx, dy) = déplacement, en cases, pour passer de la première case à la
    seconde : (0, 1) = juste en dessous, (1, 0) = juste à droite.
    """
    x1, y1 = sticker_position(*first)
    x2, y2 = sticker_position(*second)

    assert (x2 - x1, y2 - y1) == (dx * STICKER_SIZE, dy * STICKER_SIZE)


# ------------------------------------------------------------------------
# clavier
# ------------------------------------------------------------------------


@pytest.mark.parametrize("face", ["U", "D", "L", "R", "F", "B"])
def test_letter_key_gives_clockwise_move(face):
    """La touche d'une face (en minuscule, comme pygame la nomme) donne son
    quart de tour horaire."""
    assert key_to_move(face.lower(), shift=False) == face


@pytest.mark.parametrize("face", ["U", "D", "L", "R", "F", "B"])
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
