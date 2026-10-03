"""Tests de l'affichage dans le terminal (codes ANSI)."""

from rubiks.cube import Cube
from rubiks.render.terminal import RESET, colored, to_ansi


def test_a_sticker_is_a_colored_block():
    """Une case : un code de couleur de fond, deux espaces, puis le retour à la
    normale."""
    sticker = colored(0)

    assert sticker.startswith("\033[48;2;255;255;255m")
    assert sticker.endswith(RESET)


def test_pattern_has_nine_lines_and_54_stickers():
    """Même disposition que print(cube) : 9 lignes, 54 cases."""
    text = to_ansi(Cube())

    assert len(text.splitlines()) == 9
    assert text.count(RESET) == 54


def test_pattern_follows_the_cube():
    """Après un mouvement, l'affichage change (il lit bien cube.state)."""
    cube = Cube()
    before = to_ansi(cube)

    cube.move("R")

    assert to_ansi(cube) != before
