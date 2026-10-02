"""Tests de la séparation entre la logique (cube, règles du jeu) et l'affichage."""

import subprocess
import sys

import pytest


@pytest.mark.parametrize("module", ["rubiks.cube", "rubiks.game"])
def test_logic_modules_do_not_load_pygame(module):
    """Importer le cube ou les règles du jeu ne doit pas charger pygame.

    Le test lance un Python neuf (dans lequel rien n'est encore importé), y
    importe le module, puis regarde si pygame fait partie des modules chargés.
    """
    code = f"import sys, {module}; print('pygame' in sys.modules)"

    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "False"


def test_view2d_module_can_be_imported():
    """Le module d'affichage s'importe sans erreur (pygame est bien installé)."""
    from rubiks.render import view2d

    assert callable(view2d.run)
