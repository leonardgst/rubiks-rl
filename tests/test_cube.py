import rubiks
import numpy as np
import pytest

from rubiks.cube import Cube


def test_new_cube_is_solved():
    """
    Test si un cube neuf est résolu
    """
    cube = Cube() # Crée une instance de la classe Cube
    assert cube.is_solved() # Applique la fonction is_solved au nouveau cube créer


def test_each_color_appears_nine_times():
    """
    Test s'il y a exactement 9 cases de chaque couleur
    """

    # Creation d'un cube pour le test
    cube = Cube()

# Pour chaque couleur du cube, on compte le nombre de fois ou l'étiquette du cube correspond à la couleur
    for color in range(6):
        nb_cases_couleur = (cube.state == color).sum()
        assert nb_cases_couleur == 9
    
    
    
@pytest.mark.parametrize("face", ["U", "R", "F", "D", "L", "B"])
def test_quarter_turn_four_times_is_identity(face):
    """
    Vérifie que quatre quarts de tour identiques ramènent chaque case à sa position initiale.
    """
    cube = Cube()
    cube.state = np.arange(54).reshape(6, 3, 3)
    initial_state = cube.state.copy()

    for _ in range(4):
        cube.move(face)

    assert np.array_equal(cube.state, initial_state)



@pytest.mark.parametrize("face", ['U', 'R', 'F', 'D', 'L', 'B'])
def test_move_then_inverse_is_identity(face):
    """
    Vérifie que si l'on fait 1 mouvement et son inverse, on retombe sur notre état initial
    """
    cube = Cube()
    cube.state = np.arange(54).reshape(6, 3, 3)
    initial_state = cube.state.copy()

    cube.move(face)
    cube.move(f"{face}'")

    assert np.array_equal(cube.state, initial_state)


def test_sexy_move_six_times_is_identity():
    """
    Vérifie qu'appliquer 6 fois la suite de mouvement "R U R' U'" ramnène à l'état initial
    """
    cube = Cube()
    cube.state = np.arange(54).reshape(6, 3, 3)
    initial_state = cube.state.copy()

    for _ in range(6):
        cube.apply("R U R' U'")

    assert np.array_equal(cube.state, initial_state)