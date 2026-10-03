# Fiche — Phase 3 : Vue 3D manipulable

> **Emplacement dans le repo :** `docs/fiches/phase-3-vue-3d.md`
> **Durée indicative :** 12 à 20 h, en plusieurs séances. C'est la phase la plus longue du « jeu » : chaque étape se termine par un commit, chaque branche par une Pull Request, et tu peux t'arrêter après n'importe laquelle.
> **Documents liés :** `docs/cadrage.md` (section 4 « Idée clé d'architecture », section 6 « Phase 3 », section 9 « Décisions à prendre plus tard », section 10 « Risques »), la docstring de `src/rubiks/cube.py` (orientation des faces) et `src/rubiks/game.py` (règles du jeu, déjà indépendantes de l'affichage).

## Statut : phase réalisée par Claude (02/10/2026)

À ta demande, Claude a codé cette phase (et tous les « pour aller plus loin » des phases 0 à 3) pour que tu passes plus vite au RL. **La fiche reste un cours** : lis une notion, puis le code qui la met en œuvre.

| Notion de la fiche | Où la lire dans le code |
|---|---|
| 1. Coordonnées 3D, cubie + normale | `geometry.py` : `sticker_location`, `CUBIES`, `FACE_NORMALS` |
| 2. Une scène ursina, une classe qui hérite d'`Entity` | `render/view3d.py` : `CubeView`, `run` |
| 3. Parents et pivot | `view3d.py` : `start_animation`, `repaint` (`world_parent`, `parent`) |
| 4. Tourner un point d'un quart de tour | `geometry.py` : `rotate`, `rotation_matrix`, `move_rotation` |
| 5. Animer avec `time.dt`, file d'attente | `game.py` : `Player.update`, `smoothstep` ; `view3d.py` : `update` |
| 6. Jouer, animer, repeindre | `game.py` : `Player` (`shown_cube`, `Tick`) ; `view3d.py` : `repaint` |
| 7. Le grand test | `tests/test_geometry.py` : `test_move_rotates_the_layer_in_space` |
| 8. Coordonnées logiques → ursina | `view3d.py` : `to_ursina`, et le signe moins de `update` |
| 9. Couleurs partagées sans charger pygame | `render/colors.py` |
| Question de conception (notion 6) | `Game.execute` renvoie les coups joués ; `Player` s'en sert |

Ce qui **n'a pas** été fait : l'exercice du conflit de merge (étape D). Garde-le pour une occasion réelle, ou refais-le tel quel un jour sur le README : il ne dépend d'aucun code.

Trois pièges découverts en codant, ajoutés au tableau « Pièges fréquents » : le clavier AZERTY dans ursina, les raccourcis d'`EditorCamera` qui volent Maj+F, et le rendu hors écran.

## Objectif

À la fin de cette phase, j'ai :

- une **fenêtre 3D** qui montre le cube avec ses 26 petits cubes (« cubies »), lancée avec `uv run rubiks` ;
- une **caméra orbitale** : je fais tourner la vue autour du cube à la souris, et je zoome à la molette ;
- les mêmes touches qu'en 2D (`U D L R F B`, Maj pour l'inverse, Espace, Retour arrière, Échap), mais les faces **tournent en animation** ;
- un `Cube` logique qui reste **la seule source de vérité** : la 3D ne fait que montrer `cube.state` ;
- un **test qui prouve** que la géométrie 3D et les mouvements de `cube.py` racontent la même histoire ;
- mon **premier conflit de merge**, provoqué exprès et résolu à la main ;
- le tag `v1.0.0` : le jeu est fini !

**Terminé quand** (cadrage) : le jeu 3D est jouable et reste cohérent avec les tests de la phase 1.

---

## Ce que la phase 2 t'a déjà donné

Tu pars de très haut, et c'est grâce à l'architecture :

| Déjà fait | Ce que ça t'évite en phase 3 |
|---|---|
| `Cube` : état, 18 mouvements, testés | aucune logique de cube à écrire en 3D |
| `game.py` : touches → mouvements, mélange, reset, victoire, **sans pygame** | la vue 3D réutilise `Game` telle quelle |
| `test_render.py` : « le cube ne charge pas pygame » | il suffira d'ajouter la bibliothèque 3D au test |
| la boucle de jeu (événements → dessin → affichage) | même idée en 3D, présentée autrement (notion 2) |

La phase 3 ajoute donc **une seule chose** : une nouvelle façon de *montrer* le cube. Si tu te surprends à modifier `cube.py`, arrête-toi et demande-toi pourquoi.

---

## Décision de début de phase : quelle bibliothèque 3D ?

Le cadrage (section 9) laisse ce choix pour le début de la phase 3.

| | `ursina` | `pygame` + `PyOpenGL` |
|---|---|---|
| Ce qu'il faut apprendre | des **objets** (`Entity`) qu'on place, colore et fait tourner | matrices de projection, caméra, profondeur, dessin face par face… |
| Caméra orbitale à la souris | `EditorCamera()` : **une ligne** | à programmer soi-même (angles, glisser de souris, matrices) |
| Faire tourner une couche | on accroche 9 cubies à un objet « pivot » et on tourne le pivot | on calcule soi-même la rotation de chaque sommet |
| Temps avant de voir un cube à l'écran | une soirée | plusieurs soirées |
| Ce qu'on comprend de la 3D | les idées (coordonnées, axes, parents, rotations) | les idées **et** toute la mécanique en dessous |

