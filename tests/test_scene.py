"""Tests de la 3D « à la main » (rubiks.render.scene) : que des calculs."""

import numpy as np
import pytest

from rubiks.cube import Cube
from rubiks.geometry import STICKERS, best_direction, move_for_drag, sticker_location
from rubiks.render.scene import (
    CUBIE_HALF,
    Camera,
    point_in_polygon,
    scene_polygons,
    screen_directions,
    sticker_at,
)

F = 2


def test_the_center_of_the_cube_is_the_center_of_the_screen():
    """L'origine se projette au centre de l'écran, à profondeur 0."""
    camera = Camera(center=(300, 200))

    assert camera.project(np.zeros(3)) == (300, 200, 0)


def test_far_points_look_closer_to_the_center():
    """Perspective : un point plus loin paraît plus près du centre."""
    camera = Camera(center=(0, 0))
    near_x, _, _ = camera.project(np.array([1.0, 0.0, 1.0]))
    far_x, _, _ = camera.project(np.array([1.0, 0.0, -1.0]))

    assert 0 < far_x < near_x


def test_three_faces_are_visible_from_the_default_camera():
    """De la caméra par défaut, on voit U, F et R : 27 cases, pas une de plus."""
    polygons = scene_polygons(Cube(), Camera())
    stickers = [polygon.sticker for polygon in polygons if polygon.sticker is not None]
    faces = {STICKERS[index][0] for index in stickers}

    assert len(stickers) == 27
    assert faces == {0, 1, 2}  # U, R, F


def test_polygons_are_sorted_from_far_to_near():
    """Algorithme du peintre : on dessine d'abord ce qui est loin."""
    depths = [polygon.depth for polygon in scene_polygons(Cube(), Camera())]

    assert depths == sorted(depths)


def test_animation_shows_the_inside_of_the_cube():
    """Pendant R à 45 degrés, on voit des faces de plastique en plus."""
    camera = Camera()
    still = scene_polygons(Cube(), camera)
    turning = scene_polygons(Cube(), camera, move="R", angle=-45)

    assert len(turning) > len(still)


def test_point_in_polygon():
    """Un carré contient son centre, pas un point dehors (dans les deux sens)."""
    square = [(0, 0), (10, 0), (10, 10), (0, 10)]

    assert point_in_polygon((5, 5), square)
    assert point_in_polygon((5, 5), square[::-1])
    assert not point_in_polygon((15, 5), square)


def test_clicking_on_the_center_of_F_finds_F4():
    """Un clic au centre de la case F4 la retrouve (indice 2 * 9 + 4)."""
    camera = Camera()
    cubie, normal = sticker_location(F, 1, 1)
    point = np.array(cubie) + np.array(normal) * CUBIE_HALF
    x, y, _ = camera.project(camera.view_matrix() @ point)

    assert sticker_at(scene_polygons(Cube(), camera), (x, y)) == 2 * 9 + 4


def test_click_in_the_void_finds_nothing():
    """Dans un coin de l'écran, il n'y a pas de case."""
    assert sticker_at(scene_polygons(Cube(), Camera()), (1, 1)) is None


@pytest.mark.parametrize(
    ("sticker", "drag", "move"),
    [((F, 1, 2), (0, -30), "R"), ((F, 0, 1), (30, 5), "U'"), ((F, 1, 0), (0, 30), "L")],
)
def test_dragging_on_screen_gives_the_move(sticker, drag, move):
    """Glisser vers le haut de l'écran (y diminue) la colonne de droite de F : R."""
    index = STICKERS.index(sticker)
    direction = best_direction(screen_directions(index, Camera()), drag)

    assert move_for_drag(*sticker, direction) == move
