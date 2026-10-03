"""La 3D « à la main » : projeter le cube sur l'écran, sans bibliothèque 3D.

C'est ce qu'ursina (et la carte graphique) fait pour nous dans ``view3d.py``,
écrit ici en quelques fonctions numpy, pour comprendre :

1. **placer** chaque face de cubie et chaque case dans l'espace (``geometry.py``),
   en tournant de ``angle`` degrés la couche qui s'anime ;
2. **tourner le monde** selon la caméra (deux angles : ``yaw`` autour de l'axe
   vertical, ``pitch`` pour regarder d'au-dessus) ;
3. **projeter** en perspective : plus un point est loin, plus il est près du
   centre de l'écran (on divise par la distance) ;
4. **éliminer les faces de dos** (« back-face culling ») : une face dont la
   normale ne regarde pas la caméra est cachée ;
5. **trier du plus loin au plus proche** et dessiner dans cet ordre
   (« algorithme du peintre ») : ce qui est devant recouvre ce qui est derrière.

Ce module n'importe pas pygame : il ne fait que des calculs, testés dans
``tests/test_scene.py``. ``view3d_pygame.py`` dessine les polygones obtenus.
"""

from dataclasses import dataclass

import numpy as np

from rubiks.cube import Cube
from rubiks.geometry import (
    CUBIES,
    STICKERS,
    X,
    Y,
    is_in_layer,
    move_rotation,
    rotation_matrix,
    sticker_location,
    tangent_directions,
)
from rubiks.render.colors import COLORS, PLASTIC_COLOR

CUBIE_HALF = 0.48  # demi-côté d'un cubie (0.5 = cubies collés)
STICKER_HALF = 0.40  # demi-côté d'une case colorée
STICKER_LIFT = 0.01  # la case est un peu décollée du plastique (sinon elle clignote)

# Les 6 directions d'une face de cubie
DIRECTIONS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


@dataclass
class Camera:
    """Une caméra qui tourne autour du cube.

    ``yaw`` : rotation du cube autour de l'axe vertical, en degrés (négatif :
    la face R vient vers nous).
    ``pitch`` : bascule du cube vers nous, en degrés (positif : on voit U).
    ``distance`` : distance entre l'œil et le centre du cube.
    ``scale`` : taille du cube à l'écran, en pixels par unité.
    ``center`` : centre de l'écran, en pixels.
    """

    yaw: float = -35.0
    pitch: float = 28.0
    distance: float = 9.0
    scale: float = 120.0
    center: tuple[float, float] = (300.0, 280.0)

    def view_matrix(self) -> np.ndarray:
        """Matrice qui tourne le monde comme si la caméra tournait autour de lui."""
        return rotation_matrix(X, self.pitch) @ rotation_matrix(Y, self.yaw)

    def project(self, point: np.ndarray) -> tuple[float, float, float]:
        """Point du monde (déjà tourné par la vue) -> (x, y) écran et profondeur.

        En perspective, on divise par la distance à l'œil : un point deux fois
        plus loin paraît deux fois plus près du centre. Le y de l'écran va vers
        le bas, d'où le signe moins.
        """
        x, y, z = point
        factor = self.scale * self.distance / (self.distance - z)
        return self.center[0] + x * factor, self.center[1] - y * factor, z


@dataclass
class Polygon:
    """Un quadrilatère prêt à dessiner. ``sticker`` = indice de la case (0 à 53),
    ou None pour le plastique noir."""

    points: list[tuple[float, float]]
    depth: float
    color: tuple[int, int, int]
    sticker: int | None = None


def _square(center: np.ndarray, normal: np.ndarray, half: float) -> list[np.ndarray]:
    """Les 4 coins d'un carré de demi-côté ``half``, centré en ``center``,
    perpendiculaire à ``normal``, dans l'ordre du tour."""
    axis = int(np.flatnonzero(normal)[0])
    u, v = np.zeros(3), np.zeros(3)
    u[(axis + 1) % 3] = half
    v[(axis + 2) % 3] = half
    return [center + u + v, center - u + v, center - u - v, center + u - v]


