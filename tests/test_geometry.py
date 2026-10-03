"""Tests de la géométrie 3D (rubiks.geometry), sans aucune fenêtre.

Le grand test (``test_move_rotates_the_layer_in_space``) relie la phase 3 à la
phase 1 : il vérifie que les mouvements écrits à la main dans cube.py font
exactement ce que fait une vraie rotation dans l'espace.
"""

import numpy as np
import pytest
from rubiks.cube import PERMUTATIONS, Cube
from rubiks.geometry import (
    CUBIES,
    FACE_NORMALS,
    STICKERS,
    X,
    Y,
    Z,
    best_direction,
    is_in_layer,
    move_for_drag,
    move_rotation,
    permutation,
    rotate,
    rotation_matrix,
    sticker_index,
    sticker_location,
    tangent_directions,
)
from rubiks.moves import ALL_MOVES, MOVES

U, R, F, D, L, B = range(6)


# --------------------------------------------------------------------------
# Où sont les cases ?
# --------------------------------------------------------------------------


def test_there_are_26_cubies():
    """27 positions, moins le centre invisible."""
    assert len(CUBIES) == 26
    assert (0, 0, 0) not in CUBIES


def test_all_54_locations_are_different():
    """Deux cases ne sont jamais au même endroit, du même côté."""
    locations = {sticker_location(*sticker) for sticker in STICKERS}

    assert len(locations) == 54


@pytest.mark.parametrize("sticker", STICKERS)
def test_sticker_is_on_the_outside_of_its_face(sticker):
    """Chaque case est sur la face de sa normale : F a z = 1, L a x = -1..."""
    cubie, normal = sticker_location(*sticker)
    axis = [abs(c) for c in normal].index(1)

    assert normal == FACE_NORMALS[sticker[0]]
    assert sum(abs(c) for c in normal) == 1  # une seule coordonnée non nulle
    assert cubie[axis] == normal[axis]  # le cubie touche bien cette face


def test_corner_carries_three_stickers():
    """Le coin haut-droite-devant porte F2, U8 et R0 (voir cube.py)."""
    corner = (1, 1, 1)

    assert sticker_location(F, 0, 2) == (corner, (0, 0, 1))
    assert sticker_location(U, 2, 2) == (corner, (0, 1, 0))
    assert sticker_location(R, 0, 0) == (corner, (1, 0, 0))


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ((U, 2, 0), (F, 0, 0)),  # U6 et F0 : même cubie (bord haut gauche de F)
        ((F, 2, 1), (D, 0, 1)),  # F7 et D1
        ((L, 0, 2), (F, 0, 0)),  # L2 et F0
        ((R, 1, 2), (B, 1, 0)),  # R5 et B3
        ((B, 0, 2), (L, 0, 0)),  # B2 et L0
        ((D, 2, 2), (R, 2, 2)),  # D8 et R8
    ],
)
def test_neighbouring_stickers_share_a_cubie(first, second):
    """Les jonctions du patron de cube.py tombent sur le même cubie."""
    assert sticker_location(*first)[0] == sticker_location(*second)[0]


def test_sticker_index_is_the_flat_index():
    """sticker_index retrouve l'indice de cube.state mis à plat."""
    for index, sticker in enumerate(STICKERS):
        assert sticker_index(*sticker_location(*sticker)) == index


# --------------------------------------------------------------------------
# Tourner un point
# --------------------------------------------------------------------------


@pytest.mark.parametrize("axis", [X, Y, Z])
def test_four_quarter_turns_come_back(axis):
    """4 quarts de tour ramènent le point à sa place."""
    point = (1, -1, 1)

    assert rotate(point, axis, 4) == point
    assert rotate(rotate(point, axis, 1), axis, -1) == point


@pytest.mark.parametrize("axis", [X, Y, Z])
def test_point_on_the_axis_does_not_move(axis):
    """Un point sur l'axe de rotation ne bouge pas."""
    point = [0, 0, 0]
    point[axis] = 1

    assert rotate(tuple(point), axis, 1) == tuple(point)


@pytest.mark.parametrize(
    ("vector", "axis", "expected"),
    [((0, 1, 0), X, (0, 0, 1)), ((0, 0, 1), Y, (1, 0, 0)), ((1, 0, 0), Z, (0, 1, 0))],
)
def test_quarter_turn_is_counterclockwise(vector, axis, expected):
    """Règle de la main droite : autour de x, y va vers z ; autour de y, z va
    vers x ; autour de z, x va vers y."""
    assert rotate(vector, axis, 1) == expected


@pytest.mark.parametrize("axis", [X, Y, Z])
@pytest.mark.parametrize("quarter_turns", [-1, 1, 2])
def test_rotation_matrix_matches_rotate(axis, quarter_turns):
    """La version continue (pour les animations) donne le même résultat."""
    point = (1, 0, -1)
    matrix = rotation_matrix(axis, 90 * quarter_turns)

    assert np.allclose(matrix @ np.array(point), rotate(point, axis, quarter_turns))


def test_R_sends_front_right_middle_up():
    """Avec R, la case du milieu à droite de F monte sur U."""
    axis, layers, quarter_turns = move_rotation("R")
    cubie, normal = sticker_location(F, 1, 2)

    assert is_in_layer(cubie, axis, layers)
    assert rotate(cubie, axis, quarter_turns) == (1, 1, 0)
    assert rotate(normal, axis, quarter_turns) == (0, 1, 0)


