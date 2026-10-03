"""Vue 3D du cube avec ursina : le jeu complet (phase 3).

Lancer : ``uv run rubiks``. Mêmes touches que la vue 2D (voir ``game.py``).

Souris :
- clic droit + glisser : tourner la caméra autour du cube ; molette : zoomer ;
- clic gauche sur une case + glisser : tourner la couche dans ce sens.

Comment c'est construit (voir la fiche de la phase 3) :

- 26 « cubies » : chacun est une ``Entity`` vide (un *support*) placée au centre
  du cubie, avec deux sortes d'enfants : le plastique noir et ses cases colorées ;
- **jouer, animer, repeindre** : ``Player`` (``game.py``) joue le coup sur le
  ``Cube`` logique tout de suite ; la vue accroche les supports de la couche à
  un *pivot* et tourne le pivot ; à la fin, chaque support reprend sa place,
  et les 54 cases sont recolorées d'après ``cube.state``. Le cube logique reste
  la seule source de vérité ;
- les calculs (où est chaque case, quelle couche tourne, quel coup donne un
  glissement de souris) viennent de ``geometry.py``, testé sans fenêtre.

Deux pièges d'ursina, réglés ici une fois pour toutes :

- **les axes** : ursina a son z qui s'éloigne de la caméra, notre z (geometry.py)
  vient vers nous. ``to_ursina`` change le signe de z, et une rotation
  « logique » de +a degrés devient ``rotation_* = -a`` dans ursina (mesuré) ;
- **le clavier** : pour les lettres, ursina envoie la touche *physique* d'un
  clavier QWERTY (sur un clavier AZERTY, la touche « Z » arrive comme « w »).
  On écoute donc directement les événements de Panda3D (le moteur sous ursina),
  qui suivent la disposition du clavier : « z » est bien la touche Z.
"""

from direct.showbase.DirectObject import DirectObject
from ursina import (
    EditorCamera,
    Entity,
    Text,
    Ursina,
    Vec2,
    Vec3,
    application,
    camera,
    color,
    held_keys,
    mouse,
    time,
    window,
)

from rubiks.cube import Cube
from rubiks.game import KEY_TO_LETTER, Command, Game, Player
from rubiks.geometry import (
    CUBIES,
    STICKERS,
    X,
    Y,
    best_direction,
    is_in_layer,
    move_for_drag,
    move_rotation,
    sticker_location,
    tangent_directions,
)
from rubiks.render.colors import (
    BACKGROUND_COLOR,
    COLORS,
    HELP_COLOR,
    HELP_LINES,
    PLASTIC_COLOR,
    TEXT_COLOR,
    WIN_COLOR,
    format_time,
    win_message,
)

WINDOW_TITLE = "Rubik's Cube"
CUBIE_SIZE = 0.96  # côté du plastique d'un cubie (1 = cubies collés)
STICKER_SIZE = 0.84  # côté d'une case colorée
STICKER_THICKNESS = 0.02  # épaisseur d'une case
STICKER_LIFT = 0.01  # la case dépasse un peu du plastique (sinon elle clignote)
CAMERA_DISTANCE = 12  # recul de la caméra
CAMERA_START_ROTATION = (28, -35, 0)  # on voit U, F et R au lancement
DRAG_THRESHOLD = 0.02  # glissement minimal (en unités d'écran) pour tourner
TEXT_SCALE = 1.0
HELP_SCALE = 0.75
WIN_SCALE = 2.0


def to_ursina(vector: tuple[float, float, float]) -> Vec3:
    """Coordonnées logiques (z vers moi) -> coordonnées ursina (z vers le fond)."""
    return Vec3(vector[0], vector[1], -vector[2])


def ursina_color(rgb: tuple[int, int, int]) -> color.Color:
    """Couleur (0 à 255) -> couleur ursina (rgb32 attend 0 à 255, rgb 0 à 1)."""
    return color.rgb32(*rgb)


