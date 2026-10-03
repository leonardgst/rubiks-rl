"""Tests du cube logique (phase 1, complétés en phase 3).

Ces tests décrivent ce que le cube doit faire, pas comment il le fait : ils
n'utilisent que ses méthodes (move, apply, is_solved...) et son attribut state.
La façon de tourner les faces (np.rot90, tranches, permutations...) n'existe
que dans cube.py.

Le cube numéroté existe en deux versions : la fixture ``numbered_cube``
(conftest.py), quand un test n'en a besoin que d'un, et la fonction
``make_numbered_cube()``, quand il en faut deux.
"""

import numpy as np
import pytest
from rubiks.cube import MOVES, PERMUTATIONS, Cube, sequence_order
from rubiks.moves import ALL_MOVES, ROTATION_MOVES, SLICE_MOVES

FACES = ["U", "R", "F", "D", "L", "B"]


def make_numbered_cube() -> Cube:
    """Renvoie un cube dont les 54 cases portent des numéros tous différents.

    Sur un cube résolu, une bande d'une seule couleur reste identique même
    retournée : un bug d'ordre passerait inaperçu. Avec des numéros, chaque case
    est reconnaissable et le moindre déplacement se voit.
    """
    cube = Cube()
    cube.state = np.arange(54).reshape(6, 3, 3)
    return cube


def test_new_cube_is_solved():
    """Un cube neuf est résolu"""
    assert Cube().is_solved()


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
    cube = make_numbered_cube()
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
    cube = make_numbered_cube()
    initial_state = cube.state.copy()

    cube.move(face + suffixe)
    cube.move(face + inverse_suffixe)

    assert np.array_equal(cube.state, initial_state)


def test_sexy_move_six_times_is_identity():
    """
    Vérifie qu'appliquer 6 fois la suite de
    mouvement "R U R' U'" ramène à l'état initial
    """
    cube = make_numbered_cube()
    initial_state = cube.state.copy()

    for _ in range(6):
        cube.apply("R U R' U'")

    assert np.array_equal(cube.state, initial_state)


@pytest.mark.parametrize("face", FACES)
def test_copy_is_independent(face):
    """Une copie est identique à l'original,
    mais indépendante de lui.
    """
    cube = make_numbered_cube()
    cube_copy = cube.copy()

    assert np.array_equal(cube.state, cube_copy.state)

    cube_copy.state[0, 0, 0] = 99

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


def test_quarter_turn_D_from_solved_cube():
    """Test de référence : on part d'un cube résolu (U=W ; F=G) et on fait 'D'
    (quart de tour horaire, vu de dessous). Alors :
        - la ligne du bas de F est orange
        - la ligne du bas de L est bleu
        - la ligne du bas de B est rouge
        - la ligne du bas de R est verte
    et tout le reste du cube est inchangé.
    """
    cube = Cube()
    cube.move("D")

    # Les 4 lignes du bas ont tourné d'une face à la suivante
    assert (cube.state[1, 2] == 2).sum() == 3  # R : verte
    assert (cube.state[2, 2] == 4).sum() == 3  # F : orange
    assert (cube.state[4, 2] == 5).sum() == 3  # L : bleu
    assert (cube.state[5, 2] == 1).sum() == 3  # B : rouge

    # Ce qui ne doit pas bouger : le milieu et le haut des 4 faces, et toute la face U
    assert np.all(cube.state[1, :2] == 1)
    assert np.all(cube.state[2, :2] == 2)
    assert np.all(cube.state[4, :2] == 4)
    assert np.all(cube.state[5, :2] == 5)
    assert np.all(cube.state[0] == 0)


def test_quarter_turn_R_from_solved_cube():
    """Test de référence : on part d'un cube résolu et on fait R.

    Alors :
        - la colonne droite de U devient verte ;
        - la colonne droite de F devient jaune ;
        - la colonne droite de D devient bleue ;
        - la colonne gauche de B devient blanche ;
        - tout le reste est inchangé.
    """
    cube = Cube()
    cube.move("R")

    # Colonnes déplacées
    assert np.all(cube.state[0, :, 2] == 2)  # U droite : verte
    assert np.all(cube.state[2, :, 2] == 3)  # F droite : jaune
    assert np.all(cube.state[3, :, 2] == 5)  # D droite : bleue
    assert np.all(cube.state[5, :, 0] == 0)  # B gauche : blanche

    # Parties qui ne doivent pas changer
    assert np.all(cube.state[0, :, :2] == 0)  # U : gauche et milieu
    assert np.all(cube.state[2, :, :2] == 2)  # F : gauche et milieu
    assert np.all(cube.state[3, :, :2] == 3)  # D : gauche et milieu
    assert np.all(cube.state[5, :, 1:] == 5)  # B : milieu et droite

    # La face L ne bouge pas
    assert np.all(cube.state[4] == 4)

    # La face R tourne, mais reste rouge car elle était uniforme
    assert np.all(cube.state[1] == 1)


