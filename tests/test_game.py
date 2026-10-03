"""Tests des règles du jeu au clavier (rubiks.game), sans aucune fenêtre."""

import numpy as np
import pytest
from rubiks.cube import MOVES, Cube
from rubiks.game import (
    LONG_SCRAMBLE_LENGTH,
    SCRAMBLE_LENGTH,
    Command,
    Game,
    Player,
    key_to_command,
    key_to_move,
    smoothstep,
)

FACES = ["U", "D", "L", "R", "F", "B"]


# --------------------------------------------------------------------------
# Touches -> mouvements
# --------------------------------------------------------------------------


@pytest.mark.parametrize("face", FACES)
def test_letter_key_gives_clockwise_move(face):
    """La touche d'une face (en minuscule, comme pygame la nomme) donne son
    quart de tour horaire."""
    assert key_to_move(face.lower(), shift=False) == face


@pytest.mark.parametrize("face", FACES)
def test_shift_letter_key_gives_inverse_move(face):
    """Avec Maj, la même touche donne le mouvement inverse."""
    assert key_to_move(face.lower(), shift=True) == face + "'"


@pytest.mark.parametrize("shift", [False, True])
@pytest.mark.parametrize(
    "key_name", ["k", "a", "space", "escape", "backspace", "return", "1", ""]
)
def test_other_keys_give_no_move(key_name, shift):
    """Une touche qui n'est pas une face ne donne aucun mouvement."""
    assert key_to_move(key_name, shift) is None


@pytest.mark.parametrize("key_name", list("udlrfb"))
@pytest.mark.parametrize("shift", [False, True])
def test_every_key_move_is_a_valid_move(key_name, shift):
    """Chaque mouvement donné par le clavier fait partie des 18 de cube.py."""
    assert key_to_move(key_name, shift) in MOVES


# --------------------------------------------------------------------------
# Une partie
# --------------------------------------------------------------------------


def test_new_game_is_solved_but_not_won():
    """Au lancement, le cube est neuf : résolu, mais pas gagné."""
    game = Game()

    assert game.cube.is_solved()
    assert not game.is_won()
    assert game.scramble_moves == []


def test_letter_keys_play_moves():
    """Les touches jouent les mêmes mouvements que cube.apply."""
    game = Game()
    reference = Cube()

    for key_name, shift in [("r", False), ("u", False), ("r", True), ("u", True)]:
        game.press(key_name, shift)
    reference.apply("R U R' U'")

    assert np.array_equal(game.cube.state, reference.state)
    assert game.moves_played == 4


def test_unknown_key_does_nothing():
    """Une touche inconnue ne change ni le cube ni le compteur."""
    game = Game()

    game.press("x")

    assert game.cube.is_solved()
    assert game.moves_played == 0


def test_space_scrambles_the_cube():
    """Espace mélange le cube, et retient la suite du mélange."""
    game = Game()

    game.press("space")

    assert len(game.scramble_moves) == SCRAMBLE_LENGTH
    assert not game.cube.is_solved()
    assert not game.is_won()


def test_scramble_starts_from_a_new_cube():
    """Un mélange repart d'un cube neuf : la suite affichée suffit à le refaire."""
    game = Game()
    game.press("r")
    game.press("f")

    game.scramble(seed=3)
    reference = Cube()
    reference.apply(" ".join(game.scramble_moves))

    assert np.array_equal(game.cube.state, reference.state)
    assert game.moves_played == 0


def test_backspace_resets_everything():
    """Retour arrière remet un cube neuf, et oublie le mélange et les coups."""
    game = Game()
    game.press("space")
    game.press("r")

    game.press("backspace")

    assert game.cube.is_solved()
    assert game.scramble_moves == []
    assert game.moves_played == 0
    assert not game.is_won()


