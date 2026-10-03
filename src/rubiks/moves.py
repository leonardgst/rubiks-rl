"""Notation des mouvements (Singmaster), sans aucun cube : que des chaînes.

Trois familles de mouvements :

- les **18 mouvements de faces** ``U D L R F B`` (+ ``'`` et ``2``) : ``MOVES``.
  Ce sont les seuls que mélange ``scramble`` et les seuls « actions » de
  l'agent de RL (phase 4) ;
- les **tranches du milieu** ``M E S`` : M tourne comme L, E comme D, S comme F ;
- les **rotations du cube entier** ``x y z`` : x tourne comme R, y comme U,
  z comme F. Elles ne changent pas le casse-tête, seulement la façon de le tenir.

Un mouvement s'écrit ``lettre + suffixe`` : ``""`` = quart de tour horaire
(vu depuis l'extérieur de la face de référence), ``"'"`` = anti-horaire,
``"2"`` = demi-tour.
"""

# Ordre des faces dans cube.state (celui de la bibliothèque kociemba)
FACES = ("U", "R", "F", "D", "L", "B")
SLICES = ("M", "E", "S")
ROTATIONS = ("x", "y", "z")
SUFFIXES = ("", "'", "2")

# Nombre de quarts de tour horaires de chaque suffixe : X' = 3 fois X
QUARTER_TURNS = {"": 1, "2": 2, "'": 3}

# Les 18 mouvements de faces, dans l'ordre U U' U2 R R' R2 ...
MOVES = tuple(face + suffix for face in FACES for suffix in SUFFIXES)
SLICE_MOVES = tuple(s + suffix for s in SLICES for suffix in SUFFIXES)
ROTATION_MOVES = tuple(r + suffix for r in ROTATIONS for suffix in SUFFIXES)
ALL_MOVES = MOVES + SLICE_MOVES + ROTATION_MOVES

# Face opposée : deux faces opposées commutent (R L = L R)
OPPOSITE = {"U": "D", "D": "U", "R": "L", "L": "R", "F": "B", "B": "F"}


def parse_move(name: str) -> tuple[str, int]:
    """Découpe un mouvement en (lettre, nombre de quarts de tour horaires).

    "R" donne ("R", 1), "R2" donne ("R", 2), "R'" donne ("R", 3).
    Lève ValueError si le mouvement n'existe pas.
    """
    letter, suffix = name[:1], name[1:]
    if name not in ALL_MOVES:
        raise ValueError(f"mouvement non géré : {name!r}")
    return letter, QUARTER_TURNS[suffix]


def format_move(letter: str, quarter_turns: int) -> str | None:
    """L'inverse de parse_move : ("R", 3) donne "R'". 0 quart de tour donne None."""
    quarter_turns %= 4
    if quarter_turns == 0:
        return None
    return letter + {1: "", 2: "2", 3: "'"}[quarter_turns]


def inverse_move(name: str) -> str:
    """Renvoie le mouvement inverse : R <-> R', R2 reste R2."""
    letter, quarter_turns = parse_move(name)
    return format_move(letter, -quarter_turns)


def inverse_sequence(moves: list[str]) -> list[str]:
    """Renvoie la suite qui défait ``moves`` : à l'envers, chaque coup inversé.

    Principe de la chaussette et de la chaussure : pour défaire « R puis U' »,
    on défait d'abord U' (donc U), puis R (donc R').
    """
    return [inverse_move(move) for move in reversed(moves)]


def simplify(moves: list[str]) -> list[str]:
    """Fusionne les coups consécutifs sur la même face (ou tranche, ou axe).

    R R donne R2, R R' disparaît, R2 R donne R'. On recommence tant que ça
    fusionne : R U U' R' disparaît entièrement.
    """
    result: list[str] = []
    for move in moves:
        letter, quarter_turns = parse_move(move)
        if result and result[-1][0] == letter:
            _, previous = parse_move(result.pop())
            merged = format_move(letter, previous + quarter_turns)
            if merged is not None:
                result.append(merged)
        else:
            result.append(move)
    return result


def is_rotation(name: str) -> bool:
    """True pour x, y, z (et leurs variantes) : on tourne le cube, pas une couche."""
    return name[:1] in ROTATIONS
