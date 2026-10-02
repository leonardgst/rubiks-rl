"""Règles du jeu au clavier, sans aucun affichage (phase 2).

Ce module dit ce que fait chaque touche ; les affichages (2D aujourd'hui, 3D en
phase 3) se contentent de lui transmettre les touches et de dessiner le
résultat. Il n'importe pas pygame : il se teste sans ouvrir de fenêtre.

Touches (noms donnés par ``pygame.key.name``, toujours en minuscule) :

u d l r f b quart de tour horaire de la face
Maj + lettre quart de tour anti-horaire (l'inverse)
space mélanger
backspace revenir à un cube neuf
"""

from rubiks.cube import Cube

SCRAMBLE_LENGTH = 5  # nombre de coups d'un mélange (petit, pour pouvoir le refaire)

# Nom de la touche -> face du cube
KEY_TO_FACE = {"u": "U", "d": "D", "l": "L", "r": "R", "f": "F", "b": "B"}
SCRAMBLE_KEY = "space"
RESET_KEY = "backspace"


def key_to_move(key_name: str, shift: bool) -> str | None:
    """Renvoie le mouvement d'une touche, ou None si elle n'en est pas un.

    "u" donne "U" ; avec Maj, "U'" (l'inverse). Une autre touche donne None.
    """
    face = KEY_TO_FACE.get(key_name)
    if face is None:
        return None
    return face + "'" if shift else face


class Game:
    """Une partie : le cube, le dernier mélange et le nombre de coups joués."""

    def __init__(self, cube: Cube | None = None) -> None:
        """Commence une partie, avec un cube neuf ou le cube donné."""
        self.cube = cube if cube is not None else Cube()
        self.scramble_moves: list[str] = []  # vide tant qu'on n'a pas mélangé
        self.moves_played = 0  # coups joués depuis le dernier mélange

    def press(self, key_name: str, shift: bool = False) -> None:
        """Applique l'effet d'une touche. Une touche inconnue ne fait rien."""
        if key_name == SCRAMBLE_KEY:
            self.scramble()
        elif key_name == RESET_KEY:
            self.reset()
        else:
            move = key_to_move(key_name, shift)
            if move is not None:
                self.cube.move(move)
                self.moves_played += 1

    def scramble(self, seed: int | None = None) -> None:
        """Repart d'un cube neuf et le mélange de SCRAMBLE_LENGTH coups.

        Partir d'un cube neuf garantit que la suite affichée suffit à le refaire.
        Des coups peuvent s'annuler (« R R' ») : si le mélange redonne un cube
        résolu, on recommence, sinon « Résolu ! » s'afficherait aussitôt.
        Sans graine, chaque mélange est différent ; la graine sert aux tests.
        """
        self.cube = Cube()
        self.scramble_moves = self.cube.scramble(SCRAMBLE_LENGTH, seed=seed)
        while self.cube.is_solved():
            seed = None if seed is None else seed + 1  # reste reproductible
            self.cube = Cube()
            self.scramble_moves = self.cube.scramble(SCRAMBLE_LENGTH, seed=seed)
        self.moves_played = 0

    def reset(self) -> None:
        """Revient à un cube neuf, comme au lancement.

        On remplace l'objet par un Cube() neuf : l'affichage relit self.cube à
        chaque image, il verra donc le nouveau cube.
        """
        self.cube = Cube()
        self.scramble_moves = []
        self.moves_played = 0

    def is_won(self) -> bool:
        """True si le cube a été mélangé, puis résolu.

        Un cube neuf est résolu, mais on n'a rien gagné : d'où la condition
        « un mélange a eu lieu ».
        """
        return bool(self.scramble_moves) and self.cube.is_solved()
