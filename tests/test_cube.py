"""Tests du cube logique (phase 1)

Ces décrivent ce que le cube doit faire, pas comment il fait :
Ils n'utilisent que ses méthodes (move, apply, is_solved) et son attribut state.
La façon de tourner les faces (np.rot90, tranches...) n'existe que dans cube.py
"""

import numpy as np
import pytest

from rubiks.cube import Cube

FACES = ["U", "R", "F", "D", "L", "B"]


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
    cube = Cube()
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
@pytest.mark.parametrize(
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


@pytest.mark.parametrize("face", FACES)
def test_copy_is_independent(face):
    """Une copie est identique à l'originale
    mais indépendante de lui.
    """
    cube = numbered_cube()
    cube_copy = cube.copy()

    assert np.array_equal(cube.state, cube_copy.state)

    cube_copy.state[0, 0, 0] == 99

    assert cube.state[0, 0, 0] == 0


def test_str_of_solved_cube():
    """Le patron d'un cube neuf affiche chaque face avec la lettre de sa couleur."""
    expected = "\n".join(
        [
            "       W W W",
            "       W W W",
            "       W W W",
            "O O O  G G G  R R R  B B B",
            "O O O  G G G  R R R  B B B",
            "O O O  G G G  R R R  B B B",
            "       Y Y Y",
            "       Y Y Y",
            "       Y Y Y",
        ]
    )
    assert str(Cube()) == expected


def test_quarter_turn_U_from_solved_cube():
    """Test de référence : on part d'un cube résolu (U=W ; F=G) et on fait 'U'
    (quart de tour horaire, vu de dessus). Alors :
        - la ligne du haut de F est rouge
        - la ligne du haut de L est verte
        - la ligne du haut de B est orange
        - la ligne du haut de R est bleue
    et tout le reste du cube est inchangé.
    """
    cube = Cube()
    cube.move("U")

    # Les 4 lignes du haut ont tourné d'une face à la suivante
    assert (cube.state[1, 0] == 5).sum() == 3  # R : bleu
    assert (cube.state[2, 0] == 1).sum() == 3  # F : rouge
    assert (cube.state[4, 0] == 2).sum() == 3  # L : vert
    assert (cube.state[5, 0] == 4).sum() == 3  # B : orange

    # Ce qui ne doit pas bouger : le milieu et le bas des 4 faces, et toute la face D
    assert np.all(cube.state[1, 1:] == 1)
    assert np.all(cube.state[2, 1:] == 2)
    assert np.all(cube.state[4, 1:] == 4)
    assert np.all(cube.state[5, 1:] == 5)
    assert np.all(cube.state[3] == 3)


def test_U_turns_the_U_face_clockwise():
    """Test de référence : après 'R', la colonne de droite de U est verte.
    Après 'U' (quart de tour horaire, vu de dessus), cette bande verte est
    devenue la ligne du bas de U, et le reste de U est blanc.
    """
    cube = Cube()
    cube.move("R")
    cube.move("U")

    expected_face_U = np.array(
        [
            [0, 0, 0],
            [0, 0, 0],
            [2, 2, 2],
        ]
    )
    assert np.array_equal(cube.state[0], expected_face_U)
