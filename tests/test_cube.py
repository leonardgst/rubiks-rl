"""Tests du cube logique (phase 1)

Ces décrivent ce que le cube doit faire, pas comment il fait :
Ils n'utilisent que ses méthodes (move, apply, is_solved) et son attribut state.
La façon de tourner les faces (np.rot90, tranches...) n'existe que dans cube.py
"""

import numpy as np
import pytest

from rubiks.cube import Cube

FACES = ["U", "L", "F", "D", "R", "B"]


def numbered_cube() -> Cube:
    """Renvoie un cube dont les 54 cases portent des numéros tous différents.

    Sur un cube résolu, une bande d'une seule couleur reste identique même
    retournée: un bug d'ordre passerait inaperçu. Avec des numéros, chaque case 
    est reconnaissable
    et le moindre déplacement se voit.
    """
    cube = Cube()
    cube.state = np.arange(54).reshape(6, 3, 3)
    return cube


def test_new_cube_is_solved():
    """Un cube neuf est résolu"""
    assert Cube().is_solved()  # Applique la fonction is_solved au nouveau cube créer


@pytest.mark.parametrize("color", range(6))
def test_each_color_appears_nine_times(color):
    """Chaque couleur (0 à 5) apparait exactement 9 fois sur un cube neuf."""
    cube = numbered_cube()
    assert (cube.state == color).sum() == 9


@pytest.mark.parametrize("face", FACES)
def test_quarter_turn_four_times_is_identity(face):
    """
    Vérifie que quatre quarts de tour identiques
    ramènent chaque case à sa position initiale.
    """
    cube = numbered_cube()
    initial_state = cube.state.copy()

    for _ in range(4):
        cube.move(face)

    assert np.array_equal(cube.state, initial_state)


@pytest.mark.parametrize("face", FACES)
@pytest.mark.parametreize(
    ("suffixe", "inverse_suffixe"),
    [("", "'"), ("'", ""), ("2", "2")],
    ids=["X puis X'", "X' puis X", "X2 puis X2"],
)
def test_move_then_inverse_is_identity(face, suffixe, inverse_suffixe):
    """Un mouvement suivi de son inverse ramène chaque
    case à sa place.

    Un demi-tour est son propre inverse : X2 puis X2 ne change rien
    """
    cube = numbered_cube()
    initial_state = cube.state.copy()

    cube.move(face + suffixe)
    cube.move(face + inverse_suffixe)

    assert np.array_equal(cube.state, initial_state)


def test_sexy_move_six_times_is_identity():
    """
    Vérifie qu'appliquer 6 fois la suite de
    mouvement "R U R' U'" ramnène à l'état initial
    """
    cube = numbered_cube()
    initial_state = cube.state.copy()

    for _ in range(6):
        cube.apply("R U R' U'")

    assert np.array_equal(cube.state, initial_state)
