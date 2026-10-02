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
Notation Singmaster : U D L R F B = quart de tour horaire, en regardant la
face depuis l'extérieur ; ' = anti-horaire ; 2 = demi-tour. 18 mouvements.

``move()`` et ``apply()`` modifient le cube lui-même et ne renvoient rien.
Pour garder l'état d'origine, on utilise ``copy()``, qui fabrique un cube
indépendant (le tableau numpy est copié, pas partagé).
"""

import numpy as np
import random

MOVES = (
    "U",
    "U'",
    "U2",
    "R",
    "R'",
    "R2",
    "F",
    "F'",
    "F2",
    "D",
    "D'",
    "D2",
    "L",
    "L'",
    "L2",
    "B",
    "B'",
    "B2",
)


class Cube:
    """Un rubik's cube 3x3 (représentation décrite en haut)"""

    def __init__(self) -> None:
        """Créer un cube résolu: la face i est entièrement de la couleur i."""
        self.state = np.zeros((6, 3, 3), dtype=int)
        for face in range(6):
            self.state[face] = face

    def is_solved(self) -> bool:
        """Renvoie True si chaque face est d'une seule couleur."""
        for face in self.state:
            if not np.all(face == face[1, 1]):
                return False
        return True

    def copy(self) -> "Cube":
        """Fabrique un nouveau cube dont le tableau est une copie de celui ci"""
        new_cube = Cube()
        new_cube.state = self.state.copy()
        return new_cube

    def __str__(self) -> str:
        """Renvoie le patron déplié du cube, une lettre par couleur (W R G Y O B)."""
        letters = "WRGYOB"
        gap = "  "
        indent = " " * (5 + len(gap))  # 5 = largeur d'une face ("W W W")

        def row(face: int, line: int) -> str:
            return " ".join(letters[color] for color in self.state[face, line])

        lines = []
        for line in range(3):  # U, en haut
            lines.append(indent + row(0, line))
        for line in range(3):  # L F R B, côte à côte
            lines.append(gap.join(row(face, line) for face in (4, 2, 1, 5)))
        for line in range(3):  # D, en bas
            lines.append(indent + row(3, line))
        return "\n".join(lines)

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
        # Copie de l'état de départ : on lit dedans, on écrit dans self
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
        # Copie de l'état de départ : on lit dedans, on écrit dans self
        old = self.copy()

        # La face R tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[1] = np.rot90(self.state[1], k=-1)

        # Chaque face reçoit la colonne de droite de la face d'en dessous
        # sauf D qui recoit la colonne gauche de B inversée
        self.state[0, ::, 2] = old.state[2, ::, 2]  # U reçoit la colonne droite de F
        self.state[5, ::, 0] = old.state[0, ::, 2][
            ::-1
        ]  # B reçoit la colonne droite de U inversée dans sa colonne de gauche
        self.state[3, ::, 2] = old.state[5, ::, 0][
            ::-1
        ]  # D reçoit la colonne gauche de B inversée
        self.state[2, ::, 2] = old.state[3, ::, 2]  # F reçoit la colonne droite de D

    def _quarter_turn_L(self) -> None:
        """Quart de tour horaire de la face L, en modifiant le cube sur place."""
        # Copie de l'état de départ : on lit dedans, on écrit dans self
        old = self.copy()

        # La face L tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[4] = np.rot90(self.state[4], k=-1)

        # Chaque face reçoit la colonne de gauche de la face d'au dessus
        # sauf U qui recoit la colonne droite de B inversée
        self.state[0, ::, 0] = old.state[5, ::, 2][
            ::-1
        ]  # U reçoit la colonne droite de B à l'envers dans sa colonne de gauche
        self.state[5, ::, 2] = old.state[3, ::, 0][
            ::-1
        ]  # B reçoit la colonne gauche de D inversée dans sa colonne de droite
        self.state[3, ::, 0] = old.state[2, ::, 0]  # D reçoit la colonne gauche de F
        self.state[2, ::, 0] = old.state[0, ::, 0]  # F reçoit la colonne gauche de U

    def _quarter_turn_F(self) -> None:
        """Quart de tour de la face F, en modifiant le cube sur place."""
        # Copie de l'état de départ : on lit dedans, on écrit dans self
        old = self.copy()

        # La face F tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[2] = np.rot90(self.state[2], k=-1)

        # U recoit la colonne de droite de L dans sa ligne du bas
        self.state[0, 2] = old.state[4, :, 2][::-1]
        # R recoit la ligne du bas de U dans sa colonne de gauche
        self.state[1, :, 0] = old.state[0, 2]
        # D recoit la colonne de gauche de R dans sa ligne du haut
        self.state[3, 0] = old.state[1, :, 0][::-1]
        # L recoit la ligne du haut de D dans sa colonne de droite
        self.state[4, :, 2] = old.state[3, 0]

    def _quarter_turn_B(self) -> None:
        """Quart de tour de la face B, en modifiant le cube sur place."""
        # Copie de l'état de départ : on lit dedans, on écrit dans self
        old = self.copy()

        # La face B tourne sur elle-même d'un quart de tour horaire (k=-1)
        self.state[5] = np.rot90(self.state[5], k=-1)

        # U recoit la colonne de droite de R dans sa ligne du haut
        self.state[0, 0] = old.state[1, :, 2]
        # L recoit la ligne du haut de U dans sa colonne de gauche
        self.state[4, :, 0] = old.state[0, 0][::-1]
        # D recoit la colonne de gauche de L dans sa ligne du bas
        self.state[3, 2] = old.state[4, :, 0]
        # R recoit la ligne du bas de D dans sa colonne de gauche
        self.state[1, :, 2] = old.state[3, 2][::-1]

    def move(self, name: str) -> None:
        """Applique un mouvement au cube, en le modifiant sur place (U, U', U2)."""
        face, suffix = name[:1], name[1:]
        quarter_turns = {"": 1, "2": 2, "'": 3}
        if face not in ("U", "D", "R", "L", "F", "B") or suffix not in quarter_turns:
            raise ValueError(f"mouvement non géré : {name!r}")

        for _ in range(quarter_turns[suffix]):
            if face == "U":
                self._quarter_turn_U()
            elif face == "D":
                self._quarter_turn_D()
            elif face == "R":
                self._quarter_turn_R()
            elif face == "L":
                self._quarter_turn_L()
            elif face == "F":
                self._quarter_turn_F()
            elif face == "B":
                self._quarter_turn_B()

    def apply(self, moves: str) -> None:
        """Applique une suite de mouvements au cube, en le modifiant sur place"""
        moves_list = str.split(moves)
        for move in moves_list:
            self.move(move)

    def scramble(self, n: int, seed: int | None = None) -> list[str]:
        """Applique n mouvements aléatoires et renvoie la liste des mouvements joués.

        La graine permet d'obtenir un mélange reproductible : deux appels avec
        la même graine produisent la même suite de mouvements.
        """
        generator = random.Random(seed)
        moves_played = []

        for _ in range(n):
            move = generator.choice(MOVES)
            moves_played.append(move)
            self.move(move)

        return moves_played

    def inverse_sequence(self, moves: list) -> list[str]:
        """Applique la suite inverse de mouvement d'une liste"""

        def inverse_move(self, move: str) -> str:
            """Renvoie le mouvement inverse d'un mouvement"""
            if move.endswith("2"):
                return move
            elif move.endswith("'"):
                return move[:1]
            else:
                return move + "'"

        return [inverse_move(move) for move in reversed(moves)]
