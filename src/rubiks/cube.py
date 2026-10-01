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
