"""Logique pure du Rubik's Cube 3x3, sans aucun affichage.

Représentation
--------------
L'état du cube est l'attribut ``state`` : un tableau numpy d'entiers de forme
(6, 3, 3). ``state[face, ligne, colonne]`` donne la couleur d'une case.

Faces et couleurs
-----------------
Les faces sont rangées dans l'ordre U R F D L B (celui de la bibliothèque
kociemba). Une couleur est un entier de 0 à 5 : la couleur ``i`` est celle
de la face ``i`` quand le cube est résolu.

    0  U (haut)       blanc
    1  R (droite)     rouge
    2  F (devant)     vert
    3  D (bas)        jaune
    4  L (gauche)     orange
    5  B (derrière)   bleu

Orientation des faces (patron déplié)
-------------------------------------
Dans chaque face, les cases sont numérotées de 0 à 8, ligne par ligne :
la case k est en [k // 3, k % 3]. Le centre (case 4) ne bouge jamais.

              U0 U1 U2
              U3 U4 U5
              U6 U7 U8
    L0 L1 L2  F0 F1 F2  R0 R1 R2  B0 B1 B2
    L3 L4 L5  F3 F4 F5  R3 R4 R5  B3 B4 B5
    L6 L7 L8  F6 F7 F8  R6 R7 R8  B6 B7 B8
              D0 D1 D2
              D3 D4 D5
              D6 D7 D8

- L, F, R, B sont vues de face, depuis l'extérieur, avec U en haut.
- U est vue de dessus, avec F en bas (U6 U7 U8 touche F0 F1 F2).
- D est vue de dessous, avec F en haut (D0 D1 D2 touche F6 F7 F8).

Mouvements
----------
Notation Singmaster (voir ``moves.py``) : U D L R F B = quart de tour horaire,
en regardant la face depuis l'extérieur ; ' = anti-horaire ; 2 = demi-tour.
18 mouvements de faces, plus les tranches M E S et les rotations x y z.

``move()`` et ``apply()`` modifient le cube lui-même et ne renvoient rien.
Pour garder l'état d'origine, on utilise ``copy()``, qui fabrique un cube
indépendant (le tableau numpy est copié, pas partagé).

Les permutations (rapides)
--------------------------
Les quarts de tour écrits à la main en phase 1 (``_quarter_turn_*``, avec
``np.rot90`` et des tranches) restent **la référence**. Au chargement du module,
on les joue une seule fois sur un cube numéroté (0 à 53) : le résultat, mis à
plat, dit pour chaque case d'où vient son contenu. C'est la **permutation** du
mouvement. Ensuite, jouer un mouvement = une seule indexation numpy
(``state[perm]``), environ dix fois plus rapide : utile pour le RL, qui jouera
des millions de coups.

Les tranches et les rotations, elles, sont fabriquées par ``geometry.py`` (en
tournant des points dans l'espace) ; ``tests/test_geometry.py`` vérifie que la
géométrie redonne exactement les permutations des 18 mouvements écrits à la main.
"""

import numpy as np

from rubiks import geometry
from rubiks.moves import (
    ALL_MOVES,
    FACES,
    MOVES,
    QUARTER_TURNS,
    ROTATION_MOVES,
    SLICE_MOVES,
)
from rubiks.moves import inverse_sequence as _inverse_sequence
from rubiks.scramble import random_moves

__all__ = ["MOVES", "Cube", "PERMUTATIONS", "sequence_order"]

# Lettre de la couleur i dans le patron texte (W R G Y O B)
COLOR_LETTERS = "WRGYOB"


