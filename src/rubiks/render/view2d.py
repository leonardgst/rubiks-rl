"""Affichage 2D du cube dans une fenêtre pygame (phase 2).

Pour l'instant (étape C), la fenêtre est vide : elle s'ouvre, et se ferme avec
la croix ou la touche Échap. Le patron du cube et le clavier viendront aux
étapes suivantes.

Ce module importe pygame : il ne doit jamais être importé par ``cube.py``.
"""

import pygame

WINDOW_WIDTH = 640 # largeur de la fenêtre, en pixels
WINDOW_HEIGHT = 480 # hauteur de la fenêtre, en pixels
WINDOW_TITLE = "Rubik's Cube"
BACKGROUND_COLOR = (30, 30, 30) # gris foncé (rouge, vert, bleu)
FPS = 60 # nombre maximum d'images par seconde


def run() -> None:
    """Ouvre la fenêtre et fait tourner la boucle de jeu jusqu'à la fermeture."""
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

        # 2. Dessiner : un fond uni (le cube viendra à l'étape D)
        screen.fill(BACKGROUND_COLOR)

        # 3. Afficher l'image dessinée
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