class CubeView(Entity):
    """Le cube 3D, branché sur une partie : clavier, souris, animation, textes.

    Une classe qui hérite d'``Entity`` : ursina appelle ses méthodes
    ``update()`` et ``input(key)`` à chaque image et à chaque touche, même
    quand ce fichier n'est pas le script principal.
    """

    def __init__(self, game: Game) -> None:
        super().__init__()
        self.game = game
        self.player = Player(game)
        self.pivot = Entity(parent=self)  # tourne pendant une animation
        self.holders: dict[tuple[int, int, int], Entity] = {}  # cubie -> support
        self.stickers: list[Entity] = []  # indice 0 à 53 -> case colorée
        self.drag_start: Vec2 | None = None
        self.dragged_sticker: int | None = None
        self.probe = Entity(parent=self)  # point invisible, pour projeter à l'écran
        self._build_cube()
        self._build_texts()
        self.keys = KeyListener(self.on_letter)
        self.repaint()

    # ----------------------------------------------------------------------
    # Construction
    # ----------------------------------------------------------------------

    def _build_cube(self) -> None:
        """26 supports, avec leur plastique noir et leurs cases."""
        for cubie in CUBIES:
            holder = Entity(parent=self, position=to_ursina(cubie))
            Entity(
                parent=holder,
                model="cube",
                color=ursina_color(PLASTIC_COLOR),
                scale=CUBIE_SIZE,
            )
            self.holders[cubie] = holder
        for index, sticker in enumerate(STICKERS):
            cubie, normal = sticker_location(*sticker)
            scale = [STICKER_SIZE] * 3
            scale[[abs(c) for c in normal].index(1)] = STICKER_THICKNESS
            offset = CUBIE_SIZE / 2 + STICKER_LIFT
            entity = Entity(
                parent=self.holders[cubie],
                model="cube",
                position=to_ursina(tuple(c * offset for c in normal)),
                scale=Vec3(*scale),
                collider="box",  # pour savoir quelle case est sous la souris
            )
            entity.sticker_index = index
            self.stickers.append(entity)

    def _build_texts(self) -> None:
        """Les textes, accrochés à l'interface (camera.ui) et pas à la scène."""
        margin = Vec2(0.03, -0.03)
        self.win_text = Text(
            parent=camera.ui,
            origin=(0, 0.5),
            position=(0, window.top.y - 0.12),  # sous les lignes d'information
            scale=WIN_SCALE,
            color=ursina_color(WIN_COLOR),
        )
        self.info_text = Text(
            parent=camera.ui,
            origin=(-0.5, 0.5),
            position=window.top_left + margin,
            scale=TEXT_SCALE,
            color=ursina_color(TEXT_COLOR),
        )
        self.help_text = Text(
            parent=camera.ui,
            text="\n".join(
                HELP_LINES + ("Souris : clic droit = caméra, clic gauche = couche",)
            ),
            origin=(-0.5, -0.5),
            position=window.bottom_left + Vec2(0.03, 0.03),
            scale=HELP_SCALE,
            color=ursina_color(HELP_COLOR),
        )

    # ----------------------------------------------------------------------
    # Dessin : repeindre et animer
    # ----------------------------------------------------------------------

    def repaint(self) -> None:
        """Remet chaque cubie à sa place et recolore les 54 cases (notion 6)."""
        for cubie, holder in self.holders.items():
            holder.parent = self
            holder.position = to_ursina(cubie)
            holder.rotation = Vec3(0, 0, 0)
        self.pivot.rotation = Vec3(0, 0, 0)
        colors = self.player.shown_cube.state.reshape(54)
        for index, entity in enumerate(self.stickers):
            entity.color = ursina_color(COLORS[colors[index]])

    def start_animation(self, move: str) -> None:
        """Accroche au pivot (non tourné) les supports de la couche qui va tourner."""
        axis, layers, _ = move_rotation(move)
        for cubie, holder in self.holders.items():
            if is_in_layer(cubie, axis, layers):
                holder.world_parent = self.pivot

    def update(self) -> None:
        """Appelée par ursina à chaque image."""
        tick = self.player.update(time.dt)
        if tick.repaint:
            self.repaint()
        if tick.started is not None:
            self.start_animation(tick.started)
        if self.player.move is not None:
            axis, _, _ = move_rotation(self.player.move)
            attribute = {X: "rotation_x", Y: "rotation_y"}.get(axis, "rotation_z")
            # Une rotation logique de +a degrés vaut -a dans ursina (voir en haut)
            setattr(self.pivot, attribute, -self.player.angle())
        self._update_texts()

    def _update_texts(self) -> None:
        """Victoire, coups et chrono, mélange."""
        game = self.game
        self.win_text.text = win_message(game.assisted) if game.is_won() else ""
        lines = []
        if game.scramble_moves:
            lines.append(
                f"Coups : {game.moves_played}    {format_time(game.elapsed())}"
            )
            lines.append("Mélange : " + " ".join(game.scramble_moves))
        self.info_text.text = "\n".join(lines)

    # ----------------------------------------------------------------------
    # Clavier et souris
    # ----------------------------------------------------------------------

    def on_letter(self, key_name: str, shift: bool, ctrl: bool) -> None:
        """Une lettre (selon la disposition du clavier) : on la donne au jeu."""
        self.player.press(key_name, shift, ctrl)

    def input(self, key: str) -> None:
        """Appelée par ursina pour chaque événement. Les lettres arrivent par
        ``KeyListener`` : on ignore ici leur version « touche physique »."""
        shift = bool(held_keys["shift"])
        if key == "escape":
            application.quit()
        elif key == "space":
            self.player.push(Command("scramble", long=shift))
        elif key == "backspace":
            self.player.push(Command("reset"))
        elif key == "enter":
            self.player.push(Command("solve"))
        elif key == "left mouse down":
            hovered = mouse.hovered_entity
            if hovered is not None and hasattr(hovered, "sticker_index"):
                self.dragged_sticker = hovered.sticker_index
                self.drag_start = Vec2(mouse.x, mouse.y)
        elif key == "left mouse up":
            self._end_drag()

    def _end_drag(self) -> None:
        """Fin d'un glissement sur une case : on en déduit le coup à jouer."""
        sticker, start = self.dragged_sticker, self.drag_start
        self.dragged_sticker, self.drag_start = None, None
        if sticker is None or start is None:
            return
        drag = (mouse.x - start.x, mouse.y - start.y)
        if (drag[0] ** 2 + drag[1] ** 2) ** 0.5 < DRAG_THRESHOLD:
            return
        direction = best_direction(self.screen_directions(sticker), drag)
        move = move_for_drag(*STICKERS[sticker], direction)
        self.player.push(Command("move", move=move))

    def screen_position(self, point: tuple[float, float, float]) -> Vec2:
        """Où un point logique apparaît à l'écran (unités de l'interface, y vers
        le haut, comme mouse.x et mouse.y)."""
        self.probe.world_position = to_ursina(point)
        return self.probe.screen_position

    def screen_directions(self, sticker: int) -> dict:
        """Pour chaque direction où l'on peut glisser la case, son image à l'écran."""
        cubie, normal = sticker_location(*STICKERS[sticker])
        start = tuple(c + n * 0.5 for c, n in zip(cubie, normal, strict=True))
        x0, y0 = self.screen_position(start)
        directions = {}
        for direction in tangent_directions(normal):
            end = tuple(s + 0.5 * d for s, d in zip(start, direction, strict=True))
            x1, y1 = self.screen_position(end)
            directions[direction] = (x1 - x0, y1 - y0)
        return directions


