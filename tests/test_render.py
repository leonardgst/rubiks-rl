"""Tests de la séparation entre la logique du cube et l'affichage."""

import subprocess
import sys


def test_importing_cube_does_not_load_pygame():
    """Importer le cube ne doit pas charger pygame.

    Le test lance un Python neuf (dans lequel rien n'est encore importé), y
    importe rubiks.cube, puis regarde si pygame fait partie des modules chargés.
    """
    code = "import sys, rubiks.cube; print('pygame' in sys.modules)"

    result = subprocess.run(
    [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "False"


def test_view2d_module_can_be_imported():
    """Le module d'affichage s'importe sans erreur (pygame est bien installé)."""
    from rubiks.render import view2d

    assert callable(view2d.run)