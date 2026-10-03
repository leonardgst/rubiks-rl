"""Affichage 2D du cube dans une fenêtre pygame (phase 2).

La fenêtre montre le patron déplié en croix, avec la même orientation que la
docstring de ``cube.py`` et que ``print(cube)`` :

         U          Résolu !
      L  F  R  B
         D          Coups : 3
                    0:12.4
    Mélange : ...
    aide (touches)

Le patron tient dans une grille de 12 colonnes x 9 lignes de cases. Chaque face
occupe un carré de 3 x 3 cases, qui commence à un décalage qui lui est propre
(``FACE_OFFSETS``). Sous le patron, une bande de texte.

Ce que fait chaque touche est décidé par ``rubiks.game`` ; ce module ne fait
que transmettre les touches et dessiner. Il importe pygame : il ne doit jamais
être importé par ``cube.py`` ni par ``game.py``.

Lancer : ``uv run rubiks-2d``. F12 enregistre une capture (``capture-2d.png``).
"""

import pygame

from rubiks.cube import Cube
from rubiks.game import Game, Player, key_to_command
from rubiks.render.colors import (
    BACKGROUND_COLOR,
    COLORS,
    HELP_COLOR,
    HELP_LINES,
    TEXT_COLOR,
    WIN_COLOR,
    format_time,
    win_message,
)

__all__ = ["COLORS", "HELP_LINES", "run", "scramble_lines", "sticker_position"]

# --- Dimensions -----------------------------------------------------------
STICKER_SIZE = 44  # côté d'une case du patron, en pixels
STICKER_GAP = 3  # espace entre deux cases, en pixels
MARGIN = 20  # marge autour du patron, en pixels
GRID_COLUMNS = 12  # largeur du patron, en cases (4 faces côte à côte)
GRID_ROWS = 9  # hauteur du patron, en cases (3 faces l'une sous l'autre)
LINE_HEIGHT = 24  # hauteur d'une ligne de texte, en pixels
HELP_LINE_HEIGHT = 20  # hauteur d'une ligne d'aide, en pixels
MOVES_PER_LINE = 13  # coups du mélange affichés par ligne
SCRAMBLE_LINES = 2  # lignes réservées au mélange (25 coups au plus)

PATTERN_HEIGHT = 2 * MARGIN + GRID_ROWS * STICKER_SIZE
TEXT_AREA_HEIGHT = (
    SCRAMBLE_LINES * LINE_HEIGHT + len(HELP_LINES) * HELP_LINE_HEIGHT + MARGIN
)
WINDOW_WIDTH = 2 * MARGIN + GRID_COLUMNS * STICKER_SIZE
WINDOW_HEIGHT = PATTERN_HEIGHT + TEXT_AREA_HEIGHT
WINDOW_TITLE = "Rubik's Cube (2D)"
FPS = 60  # nombre maximum d'images par seconde
SECONDS_PER_MOVE = 0.12  # rythme de la solution, coup par coup
SCREENSHOT_FILE = "capture-2d.png"

# --- Textes ------------------------------------------------------------------
TEXT_SIZE = 24  # taille de la police des textes courants
HELP_TEXT_SIZE = 20  # taille de la police de l'aide
WIN_TEXT_SIZE = 44  # taille du message « Résolu ! »

# --- Disposition du patron ---------------------------------------------------
# FACE_OFFSETS[face] = (colonne, ligne) de la case en haut à gauche de la face,
# en cases (pas en pixels), dans la grille 12 x 9.
FACE_OFFSETS = {
    0: (3, 0),  # U : en haut, au-dessus de F
    1: (6, 3),  # R : à droite de F
    2: (3, 3),  # F : au centre
    3: (3, 6),  # D : en bas, sous F
    4: (0, 3),  # L : à gauche de F
    5: (9, 3),  # B : à droite de R
}


def sticker_position(face: int, row: int, col: int) -> tuple[int, int]:
    """Renvoie (x, y), en pixels, du coin haut gauche de la case (face, row, col).

    Attention à l'ordre : dans ``cube.state`` on écrit [ligne, colonne], mais à
    l'écran on écrit (x, y), c'est-à-dire (colonne, ligne).
    """
    offset_col, offset_row = FACE_OFFSETS[face]
    x = MARGIN + (offset_col + col) * STICKER_SIZE
    y = MARGIN + (offset_row + row) * STICKER_SIZE
    return x, y


def scramble_lines(moves: list[str]) -> list[str]:
    """Découpe la suite du mélange en lignes de MOVES_PER_LINE coups au plus.

    La première ligne commence par « Mélange : ». Sans mélange : aucune ligne.
    """
    if not moves:
        return []
    chunks = [
        " ".join(moves[i : i + MOVES_PER_LINE])
        for i in range(0, len(moves), MOVES_PER_LINE)
    ]
    return ["Mélange : " + chunks[0]] + chunks[1:]


