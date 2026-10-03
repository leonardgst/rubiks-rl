"""Fixtures partagées par tous les fichiers de tests.

Une fixture est une fonction marquée ``@pytest.fixture`` : un test qui a un
paramètre du même nom reçoit ce qu'elle renvoie, tout neuf pour chaque test.
pytest trouve ce fichier tout seul (il s'appelle forcément ``conftest.py``).
"""

import numpy as np
import pytest
from rubiks.cube import Cube


@pytest.fixture
def numbered_cube() -> Cube:
    """Un cube dont les 54 cases portent des numéros tous différents (0 à 53).

    Sur un cube résolu, une bande d'une seule couleur reste identique même
    retournée : un bug d'ordre passerait inaperçu. Avec des numéros, chaque
    case est reconnaissable et le moindre déplacement se voit.
    """
    cube = Cube()
    cube.state = np.arange(54).reshape(6, 3, 3)
    return cube


class FakeClock:
    """Une fausse horloge pour tester le chrono : on avance le temps à la main."""

    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock() -> FakeClock:
    """Une horloge qui ne bouge que quand le test le décide."""
    return FakeClock()