def _face_polygon(
    corners: list[np.ndarray],
    normal: np.ndarray,
    transform: np.ndarray,
    camera: Camera,
    color: tuple[int, int, int],
    sticker: int | None,
) -> Polygon | None:
    """Tourne, élimine si la face est de dos, puis projette. None si cachée."""
    turned = [transform @ corner for corner in corners]
    face_center = sum(turned) / 4
    turned_normal = transform @ normal
    eye = np.array([0.0, 0.0, camera.distance])
    if np.dot(turned_normal, eye - face_center) <= 0:  # face de dos
        return None
    projected = [camera.project(corner) for corner in turned]
    depth = sum(p[2] for p in projected) / 4
    return Polygon([(p[0], p[1]) for p in projected], depth, color, sticker)


def scene_polygons(
    cube: Cube, camera: Camera, move: str | None = None, angle: float = 0.0
) -> list[Polygon]:
    """Tous les polygones visibles, du plus loin au plus proche.

    ``move`` et ``angle`` : le mouvement qui s'anime et son angle actuel (en
    degrés, convention de geometry.py) ; les cubies de sa couche tournent.
    """
    view = camera.view_matrix()
    if move is not None:
        axis, layers, _ = move_rotation(move)
        turned_view = view @ rotation_matrix(axis, angle)
    else:
        axis, layers, turned_view = 0, (), view

    def moving(position: tuple[int, int, int]) -> bool:
        return move is not None and is_in_layer(position, axis, layers)

    polygons: list[Polygon] = []

    # Le plastique : chaque face de cubie, sauf celles collées à un voisin du
    # même bloc (elles ne se voient jamais)
    for cubie in CUBIES:
        transform = turned_view if moving(cubie) else view
        for direction in DIRECTIONS:
            neighbour = tuple(c + d for c, d in zip(cubie, direction, strict=True))
            inside = all(abs(c) <= 1 for c in neighbour)
            if inside and moving(neighbour) == moving(cubie):
                continue
            normal = np.array(direction, dtype=float)
            corners = _square(np.array(cubie) + normal * CUBIE_HALF, normal, CUBIE_HALF)
            polygon = _face_polygon(
                corners, normal, transform, camera, PLASTIC_COLOR, None
            )
            if polygon is not None:
                polygons.append(polygon)

    # Les cases colorées, posées sur le plastique
    colors = cube.state.reshape(54)
    for index, sticker in enumerate(STICKERS):
        cubie, normal_tuple = sticker_location(*sticker)
        transform = turned_view if moving(cubie) else view
        normal = np.array(normal_tuple, dtype=float)
        center = np.array(cubie) + normal * (CUBIE_HALF + STICKER_LIFT)
        corners = _square(center, normal, STICKER_HALF)
        color = COLORS[colors[index]]
        polygon = _face_polygon(corners, normal, transform, camera, color, index)
        if polygon is not None:
            polygons.append(polygon)

    polygons.sort(key=lambda polygon: polygon.depth)  # du plus loin au plus proche
    return polygons


def point_in_polygon(
    point: tuple[float, float], polygon: list[tuple[float, float]]
) -> bool:
    """True si le point est dans le polygone convexe (même côté de chaque bord)."""
    signs = []
    for (x1, y1), (x2, y2) in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        cross = (x2 - x1) * (point[1] - y1) - (y2 - y1) * (point[0] - x1)
        signs.append(cross >= 0)
    return all(signs) or not any(signs)


def sticker_at(polygons: list[Polygon], point: tuple[float, float]) -> int | None:
    """La case sous la souris : la plus proche parmi celles qui contiennent le point."""
    for polygon in reversed(polygons):  # du plus proche au plus loin
        if polygon.sticker is not None and point_in_polygon(point, polygon.points):
            return polygon.sticker
    return None


def screen_directions(
    sticker: int, camera: Camera
) -> dict[tuple[int, int, int], tuple[float, float]]:
    """Pour chaque direction où l'on peut glisser une case, son image à l'écran."""
    cubie, normal = sticker_location(*STICKERS[sticker])
    view = camera.view_matrix()
    start = np.array(cubie) + np.array(normal) * CUBIE_HALF
    x0, y0, _ = camera.project(view @ start)
    result = {}
    for direction in tangent_directions(normal):
        x1, y1, _ = camera.project(view @ (start + 0.5 * np.array(direction)))
        result[direction] = (x1 - x0, y1 - y0)
    return result
