"""Géométrie 3D du cube, en coordonnées « logiques », sans aucun affichage.

Ce module ne dépend que de numpy : il se teste sans fenêtre, et sert aux deux
vues 3D (ursina et pygame) **et** au cube logique, qui y fabrique les
permutations des tranches (M E S) et des rotations (x y z).

Convention
----------
Le cube est centré sur l'origine. Repère direct (main droite) :

- x vers R (la droite), y vers U (le haut), z vers F (vers moi) ;
- chaque petit cube (« cubie ») a un centre dont les coordonnées valent -1, 0
  ou 1 : 27 positions moins le centre invisible, soit 26 cubies ;
- chaque face a une **normale**, la flèche qui sort de la face : F a (0, 0, 1).

Une case (« sticker ») se décrit par **un cubie et une normale** : la case F2
(en haut à droite de F) est collée sur le cubie (1, 1, 1), du côté (0, 0, 1).

Rotations
---------
On compte les rotations en **quarts de tour anti-horaires autour de l'axe
positif** (règle de la main droite : pouce sur l'axe, les doigts donnent le
sens). « R = horaire vu depuis la droite » vaut donc -1 quart de tour autour
de +x, et « L = horaire vu depuis la gauche » vaut +1 quart de tour autour de +x.
"""

import numpy as np

from rubiks.moves import parse_move

Vector = tuple[int, int, int]

X, Y, Z = 0, 1, 2  # numéros des axes

# Normale de chaque face, dans l'ordre U R F D L B de cube.py
FACE_NORMALS: tuple[Vector, ...] = (
    (0, 1, 0),  # U
    (1, 0, 0),  # R
    (0, 0, 1),  # F
    (0, -1, 0),  # D
    (-1, 0, 0),  # L
    (0, 0, -1),  # B
)

# Pour chaque lettre : (axe, couches qui tournent, quarts de tour anti-horaires
# autour de l'axe positif pour le mouvement « horaire » sans suffixe)
LAYER_ROTATIONS: dict[str, tuple[int, tuple[int, ...], int]] = {
    "U": (Y, (1,), -1),
    "D": (Y, (-1,), 1),
    "R": (X, (1,), -1),
    "L": (X, (-1,), 1),
    "F": (Z, (1,), -1),
    "B": (Z, (-1,), 1),
    "M": (X, (0,), 1),  # comme L
    "E": (Y, (0,), 1),  # comme D
    "S": (Z, (0,), -1),  # comme F
    "x": (X, (-1, 0, 1), -1),  # comme R, tout le cube
    "y": (Y, (-1, 0, 1), -1),  # comme U, tout le cube
    "z": (Z, (-1, 0, 1), -1),  # comme F, tout le cube
}


def sticker_location(face: int, row: int, col: int) -> tuple[Vector, Vector]:
    """Renvoie (centre du cubie, normale) de la case (face, row, col).

    Les formules se lisent sur la docstring de cube.py : L, F, R, B vues de face
    avec U en haut ; U vue de dessus avec F en bas ; D vue de dessous avec F en
    haut. Exemple : la ligne 0 de F est en haut (y = 1), la colonne 0 à gauche
    (x = -1).
    """
    if face == 0:  # U : ligne 2 contre F (z = 1), colonne 0 à gauche
        cubie = (col - 1, 1, row - 1)
    elif face == 1:  # R : colonne 0 contre F, colonne 2 contre B
        cubie = (1, 1 - row, 1 - col)
    elif face == 2:  # F
        cubie = (col - 1, 1 - row, 1)
    elif face == 3:  # D : ligne 0 contre F, colonne 0 à gauche
        cubie = (col - 1, -1, 1 - row)
    elif face == 4:  # L : colonne 0 contre B, colonne 2 contre F
        cubie = (-1, 1 - row, col - 1)
    elif face == 5:  # B : vue de derrière, colonne 0 contre R
        cubie = (1 - col, 1 - row, -1)
    else:
        raise ValueError(f"face inconnue : {face!r}")
    return cubie, FACE_NORMALS[face]


# Les 54 cases dans l'ordre de cube.state mis à plat : indice = face*9 + row*3 + col
STICKERS: tuple[tuple[int, int, int], ...] = tuple(
    (face, row, col) for face in range(6) for row in range(3) for col in range(3)
)
_INDEX_OF_LOCATION = {
    sticker_location(*sticker): index for index, sticker in enumerate(STICKERS)
}

# Les 26 cubies visibles
CUBIES: tuple[Vector, ...] = tuple(
    (x, y, z)
    for x in (-1, 0, 1)
    for y in (-1, 0, 1)
    for z in (-1, 0, 1)
    if (x, y, z) != (0, 0, 0)
)


def sticker_index(cubie: Vector, normal: Vector) -> int:
    """Renvoie l'indice (0 à 53) de la case posée sur ce cubie, de ce côté."""
    return _INDEX_OF_LOCATION[(tuple(cubie), tuple(normal))]


