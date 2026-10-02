"""Rubik's Cube 3x3 : logique (cube.py), affichage (render/) et, plus tard, RL."""


def main() -> None:
    """Point d'entrée de ``uv run rubiks`` : lance l'affichage 2D."""
    # Import placé DANS la fonction, et pas en haut du fichier : sinon,
    # « import rubiks.cube » chargerait aussi pygame (ce fichier est exécuté
    # avant cube.py), y compris dans les tests et plus tard pendant le RL.
    from rubiks.render.view2d import run

    run()