**Je recommande `ursina`.** L'objectif de la phase est un *jeu* 3D jouable ; les notions qui comptent pour toi (coordonnées 3D, cubies, rotations, animation, caméra) sont toutes là, et le risque n° 1 du cadrage (« la 3D prend beaucoup plus de temps que prévu ») reste sous contrôle. OpenGL est très formateur, mais c'est un projet à lui seul : garde-le pour un bonus.

Quelques faits utiles, vérifiés au moment d'écrire la fiche : ursina est en version 8.x, demande **Python 3.12 ou plus** (c'est notre version), et s'appuie sur le moteur Panda3D, installé automatiquement avec lui.

Ta décision se note dans `docs/cadrage.md`, section 9, ligne « Bibliothèque 3D » (étape B), comme pour pygame.

---

## Notions Python à connaître

Comme d'habitude : **noms en anglais, commentaires en français**, et des mini-exemples **hors projet**. Pour les essayer : ursina ajouté au projet (étape C), un fichier `essai.py` à la racine, **non commité**, lancé avec `uv run python essai.py`.

### 1. Les coordonnées 3D

En 2D, un point avait deux nombres `(x, y)`. En 3D, il en a **trois** : `(x, y, z)`.

Pour le cube, je te propose cette convention « logique », simple à retenir, avec le cube **centré sur l'origine** :

```
        y (vers U, le haut)
        │
        │
        └──────── x (vers R, la droite)
       ╱
      ╱
     z (vers F, vers moi)
```

- Chaque cubie a un **centre** dont les coordonnées valent `-1`, `0` ou `1`. Exemple : le coin en haut, à droite, devant (blanc-rouge-vert) est en `(1, 1, 1)` ; le centre de la face F est en `(0, 0, 1)`.
- 3 × 3 × 3 = 27 positions, moins le centre invisible `(0, 0, 0)` : **26 cubies**.
- Chaque face a une **normale** : la flèche qui sort de la face, vers l'extérieur. F a la normale `(0, 0, 1)`, U a `(0, 1, 0)`, L a `(-1, 0, 0)`…

**Une case (sticker) = un cubie + une normale.** La case F2 (en haut à droite de F) est collée sur le cubie `(1, 1, 1)`, du côté de la normale `(0, 0, 1)`. Le même cubie porte aussi U8 (normale `(0, 1, 0)`) et R0 (normale `(1, 0, 0)`) : c'est un coin, il a 3 cases.

Mini-exercice (sur papier, avant de coder) : sur un **vrai cube** tenu blanc en haut et vert devant, trouve le cubie et la normale de U0, L6, R2, B0 et D8. Relis bien la docstring de `cube.py` : « U vue de dessus avec F en bas », « D vue de dessous avec F en haut »… c'est elle qui fait foi.

### 2. Une scène ursina : des objets, pas une boucle

Avec pygame, **tu écrivais** la boucle de jeu. Avec ursina, la boucle existe déjà, cachée dans `app.run()`. Toi, tu crées des **objets** (`Entity`), et ursina les dessine à chaque image. Les trois temps de la boucle sont toujours là, mais c'est ursina qui les enchaîne et qui **t'appelle** :

| Temps de la boucle (phase 2) | Avec ursina |
|---|---|
| 1. lire les événements | ursina appelle la méthode `input(key)` des objets, une fois par touche |
| 2. dessiner | ursina dessine tout seul tous les objets existants |
| (entre les deux) faire avancer le jeu | ursina appelle la méthode `update()` des objets, à chaque image |

Mini-exemple (hors projet) : une boîte qui tourne, une caméra orbitale, Espace change la couleur.

```python
from ursina import EditorCamera, Entity, Ursina, application, color, time

app = Ursina()  # crée la fenêtre (à faire AVANT de créer des Entity)


class SpinningBox(Entity):
    """Une boîte qui tourne sur elle-même."""

    def __init__(self) -> None:
        super().__init__(model="cube", color=color.orange)

    def update(self) -> None:
        # appelée à chaque image ; time.dt = secondes écoulées depuis l'image précédente
        self.rotation_y += 90 * time.dt  # 90 degrés par seconde, quelle que soit la vitesse du PC

    def input(self, key: str) -> None:
        # appelée une fois par événement clavier ou souris
        print(key)  # pour voir les noms exacts des touches
        if key == "space":
            self.color = color.azure
        elif key == "escape":
            application.quit()


SpinningBox()
EditorCamera()  # clic droit + glisser : tourner autour ; molette : zoomer
app.run()  # la boucle de jeu, cachée ici
```

**À essayer :** remplace `90 * time.dt` par `1`. Pourquoi la vitesse dépend-elle maintenant de ton ordinateur ? Puis lis ce que `print(key)` affiche quand tu appuies sur `u`, quand tu le relâches, et avec Maj enfoncée.