class Cube:
    """Un rubik's cube 3x3 (représentation décrite en haut du module)."""

    def __init__(self) -> None:
        """Crée un cube résolu : la face i est entièrement de la couleur i."""
        self.state = np.zeros((6, 3, 3), dtype=int)
        for face in range(6):
            self.state[face] = face

    # ----------------------------------------------------------------------
    # Comparer, afficher, copier
    # ----------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        """Deux cubes sont égaux si toutes leurs cases ont la même couleur.

        Permet d'écrire ``assert cube_a == cube_b`` dans les tests.
        """
        if not isinstance(other, Cube):
            return NotImplemented
        return np.array_equal(self.state, other.state)

    # Un objet modifiable qui définit __eq__ ne doit pas servir de clé de dict
    __hash__ = None

    def __repr__(self) -> str:
        """Affichage lisible (et recopiable) dans les messages d'erreur de pytest."""
        return f"Cube.from_facelets({self.facelets()!r})"

    def __str__(self) -> str:
        """Renvoie le patron déplié du cube, une lettre par couleur (W R G Y O B)."""
        gap = "  "
        indent = " " * (5 + len(gap))  # 5 = largeur d'une face ("W W W")

        def row(face: int, line: int) -> str:
            return " ".join(COLOR_LETTERS[color] for color in self.state[face, line])

        lines = []
        for line in range(3):  # U, en haut
            lines.append(indent + row(0, line))
        for line in range(3):  # L F R B, côte à côte
            lines.append(gap.join(row(face, line) for face in (4, 2, 1, 5)))
        for line in range(3):  # D, en bas
            lines.append(indent + row(3, line))
        return "\n".join(lines)

    def facelets(self) -> str:
        """Les 54 cases en une chaîne, une lettre de face par couleur.

        Ordre U R F D L B, ligne par ligne : c'est le format de la bibliothèque
        kociemba. Un cube neuf donne "UUUUUUUUURRRRRRRRRFFF...".
        """
        return "".join(FACES[color] for color in self.state.reshape(-1))

    @classmethod
    def from_facelets(cls, facelets: str) -> "Cube":
        """Fabrique un cube à partir d'une chaîne de ``facelets()``."""
        if len(facelets) != 54 or any(letter not in FACES for letter in facelets):
            raise ValueError("il faut 54 lettres parmi U R F D L B")
        cube = cls()
        cube.state = np.array([FACES.index(c) for c in facelets]).reshape(6, 3, 3)
        return cube

    def copy(self) -> "Cube":
        """Fabrique un nouveau cube dont le tableau est une copie de celui-ci."""
        new_cube = Cube()
        new_cube.state = self.state.copy()
        return new_cube

    def is_solved(self) -> bool:
        """Renvoie True si chaque face est d'une seule couleur."""
        for face in self.state:
            if not np.all(face == face[1, 1]):
                return False
        return True

    # ----------------------------------------------------------------------
    # Les quarts de tour de la phase 1 : la référence
    # ----------------------------------------------------------------------

    def _quarter_turn_U(self) -> None:
        """Quart de tour horaire de la face U, en modifiant le cube sur place."""
        # Copie de l'état de départ : on lit dedans, on écrit dans self
        old = self.copy()

        # La face U tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[0] = np.rot90(self.state[0], k=-1)

        # Cycle = L -> B -> R -> F -> L
        self.state[2, 0] = old.state[1, 0]  # F reçoit la ligne de R
        self.state[4, 0] = old.state[2, 0]  # L reçoit la ligne de F
        self.state[5, 0] = old.state[4, 0]  # B reçoit la ligne de L
        self.state[1, 0] = old.state[5, 0]  # R reçoit la ligne de B

    def _quarter_turn_D(self) -> None:
        """Quart de tour horaire de la face D, en modifiant le cube sur place."""
        old = self.copy()

        # La face D tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[3] = np.rot90(self.state[3], k=-1)

        # Cycle = L -> F -> R -> B -> L
        self.state[2, 2] = old.state[4, 2]  # F reçoit la ligne de L
        self.state[4, 2] = old.state[5, 2]  # L reçoit la ligne de B
        self.state[5, 2] = old.state[1, 2]  # B reçoit la ligne de R
        self.state[1, 2] = old.state[2, 2]  # R reçoit la ligne de F

    def _quarter_turn_R(self) -> None:
        """Quart de tour horaire de la face R, en modifiant le cube sur place."""
        old = self.copy()

        # La face R tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[1] = np.rot90(self.state[1], k=-1)

        # Chaque face reçoit la colonne de droite de la face d'en dessous,
        # sauf D, qui reçoit la colonne gauche de B, inversée
        self.state[0, :, 2] = old.state[2, :, 2]  # U <- colonne droite de F
        self.state[5, :, 0] = old.state[0, :, 2][::-1]  # B <- droite de U, inversée
        self.state[3, :, 2] = old.state[5, :, 0][::-1]  # D <- gauche de B, inversée
        self.state[2, :, 2] = old.state[3, :, 2]  # F <- colonne droite de D

    def _quarter_turn_L(self) -> None:
        """Quart de tour horaire de la face L, en modifiant le cube sur place."""
        old = self.copy()

        # La face L tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[4] = np.rot90(self.state[4], k=-1)

        # Chaque face reçoit la colonne de gauche de la face d'au-dessus,
        # sauf U, qui reçoit la colonne droite de B, inversée
        self.state[0, :, 0] = old.state[5, :, 2][::-1]  # U <- droite de B, inversée
        self.state[5, :, 2] = old.state[3, :, 0][::-1]  # B <- gauche de D, inversée
        self.state[3, :, 0] = old.state[2, :, 0]  # D <- colonne gauche de F
        self.state[2, :, 0] = old.state[0, :, 0]  # F <- colonne gauche de U

    def _quarter_turn_F(self) -> None:
        """Quart de tour horaire de la face F, en modifiant le cube sur place."""
        old = self.copy()

        # La face F tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[2] = np.rot90(self.state[2], k=-1)

        # U reçoit la colonne de droite de L (inversée) dans sa ligne du bas
        self.state[0, 2] = old.state[4, :, 2][::-1]
        # R reçoit la ligne du bas de U dans sa colonne de gauche
        self.state[1, :, 0] = old.state[0, 2]
        # D reçoit la colonne de gauche de R (inversée) dans sa ligne du haut
        self.state[3, 0] = old.state[1, :, 0][::-1]
        # L reçoit la ligne du haut de D dans sa colonne de droite
        self.state[4, :, 2] = old.state[3, 0]

    def _quarter_turn_B(self) -> None:
        """Quart de tour horaire de la face B, en modifiant le cube sur place."""
        old = self.copy()

        # La face B tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[5] = np.rot90(self.state[5], k=-1)

        # U reçoit la colonne de droite de R dans sa ligne du haut
        self.state[0, 0] = old.state[1, :, 2]
        # L reçoit la ligne du haut de U (inversée) dans sa colonne de gauche
        self.state[4, :, 0] = old.state[0, 0][::-1]
        # D reçoit la colonne de gauche de L dans sa ligne du bas
        self.state[3, 2] = old.state[4, :, 0]
        # R reçoit la ligne du bas de D (inversée) dans sa colonne de droite
        self.state[1, :, 2] = old.state[3, 2][::-1]

    # ----------------------------------------------------------------------
    # Jouer
    # ----------------------------------------------------------------------

    def move(self, name: str) -> None:
        """Applique un mouvement au cube, en le modifiant sur place.

        Accepte les 18 mouvements de faces (U, U', U2...), les tranches (M, E,
        S) et les rotations (x, y, z). Lève ValueError pour un nom inconnu.
        """
        perm = PERMUTATIONS.get(name)
        if perm is None:
            raise ValueError(f"mouvement non géré : {name!r}")
        self.state = self.state.reshape(54)[perm].reshape(6, 3, 3)

    def apply(self, moves: str) -> None:
        """Applique une suite de mouvements (« R U R' U' »), sur place."""
        for move in moves.split():
            self.move(move)

    def scramble(self, n: int, seed: int | None = None) -> list[str]:
        """Applique n mouvements aléatoires et renvoie la liste des mouvements joués.

        Jamais deux coups de suite sur la même face (voir ``scramble.py``). La
        graine permet d'obtenir un mélange reproductible.
        """
        moves_played = random_moves(n, seed=seed)
        for move in moves_played:
            self.move(move)
        return moves_played

    def inverse_sequence(self, moves: list[str]) -> list[str]:
        """Renvoie la suite inverse d'une liste de mouvements.

        Gardée pour compatibilité : elle n'utilise pas le cube. Préférer la
        fonction ``rubiks.moves.inverse_sequence``.
        """
        return _inverse_sequence(moves)