def test_quarter_turn_L_from_solved_cube():
    """Test de référence : on part d'un cube résolu et on fait L.

    Alors :
        - la colonne gauche de U devient bleue ;
        - la colonne gauche de F devient blanche ;
        - la colonne gauche de D devient verte ;
        - la colonne droite de B devient jaune ;
        - tout le reste est inchangé.
    """
    cube = Cube()
    cube.move("L")

    # Colonnes déplacées
    assert np.all(cube.state[0, :, 0] == 5)  # U gauche : bleue
    assert np.all(cube.state[2, :, 0] == 0)  # F gauche : blanche
    assert np.all(cube.state[3, :, 0] == 2)  # D gauche : verte
    assert np.all(cube.state[5, :, 2] == 3)  # B droite : jaune

    # Parties qui ne doivent pas changer
    assert np.all(cube.state[0, :, 1:] == 0)  # U : milieu et droite
    assert np.all(cube.state[2, :, 1:] == 2)  # F : milieu et droite
    assert np.all(cube.state[3, :, 1:] == 3)  # D : milieu et droite
    assert np.all(cube.state[5, :, :2] == 5)  # B : gauche et milieu

    # La face R ne bouge pas
    assert np.all(cube.state[1] == 1)

    # La face L tourne, mais reste orange car elle était uniforme
    assert np.all(cube.state[4] == 4)


def test_quarter_turn_F_from_solved_cube():
    """Test de référence : on part d'un cube résolu et on fait F.

    Alors :
        - la ligne du bas de U devient orange ;
        - la colonne gauche de R devient blanche ;
        - la ligne du haut de D devient rouge ;
        - la colonne droite de L devient jaune ;
        - tout le reste est inchangé.
    """
    cube = Cube()
    cube.move("F")

    # Lignes et colonnes déplacées
    assert np.all(cube.state[0, 2] == 4)  # U bas : orange
    assert np.all(cube.state[1, :, 0] == 0)  # R gauche : blanche
    assert np.all(cube.state[3, 0] == 1)  # D haut : rouge
    assert np.all(cube.state[4, :, 2] == 3)  # L droite : jaune

    # Parties qui ne doivent pas changer
    assert np.all(cube.state[0, :2] == 0)  # U : haut et milieu
    assert np.all(cube.state[1, :, 1:] == 1)  # R : milieu et droite
    assert np.all(cube.state[3, 1:] == 3)  # D : milieu et bas
    assert np.all(cube.state[4, :, :2] == 4)  # L : gauche et milieu

    # La face B ne bouge pas
    assert np.all(cube.state[5] == 5)

    # La face F tourne, mais reste verte car elle était uniforme
    assert np.all(cube.state[2] == 2)


def test_quarter_turn_B_from_solved_cube():
    """Test de référence : on part d'un cube résolu et on fait B.

    Alors :
        - la ligne du haut de U devient rouge ;
        - la colonne gauche de L devient blanche ;
        - la ligne du bas de D devient orange ;
        - la colonne droite de R devient jaune ;
        - tout le reste est inchangé.
    """
    cube = Cube()
    cube.move("B")

    # Lignes et colonnes déplacées
    assert np.all(cube.state[0, 0] == 1)  # U haut : rouge
    assert np.all(cube.state[4, :, 0] == 0)  # L gauche : blanche
    assert np.all(cube.state[3, 2] == 4)  # D bas : orange
    assert np.all(cube.state[1, :, 2] == 3)  # R droite : jaune

    # Parties qui ne doivent pas changer
    assert np.all(cube.state[0, 1:] == 0)  # U : milieu et bas
    assert np.all(cube.state[4, :, 1:] == 4)  # L : milieu et droite
    assert np.all(cube.state[3, :2] == 3)  # D : haut et milieu
    assert np.all(cube.state[1, :, :2] == 1)  # R : gauche et milieu

    # La face F ne bouge pas
    assert np.all(cube.state[2] == 2)

    # La face B tourne, mais reste bleue car elle était uniforme
    assert np.all(cube.state[5] == 5)