**Pourquoi une classe qui hérite de `Entity` ?** Ursina sait aussi appeler des fonctions `update()` et `input()` écrites « en vrac », mais **seulement dans le fichier lancé directement** (le script principal). Avec `uv run rubiks`, le script principal n'est pas `view3d.py` : ces fonctions ne seraient jamais appelées, sans aucun message d'erreur. Les méthodes d'une `Entity` marchent partout. (C'est l'héritage : `SpinningBox` *est une* `Entity`, avec en plus ce qu'on lui ajoute ; `super().__init__(...)` construit la partie `Entity`.)

### 3. Parents et enfants : l'astuce pour tourner une couche

Une `Entity` peut avoir un **parent**. Ses coordonnées sont alors **relatives** au parent : si le parent tourne, l'enfant tourne avec lui, comme une lune autour d'une planète qui tourne.

Mini-exemple (hors projet) : un bras de manège.

```python
pivot = Entity()  # un objet invisible, au centre
seat = Entity(model="cube", color=color.red, scale=0.3, parent=pivot, x=2)
# seat est à 2 unités du pivot ; si le pivot tourne, seat décrit un cercle
```

Pour faire tourner la couche R :

1. on crée (ou on réutilise) un **pivot** au centre du cube ;
2. on accroche au pivot les 9 cubies dont `x == 1` ;
3. on fait tourner le pivot de 0 à 90 degrés, petit à petit (notion 5) ;
4. à la fin, on remet tout en place (notion 6).

Attention à la différence entre `parent` et `world_parent` : changer `parent` **garde les coordonnées relatives** (le cubie « saute » à un autre endroit si le nouveau parent est ailleurs ou tourné), changer `world_parent` **garde la position à l'écran**. Si ton pivot est au centre et non tourné au moment d'accrocher les cubies, les deux donnent le même résultat. Bonne occasion de vérifier que tu as compris.

### 4. Tourner un point d'un quart de tour

C'est le cœur mathématique de la phase, et il tient en quelques lignes.

En 2D d'abord (hors projet) : tourner un point de 90° **dans le sens inverse des aiguilles d'une montre** autour de l'origine, c'est

```
(x, y)  →  (-y, x)
```

Vérifie sur un dessin : `(1, 0)` (à droite) devient `(0, 1)` (en haut). `(0, 1)` devient `(-1, 0)` (à gauche). Et dans **le sens des aiguilles d'une montre** ? Trouve-le toi-même, puis vérifie avec deux points.

En 3D, tourner autour d'un axe, c'est **la même chose dans le plan perpendiculaire** à cet axe : la coordonnée de l'axe ne bouge pas. Tourner autour de l'axe x, c'est tourner le couple `(y, z)` et garder `x`. Le centre d'un cubie **et** la normale de chaque case tournent de la même façon.

**Le sens.** « R = horaire en regardant la face depuis l'extérieur » : tu regardes la face R depuis la droite, donc depuis les `x` positifs, et tu tournes dans le sens des aiguilles. Pour L, tu regardes depuis les `x` négatifs : le même « horaire » est l'inverse vu depuis la droite. Méthode sûre : prends **un point** dont tu connais la destination sur un vrai cube (avec R, la case du milieu à droite de F monte sur U) et vérifie ta formule avec lui.

Avec numpy, un point est un petit tableau `np.array([x, y, z])`, et la rotation peut s'écrire comme une **matrice 3 × 3** : `new_point = matrix @ point` (`@` = produit matriciel). Ce n'est pas obligatoire : une fonction qui échange et change le signe des bonnes coordonnées suffit très bien. Choisis ce que tu sais expliquer.

### 5. Animer : avancer un peu à chaque image

Une animation, c'est un nombre qui va **de 0 à 90 degrés en, disons, 0,2 seconde**, un peu plus à chaque image :

```python
# dans update() (hors projet, schéma) :
self.angle += SPEED * time.dt          # SPEED en degrés par seconde
if self.angle >= 90:                   # fini ?
    self.angle = 90
    ...                                # fin de l'animation (notion 6)
pivot.rotation_x = self.angle * sign   # sign = +1 ou -1 selon le sens
```

Pendant une animation, **que fait une nouvelle touche ?** Trois choix possibles : l'ignorer (simple, mais frustrant quand on tape vite), la **mettre en file d'attente** (une `list` : on ajoute à la fin avec `append`, on prend au début avec `pop(0)`), ou terminer l'animation en cours tout de suite. Commence par l'ignorer, puis passe à la file d'attente : c'est un très bon exercice.

Ursina propose aussi `entity.animate_rotation(...)`, qui anime tout seul. C'est pratique, mais la version « à la main » ci-dessus te fait comprendre ce qu'il fait, et te laisse le contrôle de la fin de l'animation, dont tu as besoin.

### 6. Une seule source de vérité : la stratégie « jouer, animer, repeindre »

C'est **l'idée la plus importante de la phase**. Deux façons de faire existent :

- **Mauvaise idée :** les cubies 3D gardent leur position et leur orientation après chaque rotation, et deviennent *eux-mêmes* l'état du cube. Il y a alors **deux** cubes (le `Cube` logique et le cube 3D), qui finissent tôt ou tard par ne plus être d'accord (arrondis des angles, erreurs de sens…), et rien ne te prévient.
- **Bonne idée :** le `Cube` logique est **le seul** à savoir où sont les couleurs. La 3D n'est qu'un **dessin** de `cube.state`.