@pytest.mark.parametrize("seed", range(5))
def test_solving_after_scramble_wins(seed):
    """Mélanger, puis jouer au clavier la suite inverse : la partie est gagnée.

    C'est le critère de fin de la phase 2, joué par un test.
    """
    game = Game()
    game.scramble(seed=seed)
    assert not game.is_won()

    for move in game.cube.inverse_sequence(game.scramble_moves):
        # « R' » se tape Maj + r ; « R2 » se tape r deux fois
        if move.endswith("2"):
            game.press(move[0].lower())
            game.press(move[0].lower())
        else:
            game.press(move[0].lower(), shift=move.endswith("'"))

    assert game.is_won()


def test_scramble_never_gives_a_solved_cube(monkeypatch):
    """Si les coups du mélange s'annulent tous, on mélange à nouveau.

    On force le premier mélange à être « R R' » (le cube redevient résolu) en
    remplaçant temporairement Cube.scramble (monkeypatch le remet ensuite).
    """
    real_scramble = Cube.scramble
    calls = []

    def fake_scramble(cube, n, seed=None):
        calls.append(seed)
        if len(calls) == 1:
            cube.apply("R R'")
            return ["R", "R'"]
        return real_scramble(cube, n, seed=seed)

    monkeypatch.setattr(Cube, "scramble", fake_scramble)
    game = Game()

    game.scramble(seed=0)

    assert len(calls) == 2  # un second mélange a eu lieu
    assert not game.cube.is_solved()
    assert not game.is_won()


# --------------------------------------------------------------------------
# Les touches de la phase 3 : Ctrl, tranches, rotations, commandes
# --------------------------------------------------------------------------


@pytest.mark.parametrize("face", FACES)
def test_ctrl_letter_key_gives_half_turn(face):
    """Avec Ctrl, la touche d'une face donne le demi-tour."""
    assert key_to_move(face.lower(), shift=False, ctrl=True) == face + "2"


@pytest.mark.parametrize(
    ("key_name", "move"),
    [("m", "M"), ("e", "E"), ("s", "S"), ("x", "x"), ("y", "y"), ("z", "z")],
)
def test_slice_and_rotation_keys(key_name, move):
    """M E S pour les tranches, X Y Z pour tourner tout le cube."""
    assert key_to_move(key_name, shift=False) == move
    assert key_to_move(key_name, shift=True) == move + "'"


@pytest.mark.parametrize(
    ("key_name", "shift", "ctrl", "expected"),
    [
        ("z", False, True, Command("undo")),  # Ctrl+Z annule, ce n'est pas z2
        ("z", False, False, Command("move", move="z")),
        ("space", False, False, Command("scramble")),
        ("space", True, False, Command("scramble", long=True)),
        ("backspace", False, False, Command("reset")),
        ("return", False, False, Command("solve")),
        ("r", True, False, Command("move", move="R'")),
        ("k", False, False, None),
    ],
)
def test_key_to_command(key_name, shift, ctrl, expected):
    """Chaque touche devient une commande (ou rien)."""
    assert key_to_command(key_name, shift, ctrl) == expected


# --------------------------------------------------------------------------
# Coups, annulation, solution
# --------------------------------------------------------------------------


def test_rotations_are_not_counted_as_moves():
    """Tourner tout le cube (x y z) ne compte pas comme un coup."""
    game = Game()

    game.press("x")
    game.press("r")

    assert game.moves_played == 1


def test_undo_plays_the_inverse_of_the_last_move():
    """Ctrl+Z défait le dernier coup, et le compteur recule."""
    game = Game()
    game.press("r")
    game.press("u")

    undone = game.press("z", ctrl=True)

    reference = Cube()
    reference.move("R")
    assert undone == ["U'"]
    assert game.cube == reference
    assert game.moves_played == 1


def test_undo_with_nothing_to_undo_does_nothing():
    """Sans coup joué, Ctrl+Z ne fait rien (il ne défait pas le mélange)."""
    game = Game()
    game.scramble(seed=0)
    scrambled = game.cube.copy()

    assert game.undo() is None
    assert game.cube == scrambled


@pytest.mark.parametrize("seed", range(5))
def test_solution_solves_the_cube(seed):
    """Entrée joue la solution : le cube est résolu, avec aide."""
    game = Game()
    game.scramble(seed=seed, length=LONG_SCRAMBLE_LENGTH)
    game.press("r")
    game.press("f", shift=True)

    game.press("return")

    assert game.is_won()
    assert game.assisted


