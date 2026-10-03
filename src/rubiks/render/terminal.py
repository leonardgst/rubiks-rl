"""Affichage du cube dans le terminal, en couleurs (codes ANSI).

Un second affichage, qui n'a besoin que de ``cube.state`` : la preuve que la
logique et l'affichage sont bien séparés. Aucune bibliothèque à installer.

Lancer : ``uv run rubiks-terminal``, puis taper des mouvements (« R U R' U' »),
``melange``, ``solution``, ``neuf`` ou ``q`` pour quitter.

Code ANSI : ``"\\033[48;2;R;G;Bm"`` change la couleur de fond (en 24 bits),
``"\\033[0m"`` remet les couleurs par défaut. La plupart des terminaux récents
les comprennent (y compris celui de Windows 10 et plus).
"""

from rubiks.cube import Cube
from rubiks.game import Game
from rubiks.moves import ALL_MOVES
from rubiks.render.colors import COLORS

RESET = "\033[0m"
STICKER = "  "  # une case = deux espaces sur fond coloré (presque carré)
GAP = " "  # espace entre deux faces


def colored(color: int) -> str:
    """Une case de la couleur ``color`` (0 à 5)."""
    red, green, blue = COLORS[color]
    return f"\033[48;2;{red};{green};{blue}m{STICKER}{RESET}"


def to_ansi(cube: Cube) -> str:
    """Le patron déplié en couleurs, même disposition que ``print(cube)``."""

    def row(face: int, line: int) -> str:
        return "".join(colored(color) for color in cube.state[face, line])

    indent = " " * (3 * len(STICKER) + len(GAP))
    lines = [indent + row(0, line) for line in range(3)]
    lines += [GAP.join(row(face, line) for face in (4, 2, 1, 5)) for line in range(3)]
    lines += [indent + row(3, line) for line in range(3)]
    return "\n".join(lines)


def run() -> None:
    """Petite boucle : lire une ligne, jouer, afficher."""
    game = Game()
    print("Mouvements (R U R' U'), melange, solution, neuf, q pour quitter.")
    while True:
        print(to_ansi(game.cube))
        if game.is_won():
            print("Résolu !")
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if line in ("q", "quit", "exit"):
            break
        if line == "melange":
            game.scramble()
            print("Mélange :", " ".join(game.scramble_moves))
        elif line == "solution":
            print("Solution :", " ".join(game.solution()) or "(rien à faire)")
        elif line == "neuf":
            game.reset()
        else:
            moves = line.split()
            unknown = [move for move in moves if move not in ALL_MOVES]
            if unknown:  # on vérifie tout avant de jouer quoi que ce soit
                print("Mouvement inconnu :", " ".join(unknown))
                continue
            for move in moves:
                game.play(move)


if __name__ == "__main__":
    run()