class KeyListener(DirectObject):
    """Écoute les lettres du jeu selon la disposition du clavier (AZERTY compris).

    Panda3D nomme les événements « u », « shift-u », « control-u ».
    """

    def __init__(self, callback) -> None:
        super().__init__()
        for key_name in KEY_TO_LETTER:
            self.accept(key_name, callback, [key_name, False, False])
            self.accept(f"shift-{key_name}", callback, [key_name, True, False])
            self.accept(f"control-{key_name}", callback, [key_name, False, True])


def setup_camera() -> EditorCamera:
    """Caméra orbitale (clic droit), un peu au-dessus et à droite du cube.

    EditorCamera a des raccourcis (Maj+F, Maj+P, Alt+F) qui gêneraient F' : on
    les désactive.
    """
    camera.position = (0, 0, -CAMERA_DISTANCE)
    editor_camera = EditorCamera(rotation_speed=150)
    editor_camera.shortcuts = {
        "toggle_orthographic": "",
        "focus": "",
        "reset_center": "",
    }
    editor_camera.rotation = Vec3(*CAMERA_START_ROTATION)
    return editor_camera


def run(cube: Cube | None = None, **ursina_options) -> None:
    """Ouvre la fenêtre 3D et lance le jeu jusqu'à la fermeture.

    ``ursina_options`` est transmis à ``Ursina(...)`` (par exemple
    ``window_type="offscreen"`` pour faire des captures sans écran).
    """
    app = Ursina(title=WINDOW_TITLE, development_mode=False, **ursina_options)
    window.color = ursina_color(BACKGROUND_COLOR)
    for name in ("fps_counter", "entity_counter", "collider_counter", "cog_button"):
        widget = getattr(window, name, None)
        if widget is not None:
            widget.enabled = False
    setup_camera()
    CubeView(Game(cube))
    app.run()


if __name__ == "__main__":
    run()