def test_solution_is_simplified():
    """« R » puis « R » : la solution est R2, pas R' R'."""
    game = Game()
    game.press("r")
    game.press("r")

    assert game.solution() == ["R2"]


def test_long_scramble():
    """Maj + Espace : un long mélange."""
    game = Game()

    game.press("space", shift=True)

    assert len(game.scramble_moves) == LONG_SCRAMBLE_LENGTH


# --------------------------------------------------------------------------
# Le chronomètre (avec une fausse horloge : voir conftest.py)
# --------------------------------------------------------------------------


def test_timer_waits_for_the_first_move(clock):
    """Le chrono ne démarre qu'au premier coup après le mélange."""
    game = Game(clock=clock)
    game.scramble(seed=0)
    clock.advance(10)

    assert game.elapsed() is None

    game.press("r")
    clock.advance(2.5)

    assert game.elapsed() == 2.5


def test_timer_stops_when_solved(clock):
    """Le chrono s'arrête quand le cube est résolu."""
    game = Game(clock=clock)
    game.scramble(seed=0)
    game.press("r")
    clock.advance(4)

    game.press("return")  # la solution, d'un coup
    clock.advance(100)

    assert game.is_won()
    assert game.elapsed() == 4


def test_timer_does_not_run_without_scramble(clock):
    """Sans mélange, pas de chrono : on joue librement."""
    game = Game(clock=clock)

    game.press("r")
    clock.advance(3)

    assert game.elapsed() is None


# --------------------------------------------------------------------------
# Player : la file d'attente des vues animées
# --------------------------------------------------------------------------


def test_smoothstep_goes_from_0_to_1():
    """L'animation part de 0, arrive à 1, et passe par 0.5 au milieu."""
    assert smoothstep(0) == 0
    assert smoothstep(1) == 1
    assert smoothstep(0.5) == 0.5
    assert smoothstep(2) == 1  # on ne dépasse jamais 90 degrés


def test_player_plays_the_move_at_once_but_shows_the_old_cube():
    """Jouer, animer, repeindre : le cube logique tourne tout de suite, la vue
    montre l'ancien cube pendant l'animation, puis le nouveau."""
    game = Game()
    player = Player(game, seconds_per_quarter_turn=1.0)
    player.push(Command("move", move="R"))

    tick = player.update(0)

    assert tick.started == "R"
    assert not game.cube.is_solved()  # 1. jouer : la logique est à jour
    assert player.shown_cube.is_solved()  # 2. animer : la vue montre l'avant

    player.update(0.5)
    assert player.angle() == pytest.approx(-45)  # R : vers -90 degrés

    tick = player.update(0.6)
    assert tick.repaint  # 3. repeindre
    assert player.move is None
    assert player.shown_cube is game.cube


def test_player_plays_commands_one_after_the_other():
    """Deux coups tapés vite : le second attend la fin du premier."""
    game = Game()
    player = Player(game, seconds_per_quarter_turn=1.0)
    player.press("r")
    player.press("u")

    player.update(0)
    assert player.move == "R"
    assert game.history == ["R"]

    player.update(2)  # fin de R, début de U dans la même image
    assert player.move == "U"
    assert game.history == ["R", "U"]


def test_player_plays_the_solution_move_by_move():
    """Entrée : la solution est jouée coup par coup, puis le cube est gagné."""
    game = Game()
    game.scramble(seed=1)
    player = Player(game, seconds_per_quarter_turn=0.1)
    player.press("return")

    steps = 0
    player.update(0)
    while player.busy:
        assert player.move is not None
        player.update(1)
        steps += 1

    assert steps == len(game.history)
    assert game.is_won()
    assert game.assisted


def test_player_runs_instant_commands_and_asks_for_repaint():
    """Mélanger ou recommencer n'a pas d'animation : on repeint, c'est tout."""
    game = Game()
    player = Player(game)
    player.press("space")

    tick = player.update(0)

    assert tick.repaint
    assert tick.started is None
    assert game.scramble_moves
