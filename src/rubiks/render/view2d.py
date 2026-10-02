"""Affichage 2D du cube dans une fenêtre pygame (phase 2).

La fenêtre montre le patron déplié en croix, avec la même orientation que la
docstring de ``cube.py`` et que ``print(cube)`` :

U Résolu !
L F R B
D Coups : 3
Mélange : ...
aide (touches)

Le patron tient dans une grille de 12 colonnes x 9 lignes de cases. Chaque face
occupe un carré de 3 x 3 cases, qui commence à un décalage qui lui est propre
(``FACE_OFFSETS``). Sous le patron, une bande de texte.

Ce que fait chaque touche est décidé par ``rubiks.game`` ; ce module ne fait
que transmettre les touches et dessiner. Il importe pygame : il ne doit jamais
être importé par ``cube.py`` ni par ``game.py``.
"""

import pygame

from rubiks.cube import Cube
from rubiks.game import Game

# --- Dimensions -----------------------------------------------------------
STICKER_SIZE = 40  # côté d'une case du patron, en pixels
STICKER_GAP = 3  # espace entre deux cases, en pixels
MARGIN = 20  # marge autour du patron, en pixels
GRID_COLUMNS = 12  # largeur du patron, en cases (4 faces côte à côte)
GRID_ROWS = 9  # hauteur du patron, en cases (3 faces l'une sous l'autre)
TEXT_AREA_HEIGHT = 140  # bande de texte sous le patron, en pixels
LINE_HEIGHT = 24  # hauteur d'une ligne de texte, en pixels
MOVES_PER_LINE = 12  # coups du mélange affichés par ligne

PATTERN_HEIGHT = 2 * MARGIN + GRID_ROWS * STICKER_SIZE
WINDOW_WIDTH = 2 * MARGIN + GRID_COLUMNS * STICKER_SIZE
WINDOW_HEIGHT = PATTERN_HEIGHT + TEXT_AREA_HEIGHT
WINDOW_TITLE = "Rubik's Cube"
FPS = 60  # nombre maximum d'images par seconde

# --- Textes ------------------------------------------------------------------
TEXT_SIZE = 24  # taille de la police des textes courants
WIN_TEXT_SIZE = 56  # taille du message « Résolu ! »
HELP_LINES = (
    "U D L R F B : tourner Maj + lettre : sens inverse",
    "Espace : mélanger Retour arrière : recommencer",
    "Échap : quitter",
)

# --- Couleurs (rouge, vert, bleu), de 0 à 255 --------------------------------
BACKGROUND_COLOR = (30, 30, 30)  # gris foncé
TEXT_COLOR = (230, 230, 230)  # gris très clair
HELP_COLOR = (150, 150, 150)  # gris moyen
WIN_COLOR = (90, 220, 120)  # vert clair
# COLORS[i] = couleur de la face i du cube résolu (ordre U R F D L B de cube.py)
COLORS = (
    (255, 255, 255),  # 0 U : blanc
    (200, 20, 20),  # 1 R : rouge
    (20, 160, 60),  # 2 F : vert
    (255, 215, 0),  # 3 D : jaune
    (255, 120, 0),  # 4 L : orange
    (20, 70, 200),  # 5 B : bleu
)

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


def draw_cube(screen: pygame.Surface, cube: Cube) -> None:
    """Dessine les 54 cases du cube, en lisant ``cube.state``."""
    side = STICKER_SIZE - STICKER_GAP  # case un peu plus petite que la grille
    for face in range(6):
        for row in range(3):
            for col in range(3):
                x, y = sticker_position(face, row, col)
                color = COLORS[cube.state[face, row, col]]
                pygame.draw.rect(screen, color, (x, y, side, side))


def draw_texts(
    screen: pygame.Surface,
    game: Game,
    font: pygame.font.Font,
    win_font: pygame.font.Font,
) -> None:
    """Dessine les textes : « Résolu ! », coups joués, mélange et aide."""
    # Coin en haut à droite du patron (vide) : le message de victoire
    if game.is_won():
        image = win_font.render("Résolu !", True, WIN_COLOR)
        x, y = sticker_position(1, 0, 0)  # au-dessus de la face R
        screen.blit(image, (x, MARGIN + STICKER_SIZE))

    # Coin en bas à droite du patron (vide) : le nombre de coups depuis le mélange
    if game.scramble_moves:
        image = font.render(f"Coups : {game.moves_played}", True, TEXT_COLOR)
        x, _ = sticker_position(1, 0, 0)  # aligné sur la face R
        _, y = sticker_position(3, 0, 0)  # à la hauteur de la face D
        screen.blit(image, (x + STICKER_GAP * 3, y + STICKER_GAP * 3))

    # Bande sous le patron : la suite du mélange, puis l'aide
    y = PATTERN_HEIGHT - MARGIN // 2
    for line in scramble_lines(game.scramble_moves):
        screen.blit(font.render(line, True, TEXT_COLOR), (MARGIN, y))
        y += LINE_HEIGHT
    y = WINDOW_HEIGHT - MARGIN // 2 - LINE_HEIGHT * len(HELP_LINES)
    for line in HELP_LINES:
        screen.blit(font.render(line, True, HELP_COLOR), (MARGIN, y))
        y += LINE_HEIGHT


def run(cube: Cube | None = None) -> None:
    """Ouvre la fenêtre et fait tourner le jeu jusqu'à la fermeture.

    Sans argument, la partie commence avec un cube neuf (résolu). On peut aussi
    passer un cube déjà mélangé, par exemple pour vérifier le dessin.
    """
    game = Game(cube)

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, TEXT_SIZE)  # créées une seule fois,
    win_font = pygame.font.Font(None, WIN_TEXT_SIZE)  # avant la boucle

    running = True
    while running:
        # 1. Lire les événements : fermeture, sinon la touche va au jeu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    # KEYDOWN arrive une seule fois par appui : un appui = un coup
                    key_name = pygame.key.name(event.key)
                    shift = bool(event.mod & pygame.KMOD_SHIFT)  # & et pas ==
                    game.press(key_name, shift)

        # 2. Dessiner : fond uni, patron, textes
        screen.fill(BACKGROUND_COLOR)
        draw_cube(screen, game.cube)
        draw_texts(screen, game, font, win_font)

        # 3. Afficher l'image dessinée
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