# --------------------------------------------------------------------------
# Les permutations, fabriquées une fois pour toutes au chargement du module
# --------------------------------------------------------------------------


def _face_permutation(face: str) -> np.ndarray:
    """Permutation d'un quart de tour horaire, obtenue en jouant le code de la
    phase 1 sur un cube numéroté."""
    numbered = Cube()
    numbered.state = np.arange(54).reshape(6, 3, 3)
    getattr(numbered, f"_quarter_turn_{face}")()
    return numbered.state.reshape(54).copy()


def _build_permutations() -> dict[str, np.ndarray]:
    """Les permutations des 36 mouvements (18 faces, 9 tranches, 9 rotations)."""
    permutations: dict[str, np.ndarray] = {}
    for face in FACES:
        quarter = _face_permutation(face)
        power = np.arange(54)
        for suffix in sorted(QUARTER_TURNS, key=QUARTER_TURNS.get):
            power = power[quarter]  # un quart de tour de plus : 1, 2 puis 3
            permutations[face + suffix] = power.copy()
    for name in SLICE_MOVES + ROTATION_MOVES:
        permutations[name] = geometry.permutation(name)
    assert set(permutations) == set(ALL_MOVES)
    return permutations


PERMUTATIONS = _build_permutations()


def sequence_order(sequence: str) -> int:
    """Combien de fois faut-il répéter une suite pour revenir au cube de départ ?

    « R U » : 105 fois. On compose les permutations jusqu'à retrouver
    l'identité (au plus 1260 fois : c'est le maximum pour un Rubik's Cube).
    """
    step = np.arange(54)
    for move in sequence.split():
        step = step[PERMUTATIONS[move]]
    identity = np.arange(54)
    current = step.copy()
    for order in range(1, 1261):
        if np.array_equal(current, identity):
            return order
        current = current[step]
    raise AssertionError("ordre supérieur à 1260 : impossible pour un cube 3x3")