Concrètement, quand une touche donne un mouvement, par exemple `R` :

1. **jouer** : le `Game` applique `R` au `Cube` logique, **tout de suite** (rien de nouveau, c'est `game.press`) ;
2. **animer** : la 3D fait tourner la couche R de 0 à 90° ; les cubies montrent encore les *anciennes* couleurs, qui tournent ;
3. **repeindre** : à la fin, on remet chaque cubie à sa place de départ, rotation à zéro, et on **recolore les 54 cases** à partir de `cube.state`.

L'œil ne voit aucune différence : les anciennes couleurs, tournées de 90°, sont exactement à la place des nouvelles. Si ce n'est pas le cas, ta géométrie ou ton sens de rotation est faux… et le test de la notion 7 te l'aura déjà dit. Bonus : Espace et Retour arrière n'ont pas besoin d'animation, il suffit de **repeindre**.

**Une petite question de conception :** pour savoir *quelle* couche animer, la vue doit connaître le mouvement joué. Aujourd'hui, `Game.press` ne renvoie rien. Qu'est-ce que tu pourrais changer, **sans casser** la vue 2D ni les tests de `test_game.py` ?

### 7. Le test qui relie la 3D et la logique

Une fenêtre se teste mal (phase 2, notion 6). Donc, comme en 2D, on sort les calculs dans des **fonctions pures**, dans un module **qui n'importe pas ursina** (par exemple `src/rubiks/geometry.py`) :

- **« où est cette case ? »** : `(face, row, col)` → `(centre du cubie, normale)` ;
- **« tourner un point »** : un point (ou une normale), un mouvement → le point tourné (notion 4) ;
- **« quels cubies dans cette couche ? »** : un mouvement → les cubies dont, par exemple, `x == 1`.

Les tests faciles d'abord, comme pour le patron 2D : les 54 couples (cubie, normale) sont **tous différents** ; chaque normale a une seule coordonnée non nulle ; chaque case de F a `z == 1` et la normale `(0, 0, 1)`…

Puis **le grand test**, celui qui fait le lien avec la phase 1. L'idée :

1. on fabrique un cube où **chaque case a une couleur différente** : 54 « couleurs », de 0 à 53 (indice : `np.arange` et `reshape`, puis on remplace `cube.state`) ;
2. on applique un mouvement, par exemple `R`, avec `cube.move` ;
3. pour chaque étiquette de 0 à 53 : on regarde **où elle était** avant (cubie + normale), et **où elle est** après ;
4. si elle était dans la couche tournée, sa nouvelle place doit être **l'ancienne place tournée d'un quart de tour** (notion 4) ; sinon, elle ne doit **pas avoir bougé**.

Paramétré sur les 6 faces, ce test vérifie à la fois ta géométrie, ton sens de rotation **et** les mouvements de `cube.py`. Bonne nouvelle : avec la convention de la notion 1, tes 6 mouvements actuels le passent. S'il est rouge, l'erreur est donc dans ta géométrie ou ta rotation, pas dans `cube.py`.

Pense à le voir **rouge** d'abord (par exemple en inversant exprès le sens d'une rotation).

### 8. Des coordonnées logiques aux coordonnées ursina

Ursina a sa propre convention : `y` vers le haut comme nous, mais `z` **s'éloigne** de la caméra (la caméra par défaut regarde vers les `z` positifs). Avec notre convention (`z` vers F, vers moi), la face F serait donc… **de dos**.

Deux solutions : convertir à un seul endroit (une petite fonction « logique → écran », par exemple qui change le signe de `z`), ou placer la caméra de l'autre côté. Dans les deux cas, **un seul endroit** du code s'en occupe : le reste parle uniquement en coordonnées logiques, celles que tes tests vérifient.

Conséquence à surveiller : changer le signe d'un axe change aussi le **sens apparent** des rotations autour des autres axes. Si certaines faces tournent à l'envers pendant l'animation alors que le test de la notion 7 est vert, c'est le signe de l'animation qui est faux, pas ta géométrie.

### 9. Des couleurs et des tailles en constantes

Comme en 2D : aucune valeur « magique ». Taille d'un cubie, espace entre cubies, épaisseur d'une case, couleur du plastique (noir), vitesse de l'animation, couleurs des faces… en constantes en haut de `view3d.py`.

Pour les couleurs, vérifie dans la documentation de ta version d'ursina quelle fonction accepte des nombres **de 0 à 255** (tes couleurs de `view2d.py`) et laquelle attend des nombres **de 0 à 1**. Réutiliser `COLORS` de `view2d.py` est tentant, mais importer `view2d` chargerait pygame dans la vue 3D : où ranger ces couleurs pour que les deux vues les partagent ?

---

## Notions Git de l'étape

### Le conflit de merge, expliqué simplement

Git sait fusionner tout seul deux branches qui ont modifié **des endroits différents**. Mais si les deux ont modifié **la même ligne** de deux façons différentes, Git ne peut pas deviner laquelle garder : c'est un **conflit**. Git s'arrête, et te demande de choisir.

Dans le fichier, Git écrit alors les deux versions, encadrées par des **marqueurs** :