def rotate(vector: Vector, axis: int, quarter_turns: int) -> Vector:
    """Tourne un point (ou une normale) de quarter_turns quarts de tour
    anti-horaires autour de l'axe positif ``axis``.

    Un quart de tour anti-horaire dans le plan (a, b) : (a, b) -> (-b, a).
    Autour de x, le plan est (y, z) ; autour de y, (z, x) ; autour de z, (x, y).
    La coordonnée de l'axe ne bouge pas. Calcul exact, en entiers.
    """
    a, b = ((Y, Z), (Z, X), (X, Y))[axis]
    result = list(vector)
    for _ in range(quarter_turns % 4):
        result[a], result[b] = -result[b], result[a]
    return tuple(result)


def rotation_matrix(axis: int, degrees: float) -> np.ndarray:
    """Matrice 3 x 3 d'une rotation anti-horaire de ``degrees`` autour de l'axe.

    Version continue de ``rotate`` (pour les animations) :
    ``rotation_matrix(axis, 90 * q) @ v`` donne ``rotate(v, axis, q)``.
    """
    angle = np.radians(degrees)
    c, s = np.cos(angle), np.sin(angle)
    a, b = ((Y, Z), (Z, X), (X, Y))[axis]
    matrix = np.eye(3)
    matrix[a, a], matrix[a, b] = c, -s
    matrix[b, a], matrix[b, b] = s, c
    return matrix


def move_rotation(name: str) -> tuple[int, tuple[int, ...], int]:
    """Renvoie (axe, couches, quarts de tour) d'un mouvement.

    Les quarts de tour sont anti-horaires autour de l'axe positif, et gardent
    le sens du mouvement pour l'animation : R = -1, R' = +1, R2 = -2.
    """
    letter, quarter_turns = parse_move(name)
    axis, layers, base = LAYER_ROTATIONS[letter]
    signed = {1: 1, 2: 2, 3: -1}[quarter_turns] * base
    return axis, layers, signed


def is_in_layer(cubie: Vector, axis: int, layers: tuple[int, ...]) -> bool:
    """True si le cubie fait partie des couches qui tournent."""
    return cubie[axis] in layers


def permutation(name: str) -> np.ndarray:
    """Renvoie la permutation des 54 cases faite par un mouvement.

    Après le mouvement, la case i contient ce qui était dans la case
    ``perm[i]`` : ``new_flat = old_flat[perm]``.
    """
    axis, layers, quarter_turns = move_rotation(name)
    perm = np.arange(54)
    for old_index, sticker in enumerate(STICKERS):
        cubie, normal = sticker_location(*sticker)
        if is_in_layer(cubie, axis, layers):
            new_index = sticker_index(
                rotate(cubie, axis, quarter_turns), rotate(normal, axis, quarter_turns)
            )
            perm[new_index] = old_index
    return perm


# --------------------------------------------------------------------------
# Tourner une couche à la souris
# --------------------------------------------------------------------------


def tangent_directions(normal: Vector) -> list[Vector]:
    """Les 4 directions dans le plan d'une face : on peut glisser vers elles."""
    axis = [abs(c) for c in normal].index(1)
    directions = []
    for other in range(3):
        if other != axis:
            for sign in (1, -1):
                direction = [0, 0, 0]
                direction[other] = sign
                directions.append(tuple(direction))
    return directions


def move_from_rotation(axis: int, layer: int, quarter_turns: int) -> str:
    """Nom du mouvement qui tourne une seule couche (-1, 0 ou 1) d'un quart de
    tour (+1 ou -1, anti-horaire autour de l'axe positif)."""
    for letter, (letter_axis, layers, base) in LAYER_ROTATIONS.items():
        if letter_axis == axis and layers == (layer,):
            return letter if quarter_turns == base else letter + "'"
    raise ValueError(f"aucune couche {layer} sur l'axe {axis}")


def move_for_drag(face: int, row: int, col: int, direction: Vector) -> str:
    """Mouvement obtenu en faisant glisser la case (face, row, col) vers
    ``direction`` (une des 4 directions de ``tangent_directions``).

    L'axe de rotation est perpendiculaire à la normale et à la direction :
    c'est leur produit vectoriel. Tourner d'un quart de tour anti-horaire
    autour de ``normale x direction`` pousse la face vers ``direction``.
    """
    cubie, normal = sticker_location(face, row, col)
    rotation_axis = np.cross(normal, direction)
    axis = int(np.flatnonzero(rotation_axis)[0])
    quarter_turns = int(rotation_axis[axis])  # +1 ou -1
    return move_from_rotation(axis, cubie[axis], quarter_turns)


def best_direction(
    screen_directions: dict[Vector, tuple[float, float]], drag: tuple[float, float]
) -> Vector:
    """Choisit la direction 3D dont l'image à l'écran ressemble le plus au
    glissement de la souris (le plus grand produit scalaire, une fois normalisé).
    """

    def score(item: tuple[Vector, tuple[float, float]]) -> float:
        dx, dy = item[1]
        length = (dx * dx + dy * dy) ** 0.5 or 1.0
        return (dx * drag[0] + dy * drag[1]) / length

    return max(screen_directions.items(), key=score)[0]
