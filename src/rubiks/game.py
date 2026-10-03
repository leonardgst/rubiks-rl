"""Règles du jeu au clavier, sans aucun affichage.

Ce module dit ce que fait chaque touche et tient la partie (mélange, coups
joués, chronomètre, annulation, solution). Les affichages (2D, 3D ursina, 3D
pygame) se contentent de lui transmettre les touches et de dessiner le
résultat. Il n'importe aucune bibliothèque d'affichage : il se teste sans
ouvrir de fenêtre.

Touches (noms en minuscule, comme les donne ``pygame.key.name``) :

    u d l r f b      quart de tour horaire de la face
    m e s            tranche du milieu (M comme L, E comme D, S comme F)
    x y z            tourner tout le cube (x comme R, y comme U, z comme F)
    Maj + lettre     sens inverse (R')
    Ctrl + lettre    demi-tour (R2)
    Ctrl + z         annuler le dernier coup
    space            mélanger (Maj + Espace : long mélange)
    backspace        revenir à un cube neuf
    return           montrer la solution, coup par coup

Deux façons de jouer :

- ``Game.press`` applique tout **tout de suite** (tests, affichage terminal) ;
- ``Player`` met les commandes en **file d'attente** et donne à chaque
  mouvement une durée, pour que les vues 3D l'animent (et que la vue 2D montre
  la solution coup par coup).
"""

import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from rubiks.cube import Cube
from rubiks.geometry import move_rotation
from rubiks.moves import inverse_move, inverse_sequence, is_rotation
from rubiks.moves import simplify as simplify_moves

SCRAMBLE_LENGTH = 5  # mélange court (Espace) : on peut le refaire à la main
LONG_SCRAMBLE_LENGTH = 25  # mélange complet (Maj + Espace)

# Nom de la touche -> lettre du mouvement
KEY_TO_LETTER = {
    "u": "U",
    "d": "D",
    "l": "L",
    "r": "R",
    "f": "F",
    "b": "B",
    "m": "M",
    "e": "E",
    "s": "S",
    "x": "x",
    "y": "y",
    "z": "z",
}
SCRAMBLE_KEY = "space"
RESET_KEY = "backspace"
SOLVE_KEY = "return"
UNDO_KEY = "z"  # avec Ctrl


@dataclass(frozen=True)
class Command:
    """Une action du joueur : ``kind`` vaut "move", "undo", "scramble", "reset"
    ou "solve". ``move`` sert pour "move" ; ``long`` pour "scramble"."""

    kind: str
    move: str | None = None
    long: bool = False


def key_to_move(key_name: str, shift: bool, ctrl: bool = False) -> str | None:
    """Renvoie le mouvement d'une touche, ou None si elle n'en est pas un.

    "u" donne "U" ; avec Maj, "U'" ; avec Ctrl, "U2". Une autre touche donne None.
    """
    letter = KEY_TO_LETTER.get(key_name)
    if letter is None:
        return None
    if ctrl:
        return letter + "2"
    return letter + "'" if shift else letter


def key_to_command(
    key_name: str, shift: bool = False, ctrl: bool = False
) -> Command | None:
    """Traduit une touche (et Maj / Ctrl) en commande, ou None si elle ne fait rien."""
    if ctrl and key_name == UNDO_KEY:
        return Command("undo")
    if key_name == SCRAMBLE_KEY:
        return Command("scramble", long=shift)
    if key_name == RESET_KEY:
        return Command("reset")
    if key_name == SOLVE_KEY:
        return Command("solve")
    move = key_to_move(key_name, shift, ctrl)
    if move is not None:
        return Command("move", move=move)
    return None


