# Fiche — Phase 2 : Affichage 2D et contrôle clavier

> **Emplacement dans le repo :** `docs/fiches/phase-2-affichage-2d.md`
> **Durée indicative :** 6 à 10 h, en plusieurs séances. Chaque étape se termine par un commit, et chaque branche par une Pull Request : tu peux t'arrêter après n'importe laquelle.
> **Documents liés :** `docs/cadrage.md` (section 4 « Idée clé d'architecture », section 6 « Phase 2 », section 7 « Méthode de travail avec Git », section 9 « Décisions à prendre plus tard ») et la docstring de `src/rubiks/cube.py` (le patron déplié).

## Objectif

À la fin de cette phase, j'ai :

- une fenêtre qui affiche le cube en **patron déplié en croix**, lancée avec `uv run rubiks` ;
- des touches pour jouer : `U D L R F B` pour un quart de tour horaire, **Maj** + la lettre pour l'inverse, une touche pour **mélanger**, une pour **réinitialiser**, et un message **« Résolu ! »** quand je termine ;
- un `Cube` qui ne sait toujours **rien** de l'affichage : l'affichage lit le cube, le cube ignore l'affichage ;
- quatre ou cinq **petites branches**, chacune avec sa Pull Request, et le tag `v0.2.0`.

**Terminé quand** (cadrage) : je peux mélanger puis refaire le cube au clavier.

---

## Décision de début de phase : terminal ou fenêtre ?

Le cadrage (section 9) laisse ce choix pour le début de la phase 2.

| | Terminal coloré | Fenêtre `pygame` |
|---|---|---|
| Ce qu'il faut apprendre | codes couleur ANSI | une bibliothèque : fenêtre, événements, dessin |
| Lire une touche | `input()` attend **Entrée** : on ne joue pas « en direct » | chaque touche arrive tout de suite, comme dans un jeu |
| Détecter **Maj** | difficile, et différent selon Windows / Mac / Linux | une ligne |
| Préparation de la phase 3 | aucune | la **boucle de jeu** et les **événements** sont exactement les mêmes notions en 3D |

**Je recommande `pygame`.** L'objectif de la phase parle d'une *fenêtre*, la touche Maj est demandée, et ce que tu apprends ici (boucle de jeu, événements clavier) resservira tel quel avec la vue 3D. Le terminal reste une bonne idée pour plus tard, comme second affichage (voir « Pour aller plus loin »).

Ta décision se note dans `docs/cadrage.md`, section 9, ligne « Affichage 2D » (étape B).

---

## Notions Python à connaître

Comme en phase 1 : **noms en anglais, commentaires en français**, et des mini-exemples **hors projet**. Pour les essayer, il faut pygame dans le projet (étape C), puis : enregistrer l'exemple dans un fichier hors de `src/` (par exemple `essai.py` à la racine, **sans le commiter**) et lancer `uv run python essai.py`.

### 1. Une fenêtre pygame

pygame est une bibliothèque pour faire des jeux 2D. Trois idées suffisent pour commencer :

- **La fenêtre est un tableau de pixels.** On y dessine des formes, puis on demande à pygame de l'afficher.
- **Les coordonnées partent du coin en haut à gauche.** `x` augmente vers la droite, et **`y` augmente vers le bas** (l'inverse des maths du lycée).
- **Une couleur est un triplet (rouge, vert, bleu)**, chaque nombre allant de 0 à 255 : `(255, 0, 0)` est rouge, `(255, 255, 255)` est blanc, `(0, 0, 0)` est noir.

```
(0, 0) ───────────► x
│
│ (50, 40) ┌───────────┐
│ │ rectangle │ hauteur 60
│ └───────────┘
▼ largeur 100
y
```

Un rectangle se décrit par `(x, y, largeur, hauteur)` : `(x, y)` est son coin **en haut à gauche**.

### 2. La boucle de jeu

Un programme habituel s'exécute de haut en bas, puis s'arrête. Un jeu, lui, tourne **en boucle** jusqu'à ce qu'on le ferme. À chaque tour de boucle (une *image*, ou *frame*), il fait toujours les trois mêmes choses :

1. **lire les événements** : touches appuyées, clic sur la croix de la fenêtre… ;
2. **dessiner** l'image complète, en partant d'un fond vide ;
3. **afficher** l'image dessinée.

Mini-exemple (hors projet) : une fenêtre avec un rectangle blanc.

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((400, 300)) # largeur, hauteur en pixels
pygame.display.set_caption("Ma première fenêtre")
clock = pygame.time.Clock()

running = True
while running:
# 1. Lire les événements
for event in pygame.event.get():
if event.type == pygame.QUIT: # clic sur la croix de la fenêtre
running = False

# 2. Dessiner : on repart d'un fond uni à chaque image
screen.fill((30, 30, 30))
pygame.draw.rect(screen, (255, 255, 255), (50, 40, 100, 60))

# 3. Afficher ce qui a été dessiné
pygame.display.flip()
clock.tick(60) # au plus 60 images par seconde

pygame.quit()
```

**À essayer :** commente `pygame.display.flip()`. Puis commente `screen.fill(...)` et fais bouger le rectangle (`x` qui augmente à chaque image). Que se passe-t-il dans chaque cas ?

Pourquoi `clock.tick(60)` ? Sans lui, la boucle tourne aussi vite que possible et occupe 100 % d'un cœur du processeur, pour rien.

### 3. Les événements clavier

Chaque appui sur une touche crée un événement `pygame.KEYDOWN`. Il contient :

- `event.key` : la touche, sous forme d'un nombre (par exemple `pygame.K_u`) ;
- `event.mod` : les touches de modification (Maj, Ctrl, Alt…) enfoncées à ce moment-là.

`pygame.key.name(event.key)` traduit la touche en texte : `"u"`, `"space"`, `"backspace"`, `"escape"`… **Avec ou sans Maj, le nom reste en minuscule** : `"u"`. Maj se lit à part, dans `event.mod`.

**Lire Maj : l'opérateur `&`.** `event.mod` est un seul nombre qui range plusieurs interrupteurs côte à côte : un pour Maj gauche, un pour Maj droite, un pour Ctrl, un pour Verr. Num… `event.mod & pygame.KMOD_SHIFT` garde seulement les interrupteurs de Maj, et éteint tous les autres. Le résultat vaut 0 si aucune touche Maj n'est enfoncée. `bool(...)` le transforme en `True` / `False`.

Mini-exemple (hors projet) : une lampe qu'on allume avec Espace, et qui devient rouge avec Maj + Espace.

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()

lamp_color = (60, 60, 60) # éteinte
running = True
while running:
for event in pygame.event.get():
if event.type == pygame.QUIT:
running = False
elif event.type == pygame.KEYDOWN:
name = pygame.key.name(event.key)
shift = bool(event.mod & pygame.KMOD_SHIFT)
print(name, shift) # pour voir ce qui arrive
if name == "space":
lamp_color = (255, 60, 60) if shift else (255, 230, 80)
elif name == "escape":
running = False

screen.fill((20, 20, 20))
pygame.draw.circle(screen, lamp_color, (150, 150), 60)
pygame.display.flip()
clock.tick(60)

pygame.quit()
```

**Pourquoi `KEYDOWN`, et pas « la touche est-elle enfoncée ? »** pygame propose aussi `pygame.key.get_pressed()`, qui répond à chaque image « cette touche est-elle enfoncée en ce moment ? ». Si tu tiens `U` pendant une demi-seconde, ça fait 30 images, donc 30 mouvements. `KEYDOWN` arrive **une seule fois par appui** : un appui, un mouvement. C'est ce qu'on veut.

### 4. Écrire du texte

pygame ne dessine pas du texte directement : il fabrique d'abord une **image** du texte, puis on la colle sur l'écran avec `blit`.

```python
font = pygame.font.Font(None, 36) # None = police par défaut, taille 36
image = font.render("Bonjour !", True, (255, 255, 0)) # texte, lissage, couleur
screen.blit(image, (20, 20)) # colle l'image avec son coin haut gauche en (20, 20)
```

Crée la police **une seule fois**, avant la boucle : la recréer à chaque image ralentit le programme pour rien. `render` et `blit`, eux, se font à chaque image, entre `fill` et `flip`.

### 5. Dessiner une grille : des cases aux pixels

Le patron du cube est une grille de petits carrés. Le calcul est toujours le même : **position en pixels = numéro de case × taille d'une case** (plus une marge éventuelle).

Mini-exemple (hors projet) : un damier 8 × 8.

```python
SIZE = 40 # côté d'une case, en pixels

for row in range(8):
for col in range(8):
x = col * SIZE # la colonne donne x
y = row * SIZE # la ligne donne y
color = (240, 240, 240) if (row + col) % 2 == 0 else (60, 60, 60)
pygame.draw.rect(screen, color, (x, y, SIZE, SIZE))
```

**Attention à l'ordre :** dans un tableau numpy, on écrit `[ligne, colonne]`, mais à l'écran on écrit `(x, y)`, c'est-à-dire **(colonne, ligne)**. C'est la première source de patron « couché sur le côté ».

**Pour le cube :** le patron de ta docstring tient dans une grille de **12 colonnes × 9 lignes** de cases. Chaque face y occupe un carré 3 × 3, et commence à un **décalage** (en cases) qui lui est propre. Par exemple, U commence à la colonne 3, ligne 0. À toi de trouver les décalages de L, F, R, B et D, sur ton dessin du patron : ta méthode `__str__` fait déjà ce travail, avec des lettres au lieu de pixels.

Pour qu'on voie les cases séparément, dessine chaque carré un peu plus petit que la grille (une marge de 2 ou 3 pixels), ou ajoute un contour : `pygame.draw.rect(screen, color, rect, width=2)` ne dessine que le bord.

### 6. Séparer ce qui se teste de ce qui s'affiche

Une fenêtre se teste mal : pytest ne peut pas regarder l'écran. La solution : **sortir les calculs de la boucle de jeu**, dans de petites fonctions **pures** (des entrées, une sortie, aucune fenêtre). Elles, pytest sait les tester.

Dans ce projet, deux candidates évidentes :

- **« quelle touche donne quel mouvement ? »** : une fonction qui reçoit le nom de la touche et l'état de Maj, et renvoie le nom du mouvement, ou `None` si la touche ne correspond à aucun mouvement ;
- **« où se dessine telle case ? »** : une fonction qui reçoit `(face, ligne, colonne)` et renvoie la position en pixels.

La boucle de jeu, elle, ne fait plus que **relier** ces fonctions à pygame.

Mini-exemple (hors projet) : les flèches d'un jeu, en ZQSD.

```python
DIRECTIONS = {"z": "up", "s": "down", "q": "left", "d": "right"}


def key_to_direction(name: str) -> str | None:
"""Renvoie la direction d'une touche, ou None si la touche n'en est pas une."""
return DIRECTIONS.get(name) # .get renvoie None si la clé est absente


# et son test, sans aucune fenêtre :
def test_unknown_key_gives_none():
assert key_to_direction("x") is None
```

Note `str | None` : « une chaîne, **ou** rien ». Et `is None` plutôt que `== None` : c'est la façon habituelle de tester `None` en Python.

### 7. Un sous-paquet et le point d'entrée `uv run rubiks`

Le cadrage range l'affichage dans `src/rubiks/render/`. Un dossier devient un **sous-paquet** importable quand il contient un fichier `__init__.py` (il peut être vide, ou ne contenir qu'une docstring). On importe alors avec `from rubiks.render.view2d import …`, et depuis `view2d.py`, le cube s'importe comme dans les tests : `from rubiks.cube import Cube`.

`uv run rubiks` existe déjà : dans `pyproject.toml`, la ligne `rubiks = "rubiks:main"` (section `[project.scripts]`) veut dire « appelle la fonction `main` du paquet `rubiks` », c'est-à-dire celle de `src/rubiks/__init__.py`. Pour l'instant, elle affiche `Hello from rubiks!`. Il suffira qu'elle lance la fenêtre.

**Le piège de l'import (important pour le RL plus tard).** Quand on écrit `import rubiks.cube`, Python exécute **d'abord** `rubiks/__init__.py`. Si ce fichier importe `view2d` tout en haut, alors **chaque** `import rubiks.cube` charge aussi pygame, y compris dans les tests et plus tard dans l'entraînement RL, qui n'affiche rien. La règle « le cube ne dépend pas de l'affichage » serait cassée sans que tu t'en rendes compte. Indice pour l'éviter : un `import` peut aussi s'écrire **à l'intérieur** d'une fonction ; il n'est alors exécuté que lorsque la fonction est appelée.

Commande pour vérifier (elle doit afficher `False`) :

```bash
uv run python -c "import sys, rubiks.cube; print('pygame' in sys.modules)"
```

---

## Notions Git de l'étape

### Plusieurs petites branches

En phase 1, une seule grosse branche a vécu plusieurs jours. Cette fois, on découpe : **une branche = une petite fonctionnalité**, qui vit quelques heures, avec sa propre Pull Request.

```
main ●──────●─────────●─────────●─────────●──────● ← tag v0.2.0
\ / \ / \ / \ / \ /
●──● ●─●─●─● ●─●─●─● ●─●─●─● ●──●
docs/ feature/ feature/ feature/ docs/
fiche window draw keyboard clôture
```

Pourquoi c'est mieux :

- une petite PR se relit en cinq minutes ; une grosse, on la survole ;
- `main` reçoit souvent du code qui marche : tu peux t'arrêter entre deux branches sans rien laisser à moitié fait ;
- si une idée ne mène nulle part, tu supprimes la branche, et `main` n'a rien vu.

**La règle d'or : chaque branche part d'un `main` à jour.**

```bash
git switch main
git pull # récupère le merge de la PR précédente
git switch -c feature/nouvelle-branche
```

Si tu oublies le `git pull`, ta nouvelle branche part d'un `main` en retard : elle ne contient pas le travail de la branche précédente.

### Ce qui s'est passé en fin de phase 1 (pour comprendre le graphe)

Deux choses intéressantes sont arrivées sur `feature/cube-model` :

1. **Une modification faite sur GitHub** (« Update README.md », éditée dans le navigateur) pendant que ta branche locale avait d'autres commits. Les deux versions de la branche avaient **divergé**. `git pull` les a réunies avec un **commit de merge** : c'est le losange que tu vois dans le graphe.
2. **Le commit de clôture a été fait après le merge de la PR n°1.** Une PR mergée est terminée : les commits ajoutés ensuite à la branche **n'arrivent pas** dans `main`. Ils attendent une nouvelle PR.

Les deux se voient très bien avec les commandes de lecture ci-dessous. C'est l'occasion de s'entraîner à les lire.

### Lire l'historique

| Commande | À quoi ça sert |
|---|---|
| `git log --oneline --graph --all` | le graphe de **toutes** les branches. Chaque `*` est un commit ; les traits `\|`, `/` et `\` montrent d'où viennent les commits ; un commit avec deux parents est un **merge** |
| `git log --oneline main..feature/x` | les commits de `feature/x` qui **ne sont pas encore** dans `main` (« ce que la PR apportera ») |
| `git show <hash>` | le détail d'un commit : auteur, date, message et modifications |
| `git log -p -- src/rubiks/cube.py` | l'histoire d'un seul fichier, avec les modifications de chaque commit |
| `git diff main` | ce qui diffère entre `main` et l'état actuel de ton dossier |
| `git log --oneline -5` | seulement les 5 derniers commits |

Dans `git log`, la sortie s'affiche page par page : **Espace** pour avancer, **q** pour quitter.

**Exercice (avant l'étape A) :** lance `git fetch`, puis `git log --oneline origin/main..origin/feature/cube-model`. Quels commits affiche-t-il ? Pourquoi ne sont-ils pas dans `main` ? Puis `git log --oneline --graph --all` : retrouve le commit de merge créé par `git pull`, et celui de la PR n°1.

### Petit rappel : un bon message de commit

- **Une ligne de titre courte** (moins de 70 caractères environ), au format `type: description`.
- Les détails vont dans le **corps** du message, après une ligne vide : `git commit -m "fix: corrige le test de copie" -m "On comparait (==) au lieu d'affecter (=)."` (deux `-m` = titre puis corps).
- Les types sont au singulier : `test:`, pas `tests:`.
- Une modification faite sur GitHub reçoit un message par défaut (« Update README.md ») : GitHub te laisse le changer avant de valider.

---

## Tâches (dans l'ordre)

**Bloqué ?** Demande-moi un indice. Je réponds par niveaux : (1) une question ou une piste, (2) l'explication de la notion, (3) un petit exemple hors projet, (4) la solution, seulement si tu la demandes.

**À chaque branche, le même cycle** (cadrage, section 7) : `main` à jour → `git switch -c …` → commits → `uv run pytest` + `uv run ruff check .` → `git push -u origin …` → PR → **Create a merge commit** → **Delete branch** → `git switch main` → `git pull` → `git branch -d …` → `git fetch --prune`.

### Étape A — Clore vraiment la phase 1

Voir la relecture de fin de phase 1. En résumé, sur `feature/cube-model` (qui existe encore) :

- [ ] Mettre à jour l'annexe B du cadrage (phases 0 et 1 : « Terminé », tag, date).
- [ ] (Recommandé) Ajouter le test des noms de mouvement invalides et l'exemple d'utilisation du README.
- [ ] `git push`, puis PR n°2 `feature/cube-model` → `main`, merge, suppression de la branche.
- [ ] Sur `main` à jour : poser et envoyer le tag `v0.1.0` (`git tag -a v0.1.0 -m "Phase 1 : cube logique"`, puis `git push origin v0.1.0`).
- [ ] Vérifier : `git log --oneline --graph --all` montre le tag sur `main`, et `git branch -a` ne montre plus que `main`.

### Étape B — Branche `docs/fiche-phase-2`

Une toute petite branche, pour roder le cycle.

- [ ] Créer la branche depuis `main` à jour.
- [ ] Placer cette fiche dans `docs/fiches/phase-2-affichage-2d.md`. Commit : `docs: ajoute la fiche de la phase 2`.
- [ ] Dans `docs/cadrage.md`, section 9, noter la décision pour l'affichage 2D (par exemple « Décidé : `pygame` », avec la date). Commit : `docs: choisit pygame pour l'affichage 2D`.
- [ ] Push, PR, merge, rangement.

### Étape C — Branche `feature/view2d-window` : une fenêtre vide

- [ ] Ajouter pygame (dépendance **principale** : le jeu en a besoin pour tourner) :

```bash
uv add pygame
```

Regarde `git diff` : quelles lignes ont changé dans `pyproject.toml` ? Et `uv.lock` ?
- [ ] Commit, avec **les deux** fichiers ensemble : `build: ajoute pygame aux dépendances`.
- [ ] Créer `src/rubiks/render/__init__.py` (une docstring d'une ligne suffit) et `src/rubiks/render/view2d.py`, avec une docstring de module qui dit à quoi sert le fichier.
- [ ] Dans `view2d.py`, une fonction `run()` qui ouvre une fenêtre vide, avec un titre, et qui se ferme avec la croix **ou** la touche Échap (notions 2 et 3).
- [ ] Faire appeler `run()` par `main()` dans `src/rubiks/__init__.py`, **sans** casser la règle « le cube ne dépend pas de l'affichage » (notion 7).
- [ ] Vérifier :
- `uv run rubiks` ouvre la fenêtre ;
- la commande de la notion 7 affiche `False` ;
- `uv run pytest` est toujours vert.
- [ ] Commit : `feat: ouvre la fenêtre de l'affichage 2D`. Puis push, PR, merge, rangement.

### Étape D — Branche `feature/view2d-draw` : dessiner le cube

- [ ] Une constante avec les 6 couleurs RVB, **dans l'ordre des couleurs du cube** (0 = blanc, 1 = rouge, 2 = vert, 3 = jaune, 4 = orange, 5 = bleu). Un tuple de 6 tuples suffit : `COLORS[color]` donne alors la couleur à dessiner.
- [ ] Une fonction pure qui donne la position en pixels d'une case `(face, row, col)` (notions 5 et 6). Les décalages des faces se lisent sur ton patron.
- [ ] Ses tests, dans un nouveau fichier `tests/test_view2d.py` :
- les 54 positions sont **toutes différentes** (indice : un `set` de tuples, et sa longueur) ;
- la case U6 est **juste au-dessus** de F0 : même `x`, et un `y` plus petit d'une case ;
- (au choix) la case L2 est **juste à gauche** de F0, ou une autre jonction du patron.

Ces tests vérifient que ton dessin respecte l'orientation décrite dans `cube.py`. Pense à les voir **rouges** d'abord.
- [ ] Dans la boucle de jeu, dessiner les 54 cases à partir de `cube.state`. L'affichage **lit** `cube.state`, il ne le modifie jamais.
- [ ] Vérifier à l'œil : lance la fenêtre avec un cube mélangé (par exemple `cube.scramble(5, seed=0)` provisoirement dans `run()`), puis compare avec `print(cube)` après le même mélange dans la console. Les deux patrons doivent être identiques. Retire le mélange provisoire avant de commiter.
- [ ] Commits (au moins deux : la fonction + ses tests, puis le dessin). Push, PR, merge, rangement.

### Étape E — Branche `feature/keyboard-moves` : jouer au clavier

- [ ] Une fonction pure qui transforme une touche en mouvement (notion 6) : `"u"` sans Maj donne `"U"`, `"u"` avec Maj donne `"U'"`, et une touche qui n'est pas une face (`"x"`, `"space"`, `"escape"`…) donne `None`.
- [ ] Ses tests, paramétrés : les 12 cas des 6 faces (avec et sans Maj), et quelques touches qui doivent donner `None`.
- [ ] Dans la boucle, à chaque `KEYDOWN` : trouver le mouvement, et s'il existe, l'appliquer avec `cube.move(...)`.
- [ ] Vérifier à l'œil, sur un **vrai cube** tenu blanc en haut et vert devant : `R`, puis `Maj+R`, puis `F` et `B` (les plus traîtres). Le patron doit bouger comme ton vrai cube.
- [ ] Commits, push, PR, merge, rangement.

### Étape F — Branche `feature/scramble-reset` : mélanger, recommencer, gagner

- [ ] **Espace** : mélange le cube. Choisis un nombre de coups dans une constante (commence petit, 4 ou 5, pour pouvoir le refaire).
- [ ] **Retour arrière** (`"backspace"`) : remet un cube neuf. Réfléchis : vaut-il mieux remplacer l'objet par `Cube()`, ou modifier l'objet existant ?
- [ ] Afficher sous le patron la **suite de mouvements du mélange** (notion 4). Elle te permet de vérifier, et de refaire le cube même sans savoir le résoudre : `inverse_sequence` te dit quoi taper.
- [ ] Afficher **« Résolu ! »** quand le cube est résolu… mais pas au lancement, quand le cube est neuf. Que doit retenir le programme pour faire la différence ?
- [ ] Afficher en bas de la fenêtre une ligne d'aide : quelles touches font quoi.
- [ ] Vérifier le critère de la phase : mélanger, puis refaire le cube au clavier, jusqu'au message.
- [ ] Commits, push, PR, merge, rangement.

### Étape G — Nettoyer et clore (branche `docs/cloture-phase-2`)

**Leçon de la phase 1 :** la clôture se fait **dans une branche, avant le merge**. Après le merge, il est trop tard pour cette PR.

- [ ] Depuis la racine : `uv run ruff check .`, `uv run ruff format .`, `uv run pytest`.
- [ ] Relire `view2d.py` : une docstring par fonction, des annotations de type, aucun nombre « magique » sans nom (taille des cases, marges, couleurs… en constantes en haut du fichier).
- [ ] `README.md` : mettre à jour l'avancement, et ajouter un tableau des touches.
- [ ] `docs/cadrage.md`, annexe B : phase 2 « Terminé » avec la date. `CLAUDE.md` : phase en cours = phase 3.
- [ ] (Optionnel) `uv version --bump minor` fait passer la version du projet de `0.1.0` à `0.2.0`, dans `pyproject.toml` **et** `uv.lock` : commit `build: passe la version à 0.2.0`.
- [ ] Commit `docs: clôture la phase 2`, push, PR, merge, rangement.
- [ ] Sur `main` à jour : `uv sync`, `uv run pytest`, `uv run rubiks` une dernière fois, puis le tag :

```bash
git tag -a v0.2.0 -m "Phase 2 : affichage 2D et clavier"
git push origin v0.2.0
```

- [ ] Me demander une relecture, puis la fiche de la phase 3.

---

## Comment vérifier que c'est bon

- [ ] `uv run pytest -v` : tout est vert, les tests de la phase 1 **et** ceux de `test_view2d.py` (positions des cases, touches).
- [ ] Aucun test n'ouvre de fenêtre.
- [ ] `uv run ruff check .` → `All checks passed!` et `uv run ruff format --check .` ne signale rien.
- [ ] `uv run python -c "import sys, rubiks.cube; print('pygame' in sys.modules)"` affiche `False`.
- [ ] À l'écran :
- `uv run rubiks` ouvre la fenêtre avec le cube résolu, sans « Résolu ! » ;
- le patron a la même forme et la même orientation que `print(Cube())` ;
- chaque lettre fait le bon quart de tour, Maj fait l'inverse, et chaque appui ne fait **qu'un** mouvement ;
- Espace mélange, Retour arrière réinitialise, Échap et la croix ferment la fenêtre ;
- après un mélange, je refais le cube et « Résolu ! » apparaît.
- [ ] `git log --oneline --graph --all` montre plusieurs petites branches qui partent de `main` et y reviennent, et les tags `v0.1.0` et `v0.2.0`.
- [ ] Sur GitHub : toutes les PR sont **Merged**, il ne reste que la branche `main`, les deux tags sont visibles.
- [ ] Je sais expliquer avec mes mots :
- les trois temps d'une boucle de jeu, et ce qui se passe si on en oublie un ;
- la différence entre `KEYDOWN` et `get_pressed()` ;
- pourquoi `event.mod & pygame.KMOD_SHIFT`, et pas `==` ;
- pourquoi les calculs sont sortis dans des fonctions pures ;
- pourquoi `import rubiks.cube` ne doit pas charger pygame ;
- ce que montre `git log main..ma-branche`, et pourquoi chaque branche part d'un `main` à jour.

---

## Pièges fréquents

| Symptôme | Cause | Solution |
|---|---|---|
| la fenêtre se fige, Windows dit « Ne répond pas » | les événements ne sont pas lus à chaque image | une boucle `for event in pygame.event.get()` à **chaque** tour de la boucle de jeu |
| la fenêtre s'ouvre et se referme aussitôt | pas de boucle, ou `running` vaut `False` dès le départ | revoir la notion 2 |
| la fenêtre reste noire | `pygame.display.flip()` oublié | dessiner, **puis** `flip()`, à chaque image |
| les anciens dessins restent, ça laisse des traces | `screen.fill(...)` oublié au début du dessin | repartir d'un fond uni à chaque image |
| le patron est à l'envers, ou couché sur le côté | `y` va vers le bas, ou `[ligne, colonne]` confondu avec `(x, y)` | notion 5 ; les tests de jonction U6/F0 le détectent |
| un appui fait plusieurs mouvements | `pygame.key.get_pressed()` utilisé au lieu de `KEYDOWN` | réagir aux événements `KEYDOWN` (notion 3) |
| Maj n'est pas détectée (chez toi, ou seulement quand Verr. Num est allumé) | `event.mod == pygame.KMOD_SHIFT` : `mod` contient aussi les autres interrupteurs | `bool(event.mod & pygame.KMOD_SHIFT)` |
| Maj + U donne un `"U"` majuscule inattendu, ou Verr. Maj inverse tout | `event.unicode` utilisé : il dépend de Maj **et** de Verr. Maj | utiliser `pygame.key.name(event.key)` (toujours en minuscule) et `event.mod` |
| « Résolu ! » s'affiche dès le lancement | un cube neuf est résolu | retenir qu'un mélange a eu lieu (étape F) |
| la commande de la notion 7 affiche `True` | `rubiks/__init__.py` importe `view2d` (donc pygame) tout en haut | déplacer cet import dans la fonction `main` |
| `ModuleNotFoundError: No module named 'pygame'` | `uv add pygame` oublié, ou `python` lancé sans `uv run` | étape C ; toujours `uv run` |
| `pygame.error: video system not initialized` | `pygame.init()` oublié, ou du dessin après `pygame.quit()` | `init()` au début, `quit()` **après** la boucle |
| un message « Hello from the pygame community » au lancement | message normal de pygame | rien à faire (on peut le masquer, mais ce n'est pas utile) |
| le texte est lent, la fenêtre rame | police recréée à chaque image | créer la police une seule fois, avant la boucle (notion 4) |
| un test ouvre une fenêtre, ou plante sur une machine sans écran | la boucle de jeu est testée directement | tester seulement les fonctions pures (notion 6) |
| ma nouvelle branche n'a pas le travail de la précédente | branche créée depuis un `main` en retard | `git switch main` + `git pull` **avant** `git switch -c` |
| `! [rejected] … (fetch first)` au `git push` | quelqu'un (toi, sur GitHub) a ajouté un commit à la branche | `git pull`, puis `git push`. Le `pull` peut créer un commit de merge : c'est normal |
| un commit fait après le merge n'arrive pas dans `main` | une PR mergée est close ; la branche ne la met plus à jour | faire la clôture **avant** le merge, ou ouvrir une nouvelle PR |
| `git log` affiche `:` en bas et ne rend pas la main | la sortie s'affiche page par page | `q` pour quitter |

---

## Pour aller plus loin (optionnel)

- **Annuler (Ctrl+Z).** Garde la liste des mouvements joués depuis le début ; Ctrl+Z joue l'inverse du dernier et le retire de la liste. `event.mod & pygame.KMOD_CTRL` détecte Ctrl.
- **Compteur et chronomètre.** Affiche le nombre de mouvements depuis le mélange, et le temps écoulé (`pygame.time.get_ticks()` donne les millisecondes depuis le lancement).
- **Les demi-tours au clavier.** Par exemple Ctrl + lettre pour `X2`. Ta fonction de touches et ses tests s'étendent facilement.
- **Un second affichage, dans le terminal.** Une fonction qui affiche le patron en couleurs avec les codes ANSI (`"\033[41m \033[0m"` dessine un carré à fond rouge dans la plupart des terminaux). Si elle n'a besoin que de `cube.state`, c'est la preuve que logique et affichage sont bien séparés.
- **Un test automatique de la règle « pas de pygame dans le cube ».** Avec `subprocess.run([sys.executable, "-c", "..."], capture_output=True, text=True)`, un test peut lancer la commande de la notion 7 dans un Python neuf et vérifier sa sortie. Ainsi, plus personne ne pourra casser la règle sans que les tests le voient.
- **Une capture d'écran dans le README.** `pygame.image.save(screen, "docs/capture.png")` enregistre la fenêtre ; une ligne `![Le jeu](docs/capture.png)` l'affiche dans le README sur GitHub.
- **Un alias Git pour le graphe.** `git config --global alias.lg "log --oneline --graph --all"` : ensuite, `git lg` suffit.
- **Protéger `main` sur GitHub** (si ce n'est pas déjà fait) : *Settings* → *Rules* → *Rulesets*, exiger une Pull Request avant tout merge dans `main`.
- **Une release GitHub** pour `v0.2.0`, avec une capture d'écran et la liste des touches.
- **pygame-ce.** Il existe une version de pygame maintenue par la communauté, `pygame-ce`, qui s'utilise presque à l'identique (`import pygame`). Bon à savoir si tu lis de la documentation récente ; pas besoin de changer.