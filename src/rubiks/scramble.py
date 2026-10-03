"""Mélanges aléatoires : des suites de mouvements, sans cube.

Un bon mélange ne gaspille pas de coups : « R puis R' » s'annule et
« R puis R2 » fait simplement R'. On interdit donc deux coups de suite sur la
même face. (Les faces opposées, comme R puis L, restent permises : elles
commutent, mais ne s'annulent pas.)
"""

import random

from rubiks.moves import MOVES


def random_moves(n: int, seed: int | None = None) -> list[str]:
    """Renvoie n mouvements aléatoires parmi les 18, jamais deux fois la même face
    de suite.

    La graine rend le mélange reproductible : même graine, même suite.
    """
    generator = random.Random(seed)
    moves: list[str] = []
    for _ in range(n):
        previous_face = moves[-1][0] if moves else None
        choices = [move for move in MOVES if move[0] != previous_face]
        moves.append(generator.choice(choices))
    return moves