@pytest.mark.parametrize(
    ("move", "face_index"),
    [
        ("U", 0),
        ("R", 1),
        ("F", 2),
        ("D", 3),
        ("L", 4),
        ("B", 5),
    ],
)
def test_move_turns_its_face_clockwise(move, face_index):
    """Vérifie que chaque mouvement tourne sa propre face d'un quart de tour
    dans le sens horaire, lorsqu'elle est regardée depuis l'extérieur.

    Le cube numéroté permet de vérifier la position exacte de chaque case,
    contrairement à un cube résolu dont chaque face est uniforme.
    """
    cube = make_numbered_cube()
    initial_face = cube.state[face_index].copy()

    cube.move(move)

    expected_face = np.rot90(initial_face, k=-1)

    assert np.array_equal(cube.state[face_index], expected_face)


@pytest.mark.parametrize("face", FACES)
def test_quarter_turn_moves_twenty_stickers(face):
    """Vérifie qu'un quart de tour déplace exactement 20 cases.

    Un mouvement déplace les 8 cases non centrales de la face tournée,
    ainsi que 12 cases appartenant aux quatre faces adjacentes.
    Le cube numéroté permet de détecter chaque changement de position.
    """
    cube = make_numbered_cube()
    initial_state = cube.state.copy()

    cube.move(face)

    number_of_moved_stickers = (cube.state != initial_state).sum()

    assert number_of_moved_stickers == 20


@pytest.mark.parametrize("face", FACES)
@pytest.mark.parametrize("suffix", ["", "'", "2"])
def test_centers_never_move(face, suffix):
    """Vérifie que les six centres restent à leur position initiale.

    Le test couvre les quarts de tour horaires, les quarts de tour
    antihoraires et les demi-tours pour chacune des six faces.
    """
    cube = make_numbered_cube()
    initial_centers = cube.state[:, 1, 1].copy()

    cube.move(face + suffix)

    assert np.array_equal(cube.state[:, 1, 1], initial_centers)


@pytest.mark.parametrize(
    ("first_face", "second_face"),
    [
        ("U", "D"),
        ("R", "L"),
        ("F", "B"),
    ],
    ids=["U et D", "R et L", "F et B"],
)
def test_opposite_faces_commute(first_face, second_face):
    """Vérifie que deux mouvements sur des faces opposées commutent.

    Appliquer la première face puis la seconde doit produire le même état
    que les appliquer dans l'ordre inverse, car deux faces opposées ne
    déplacent aucune case commune.
    """
    first_cube = make_numbered_cube()
    second_cube = make_numbered_cube()

    first_cube.move(first_face)
    first_cube.move(second_face)

    second_cube.move(second_face)
    second_cube.move(first_face)

    assert np.array_equal(first_cube.state, second_cube.state)


def test_apply_is_equivalent_to_individual_moves():
    """Vérifie si la fonction apply et une suite de
    fonction move renvoient le même cube."""
    first_cube = make_numbered_cube()
    second_cube = make_numbered_cube()

    first_cube.apply("U R U' U R'")
    second_cube.move("U")
    second_cube.move("R")
    second_cube.move("U'")
    second_cube.move("U")
    second_cube.move("R'")

    assert np.array_equal(first_cube.state, second_cube.state)


def test_apply_empty_string_does_nothing():
    """Vérifie qu'une chaîne vide ne modifie pas l'état du cube."""
    cube = make_numbered_cube()
    initial_state = cube.state.copy()

    cube.apply("")

    assert np.array_equal(cube.state, initial_state)


def test_apply_unknown_move_raises_value_error():
    """Vérifie qu'une suite contenant un mouvement inconnu lève ValueError."""
    cube = Cube()

    with pytest.raises(ValueError):
        cube.apply("R U X F")


@pytest.mark.parametrize("n", [0, 1, 5, 100])
def test_scramble_returns_n_moves(n):
    """scramble(n) renvoie une liste d'exactement n mouvements (même pour n = 0)."""
    cube = Cube()

    moves_played = cube.scramble(n, seed=0)

    assert len(moves_played) == n


