import rubiks
import numpy as np


from rubiks.cube import Cube

def test_import_rubiks():
    assert hasattr(rubiks, "main")

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
    
    
    

def test_quarter_turn_four_times_is_identity():


def test_move_then_inverse_is_identity():


def test_sexy_move_six_times_is_identity():
