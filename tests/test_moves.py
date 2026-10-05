"""Tests de la notation des mouvements (rubiks.moves) : que des chaînes."""

import pytest

from rubiks.moves import (
    ALL_MOVES,
    MOVES,
    format_move,
    inverse_move,
    inverse_sequence,
    is_rotation,
    parse_move,
    simplify,
)


def test_there_are_18_face_moves():
    """6 faces x 3 variantes : les 18 actions de l'agent de RL."""
    assert len(MOVES) == 18
    assert len(set(MOVES)) == 18


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("R", ("R", 1)),
        ("R2", ("R", 2)),
        ("R'", ("R", 3)),
        ("M'", ("M", 3)),
        ("x2", ("x", 2)),
    ],
)
def test_parse_move(name, expected):
    """Un mouvement = une lettre + un nombre de quarts de tour horaires."""
    assert parse_move(name) == expected


@pytest.mark.parametrize("name", ["", "X", "R3", "r", "R''", "RU"])
def test_parse_move_rejects_unknown_names(name):
    """Un nom inconnu lève ValueError."""
    with pytest.raises(ValueError):
        parse_move(name)


@pytest.mark.parametrize("name", ALL_MOVES)
def test_format_is_the_inverse_of_parse(name):
    """format_move refabrique le nom à partir de parse_move."""
    assert format_move(*parse_move(name)) == name


def test_format_four_quarter_turns_is_nothing():
    """4 quarts de tour (ou 0) : pas de mouvement du tout."""
    assert format_move("R", 4) is None
    assert format_move("R", 0) is None
    assert format_move("R", 5) == "R"


@pytest.mark.parametrize(
    ("move", "inverse"), [("R", "R'"), ("R'", "R"), ("R2", "R2"), ("y", "y'")]
)
def test_inverse_move(move, inverse):
    """R <-> R', et un demi-tour est son propre inverse."""
    assert inverse_move(move) == inverse


def test_inverse_sequence_reverses_and_inverts():
    """Pour défaire R puis U' puis F2 : F2, puis U, puis R'."""
    assert inverse_sequence(["R", "U'", "F2"]) == ["F2", "U", "R'"]


@pytest.mark.parametrize(
    ("moves", "expected"),
    [
        (["R", "R"], ["R2"]),
        (["R", "R'"], []),
        (["R2", "R"], ["R'"]),
        (["R", "R", "R"], ["R'"]),
        (["R", "U", "U'", "R'"], []),  # les fusions s'enchaînent
        (["R", "L", "R"], ["R", "L", "R"]),  # pas consécutifs : on n'y touche pas
        (["x", "x'", "U"], ["U"]),
        ([], []),
    ],
)
def test_simplify(moves, expected):
    """Les coups consécutifs sur la même face fusionnent."""
    assert simplify(moves) == expected


def test_is_rotation():
    """Seuls x, y, z tournent le cube entier."""
    assert is_rotation("x'")
    assert not is_rotation("R")
    assert not is_rotation("M2")