def test_scramble_returns_only_valid_moves():
    """Tous les mouvements renvoyés font partie des 18 mouvements de MOVES."""
    cube = Cube()

    moves_played = cube.scramble(200, seed=0)

    assert all(move in MOVES for move in moves_played)


def test_scramble_same_seed_gives_same_moves():
    """Même graine, même mélange : mêmes mouvements et même état final.

    On part du cube numéroté pour comparer l'état case par case.
    """
    first_cube = make_numbered_cube()
    second_cube = make_numbered_cube()

    first_moves = first_cube.scramble(30, seed=42)
    second_moves = second_cube.scramble(30, seed=42)

    assert first_moves == second_moves  # deux listes se comparent avec ==
    assert np.array_equal(first_cube.state, second_cube.state)  # pas deux tableaux


def test_scramble_different_seeds_give_different_moves():
    """Deux graines différentes donnent deux mélanges différents.

    Les graines sont fixées : le résultat est toujours le même, le test n'est pas
    aléatoire. Sur 30 coups, deux suites identiques par hasard : 1 chance sur 18**30.
    """
    first_moves = Cube().scramble(30, seed=1)
    second_moves = Cube().scramble(30, seed=2)

    assert first_moves != second_moves


@pytest.mark.parametrize("color", range(6))
def test_scramble_keeps_each_color_nine_times(color):
    """Après un long mélange, chaque couleur apparaît toujours exactement 9 fois.

    Un mouvement qui dupliquerait une bande (piège des vues numpy) casserait ce
    compte.
    """
    cube = Cube()

    cube.scramble(100, seed=0)

    assert (cube.state == color).sum() == 9


def test_scramble_returns_the_moves_it_played():
    """La liste renvoyée est fidèle : la rejouer sur un cube identique donne le
    même état que le cube mélangé.

    apply attend une chaîne : on rassemble la liste avec " ".join(...).
    """
    scrambled_cube = make_numbered_cube()
    replayed_cube = make_numbered_cube()

    moves_played = scrambled_cube.scramble(30, seed=7)
    replayed_cube.apply(" ".join(moves_played))

    assert np.array_equal(scrambled_cube.state, replayed_cube.state)


# --------------------------------------------------------------------------
# mélange puis suite inverse
# --------------------------------------------------------------------------


@pytest.mark.parametrize("seed", range(5))
@pytest.mark.parametrize("n", [1, 20, 100])
def test_scramble_then_inverse_sequence_solves_cube(n, seed):
    """Mélanger, puis appliquer la suite inverse au MÊME cube, le résout.

    On vérifie aussi que le mélange a bien désordonné le cube : sinon le test
    passerait même si scramble ne faisait rien.
    """
    cube = Cube()

    moves_played = cube.scramble(n, seed=seed)
    assert not cube.is_solved()

    cube.apply(" ".join(cube.inverse_sequence(moves_played)))

    assert cube.is_solved()


@pytest.mark.parametrize("seed", range(5))
def test_scramble_then_inverse_sequence_restores_numbered_cube(seed):
    """Version stricte : sur le cube numéroté, chaque case retrouve sa place.

    Attention : is_solved() vaut toujours False sur un cube numéroté (ses faces
    ne sont jamais unies). On compare donc à l'état de départ gardé de côté.
    """
    cube = make_numbered_cube()
    initial_state = cube.state.copy()

    moves_played = cube.scramble(50, seed=seed)
    cube.apply(" ".join(cube.inverse_sequence(moves_played)))

    assert np.array_equal(cube.state, initial_state)


# --------------------------------------------------------------------------
# inverse_sequence seule
# --------------------------------------------------------------------------


def test_inverse_sequence_reverses_order_and_inverts_each_move():
    """La suite inverse se lit à l'envers, chaque mouvement étant inversé.

    Principe de la chaussette et de la chaussure : pour défaire "R puis U' puis
    F2", on défait d'abord F2 (son propre inverse), puis U' (donc U), puis R
    (donc R').
    """
    cube = Cube()

    assert cube.inverse_sequence(["R", "U'", "F2"]) == ["F2", "U", "R'"]


def test_inverse_sequence_of_empty_list_is_empty():
    """L'inverse d'une suite vide est une suite vide."""
    cube = Cube()

    assert cube.inverse_sequence([]) == []


def test_inverse_of_inverse_sequence_is_original():
    """Inverser deux fois une suite redonne la suite de départ."""
    cube = Cube()
    moves = ["U", "R'", "F2", "D", "L'", "B2"]

    twice_inverted = cube.inverse_sequence(cube.inverse_sequence(moves))

    assert twice_inverted == moves