```
<<<<<<< HEAD
La version de la branche où je suis (ici, ma branche)
=======
La version de la branche que je fusionne (ici, main)
>>>>>>> main
```

**Résoudre**, c'est :

1. ouvrir le fichier, choisir (garder une version, l'autre, ou un mélange des deux) ;
2. **supprimer les trois lignes de marqueurs** ;
3. `git add fichier` : « ce conflit est résolu » ;
4. `git commit` : termine le merge (Git propose un message tout prêt).

| Commande | À quoi ça sert |
|---|---|
| `git merge main` | (depuis ma branche) intègre les nouveautés de `main` dans ma branche |
| `git status` | pendant un conflit : liste les fichiers « both modified » à résoudre |
| `git diff` | montre les conflits restants |
| `git merge --abort` | panique ? annule le merge en cours et revient à l'état d'avant |
| `git log --oneline --graph --all` | après : le commit de merge a **deux parents** |

Un conflit n'est **pas une erreur**, ni une panne : c'est Git qui te demande ton avis. Et tant que tu n'as pas fait `git commit`, `git merge --abort` remet tout comme avant.

VS Code (et la plupart des éditeurs) affichent les conflits en couleur, avec des boutons « Accept Current / Incoming / Both ». C'est pratique, mais fais le premier **à la main**, pour voir les marqueurs.

### L'exercice : un conflit provoqué exprès (étape D)

```
main ●────────────────●──────────────────────● (merge de la PR B)
      \              ╱ (PR A)               ╱
       ●── A ───────●                      ╱
        \                                 ╱
         ●── B ──── git merge main ──●───●   ← conflit, résolu ici
```

Deux branches partent du **même** `main`, et modifient **la même ligne** du README, chacune à sa façon. A est mergée en premier : B entre alors en conflit avec `main`. On résout le conflit **dans la branche B**, avant sa PR. Les détails sont à l'étape D.

### Ranger après soi : supprimer les branches distantes

Une branche mergée dont on n'a plus besoin se supprime **aussi sur GitHub**, sinon elles s'accumulent (c'est le cas aujourd'hui, voir étape A) :

| Commande / action | À quoi ça sert |
|---|---|
| bouton **Delete branch** sur la PR mergée | supprime la branche sur GitHub |
| `git push origin --delete nom-de-branche` | la même chose, depuis le terminal |
| `git fetch --prune` | oublie, en local, les branches distantes qui n'existent plus |
| `git branch -a` | liste les branches locales **et** distantes (`remotes/origin/…`) |

---

## Tâches (dans l'ordre)

**Bloqué ?** Demande-moi un indice. Je réponds par niveaux : (1) une question ou une piste, (2) l'explication de la notion, (3) un petit exemple hors projet, (4) la solution, seulement si tu la demandes.

**À chaque branche, le même cycle** (cadrage, section 7) : `main` à jour → `git switch -c …` → commits → `uv run pytest` + `uv run ruff check .` → `git push -u origin …` → PR → **Create a merge commit** → **Delete branch** → `git switch main` → `git pull` → `git branch -d …` → `git fetch --prune`.

### Étape A — Finir de ranger la phase 2 (branche `docs/rangement-phase-2`)

Voir la relecture de fin de phase 2. En résumé :

- [ ] Supprimer sur GitHub les 4 branches déjà mergées (`docs/fiche-phase-2`, `feature/view2d-window`, `view2d-draw`, `feature/scramble-reset`), puis `git fetch --prune`. Vérifier : `git branch -a` ne montre plus que `main` (et `origin/main`).
- [ ] Dans une branche `docs/rangement-phase-2` :
  - [ ] `README.md` : ajouter le tableau des touches (demandé à l'étape G de la phase 2), et revoir la phrase d'avancement (le mélange est affiché, on ne « devine » plus rien).
  - [ ] (Recommandé) Les petites corrections de `cube.py` signalées en relecture (commentaires, annotations).
- [ ] Push, PR, merge, rangement. **Cette fois, pas de commit directement sur `main`.**

### Étape B — Branche `docs/fiche-phase-3`

- [ ] Placer cette fiche dans `docs/fiches/phase-3-vue-3d.md`. Commit : `docs: ajoute la fiche de la phase 3`.
- [ ] Dans `docs/cadrage.md`, section 9, noter la décision pour la bibliothèque 3D, avec la date. Commit : `docs: choisit ursina pour la vue 3D` (ou ton choix).
- [ ] Push, PR, merge, rangement.

### Étape C — Branche `feature/view3d-window` : une scène 3D

- [ ] Ajouter ursina (dépendance **principale**) :

  ```bash
  uv add ursina
  ```

  Regarde `git diff uv.lock` : combien de paquets sont arrivés avec lui ? Lesquels reconnais-tu ?
- [ ] Commit, avec **les deux** fichiers : `build: ajoute ursina aux dépendances`.
- [ ] Créer `src/rubiks/render/view3d.py` (docstring de module), avec une fonction `run()` qui ouvre une fenêtre ursina avec **un seul cube gris** au centre, une `EditorCamera`, et qui se ferme avec Échap (notion 2).
- [ ] Choisir comment lancer la vue 3D : remplacer la 2D dans `uv run rubiks` ? Ajouter une seconde commande dans `[project.scripts]` (par exemple `rubiks2d`) pour garder les deux ? Ton choix, mais **l'import d'ursina reste dans la fonction** (phase 2, notion 7).
- [ ] Ajouter `"ursina"` au test `test_logic_modules_do_not_load_pygame` de `tests/test_render.py` (et renommer le test, puisqu'il ne parle plus que de pygame).
- [ ] Vérifier : la fenêtre s'ouvre, le cube tourne à la souris, `uv run pytest` est vert.
- [ ] Commit `feat: ouvre la fenêtre de la vue 3D`, push, PR, merge, rangement.

### Étape D — L'exercice du conflit (branches `docs/conflit-a` et `docs/conflit-b`)

Un exercice à part, sur la documentation, pour apprendre sans risque.

- [ ] Depuis `main` à jour, créer `docs/conflit-a`. Modifier la ligne **Avancement** du README (par exemple « phase 3 : la scène 3D s'ouvre »). Commit, push. **Ne pas encore ouvrir de PR.**
- [ ] Revenir sur `main` (**sans** `git pull` : il n'y a rien de nouveau), créer `docs/conflit-b`. Modifier **la même ligne**, autrement (par exemple « phase 3 : en cours, vue 3D avec ursina »). Commit, push.
- [ ] Ouvrir la PR de `docs/conflit-a`, la merger. Rangement habituel.
- [ ] Ouvrir la PR de `docs/conflit-b` : que dit GitHub ? Ne pas cliquer sur « Resolve conflicts » : on résout en local.
- [ ] Sur `docs/conflit-b` : `git merge main`. Lire le message de Git, puis `git status`, puis ouvrir le README et trouver les marqueurs.
- [ ] Résoudre : écrire **la** ligne que tu veux garder, supprimer les marqueurs, `git add README.md`, `git commit`.
- [ ] `git log --oneline --graph --all` : retrouver le commit de merge et ses deux parents. Push : la PR n'a plus de conflit. Merger, ranger.
- [ ] (Pour t'entraîner) Recommence une fois, et termine cette fois par `git merge --abort` au lieu de résoudre : que devient la branche ?

### Étape E — Branche `feature/geometry` : la géométrie 3D, testée, sans fenêtre

- [ ] Créer `src/rubiks/geometry.py` : **aucun import d'ursina ni de pygame**, seulement numpy.
- [ ] Une fonction qui donne `(centre du cubie, normale)` d'une case `(face, row, col)` (notion 1). Commence par F (la notion 1 te donne F2 ; trouve la règle pour les 9 cases), puis les 5 autres, en t'aidant de ton vrai cube et de tes réponses au mini-exercice.
- [ ] Ses tests faciles dans `tests/test_geometry.py` (notion 7) : 54 couples tous différents, une seule coordonnée non nulle par normale, la bonne normale pour chaque face, et quelques cases connues (F2, U8 et R0 sur le cubie `(1, 1, 1)`…).
- [ ] Une fonction qui tourne un point d'un quart de tour, pour un mouvement donné (notion 4). Ses tests : 4 quarts de tour reviennent au point de départ ; un point **sur l'axe** ne bouge pas ; la case du milieu à droite de F, avec `R`, va bien sur U.
- [ ] Une fonction « est-ce que ce cubie fait partie de la couche de ce mouvement ? ».
- [ ] **Le grand test** de la notion 7, paramétré sur les 6 faces. Le voir rouge, puis vert.
- [ ] Ajouter `"rubiks.geometry"` au test qui vérifie qu'aucune bibliothèque d'affichage n'est chargée.
- [ ] Commits (au moins un par fonction et ses tests), push, PR, merge, rangement.

### Étape F — Branche `feature/view3d-cube` : dessiner le cube

- [ ] Les **26 cubies** : un petit cube noir à chaque position `(x, y, z)` avec `x, y, z` dans `-1, 0, 1`, sauf le centre. Un léger espace entre eux rend le cube plus lisible (constante).
- [ ] Les **54 cases** : pour chaque `(face, row, col)`, une plaque fine et colorée, **enfant** de son cubie, posée du côté de sa normale, légèrement à l'extérieur (sinon elle se cache dans le cube noir). Garde un moyen de retrouver la plaque d'une case, par exemple un dictionnaire `(face, row, col) → Entity`.
- [ ] Une fonction « repeindre » : donne à chaque plaque la couleur lue dans `cube.state` (notion 6). Elle **lit** `cube.state`, elle ne le modifie jamais.
- [ ] La conversion « logique → ursina » à **un seul endroit** (notion 8).
- [ ] Vérifier à l'œil, avec un mélange provisoire (`cube.scramble(5, seed=0)`) : comparer la 3D avec `print(cube)` et la fenêtre 2D. Regarder surtout **B** et **D**, les deux faces qu'on voit « à l'envers ». Retirer le mélange provisoire avant de commiter.
- [ ] Commits, push, PR, merge, rangement.

### Étape G — Branche `feature/view3d-keyboard` : jouer, sans animation d'abord

- [ ] Brancher le clavier sur un `Game` : chaque touche va à `game.press(...)`, puis on **repeint**. Lire Maj : regarde ce que `print(key)` affiche, et ce que contient `held_keys` (notion 2).
- [ ] Afficher « Résolu ! », la suite du mélange et l'aide (`Text` d'ursina).
- [ ] Vérifier : on peut déjà mélanger et refaire le cube en 3D, **sans animation**. C'est un jeu jouable : ce commit vaut de l'or si la suite résiste.
- [ ] Commits, push, PR, merge, rangement.

### Étape H — Branche `feature/view3d-animation` : les faces qui tournent

- [ ] Répondre à la question de conception de la notion 6 (comment la vue sait quel mouvement animer), et adapter `game.py` **et** ses tests.
- [ ] L'animation d'un quart de tour : pivot, 9 cubies accrochés, angle qui avance avec `time.dt`, puis « repeindre » à la fin (notions 3, 5, 6).
- [ ] Le **sens** de rotation de chaque face : vérifier les 6 faces, à l'œil, sur ton vrai cube. Les couleurs ne doivent **pas sauter** à la fin de l'animation.
- [ ] Les touches tapées pendant une animation : ignorées d'abord, puis en file d'attente.
- [ ] Vérifier le critère de la phase : mélanger, puis refaire le cube au clavier en 3D, jusqu'à « Résolu ! ».
- [ ] Commits, push, PR, merge, rangement.

### Étape I — Nettoyer et clore (branche `docs/cloture-phase-3`)

**Toujours la même leçon :** la clôture se fait **dans une branche, avant le merge**, y compris le changement de version.

- [ ] `uv run ruff check .`, `uv run ruff format .`, `uv run pytest`.
- [ ] Relire `geometry.py` et `view3d.py` : une docstring par fonction, des annotations de type, aucun nombre magique.
- [ ] `README.md` : avancement, comment lancer le jeu, touches et souris, et pourquoi pas une capture d'écran.
- [ ] `docs/cadrage.md` : annexe B (phase 3 « Fait », tag, date), et la mention « Phase 3 terminée » dans la section 6. `CLAUDE.md` : phase en cours = phase 4.
- [ ] `uv version --bump major` : passe la version à `1.0.0`. Commit `build: passe à la version 1.0.0`, **dans cette branche**.
- [ ] Commit `docs: clôture la phase 3`, push, PR, merge, rangement.
- [ ] Sur `main` à jour : `uv sync`, `uv run pytest`, une dernière partie, puis le tag :

  ```bash
  git tag -a v1.0.0 -m "Phase 3 : vue 3D, le jeu est fini"
  git push origin v1.0.0
  ```

- [ ] Me demander une relecture, puis la fiche de la phase 4 (le cours de RL commence !).

---

## Comment vérifier que c'est bon

- [ ] `uv run pytest -v` : tout est vert, les tests des phases 1 et 2 **et** ceux de `test_geometry.py`, dont le grand test sur les 6 faces.
- [ ] Aucun test n'ouvre de fenêtre.
- [ ] `uv run ruff check .` → `All checks passed!`, et `uv run ruff format --check .` ne signale rien.
- [ ] Le test « pas de bibliothèque d'affichage dans la logique » couvre `rubiks.cube`, `rubiks.game` et `rubiks.geometry`, pour pygame **et** ursina.
- [ ] À l'écran :
  - la fenêtre 3D s'ouvre avec un cube résolu, blanc en haut, vert devant, sans « Résolu ! » ;
  - clic droit + glisser fait tourner la vue autour du cube, la molette zoome ;
  - chaque lettre fait tourner la bonne couche, dans le bon sens, Maj fait l'inverse ;
  - à la fin de chaque animation, **aucune couleur ne saute** ;
  - le cube 3D, `print(cube)` et la vue 2D montrent la même chose après le même mélange ;
  - Espace mélange, Retour arrière réinitialise, Échap ferme ;
  - après un mélange, je refais le cube en 3D et « Résolu ! » apparaît.
- [ ] `git log --oneline --graph --all` montre le commit de merge de l'exercice du conflit, et les tags `v0.1.0`, `v0.2.0` et `v1.0.0`.
- [ ] Sur GitHub : toutes les PR sont **Merged**, il ne reste que `main`, les trois tags sont visibles.
- [ ] Je sais expliquer avec mes mots :
  - pourquoi une case se décrit par un cubie **et** une normale ;
  - comment tourner un point d'un quart de tour autour d'un axe, et comment je sais que c'est le bon sens ;
  - ce que fait un parent en 3D, et pourquoi il sert à tourner une couche ;
  - pourquoi le `Cube` logique reste la seule source de vérité, et ce que fait « repeindre » ;
  - pourquoi `90 * time.dt`, et pas `1` ;
  - ce qu'est un conflit de merge, comment on le résout, et comment on l'annule.

---

## Pièges fréquents

| Symptôme | Cause | Solution |
|---|---|---|
| `update()` ou `input()` ne sont jamais appelées, sans erreur | fonctions écrites « en vrac » dans `view3d.py`, qui n'est pas le script principal | des méthodes d'une classe qui hérite de `Entity` (notion 2) |
| `Entity` plante ou rien ne s'affiche | `Entity` créée avant `Ursina()` | `app = Ursina()` en premier |
| la face verte est à l'arrière au lancement | `z` d'ursina s'éloigne de la caméra, notre `z` vient vers nous | convertir à un seul endroit (notion 8) |
| les couleurs « sautent » à la fin d'une animation | sens de l'animation faux, ou géométrie fausse | si le grand test est vert : c'est le signe de l'animation ; sinon, la géométrie |
| les cases sont invisibles ou clignotent | plaque exactement sur la surface du cube noir : les deux se battent pour s'afficher | décoller légèrement la plaque vers l'extérieur, le long de la normale |
| après quelques mouvements, les cubies dérivent ou se décalent | les cubies gardent leur rotation d'une animation à l'autre (erreurs d'arrondi qui s'accumulent) | « repeindre » : remettre chaque cubie à sa place, rotation à zéro (notion 6) |
| un cubie « saute » quand on l'accroche au pivot | `parent` change les coordonnées relatives | pivot au centre et non tourné au moment d'accrocher, ou `world_parent` (notion 3) |
| l'animation va plus vite sur un PC rapide | angle augmenté d'une valeur fixe par image | multiplier par `time.dt` (notion 5) |
| l'angle final vaut 90,7° et le cube se tord | le dernier pas d'animation dépasse 90 | borner l'angle à 90 avant de repeindre |
| taper vite casse le cube à l'écran | une nouvelle animation démarre pendant la précédente | ignorer, puis mettre en file d'attente (notion 5) |
| les couleurs sont toutes blanches ou délavées | couleurs 0–255 données à une fonction qui attend 0–1 | vérifier la fonction de couleur de ta version (notion 9) |
| `import rubiks.cube` charge ursina | import d'ursina en haut de `rubiks/__init__.py`, ou couleurs importées depuis une vue | imports dans les fonctions ; test de `test_render.py` |
| `ModuleNotFoundError: No module named 'ursina'` | `uv add ursina` oublié, ou `python` sans `uv run` | étape C ; toujours `uv run` |
| la fenêtre est noire ou plante au lancement sous Linux / machine virtuelle | pilote graphique 3D absent ou trop ancien | tester sur ta machine habituelle ; me montrer le message d'erreur complet |
| sur un clavier AZERTY, la touche Z fait W (et A fait Q) | ursina envoie la touche **physique** d'un clavier QWERTY pour les lettres | écouter les événements de Panda3D, qui suivent la disposition (`KeyListener` dans `view3d.py`) |
| Maj+F fait sauter la caméra au lieu de jouer F' | raccourci « focus » d'`EditorCamera` | vider `editor_camera.shortcuts` (`setup_camera` dans `view3d.py`) |
| maintenir le clic droit et taper une lettre déplace la caméra | `EditorCamera` se déplace avec W A S D Q E quand le clic droit est enfoncé | relâcher le clic droit avant de jouer |
| capture hors écran (`window_type="offscreen"`) : textes géants ou absents | l'interface n'est pas redimensionnée sans vraie fenêtre | régler `camera.ui_lens.set_film_size(...)` (seulement pour les captures automatiques) |
| `CONFLICT (content): Merge conflict in README.md` | même ligne modifiée dans deux branches | c'est l'exercice : notions Git |
| `git commit` refuse : « you have unmerged paths » | un fichier en conflit n'a pas été `git add` | `git status`, résoudre, `git add`, puis `git commit` |
| le README sur GitHub contient `<<<<<<<` | marqueurs oubliés lors de la résolution | supprimer les trois lignes de marqueurs, commit, push |
| `git branch -a` liste des branches mergées depuis longtemps | branches distantes jamais supprimées | Delete branch sur GitHub, puis `git fetch --prune` |

---

## Pour aller plus loin (optionnel)

- **Les demi-tours animés** : `R2` = une animation de 180°, ou deux de 90°. Lequel est le plus agréable ?
- **Annuler (Ctrl+Z)** avec animation : jouer l'inverse du dernier mouvement (`inverse_sequence` le sait déjà).
- **Tourner tout le cube** (`x`, `y`, `z` en notation Singmaster) : ici, c'est juste la caméra qui bouge… ou pas ? Réfléchis à ce que ça changerait pour `cube.state`.
- **Les tranches du milieu** (`M`, `E`, `S`) : 9 mouvements de plus. Que faudrait-il ajouter à `cube.py`, et pourquoi ce n'est **pas** une bonne idée pour le RL de la phase 4 ?
- **Faire tourner une face à la souris** : cliquer sur une case et glisser. Ursina sait dire quelle `Entity` est sous la souris (`mouse.hovered_entity`). Difficile, mais très satisfaisant.
- **Rejouer une solution** : une touche qui joue, animée, la suite inverse du mélange. C'est exactement ce qu'il faudra pour le bonus « voir l'agent RL résoudre le cube » (cadrage, section 6).
- **Une vue OpenGL à la main**, avec `pygame` + `PyOpenGL`, pour comprendre ce qu'ursina fait pour toi. Ta géométrie de `geometry.py` resservirait telle quelle : c'est la preuve qu'elle est bien séparée.
- **Une release GitHub** pour `v1.0.0`, avec une capture ou un GIF du cube qui tourne.
