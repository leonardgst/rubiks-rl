"""Vue 3D « à la main » dans une fenêtre pygame, sans bibliothèque 3D.

Les calculs (placer, tourner, projeter, trier) sont dans ``scene.py`` ; ce
module ne fait que dessiner les polygones avec ``pygame.draw.polygon`` et lire
le clavier et la souris. Mêmes touches que les autres vues (voir ``game.py``).

Souris :
- clic gauche sur une case + glisser : tourner la couche dans ce sens ;
- clic gauche dans le vide (ou clic droit) + glisser : tourner la caméra ;
- molette : zoomer.

Lancer : ``uv run rubiks-3d-pygame``. F12 enregistre une capture.
"""

import pygame

from rubiks.cube import Cube
from rubiks.game import Command, Game, Player
from rubiks.geometry import STICKERS, best_direction, move_for_drag
from rubiks.render.colors import (
    BACKGROUND_COLOR,
    HELP_COLOR,
    HELP_LINES,
    TEXT_COLOR,
    WIN_COLOR,
    format_time,
    win_message,
)
from rubiks.render.scene import Camera, scene_polygons, screen_directions, sticker_at

WINDOW_WIDTH = 760
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Rubik's Cube (3D pygame)"
FPS = 60
CUBE_SCALE = 100  # taille du cube à l'écran, en pixels par unité
CUBE_CENTER_Y = 290  # hauteur du centre du cube, en pixels (les textes sont dessous)
SCREENSHOT_FILE = "capture-3d-pygame.png"

MARGIN = 16  # marge des textes, en pixels
LINE_HEIGHT = 24
HELP_LINE_HEIGHT = 20
TEXT_SIZE = 24
HELP_TEXT_SIZE = 20
WIN_TEXT_SIZE = 44

ORBIT_SPEED = 0.4  # degrés de caméra par pixel de souris
MIN_PITCH, MAX_PITCH = -89.0, 89.0
ZOOM_STEP = 1.1  # un cran de molette = 10 % plus grand
DRAG_THRESHOLD = 12  # pixels à glisser avant de tourner une couche


def draw_hud(
    screen: pygame.Surface, game: Game, fonts: dict[str, pygame.font.Font]
) -> None:
    """Les textes par-dessus la scène : victoire, coups, chrono, mélange, aide."""
    if game.is_won():
        image = fonts["win"].render(win_message(game.assisted), True, WIN_COLOR)
        screen.blit(image, image.get_rect(midtop=(WINDOW_WIDTH // 2, MARGIN)))
    if game.scramble_moves:
        lines = [f"Coups : {game.moves_played}", format_time(game.elapsed())]
        for i, line in enumerate(lines):
            image = fonts["text"].render(line, True, TEXT_COLOR)
            screen.blit(image, (MARGIN, MARGIN + i * LINE_HEIGHT))
        scramble = "Mélange : " + " ".join(game.scramble_moves)
        image = fonts["help"].render(scramble, True, TEXT_COLOR)
        y = WINDOW_HEIGHT - MARGIN - HELP_LINE_HEIGHT * (len(HELP_LINES) + 1)
        screen.blit(image, (MARGIN, y))
    y = WINDOW_HEIGHT - MARGIN - HELP_LINE_HEIGHT * len(HELP_LINES)
    for line in HELP_LINES:
        screen.blit(fonts["help"].render(line, True, HELP_COLOR), (MARGIN, y))
        y += HELP_LINE_HEIGHT


def draw_scene(screen: pygame.Surface, player: Player, camera: Camera) -> list:
    """Dessine le cube (tel que l'animation le montre) ; renvoie les polygones."""
    polygons = scene_polygons(player.shown_cube, camera, player.move, player.angle())
    for polygon in polygons:  # du plus loin au plus proche : algorithme du peintre
        pygame.draw.polygon(screen, polygon.color, polygon.points)
    return polygons


def run(cube: Cube | None = None) -> None:
    """Ouvre la fenêtre et fait tourner le jeu jusqu'à la fermeture."""
    game = Game(cube)
    player = Player(game)
    camera = Camera(scale=CUBE_SCALE, center=(WINDOW_WIDTH / 2, CUBE_CENTER_Y))

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    fonts = {
        "text": pygame.font.Font(None, TEXT_SIZE),
        "help": pygame.font.Font(None, HELP_TEXT_SIZE),
        "win": pygame.font.Font(None, WIN_TEXT_SIZE),
    }

    polygons: list = []
    dragged_sticker: int | None = None  # case attrapée au clic gauche
    drag_start = (0, 0)
    orbiting = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F12:
                    pygame.image.save(screen, SCREENSHOT_FILE)
                else:
                    shift = bool(event.mod & pygame.KMOD_SHIFT)
                    ctrl = bool(event.mod & pygame.KMOD_CTRL)
                    player.press(pygame.key.name(event.key), shift, ctrl)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
                sticker = sticker_at(polygons, event.pos) if event.button == 1 else None
                if sticker is not None:
                    dragged_sticker, drag_start = sticker, event.pos
                else:
                    orbiting = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button in (1, 3):
                if dragged_sticker is not None:
                    dx, dy = event.pos[0] - drag_start[0], event.pos[1] - drag_start[1]
                    if dx * dx + dy * dy >= DRAG_THRESHOLD**2:
                        directions = screen_directions(dragged_sticker, camera)
                        direction = best_direction(directions, (dx, dy))
                        move = move_for_drag(*STICKERS[dragged_sticker], direction)
                        player.push(Command("move", move=move))
                dragged_sticker = None
                orbiting = False
            elif event.type == pygame.MOUSEMOTION and orbiting:
                camera.yaw += event.rel[0] * ORBIT_SPEED
                camera.pitch += event.rel[1] * ORBIT_SPEED
                camera.pitch = min(max(camera.pitch, MIN_PITCH), MAX_PITCH)
            elif event.type == pygame.MOUSEWHEEL:
                camera.scale *= ZOOM_STEP**event.y

        player.update(clock.get_time() / 1000)

        screen.fill(BACKGROUND_COLOR)
        polygons = draw_scene(screen, player, camera)
        draw_hud(screen, game, fonts)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