class Game:
    """Une partie : le cube, le dernier mélange, les coups joués, le chronomètre."""

    def __init__(
        self, cube: Cube | None = None, clock: Callable[[], float] = time.monotonic
    ) -> None:
        """Commence une partie, avec un cube neuf ou le cube donné.

        ``clock`` donne l'heure en secondes ; les tests en passent une fausse.
        """
        self.cube = cube if cube is not None else Cube()
        self.clock = clock
        self.scramble_moves: list[str] = []  # vide tant qu'on n'a pas mélangé
        self.history: list[str] = []  # coups joués depuis le dernier mélange
        self.assisted = False  # True si la solution a été demandée
        self._start: float | None = None  # début du chrono (premier coup)
        self._end: float | None = None  # fin du chrono (cube résolu)

    # ----------------------------------------------------------------------
    # Ce que l'affichage lit
    # ----------------------------------------------------------------------

    @property
    def moves_played(self) -> int:
        """Coups joués depuis le mélange. Tourner tout le cube (x y z) ne compte pas."""
        return sum(1 for move in self.history if not is_rotation(move))

    def is_won(self) -> bool:
        """True si le cube a été mélangé, puis résolu.

        Un cube neuf est résolu, mais on n'a rien gagné : d'où la condition
        « un mélange a eu lieu ».
        """
        return bool(self.scramble_moves) and self.cube.is_solved()

    def elapsed(self) -> float | None:
        """Secondes depuis le premier coup après le mélange (None avant).

        Le chrono s'arrête quand le cube est résolu.
        """
        if self._start is None:
            return None
        end = self._end if self._end is not None else self.clock()
        return end - self._start

    def solution(self) -> list[str]:
        """La suite qui ramène au cube neuf : l'inverse de tout ce qui a été joué
        depuis le cube neuf (mélange, puis coups), simplifiée."""
        return simplify_moves(inverse_sequence(self.scramble_moves + self.history))

    # ----------------------------------------------------------------------
    # Ce que les touches déclenchent
    # ----------------------------------------------------------------------

    def press(
        self, key_name: str, shift: bool = False, ctrl: bool = False
    ) -> list[str]:
        """Applique tout de suite l'effet d'une touche. Une touche inconnue ne fait
        rien. Renvoie les mouvements joués sur le cube."""
        command = key_to_command(key_name, shift, ctrl)
        if command is None:
            return []
        return self.execute(command)

    def execute(self, command: Command) -> list[str]:
        """Exécute une commande tout de suite ; renvoie les mouvements joués."""
        if command.kind == "move":
            self.play(command.move)
            return [command.move]
        if command.kind == "undo":
            undone = self.undo()
            return [] if undone is None else [undone]
        if command.kind == "scramble":
            length = LONG_SCRAMBLE_LENGTH if command.long else SCRAMBLE_LENGTH
            self.scramble(length=length)
            return []
        if command.kind == "reset":
            self.reset()
            return []
        if command.kind == "solve":
            moves = self.solution()
            self.assisted = True
            for move in moves:
                self.play(move)
            return moves
        raise ValueError(f"commande inconnue : {command.kind!r}")

    def play(self, move: str) -> None:
        """Joue un coup : le cube tourne, le coup est retenu, le chrono démarre."""
        if self.scramble_moves and self._start is None and not is_rotation(move):
            self._start = self.clock()
        self.cube.move(move)
        self.history.append(move)
        self._update_timer()

    def undo(self) -> str | None:
        """Annule le dernier coup en jouant son inverse ; renvoie cet inverse.

        Ne remonte pas avant le mélange : sans coup à annuler, renvoie None.
        """
        if not self.history:
            return None
        inverse = inverse_move(self.history.pop())
        self.cube.move(inverse)
        self._update_timer()
        return inverse

    def scramble(self, seed: int | None = None, length: int = SCRAMBLE_LENGTH) -> None:
        """Repart d'un cube neuf et le mélange de ``length`` coups.

        Partir d'un cube neuf garantit que la suite affichée suffit à le refaire.
        Des coups peuvent s'annuler (« R L R' L' ») : si le mélange redonne un
        cube résolu, on recommence, sinon « Résolu ! » s'afficherait aussitôt.
        Sans graine, chaque mélange est différent ; la graine sert aux tests.
        """
        self.cube = Cube()
        self.scramble_moves = self.cube.scramble(length, seed=seed)
        while self.cube.is_solved():
            seed = None if seed is None else seed + 1  # reste reproductible
            self.cube = Cube()
            self.scramble_moves = self.cube.scramble(length, seed=seed)
        self._new_round()

    def reset(self) -> None:
        """Revient à un cube neuf, comme au lancement.

        On remplace l'objet par un Cube() neuf : l'affichage relit self.cube à
        chaque image, il verra donc le nouveau cube.
        """
        self.cube = Cube()
        self.scramble_moves = []
        self._new_round()

    def _new_round(self) -> None:
        """Remet à zéro ce qui dépend de la manche : coups, aide, chrono."""
        self.history = []
        self.assisted = False
        self._start = None
        self._end = None

    def _update_timer(self) -> None:
        """Arrête le chrono quand le cube est résolu ; le relance sinon."""
        if self.is_won():
            if self._end is None and self._start is not None:
                self._end = self.clock()
        else:
            self._end = None


