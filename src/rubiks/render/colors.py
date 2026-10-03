"""Couleurs et textes partagés par tous les affichages.

Ce module n'importe aucune bibliothèque d'affichage : la vue 2D (pygame), les
vues 3D (ursina, pygame) et le terminal peuvent tous l'importer sans charger
les bibliothèques des autres.
"""

# COLORS[i] = couleur de la face i du cube résolu (ordre U R F D L B de cube.py),
# en (rouge, vert, bleu), de 0 à 255
COLORS = (
    (255, 255, 255),  # 0 U : blanc
    (200, 20, 20),  # 1 R : rouge
    (20, 160, 60),  # 2 F : vert
    (255, 215, 0),  # 3 D : jaune
    (255, 120, 0),  # 4 L : orange
    (20, 70, 200),  # 5 B : bleu
)

BACKGROUND_COLOR = (30, 30, 30)  # gris foncé
PLASTIC_COLOR = (18, 18, 18)  # le plastique noir du cube
TEXT_COLOR = (230, 230, 230)  # gris très clair
HELP_COLOR = (150, 150, 150)  # gris moyen
WIN_COLOR = (90, 220, 120)  # vert clair

# Aide commune aux vues qui jouent au clavier
HELP_LINES = (
    "U D L R F B : tourner   Maj : sens inverse   Ctrl : demi-tour",
    "M E S : tranches   X Y Z : tourner le cube   Ctrl+Z : annuler",
    "Espace : mélanger (Maj : long)   Retour arrière : recommencer",
    "Entrée : solution   Échap : quitter",
)


def format_time(seconds: float | None) -> str:
    """Affiche un temps en « m:ss.d » (« 0:00.0 » si le chrono n'a pas démarré)."""
    if seconds is None:
        seconds = 0.0
    minutes, rest = divmod(seconds, 60)
    return f"{int(minutes)}:{rest:04.1f}"


def win_message(assisted: bool) -> str:
    """Le message de victoire : on avoue quand la solution a été demandée."""
    return "Résolu (avec aide)" if assisted else "Résolu !"
