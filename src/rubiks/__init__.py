"""Rubik's Cube 3x3 : logique (cube.py), affichage (render/) et, plus tard, RL.

Les commandes (déclarées dans ``pyproject.toml``, section ``[project.scripts]``) :

    uv run rubiks             le jeu en 3D (ursina)
    uv run rubiks-2d          le patron en 2D (pygame)
    uv run rubiks-3d-pygame   la 3D « à la main », sans bibliothèque 3D (pygame)
    uv run rubiks-terminal    le cube en couleurs dans le terminal

Chaque import d'affichage est placé DANS sa fonction, et pas en haut du
fichier : sinon, « import rubiks.cube » chargerait aussi pygame et ursina (ce
fichier est exécuté avant cube.py), y compris dans les tests et pendant le RL.
"""


def main() -> None:
    """``uv run rubiks`` : le jeu en 3D."""
    from rubiks.render.view3d import run

    run()


def main_2d() -> None:
    """``uv run rubiks-2d`` : le patron déplié en 2D."""
    from rubiks.render.view2d import run

    run()


def main_3d_pygame() -> None:
    """``uv run rubiks-3d-pygame`` : la 3D calculée à la main, dessinée par pygame."""
    from rubiks.render.view3d_pygame import run

    run()


def main_terminal() -> None:
    """``uv run rubiks-terminal`` : le cube dans le terminal."""
    from rubiks.render.terminal import run

    run()