# --------------------------------------------------------------------------
# Jouer dans le temps : la file d'attente des vues animées
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Tick:
    """Ce que la vue doit faire après ``Player.update`` :

    - ``repaint`` : recolorer les cases à partir de ``player.shown_cube`` ;
    - ``started`` : un mouvement commence, la vue accroche sa couche au pivot.
    """

    repaint: bool = False
    started: str | None = None


def smoothstep(t: float) -> float:
    """Accélère au début et freine à la fin (0 -> 0, 1 -> 1) : l'animation
    paraît plus naturelle qu'à vitesse constante."""
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


class Player:
    """Joue les commandes une par une ; chaque mouvement dure un peu de temps.

    Stratégie « jouer, animer, repeindre » (fiche de la phase 3, notion 6) :

    1. **jouer** : au début d'un mouvement, le ``Game`` l'applique tout de
       suite au cube logique (la seule source de vérité) ;
    2. **animer** : pendant ``duration`` secondes, la vue tourne la couche de
       ``angle()`` degrés ; les cases montrent ``shown_cube``, une copie du cube
       d'*avant* le mouvement ;
    3. **repeindre** : à la fin, ``shown_cube`` redevient le vrai cube et la
       vue recolore tout, couche remise droite. L'œil ne voit pas la différence.
    """

    def __init__(self, game: Game, seconds_per_quarter_turn: float = 0.18) -> None:
        self.game = game
        self.seconds_per_quarter_turn = seconds_per_quarter_turn
        self.queue: deque[Command] = deque()
        self.move: str | None = None  # mouvement en cours d'animation
        self._snapshot: Cube | None = None  # le cube d'avant ce mouvement
        self._elapsed = 0.0
        self._duration = 0.0

    @property
    def busy(self) -> bool:
        """True tant qu'un mouvement s'anime ou que des commandes attendent."""
        return self.move is not None or bool(self.queue)

    @property
    def shown_cube(self) -> Cube:
        """Le cube à dessiner : celui d'avant le mouvement en cours, s'il y en a un."""
        return self._snapshot if self.move is not None else self.game.cube

    @property
    def progress(self) -> float:
        """Avancement du mouvement en cours, de 0 à 1 (adouci par smoothstep)."""
        if self.move is None or self._duration <= 0:
            return 0.0
        return smoothstep(self._elapsed / self._duration)

    def angle(self) -> float:
        """Angle actuel de la couche qui tourne, en degrés, anti-horaire autour de
        l'axe positif (convention de geometry.py) : R va de 0 à -90."""
        if self.move is None:
            return 0.0
        _, _, quarter_turns = move_rotation(self.move)
        return 90.0 * quarter_turns * self.progress

    def push(self, command: Command | None) -> None:
        """Ajoute une commande à la file (None est ignoré : touche inconnue)."""
        if command is not None:
            self.queue.append(command)

    def press(self, key_name: str, shift: bool = False, ctrl: bool = False) -> None:
        """Raccourci : traduit la touche et la met dans la file."""
        self.push(key_to_command(key_name, shift, ctrl))

    def update(self, dt: float) -> Tick:
        """Fait avancer le temps de ``dt`` secondes. À appeler à chaque image."""
        repaint = False
        started = None
        if self.move is not None:
            self._elapsed += dt
            if self._elapsed >= self._duration:
                self.move = None
                self._snapshot = None
                repaint = True

        while self.move is None and self.queue:
            command = self.queue.popleft()
            if command.kind == "solve":
                # La solution devient une suite de mouvements, joués un par un
                self.game.assisted = True
                moves = [Command("move", move=m) for m in self.game.solution()]
                self.queue.extendleft(reversed(moves))
                continue
            snapshot = self.game.cube.copy()
            played = self.game.execute(command)
            if played:
                self._start_move(played[0], snapshot)
                started = played[0]
            repaint = True
        return Tick(repaint=repaint, started=started)

    def _start_move(self, move: str, snapshot: Cube) -> None:
        """Commence l'animation d'un mouvement déjà joué sur le cube logique."""
        _, _, quarter_turns = move_rotation(move)
        speed_up = 1 + 0.5 * len(self.queue)  # plus la file est longue, plus vite
        self.move = move
        self._snapshot = snapshot
        self._elapsed = 0.0
        self._duration = (
            self.seconds_per_quarter_turn
            * (1 + 0.5 * (abs(quarter_turns) - 1))
            / speed_up
        )