# --------------------------------------------------------------------------
# Le grand test : la géométrie et cube.py racontent la même histoire
# --------------------------------------------------------------------------


@pytest.mark.parametrize("move", ALL_MOVES)
def test_move_rotates_the_layer_in_space(numbered_cube, move):
    """Chaque étiquette de la couche tournée arrive à sa place tournée d'un
    quart de tour ; les autres ne bougent pas.

    1. cube numéroté (54 étiquettes) ; 2. on joue le mouvement avec cube.move ;
    3. pour chaque étiquette : où était-elle, où est-elle ? ; 4. on compare
    avec la rotation dans l'espace.
    """
    axis, layers, quarter_turns = move_rotation(move)

    numbered_cube.move(move)

    flat = numbered_cube.state.reshape(54)
    where_now = {int(label): index for index, label in enumerate(flat)}
    for label, sticker in enumerate(STICKERS):
        cubie, normal = sticker_location(*sticker)
        if is_in_layer(cubie, axis, layers):
            expected = sticker_index(
                rotate(cubie, axis, quarter_turns), rotate(normal, axis, quarter_turns)
            )
        else:
            expected = label
        assert where_now[label] == expected, f"{move} : étiquette {label}"


@pytest.mark.parametrize("move", MOVES)
def test_geometry_rebuilds_the_hand_written_moves(move):
    """La permutation calculée par la géométrie est celle du code de la phase 1."""
    assert np.array_equal(permutation(move), PERMUTATIONS[move])


@pytest.mark.parametrize("move", MOVES)
def test_a_face_move_turns_nine_cubies(move):
    """Une face, c'est 9 cubies."""
    axis, layers, _ = move_rotation(move)

    assert sum(is_in_layer(cubie, axis, layers) for cubie in CUBIES) == 9


@pytest.mark.parametrize("move", ["x", "y'", "z2"])
def test_a_rotation_turns_all_cubies(move):
    """Une rotation x y z emporte les 26 cubies."""
    axis, layers, _ = move_rotation(move)

    assert sum(is_in_layer(cubie, axis, layers) for cubie in CUBIES) == 26


# --------------------------------------------------------------------------
# Tourner une couche à la souris
# --------------------------------------------------------------------------


def test_four_drag_directions_per_face():
    """Sur une face, on peut glisser vers 4 directions, toutes dans son plan."""
    for normal in FACE_NORMALS:
        directions = tangent_directions(normal)
        assert len(directions) == 4
        assert all(np.dot(direction, normal) == 0 for direction in directions)


@pytest.mark.parametrize(
    ("sticker", "direction", "move"),
    [
        ((F, 1, 2), (0, 1, 0), "R"),  # colonne de droite de F vers le haut
        ((F, 1, 2), (0, -1, 0), "R'"),
        ((F, 1, 0), (0, -1, 0), "L"),  # colonne de gauche de F vers le bas
        ((F, 1, 1), (0, 1, 0), "M'"),  # colonne du milieu vers le haut
        ((F, 0, 1), (1, 0, 0), "U'"),  # ligne du haut de F vers la droite
        ((F, 0, 1), (-1, 0, 0), "U"),
        ((F, 2, 1), (1, 0, 0), "D"),  # ligne du bas de F vers la droite
        ((U, 2, 1), (1, 0, 0), "F"),  # bord avant de U vers la droite
        ((R, 1, 0), (0, 0, -1), "E"),  # ligne du milieu de R vers l'arrière
    ],
    ids=["R", "R'", "L", "M'", "U'", "U", "D", "F", "E"],
)
def test_drag_gives_the_expected_move(sticker, direction, move):
    """Glisser une case donne le coup qu'on ferait avec les doigts."""
    assert move_for_drag(*sticker, direction) == move


@pytest.mark.parametrize("sticker", STICKERS)
def test_drag_follows_the_real_rotation(sticker):
    """Le coup obtenu en glissant tourne la couche de la case, et pousse sa face
    exactement dans le sens du glissement."""
    cubie, normal = sticker_location(*sticker)
    for direction in tangent_directions(normal):
        axis, layers, quarter_turns = move_rotation(move_for_drag(*sticker, direction))

        assert is_in_layer(cubie, axis, layers)
        assert rotate(normal, axis, quarter_turns) == direction


def test_best_direction_follows_the_mouse():
    """La direction choisie est celle dont l'image à l'écran suit la souris."""
    on_screen = {
        (1, 0, 0): (10.0, 0.0),
        (-1, 0, 0): (-10.0, 0.0),
        (0, 1, 0): (0.0, -8.0),
    }

    assert best_direction(on_screen, (3.0, 0.5)) == (1, 0, 0)
    assert best_direction(on_screen, (0.0, -5.0)) == (0, 1, 0)


def test_slices_and_rotations_keep_nine_stickers_per_color():
    """Les permutations de la géométrie gardent 9 cases de chaque couleur."""
    cube = Cube()
    cube.apply("x y' z2 M E S")
    for color in range(6):
        assert (cube.state == color).sum() == 9
