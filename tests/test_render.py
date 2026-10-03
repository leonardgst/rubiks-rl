"""Tests de la séparation entre la logique (cube, règles du jeu) et l'affichage."""

import subprocess
import sys

import pytest

PURE_MODULES = [
    "rubiks.cube",
    "rubiks.moves",
    "rubiks.scramble",
    "rubiks.geometry",
    "rubiks.game",
    "rubiks.render.colors",
    "rubiks.render.scene",
    "rubiks.render.terminal",
]


@pytest.mark.parametrize("module", PURE_MODULES)
@pytest.mark.parametrize("library", ["pygame", "ursina"])
def test_logic_modules_do_not_load_display_libraries(module, library):
    """Importer la logique ne doit charger ni pygame ni ursina.

    Le test lance un Python neuf (dans lequel rien n'est encore importé), y
    importe le module, puis regarde si la bibliothèque fait partie des modules
    chargés. Indispensable pour le RL : l'entraînement n'affiche rien et doit
    rester rapide et léger.
    """
    code = f"import sys, {module}; print({library!r} in sys.modules)"

    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "False"


def test_view2d_module_can_be_imported():
    """Le module d'affichage 2D s'importe sans erreur (pygame est bien installé)."""
    from rubiks.render import view2d

    assert callable(view2d.run)


def test_view3d_pygame_module_can_be_imported():
    """La vue 3D « à la main » s'importe sans erreur."""
    from rubiks.render import view3d_pygame

    assert callable(view3d_pygame.run)


def test_entry_points_are_callable():
    """Les commandes de pyproject.toml (uv run rubiks...) existent toutes.

    On n'importe pas ursina ici : les imports sont dans les fonctions.
    """
    import rubiks

    for name in ("main", "main_2d", "main_3d_pygame", "main_terminal"):
        assert callable(getattr(rubiks, name))