class Fonts:
    """Les polices, créées une seule fois (les recréer à chaque image est lent)."""

    def __init__(self) -> None:
        pygame.font.init()
        self.text = pygame.font.Font(None, TEXT_SIZE)
        self.help = pygame.font.Font(None, HELP_TEXT_SIZE)
        self.win = pygame.font.Font(None, WIN_TEXT_SIZE)


def draw_cube(screen: pygame.Surface, cube: Cube) -> None:
    """Dessine les 54 cases du cube, en lisant ``cube.state``."""
    side = STICKER_SIZE - STICKER_GAP  # case un peu plus petite que la grille
    for face in range(6):
        for row in range(3):
            for col in range(3):
                x, y = sticker_position(face, row, col)
                color = COLORS[cube.state[face, row, col]]
                pygame.draw.rect(screen, color, (x, y, side, side), border_radius=4)


def draw_texts(screen: pygame.Surface, game: Game, fonts: Fonts) -> None:
    """Dessine les textes : victoire, coups, chrono, mélange et aide."""
    right_x, _ = sticker_position(1, 0, 0)  # les coins vides, à droite du patron
    _, top_y = sticker_position(0, 0, 0)
    _, bottom_y = sticker_position(3, 0, 0)

    # Coin en haut à droite : le message de victoire
    if game.is_won():
        image = fonts.win.render(win_message(game.assisted), True, WIN_COLOR)
        screen.blit(image, (right_x, top_y + STICKER_SIZE))

    # Coin en bas à droite : coups et chrono depuis le mélange
    if game.scramble_moves:
        lines = [f"Coups : {game.moves_played}", format_time(game.elapsed())]
        for i, line in enumerate(lines):
            image = fonts.text.render(line, True, TEXT_COLOR)
            screen.blit(image, (right_x + STICKER_GAP * 3, bottom_y + i * LINE_HEIGHT))

    # Bande sous le patron : la suite du mélange, puis l'aide
    y = PATTERN_HEIGHT - MARGIN // 2
    for line in scramble_lines(game.scramble_moves):
        screen.blit(fonts.text.render(line, True, TEXT_COLOR), (MARGIN, y))
        y += LINE_HEIGHT
    y = WINDOW_HEIGHT - MARGIN // 2 - HELP_LINE_HEIGHT * len(HELP_LINES)
    for line in HELP_LINES:
        screen.blit(fonts.help.render(line, True, HELP_COLOR), (MARGIN, y))
        y += HELP_LINE_HEIGHT


def draw_frame(screen: pygame.Surface, game: Game, fonts: Fonts) -> None:
    """Dessine une image complète : fond uni, patron, textes."""
    screen.fill(BACKGROUND_COLOR)
    draw_cube(screen, game.cube)
    draw_texts(screen, game, fonts)


def run(cube: Cube | None = None) -> None:
    """Ouvre la fenêtre et fait tourner le jeu jusqu'à la fermeture.

    Sans argument, la partie commence avec un cube neuf (résolu). On peut aussi
    passer un cube déjà mélangé, par exemple pour vérifier le dessin.
    """
    game = Game(cube)
    # Pas d'animation en 2D : la file d'attente sert seulement à jouer la
    # solution coup par coup, au lieu de tout d'un coup
    player = Player(game, seconds_per_quarter_turn=SECONDS_PER_MOVE)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    fonts = Fonts()

    running = True
    while running:
        # 1. Lire les événements : fermeture, capture, sinon la touche va au jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F12:
                    pygame.image.save(screen, SCREENSHOT_FILE)
                else:
                    # KEYDOWN arrive une seule fois par appui : un appui = un coup
                    key_name = pygame.key.name(event.key)
                    shift = bool(event.mod & pygame.KMOD_SHIFT)  # & et pas ==
                    ctrl = bool(event.mod & pygame.KMOD_CTRL)
                    command = key_to_command(key_name, shift, ctrl)
                    if command is None:
                        continue
                    # Un coup est joué tout de suite ; la solution (et ce qui est
                    # tapé pendant qu'elle se joue) passe par la file d'attente
                    if player.busy or command.kind == "solve":
                        player.push(command)
                    else:
                        game.execute(command)

        # 2. Faire avancer la file d'attente (en secondes : tick renvoie des ms)
        player.update(clock.get_time() / 1000)

        # 3. Dessiner, puis afficher
        draw_frame(screen, game, fonts)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
