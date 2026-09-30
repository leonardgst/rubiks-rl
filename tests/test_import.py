import rubiks

from rubiks.cube import Cube


def test_import_rubiks():
    assert hasattr(rubiks, "main")