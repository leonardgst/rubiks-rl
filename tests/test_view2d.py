"""Tests de l'affichage 2D : disposition du patron et textes.

Aucun de ces tests n'ouvre de fenêtre : ils ne testent que des calculs
(sticker_position, scramble_lines et les constantes de view2d). Les touches
du clavier sont testées dans test_game.py.
"""

import pygame
import pytest

from rubiks.render.view2d import (
    COLORS,
    HELP_LINES,
    MARGIN,
    MOVES_PER_LINE,
    STICKER_SIZE,
    TEXT_SIZE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    scramble_lines,
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


# --------------------------------------------------------------------------
# Texte du mélange
# --------------------------------------------------------------------------


def test_no_scramble_gives_no_line():
    """Tant qu'on n'a pas mélangé, aucune ligne de mélange n'est affichée."""
    assert scramble_lines([]) == []


def test_short_scramble_fits_on_one_line():
    """Un mélange court tient sur une ligne, qui commence par « Mélange : »."""
    assert scramble_lines(["R", "U'", "F2"]) == ["Mélange : R U' F2"]


def test_long_scramble_is_split_without_losing_moves():
    """Un long mélange est découpé, sans perdre ni ajouter de coup."""
    moves = ["R", "U"] * 15  # 30 coups

    lines = scramble_lines(moves)

    assert len(lines) == 3  # 12 + 12 + 6 coups
    all_moves = " ".join(lines).removeprefix("Mélange : ").split()
    assert all_moves == moves
    assert all(len(line.split()) <= MOVES_PER_LINE + 2 for line in lines)


@pytest.mark.parametrize("line", HELP_LINES)
def test_help_lines_fit_in_the_window(line):
    """Chaque ligne d'aide tient en largeur dans la fenêtre (rien n'est coupé).

    pygame.font mesure un texte sans ouvrir de fenêtre.
    """
    pygame.font.init()
    font = pygame.font.Font(None, TEXT_SIZE)

    width, _ = font.size(line)

    assert MARGIN + width <= WINDOW_WIDTH - MARGIN