# --------------------------------------------------------------------------
# __eq__, __repr__ et facelets
# --------------------------------------------------------------------------


def test_cubes_compare_with_equal_sign():
    """Grâce à __eq__, deux cubes se comparent avec == (case par case)."""
    first, second = Cube(), Cube()
    assert first == second

    first.move("R")
    assert first != second

    second.move("R")
    assert first == second


def test_cube_is_never_equal_to_something_else():
    """Un cube n'est pas égal à un objet d'un autre type."""
    assert Cube() != "UUUUUUUUU"


def test_repr_can_rebuild_the_cube():
    """repr(cube) affiche une expression qui refabrique le même cube."""
    cube = Cube()
    cube.apply("R U F'")

    rebuilt = eval(repr(cube), {"Cube": Cube})  # eval : seulement dans un test

    assert rebuilt == cube


def test_facelets_of_new_cube():
    """Format kociemba : 9 U, puis 9 R, 9 F, 9 D, 9 L, 9 B."""
    assert Cube().facelets() == "".join(face * 9 for face in "URFDLB")


def test_from_facelets_rejects_bad_strings():
    """Une chaîne de mauvaise longueur, ou avec une lettre inconnue, est refusée."""
    with pytest.raises(ValueError):
        Cube.from_facelets("UUU")
    with pytest.raises(ValueError):
        Cube.from_facelets("X" * 54)


# --------------------------------------------------------------------------
# Les permutations
# --------------------------------------------------------------------------


def test_there_is_one_permutation_per_move():
    """36 permutations : 18 faces, 9 tranches, 9 rotations."""
    assert set(PERMUTATIONS) == set(ALL_MOVES)
    assert len(ALL_MOVES) == 36


@pytest.mark.parametrize("move", ALL_MOVES)
def test_each_permutation_uses_every_sticker_once(move):
    """Une permutation contient chaque numéro de 0 à 53 exactement une fois."""
    assert sorted(PERMUTATIONS[move]) == list(range(54))


@pytest.mark.parametrize("move", ALL_MOVES)
def test_every_move_four_times_is_identity(numbered_cube, move):
    """Les 36 mouvements, répétés 4 fois, ramènent au départ (même X2)."""
    initial = numbered_cube.copy()

    for _ in range(4):
        numbered_cube.move(move)

    assert numbered_cube == initial


# --------------------------------------------------------------------------
# Tranches et rotations
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("rotation", "equivalent"),
    [("x", "R M' L'"), ("y", "U E' D'"), ("z", "F S B'")],
)
def test_rotation_is_two_faces_and_a_slice(rotation, equivalent):
    """Tourner tout le cube = tourner ses trois couches (x = R M' L')."""
    rotated, layered = Cube(), Cube()

    rotated.move(rotation)
    layered.apply(equivalent)

    assert rotated == layered


@pytest.mark.parametrize("move", ROTATION_MOVES)
def test_a_rotated_cube_is_still_solved(move):
    """Tenir le cube autrement ne le mélange pas."""
    cube = Cube()

    cube.move(move)

    assert cube.is_solved()
    assert cube != Cube()  # mais les couleurs ont changé de place


@pytest.mark.parametrize("move", SLICE_MOVES)
def test_slice_moves_the_centers(numbered_cube, move):
    """Une tranche du milieu déplace 4 centres : c'est pour ça qu'elle ne fait
    pas partie des 18 actions du RL (le cube changerait d'orientation)."""
    centers = numbered_cube.state[:, 1, 1].copy()

    numbered_cube.move(move)

    assert (numbered_cube.state[:, 1, 1] != centers).sum() == 4


# --------------------------------------------------------------------------
# L'ordre d'une séquence
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("sequence", "order"),
    [("R", 4), ("R2", 2), ("R U", 105), ("R U'", 63), ("R U R' U'", 6), ("", 1)],
)
def test_sequence_order(sequence, order):
    """Combien de répétitions pour revenir au départ ? « R U » : 105 fois."""
    assert sequence_order(sequence) == order


def test_sequence_order_really_comes_back():
    """Vérification directe : R U joué 105 fois revient au cube neuf, pas avant."""
    cube = Cube()
    for repetition in range(1, 106):
        cube.apply("R U")
        assert cube.is_solved() == (repetition == 105)
