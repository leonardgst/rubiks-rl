"""Affichage 2D du cube dans une fenêtre pygame (phase 2).

La fenêtre montre le patron déplié en croix, avec la même orientation que la
docstring de ``cube.py`` et que ``print(cube)`` :

U
L F R B
D

Le patron tient dans une grille de 12 colonnes x 9 lignes de cases. Chaque face
occupe un carré de 3 x 3 cases, qui commence à un décalage qui lui est propre
(``FACE_OFFSETS``).

L'affichage LIT ``cube.state`` ; il ne le modifie jamais. Ce module importe
pygame : il ne doit jamais être importé par ``cube.py``.
"""

import pygame

from rubiks.cube import Cube

# --- Dimensions -----------------------------------------------------------
STICKER_SIZE = 40  # côté d'une case du patron, en pixels
STICKER_GAP = 3  # espace entre deux cases, en pixels
MARGIN = 20  # marge autour du patron, en pixels
GRID_COLUMNS = 12  # largeur du patron, en cases (4 faces côte à côte)
GRID_ROWS = 9  # hauteur du patron, en cases (3 faces l'une sous l'autre)

WINDOW_WIDTH = 2 * MARGIN + GRID_COLUMNS * STICKER_SIZE
WINDOW_HEIGHT = 2 * MARGIN + GRID_ROWS * STICKER_SIZE
WINDOW_TITLE = "Rubik's Cube"
FPS = 60  # nombre maximum d'images par seconde

# --- Couleurs (rouge, vert, bleu), de 0 à 255 --------------------------------
BACKGROUND_COLOR = (30, 30, 30)  # gris foncé
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


def draw_cube(screen: pygame.Surface, cube: Cube) -> None:
    """Dessine les 54 cases du cube, en lisant ``cube.state``."""
    side = STICKER_SIZE - STICKER_GAP  # case un peu plus petite que la grille
    for face in range(6):
        for row in range(3):
            for col in range(3):
                x, y = sticker_position(face, row, col)
                color = COLORS[cube.state[face, row, col]]
                pygame.draw.rect(screen, color, (x, y, side, side))


def run(cube: Cube | None = None) -> None:
    """Ouvre la fenêtre et affiche le cube jusqu'à la fermeture.

    Sans argument, on affiche un cube neuf (résolu). On peut aussi passer un
    cube déjà mélangé, par exemple pour vérifier le dessin.
    """
    if cube is None:
        cube = Cube()

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    running = True
    while running:
        # 1. Lire les événements : croix de la fenêtre ou touche Échap
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # 2. Dessiner : fond uni, puis le patron du cube
        screen.fill(BACKGROUND_COLOR)
        draw_cube(screen, cube)

        # 3. Afficher l'image dessinée
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
