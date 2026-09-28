# Fiche — Phase 1 : Le cube logique

> **Emplacement dans le repo :** `docs/fiches/phase-1-cube-logique.md`
> **Durée indicative :** 8 à 15 h, en plusieurs séances. Chaque étape se termine par un commit : tu peux t'arrêter après n'importe laquelle.
> **Documents liés :** `docs/cadrage.md` (section 4 « Notation du cube », section 6 « Phase 1 », section 7 « Méthode de travail avec Git ») et `docs/cours/uv.md` (section 7, `uv add`).

## Objectif

À la fin de cette phase, j'ai :

- une classe `Cube` dans `src/rubiks/cube.py`, **sans aucun affichage**, qui sait faire `move("R")`, `apply("R U R' U'")`, `scramble(n)`, `is_solved()` et `copy()` ;
- une batterie de tests `pytest` qui prouvent que les 18 mouvements sont justes ;
- ma première branche, ma première Pull Request, mon premier merge et mon premier tag : `v0.1.0`.

C'est la phase la plus importante du projet : l'affichage 2D, la vue 3D **et** l'agent RL utiliseront tous ce cube. Un mouvement faux ici fausserait tout le reste, sans message d'erreur (cadrage, section 10). D'où la place centrale des tests.

---

## Notions Python à connaître

Les mini-exemples suivent la convention du projet : **noms en anglais, commentaires en français**. Pour les essayer, ouvre une console Python avec `uv run python` (on en sort avec `exit()`). Les exemples numpy ne marcheront qu'après l'étape C, quand numpy sera ajouté au projet.

### 1. Classes et méthodes

Une **classe** est un *moule*. Avec ce moule, on fabrique des **objets** (on dit aussi des *instances*). Chaque objet a :

- ses propres données, les **attributs** ;
- des actions qu'il sait faire, les **méthodes** (des fonctions rangées dans la classe).

Deux mots-clés à comprendre :

- **`__init__`** est la méthode appelée automatiquement quand on fabrique un objet. Elle prépare ses attributs.
- **`self`** veut dire « l'objet lui-même ». Dans une méthode, `self.total` désigne l'attribut `total` de *cet* objet-là, pas d'un autre.

Mini-exemple (hors projet) : une tirelire.

```python
class PiggyBank:
    """Une tirelire qui compte l'argent qu'elle contient."""

    def __init__(self) -> None:
        self.total = 0  # attribut : chaque tirelire a le sien

    def add(self, amount: int) -> None:
        """Ajoute de l'argent. Modifie la tirelire, ne renvoie rien."""
        self.total += amount

    def is_empty(self) -> bool:
        """Répond à une question, sans rien modifier."""
        return self.total == 0


mine = PiggyBank()  # on fabrique un objet avec le moule
yours = PiggyBank()  # un deuxième objet, indépendant du premier
mine.add(5)
print(mine.total)  # 5
print(yours.total)  # 0
print(yours.is_empty())  # True
```

Il y a deux familles de méthodes :

| Famille | Exemple tirelire | Dans le cube |
|---|---|---|
| celles qui **modifient** l'objet (et ne renvoient rien) | `add` | `move`, `apply`, `scramble` |
| celles qui **répondent** à une question (sans rien modifier) | `is_empty` | `is_solved` |

Python fait la même distinction avec les listes : `my_list.sort()` trie la liste elle-même, alors que `sorted(my_list)` renvoie une nouvelle liste triée.

**Piège : `=` ne copie pas un objet.** Il donne un deuxième nom au *même* objet.

```python
a = PiggyBank()
b = a  # pas une copie : deux noms pour LA MÊME tirelire
b.add(10)
print(a.total)  # 10 !
```

C'est exactement pour ça que le cadrage demande une méthode `copy()` : fabriquer un **nouveau** cube, identique et indépendant.

**Constante de module.** Une valeur qui ne change jamais s'écrit en MAJUSCULES, en haut du fichier : `SUITS = ["H", "S", "D", "C"]`. Pour le cube, ce sera par exemple la liste des 18 mouvements, dans un ordre fixé une fois pour toutes. Elle servira au mélange (tirer un mouvement au hasard) et, en phase 4, l'agent RL désignera ses actions par leur numéro dans cette liste.

### 2. Découper une chaîne, dictionnaires et erreurs

Pour lire `"R U R' U'"`, il faut découper une chaîne et reconnaître chaque morceau. Mini-exemple (hors projet) : des cartes à jouer notées `"7H"` (7 de cœur), `"QS"` (dame de pique), `"10D"`.

```python
SUITS = {"H": "cœur", "S": "pique", "D": "carreau", "C": "trèfle"}


def describe(card: str) -> str:
    """Traduit '7H' en '7 de cœur'."""
    rank, suit = card[:-1], card[-1]  # tout sauf le dernier caractère, puis le dernier
    if suit not in SUITS:
        raise ValueError(f"couleur inconnue : {suit!r}")
    return f"{rank} de {SUITS[suit]}"


hand = "7H  QS 10D"
print(hand.split())  # ['7H', 'QS', '10D'] : les espaces en trop disparaissent
for card in hand.split():
    print(describe(card))
```

- `split()` sans argument coupe sur les espaces, même s'il y en a plusieurs.
- `card[-1]` est le dernier caractère, `card[:-1]` tout le reste, `card[1:]` tout sauf le premier.
- Un **dictionnaire** (`{clé: valeur}`) associe des noms à des valeurs ; `in` vérifie qu'une clé existe.
- `raise ValueError(...)` **arrête** le programme avec un message clair. C'est mieux que de continuer avec une donnée absurde : si quelqu'un demande le mouvement `"X"`, le cube doit protester, pas ne rien faire en silence. `{suit!r}` affiche la valeur entre guillemets, pratique pour repérer un espace ou un caractère bizarre.

### 3. numpy : les tableaux

**numpy** apporte un type de données, le **tableau** (`ndarray`) : une grille de nombres, à 1, 2, 3 dimensions ou plus. C'est beaucoup plus rapide qu'une liste de listes, et on peut manipuler des lignes ou des colonnes entières en une seule instruction. Par convention, on l'importe sous le nom `np`.

#### 3.1 Créer un tableau

```python
import numpy as np

grid = np.zeros((3, 3), dtype=int)  # une grille 3x3 remplie de 0 (des entiers)
print(grid.shape)  # (3, 3) : 3 lignes, 3 colonnes

numbers = np.arange(9).reshape(3, 3)  # les nombres 0 à 8, rangés en 3 lignes
print(numbers)
# [[0 1 2]
#  [3 4 5]
#  [6 7 8]]

boards = np.full((2, 3, 3), 7)  # 2 grilles de 3x3, remplies de 7
print(boards.shape)  # (2, 3, 3)
print(boards.size)  # 18 cases en tout
```

- **`shape`** (la forme) donne la taille de chaque dimension. Un tableau de forme `(2, 3, 3)`, c'est 2 grilles de 3 lignes et 3 colonnes.
- **`dtype`** (le type) dit ce que contiennent les cases : ici des entiers (`int`).

#### 3.2 Lire une case, une ligne, une colonne (indexation et slicing)

On compte **à partir de 0**. Entre crochets, on donne d'abord la ligne, puis la colonne. Le `:` veut dire « tout » : c'est le **slicing** (découpage en tranches).

```python
import numpy as np

numbers = np.arange(9).reshape(3, 3)
print(numbers[1, 2])  # 5 : ligne 1, colonne 2
print(numbers[0, :])  # [0 1 2] : toute la ligne 0
print(numbers[:, 2])  # [2 5 8] : toute la colonne 2
print(numbers[-1, :])  # [6 7 8] : -1 = la dernière ligne
print(numbers[:, 2][::-1])  # [8 5 2] : la colonne 2, à l'envers

boards = np.arange(18).reshape(2, 3, 3)
print(boards[1])  # la grille numéro 1 entière (un tableau 3x3)
print(boards[1, 0, :])  # [ 9 10 11] : grille 1, ligne 0
```

`[::-1]` veut dire « du début à la fin, par pas de -1 » : on lit à l'envers. Garde-le en tête, il servira.

#### 3.3 Écrire dans une tranche

On peut remplacer une ligne ou une colonne entière d'un coup, à condition que les tailles correspondent (3 cases dans 3 cases).

```python
import numpy as np

left = np.zeros((3, 3), dtype=int)
right = np.arange(9).reshape(3, 3)
left[:, 0] = right[0, :]  # la colonne 0 de left reçoit la ligne 0 de right
left[2, :] = right[:, 2][::-1]  # la ligne 2 de left reçoit la colonne 2, à l'envers
print(left)
# [[0 0 0]
#  [1 0 0]
#  [8 5 2]]
```

Une ligne peut recevoir une colonne, et inversement : numpy ne regarde que le nombre de cases.

#### 3.4 Tourner une grille : `np.rot90`

`np.rot90(grille, k)` fait tourner une grille de `k` quarts de tour.

```python
import numpy as np

grid = np.arange(1, 10).reshape(3, 3)
print(grid)
# [[1 2 3]
#  [4 5 6]
#  [7 8 9]]
print(np.rot90(grid))  # k=1 par défaut : quart de tour dans le sens ANTI-horaire
# [[3 6 9]
#  [2 5 8]
#  [1 4 7]]
print(np.rot90(grid, k=-1))  # k=-1 : quart de tour dans le sens horaire
# [[7 4 1]
#  [8 5 2]
#  [9 6 3]]
print(np.rot90(grid, k=2))  # demi-tour
# [[9 8 7]
#  [6 5 4]
#  [3 2 1]]
```

Deux pièges à retenir :

- **Par défaut, `np.rot90` tourne dans le sens anti-horaire.** Vérifie toujours le sens sur un petit exemple comme celui-ci, en suivant où va le `1`.
- Sur un tableau à 3 dimensions, `np.rot90` fait tourner les **deux premières** dimensions. Sur un tableau de forme `(2, 3, 3)`, il mélangerait donc les grilles entre elles (essaie : la forme devient `(3, 2, 3)`). Pour tourner une seule grille, donne-lui une seule grille : `np.rot90(boards[1], k=-1)`.

#### 3.5 Copie ou vue ? (la notion la plus piégeuse de la phase)

Quand on découpe une tranche (`grid[0, :]`), numpy ne fabrique **pas** de nouveau tableau. Il renvoie une **vue** : une fenêtre sur les *mêmes* cases. Si le tableau d'origine change, ce qu'on voit par la fenêtre change aussi.

```python
import numpy as np

grid = np.arange(9).reshape(3, 3)
top = grid[0, :]  # une VUE sur la ligne 0, pas une copie
grid[0, :] = [0, 0, 0]
print(top)  # [0 0 0] : top a changé en même temps que grid !

grid = np.arange(9).reshape(3, 3)
top = grid[0, :].copy()  # une vraie COPIE, indépendante
grid[0, :] = [0, 0, 0]
print(top)  # [0 1 2] : intacte
```

Voici le bug classique qu'il provoque : on veut échanger deux lignes.

```python
import numpy as np

grid = np.arange(9).reshape(3, 3)
saved = grid[0, :]  # on croit « mettre de côté » la ligne 0… mais c'est une vue
grid[0, :] = grid[2, :]  # la ligne 0 reçoit la ligne 2
grid[2, :] = saved  # la ligne 2 devrait recevoir l'ancienne ligne 0…
print(grid)
# [[6 7 8]
#  [3 4 5]
#  [6 7 8]]   ← raté : l'ancienne ligne 0 a été écrasée avant d'être recopiée
```

Avec `saved = grid[0, :].copy()`, on obtient bien l'échange. Pendant un mouvement du cube, 4 bandes de 3 cases tournent en cercle : c'est ce même problème, en plus grand.

À retenir :

| Opération | Résultat |
|---|---|
| `b = a` | **même** tableau, deux noms |
| `a[0, :]`, `a[:, 2]`, `a[1]` (slicing) | une **vue** |
| `np.rot90(a)` | une **vue** aussi |
| `a.copy()` | une **copie** indépendante |

En cas de doute, `np.shares_memory(a, b)` répond `True` si les deux partagent des cases.

#### 3.6 Comparer et compter

Une comparaison sur un tableau se fait **case par case** et donne un tableau de `True`/`False`.

```python
import numpy as np

votes = np.array([2, 0, 2, 1, 2, 0])
print(votes == 2)  # [ True False  True False  True False]
print(np.count_nonzero(votes == 2))  # 3 : combien de True
print(np.all(votes >= 0))  # True : toutes les cases vérifient la condition
print(np.bincount(votes))  # [2 1 3] : deux 0, un 1, trois 2
values, counts = np.unique(votes, return_counts=True)
print(values, counts)  # [0 1 2] [2 1 3]

a = np.array([1, 2, 3])
b = np.array([1, 2, 3])
print(np.array_equal(a, b))  # True : même forme et mêmes valeurs
```

**Attention :** `assert a == b` sur deux tableaux provoque l'erreur *« The truth value of an array with more than one element is ambiguous »*. Python ne sait pas si tu veux « toutes les cases égales » ou « au moins une ». Dans les tests, utilise `np.array_equal(a, b)`.

### 4. Le module `random`

`random` fait partie de la bibliothèque standard : rien à installer.

```python
import random

suits = ["pique", "cœur", "carreau", "trèfle"]
print(random.choice(suits))  # une couleur au hasard

random.seed(42)  # on fixe la « graine »…
first = [random.randint(1, 6) for _ in range(5)]
random.seed(42)  # … et on la refixe à la même valeur
second = [random.randint(1, 6) for _ in range(5)]
print(first == second)  # True : même graine, même suite de tirages

rng = random.Random(7)  # un générateur à part, avec sa propre graine
print(rng.choice(suits))  # toujours le même résultat à chaque exécution
```

- `random.choice(liste)` tire un élément au hasard.
- L'ordinateur ne tire pas vraiment au hasard : il calcule une suite de nombres qui *ont l'air* aléatoires, à partir d'un point de départ, la **graine** (*seed*). Même graine = même suite.
- **Pourquoi c'est utile :** un test doit donner le même résultat à chaque fois. Un test qui échoue « une fois sur dix » est un cauchemar à déboguer. Avec une graine fixée, le mélange est aléatoire *et* reproductible.
- `random.Random(graine)` crée un générateur indépendant. C'est plus propre que `random.seed`, qui change le hasard de tout le programme.

### 5. pytest, niveau 2

En phase 0, tu as écrit un test. Ici, tu vas en écrire une vingtaine. Quelques outils de plus.

**Des noms qui racontent.** Un nom de test doit dire ce qui est vérifié : `test_quarter_turn_four_times_is_identity` vaut mieux que `test_1`. Quand il échoue, le nom seul te dit ce qui est cassé.

**Un test = une idée.** Chaque test part de zéro (il crée son propre cube) : il ne doit jamais dépendre d'un autre test.

**Le même test sur plusieurs valeurs : `@pytest.mark.parametrize`.** Au lieu de copier-coller un test six fois (une fois par face), on l'écrit une fois et on donne la liste des valeurs.

```python
import pytest


@pytest.mark.parametrize("word", ["kayak", "radar", "level"])
def test_is_palindrome(word):
    assert word == word[::-1]


@pytest.mark.parametrize(("word", "expected"), [("kayak", True), ("cube", False)])
def test_palindrome_detection(word, expected):
    assert (word == word[::-1]) == expected
```

pytest compte alors **un test par valeur** : `test_is_palindrome[kayak]`, `test_is_palindrome[radar]`… Si une seule valeur échoue, tu sais laquelle.

**Vérifier qu'une erreur est bien levée : `pytest.raises`.**

```python
import pytest


def test_int_rejects_letters():
    with pytest.raises(ValueError):
        int("abc")  # le test passe SI cette ligne lève ValueError
```

**Rouge, puis vert.** Dans cette phase, on écrit souvent le test **avant** le code. Le test échoue d'abord (rouge), puis on code jusqu'à ce qu'il passe (vert). Ça garantit que le test sait vraiment détecter une erreur : un test qui n'a jamais été rouge ne prouve pas grand-chose.

**`failed` ou `error` ?** pytest distingue deux sortes de rouge :

- **`FAILED`** : le test a tourné, et un `assert` était faux ;
- **`ERROR`** : le test n'a même pas pu démarrer (par exemple, `from rubiks.cube import Cube` échoue parce que `Cube` n'existe pas encore).

**Options utiles :**

| Commande | Effet |
|---|---|
| `uv run pytest -v` | affiche chaque test, avec son nom et ses paramètres |
| `uv run pytest -x` | s'arrête au premier échec |
| `uv run pytest -k sexy` | ne lance que les tests dont le nom contient `sexy` |
| `uv run pytest --lf` | ne relance que les tests qui ont échoué la dernière fois (*last failed*) |

**Astuce : le cube numéroté.** Sur un cube résolu, chaque face est d'une seule couleur. Si ton code tourne une face dans le mauvais sens, ça ne se voit pas : une face unie reste unie. Pour tester les mouvements finement, remplace les couleurs par des **numéros tous différents**, de 0 à 53 (`np.arange(54).reshape(...)`). Chaque case devient identifiable, et le moindre déplacement se voit. C'est possible parce que l'état du cube sera un tableau d'entiers (voir plus bas) : un test peut y mettre ce qu'il veut.

---

## Représenter le cube (à décider avant de coder)

C'est **la** décision de la phase. Prends le temps de la lire, avec un vrai cube dans les mains si tu en as un.

### 1. La notation Singmaster (rappel du cadrage)

- 6 faces : **U** (haut), **D** (bas), **L** (gauche), **R** (droite), **F** (devant), **B** (derrière).
- `R` = quart de tour **horaire** de la face R, `R'` = anti-horaire, `R2` = demi-tour.
- 6 faces × 3 variantes = **18 mouvements**.

**« Horaire », mais vu d'où ?** Toujours **en regardant la face en face**, depuis l'extérieur du cube. Pour `R`, imagine que tu regardes le cube par la droite. Pour `L`, par la gauche. Pour `B`, par derrière. Vu de devant, `R` fait donc monter la colonne de droite, tandis que `L` fait descendre la colonne de gauche. C'est la première source d'erreurs : vérifie-le sur un vrai cube.

### 2. Les couleurs

On utilise le jeu de couleurs le plus répandu : **blanc** en haut, **vert** devant. Alors rouge est à droite, orange à gauche, bleu derrière et jaune en bas.

Dans le code, on ne stocke pas des mots (`"blanc"`) mais des **entiers de 0 à 5**. Pourquoi ?

- numpy compare et compte des entiers très vite ;
- l'agent RL ne travaillera qu'avec des nombres (phase 4) ;
- l'astuce du cube numéroté (ci-dessus) devient possible ;
- les noms de couleurs ne servent qu'à l'affichage (phase 2), qui fera la traduction.

Idée simple : la couleur `i` est la couleur de la face numéro `i` quand le cube est résolu. Une couleur, c'est « la face où cette case doit revenir ».

### 3. Trois façons de ranger les 54 cases

| | A. 6 grilles de 3×3 | B. 54 cases à plat + permutations | C. Les petits cubes (« cubies ») |
|---|---|---|---|
| **Idée** | un tableau numpy de forme `(6, 3, 3)` : une grille 3×3 par face | un tableau de 54 nombres ; chaque mouvement est une **permutation** : une liste de 54 numéros qui dit, pour chaque case, d'où vient sa nouvelle couleur | on ne stocke plus des couleurs, mais la position et l'orientation des 20 petits cubes qui bougent (8 coins, 12 arêtes) |
| **Facile à comprendre** | oui : on « voit » les faces | moyen | difficile |
| **Facile à coder** | moyen : `np.rot90` + des tranches | difficile : écrire à la main 18 listes de 54 numéros, sans une seule erreur | difficile |
| **Vitesse** | bonne | excellente | excellente |
| **Lien avec l'affichage 2D (phase 2)** | direct : le patron déplié, c'est exactement ça | il faut reconvertir | il faut reconvertir |
| **Pour le RL (phase 4)** | bonne | très bonne | très bonne, et compacte |
| **Notions numpy travaillées** | indexation, slicing, `rot90`, vues et copies | indexation avancée | peu |

**Ma recommandation : l'option A.** Elle correspond au cadrage (`np.rot90`, indexation), on voit ce qu'on fait (donc on débogue facilement), la phase 2 l'affichera directement, et elle fait travailler toutes les notions numpy de cette fiche. L'option B viendra peut-être plus tard, pour la vitesse, et tu n'auras même pas à écrire les permutations à la main : l'option A saura les fabriquer (voir « Pour aller plus loin »). L'option C est une décision de la phase 4 (cadrage, section 9).

Le choix final t'appartient. Si tu hésites, pose-moi la question : on en discute avant que tu écrives la moindre ligne.

### 4. L'ordre des faces : U R F D L B

Avec l'option A, chaque face a un numéro (sa position dans le tableau). Je propose l'ordre **U R F D L B** :

| Numéro | Face | Couleur |
|---|---|---|
| 0 | U (haut) | blanc |
| 1 | R (droite) | rouge |
| 2 | F (devant) | vert |
| 3 | D (bas) | jaune |
| 4 | L (gauche) | orange |
| 5 | B (derrière) | bleu |

Pourquoi cet ordre plutôt qu'un autre ? C'est celui qu'utilise la bibliothèque `kociemba`, notre solveur de référence de la phase 7. Le jour où il faudra lui passer un cube, la conversion sera immédiate.

### 5. L'orientation de chaque face (le point le plus délicat)

Une face est une grille 3×3 : `face[ligne, colonne]`. Mais où est la « ligne 0 » de la face U ? Et la « colonne 0 » de la face B ? Il faut une **convention**, la même partout. Voici la plus courante, celle du **patron déplié** :

```
                ┌──────────┐
                │ U0 U1 U2 │
                │ U3 U4 U5 │
                │ U6 U7 U8 │
     ┌──────────┼──────────┼──────────┬──────────┐
     │ L0 L1 L2 │ F0 F1 F2 │ R0 R1 R2 │ B0 B1 B2 │
     │ L3 L4 L5 │ F3 F4 F5 │ R3 R4 R5 │ B3 B4 B5 │
     │ L6 L7 L8 │ F6 F7 F8 │ R6 R7 R8 │ B6 B7 B8 │
     └──────────┼──────────┼──────────┴──────────┘
                │ D0 D1 D2 │
                │ D3 D4 D5 │
                │ D6 D7 D8 │
                └──────────┘
```

- Dans chaque face, les cases sont numérotées de 0 à 8, ligne par ligne : la case `k` est en `[k // 3, k % 3]`. Le centre est toujours la case 4, en `[1, 1]`.
- **L, F, R, B** sont vues **de face**, depuis l'extérieur, avec U en haut.
- **U** est vue **de dessus**, avec F en bas (la ligne `U6 U7 U8` touche F).
- **D** est vue **de dessous**, avec F en haut (la ligne `D0 D1 D2` touche F).

Ce patron dit quelles cases se touchent **quand elles sont côte à côte sur le dessin** : par exemple, la ligne `U6 U7 U8` touche la ligne `F0 F1 F2`, dans le même ordre. Mais sur le vrai cube, d'autres bords se touchent aussi : U touche B, U touche R, D touche L… Ces bords-là ne sont pas côte à côte sur le patron, et **l'ordre des cases s'y inverse parfois**. C'est là que se cachent presque tous les bugs.

**Le meilleur outil ici n'est pas l'ordinateur.** Recopie ce patron sur une feuille (grand), découpe-le, plie-le en cube, et regarde quelles cases se touchent. Ou colle des petits numéros sur un vrai cube.

### 6. Ce que fait un quart de tour, en mots

Un quart de tour de la face X fait **deux** choses :

1. **La face X tourne sur elle-même** (une grille 3×3 qui tourne d'un quart de tour, dans le bon sens). Son centre ne bouge pas.
2. **Quatre bandes de 3 cases**, sur les 4 faces voisines, **tournent en cercle** : chaque bande part sur la face voisine suivante. Pour chaque bande, il faut savoir : quelle ligne ou quelle colonne, de quelle face, dans quel ordre.

Au total, un quart de tour déplace **20 cases** : les 8 cases de la face autour du centre, plus 4 bandes de 3 cases. Les 6 centres ne bougent jamais. Les deux faces opposées à X ne sont pas touchées du tout.

Du plus facile au plus difficile :

- **U et D** : les 4 bandes sont des **lignes** (la ligne du haut de F, R, B et L pour U). Aucun retournement. Commence par là.
- **R et L** : les bandes sont des **colonnes**, et l'une d'elles passe par la face B, vue « de dos ».
- **F et B** : les bandes passent de **lignes** (sur U et D) à **colonnes** (sur L et R). Il faut vérifier l'ordre à chaque passage.

### 7. L'interface du cube (ce que le reste du projet verra)

Le cadrage fixe les noms. Voici ce que chaque méthode doit faire :

| Méthode | Ce qu'elle fait | Renvoie |
|---|---|---|
| `Cube()` | fabrique un cube résolu | un `Cube` |
| `move("R")` | applique **un** mouvement parmi les 18 et modifie le cube | rien (`None`) |
| `apply("R U R' U'")` | applique une suite de mouvements séparés par des espaces | rien |
| `scramble(n)` | applique `n` mouvements tirés au hasard | la liste des mouvements joués |
| `is_solved()` | chaque face est-elle d'une seule couleur ? | `True` ou `False` |
| `copy()` | fabrique un nouveau cube identique **et indépendant** | un `Cube` |

Plus un attribut `state` : le tableau numpy des 54 cases. Et une constante de module : la liste des 18 noms de mouvements.

### 8. Mes décisions (à noter dans le code)

À la fin de l'étape D, écris tes choix dans la **docstring du module**, tout en haut de `src/rubiks/cube.py` (entre triples guillemets, en français). Toute personne qui ouvre le fichier (toi dans trois mois, moi, Claude Code) saura comment lire l'état. Par exemple :

- représentation : tableau numpy d'entiers, forme `(6, 3, 3)` ;
- ordre des faces et couleurs : 0 U blanc, 1 R rouge, 2 F vert, 3 D jaune, 4 L orange, 5 B bleu ;
- orientation : le patron déplié (U vue de dessus avec F en bas, D vue de dessous avec F en haut, L F R B vues de face avec U en haut) ;
- les mouvements modifient le cube ; `copy()` fabrique un cube indépendant.

---

## Notions Git de l'étape

### Qu'est-ce qu'une branche ?

Jusqu'ici, tous tes commits se suivaient sur une seule ligne : `main`. Une **branche** est une **ligne de travail parallèle**. Tu peux y faire des essais, des commits à moitié finis, des tests encore rouges… sans jamais toucher à `main`, qui reste stable.

```
                               git switch -c feature/cube-model
                                             │
main                  ●────●────●  ◄─────────┘    main ne bouge plus
                                 \
feature/cube-model                ●────●────●────●    mes commits de la phase 1
```

Quand la fonctionnalité est prête et relue, on **fusionne** (*merge*) la branche dans `main` :

```
main                  ●────●────●────────────────────────●   ← commit de merge (la Pull Request)
                                 \                      /       + tag v0.1.0
feature/cube-model                ●────●────●────●────●
```

Techniquement, une branche est très simple : c'est une **étiquette** posée sur un commit, qui avance toute seule à chaque nouveau commit. Et **`HEAD`** est un repère « vous êtes ici » : il indique sur quelle branche tu travailles. Créer une branche ne copie aucun fichier : c'est instantané.

**Dans Git Bash, la branche courante s'affiche entre parenthèses dans l'invite de commande :**

```
MINGW64 /c/rubiks-rl (feature/cube-model)
$
```

Prends l'habitude d'y jeter un œil avant chaque commit. La première ligne de `git status` le dit aussi : *On branch feature/cube-model*.

### Le cycle complet d'une branche

```
1. git switch -c feature/cube-model     créer la branche et s'y placer
2. commits, commits, commits…           travailler
3. git push -u origin feature/cube-model   envoyer la branche sur GitHub
4. Pull Request sur GitHub              demander la relecture
5. Merge sur GitHub                     intégrer à main
6. git switch main + git pull           récupérer main à jour sur mon ordinateur
7. git branch -d feature/cube-model     ranger : supprimer la branche
8. git tag + git push origin v0.1.0     marquer la fin de la phase
```

C'est le cycle du cadrage (section 7). Tu le referas à chaque fonctionnalité, avec des branches plus petites.

### Les commandes de la phase

| Commande | À quoi ça sert |
|---|---|
| `git branch` | lister les branches locales (l'étoile `*` = la branche courante) |
| `git branch -a` | lister aussi les branches connues sur GitHub (`remotes/origin/…`) |
| `git switch -c feature/cube-model` | créer une branche **et** s'y placer (`-c` = *create*) |
| `git switch main` | changer de branche |
| `git push -u origin feature/cube-model` | envoyer la branche sur GitHub la première fois. `-u` retient le lien entre ta branche et celle de GitHub : ensuite, `git push` tout court suffit |
| `git log --oneline --graph --all` | l'historique de **toutes** les branches, sous forme de graphe |
| `git pull` | récupérer les nouveaux commits de GitHub (par exemple le commit de merge) |
| `git branch -d feature/cube-model` | supprimer une branche locale **déjà mergée** (Git refuse sinon : c'est une sécurité) |
| `git fetch --prune` | faire oublier à ton ordinateur les branches supprimées sur GitHub |
| `git tag -a v0.1.0 -m "…"` | poser un tag (une étiquette permanente) sur le commit courant |
| `git push origin v0.1.0` | envoyer le tag sur GitHub (`git push` seul n'envoie **pas** les tags) |
| `git tag` / `git show v0.1.0` | lister les tags / voir le détail d'un tag |

Sur Internet, tu verras souvent `git checkout` : c'est l'ancienne commande, qui fait à la fois `switch` et d'autres choses. `git switch` est plus clair ; on utilise celle-là.

### La Pull Request (PR)

Une **Pull Request** est une **demande de merge** faite sur GitHub : « voici ma branche, je propose de l'intégrer à `main` ». GitHub affiche alors, sur une seule page :

- la liste des commits de la branche ;
- l'onglet **Files changed** : toutes les modifications, ligne par ligne ;
- un fil de discussion, et la possibilité de commenter une ligne précise.

Même seul, c'est utile : c'est un moment pour **relire** avant d'intégrer, et c'est là que je peux relire ton code. Si la relecture demande des corrections, tu fais de nouveaux commits sur la même branche et tu fais `git push` : **la PR se met à jour toute seule**.

### Le merge

Au moment de merger, GitHub propose trois boutons :

| Bouton | Ce qu'il fait |
|---|---|
| **Create a merge commit** | garde tous tes commits et ajoute un commit de merge. Le graphe montre la branche et son retour dans `main` |
| Squash and merge | écrase tous les commits de la branche en un seul |
| Rebase and merge | recopie les commits un par un au bout de `main`, sans commit de merge |

**Pour cette phase : « Create a merge commit ».** Tu verras ta branche dans `git log --graph`, et `git branch -d` fonctionnera sans surprise. Les deux autres viendront plus tard, quand tu sauras ce qu'ils changent.

### Le tag

Un **tag** est une étiquette **permanente** sur un commit. Une branche avance à chaque commit ; un tag, jamais. Il sert à marquer une étape : « ici, la phase 1 est finie et tout marche ».

Le nom suit le **versionnage sémantique** (*Semantic Versioning*) : `vMAJEUR.MINEUR.CORRECTIF`.

- `v0.1.0` : le `0` en premier veut dire « en développement, rien n'est encore figé » ;
- on augmente le **mineur** quand on ajoute une fonctionnalité (`v0.2.0` à la fin de la phase 2) ;
- on augmente le **correctif** pour une correction de bug (`v0.1.1`) ;
- `v1.0.0` viendra à la fin de la phase 3 : le jeu sera fini.

On utilise un **tag annoté** (`git tag -a`) : il enregistre qui l'a posé, quand, et avec quel message. Joli hasard : la version de ton `pyproject.toml` est déjà `0.1.0`.

### Fin de l'exception de la phase 0

À partir de maintenant, **plus aucun commit directement sur `main`**. Tout passe par une branche et une Pull Request, même une faute de frappe dans la doc (avec une petite branche `docs/…` ou `fix/…`).

---

## Tâches (dans l'ordre)

**Bloqué ?** Demande-moi un indice. Je réponds par niveaux : (1) une question ou une piste, (2) l'explication de la notion, (3) un petit exemple hors projet, (4) la solution, seulement si tu la demandes.

### Étape A — Partir d'un `main` propre et créer la branche

- [ ] Dans Git Bash :

  ```bash
  cd /c/rubiks-rl
  git switch main
  git pull
  git status
  ```

  `git status` doit dire *nothing to commit, working tree clean*. Sinon, termine ou range d'abord ce qui traîne.
- [ ] Créer la branche :

  ```bash
  git switch -c feature/cube-model
  git branch
  git log --oneline --graph --all
  ```

  **Devine avant de regarder :** où est l'étoile dans `git branch` ? Dans le graphe, sur quel commit sont les étiquettes `main` et `feature/cube-model` ? Pourquoi ?
- [ ] Regarde l'invite de Git Bash : qu'est-ce qui a changé ?

### Étape B — Ajouter cette fiche et publier la branche

- [ ] Placer cette fiche dans `docs/fiches/phase-1-cube-logique.md`.
- [ ] Commit : `docs: ajoute la fiche de la phase 1`.
- [ ] Premier envoi de la branche sur GitHub :

  ```bash
  git push -u origin feature/cube-model
  ```

  **Question :** que se passe-t-il si tu tapes seulement `git push` cette première fois ? (Essaie : Git te propose lui-même la bonne commande.)
- [ ] Sur GitHub, ouvre le menu des branches (bouton **main** en haut à gauche de la liste des fichiers) : tu dois voir les deux branches. GitHub affiche peut-être un bandeau **Compare & pull request** : ignore-le pour l'instant, la PR viendra à l'étape M.

### Étape C — Ajouter numpy

- [ ] Ajouter la dépendance (dépendance principale : le cube en a besoin pour tourner, ce n'est pas un outil de développement) :

  ```bash
  uv add numpy
  git status
  git diff pyproject.toml
  ```

  **Devine :** quels fichiers apparaissent dans `git status` ? Pourquoi `.venv/` n'y est pas ?
- [ ] Vérifier : `uv run python -c "import numpy; print(numpy.__version__)"`.
- [ ] Commit, avec les **deux** fichiers ensemble : `build: ajoute numpy aux dépendances`.

### Étape D — Choisir la représentation, sur papier

Pas une ligne de code dans cette étape.

- [ ] Relire la section « Représenter le cube » et choisir une option (je recommande A).
- [ ] Recopier le patron déplié en grand, avec les numéros de cases, puis le découper et le plier en cube (ou numéroter un vrai cube).
- [ ] Répondre sur papier :
  1. Tiens le cube blanc en haut, vert devant. Fais `U`. La ligne du haut de F part vers quelle face ?
  2. Pendant un `R`, la colonne de droite de F monte vers U. Arrive-t-elle dans la colonne de droite de U ? Dans le même ordre (F2 va sur U2 ou sur U8) ?
  3. Toujours pendant `R`, la colonne qui passe de U à B : dans quelle colonne de B arrive-t-elle ? L'ordre s'inverse-t-il ?
  4. Pendant un `F`, la ligne du bas de U (`U6 U7 U8`) part vers R. Devient-elle une ligne ou une colonne de R ? Dans quel ordre ?
- [ ] Créer `src/rubiks/cube.py` avec **seulement** la docstring du module, qui décrit tes décisions (section « Mes décisions »).
- [ ] Commit : `docs: décrit la représentation du cube`.

Si tu n'es pas sûr d'une réponse, montre-moi ton papier (une photo suffit) : c'est bien moins coûteux de corriger maintenant qu'après avoir codé.

### Étape E — Écrire les tests clés (ils seront rouges)

On écrit les tests du cadrage **avant** le cube. Ils décrivent ce que le cube *doit* faire.

- [ ] Créer `tests/test_cube.py`, qui importe `Cube` avec `from rubiks.cube import Cube`.
- [ ] Y écrire **toi-même** ces tests :

  | Test | Ce qu'il vérifie |
  |---|---|
  | `test_new_cube_is_solved` | un cube neuf est résolu |
  | `test_each_color_appears_nine_times` | il y a exactement 9 cases de chaque couleur (6 couleurs) |
  | `test_quarter_turn_four_times_is_identity` | paramétré sur les 6 faces : 4 fois le même quart de tour ramène exactement à l'état de départ. Pars du **cube numéroté** : sur un cube résolu, une face qui tourne dans le mauvais sens ne se verrait pas |
  | `test_move_then_inverse_is_identity` | paramétré sur les 6 faces : `X` puis `X'` ramène à l'état de départ (et `X'` puis `X`, et `X2` puis `X2`) |
  | `test_sexy_move_six_times_is_identity` | `R U R' U'` répété 6 fois ramène à l'état de départ |

  Pour comparer deux états, pense à `np.array_equal` (notion 3.6). Pour garder l'état de départ de côté, pense à la différence entre copie et vue (notion 3.5).
- [ ] Lancer `uv run pytest -v`. **Devine :** `FAILED` ou `ERROR` ? Pourquoi ?
- [ ] Commit : `test: ajoute les tests clés du cube`.

Des tests rouges sur une branche, c'est normal et même voulu : c'est `main` qui doit toujours rester vert.

### Étape F — Le cube résolu

- [ ] Dans `cube.py`, écrire la classe `Cube` avec :
  - `__init__` : crée l'attribut `state`, le tableau des 54 cases d'un cube résolu. Indice : la face numéro `i` est remplie avec la valeur `i`. Il existe plusieurs façons de le faire ; une boucle `for` est parfaitement acceptable ;
  - `is_solved()` : chaque face est-elle d'une seule couleur ? Indice : compare toute la face à une de ses cases (notion 3.6) ;
  - `copy()` : fabrique un nouveau `Cube` dont le tableau est une **copie** de celui-ci.
- [ ] Ajouter le test `test_copy_is_independent` : modifier la copie (par exemple en changeant une case de son `state`) ne doit pas modifier l'original.
- [ ] `uv run pytest -v` : quels tests passent maintenant ? Pourquoi les autres échouent-ils encore ?
- [ ] (Recommandé) Ajouter une méthode `__str__` qui renvoie le patron en texte, avec une lettre par couleur (`W R G Y O B`). `print(cube)` l'affiche. Ce n'est pas encore l'affichage de la phase 2, juste un outil de débogage, mais il va te faire gagner des heures.
- [ ] Commit : `feat: ajoute la classe Cube (état résolu, is_solved, copy)`.

### Étape G — Le premier mouvement : U

- [ ] Écrire d'abord un **test de référence** : pars d'un cube résolu, fais `U`, et vérifie les couleurs que tu observes sur un vrai cube (tenu blanc en haut, vert devant). Par exemple : quelle couleur a maintenant la ligne du haut de F ? Et celle de R ?

  <details>
  <summary>Réponse (vérifie d'abord sur un vrai cube)</summary>

  Après `U`, la ligne du haut de F est **rouge** (elle vient de R), et la ligne du haut de R est **bleue** (elle vient de B). Le reste de F est toujours vert.
  </details>

- [ ] Écrire une méthode qui fait un quart de tour horaire de U, en deux temps (section « Ce que fait un quart de tour ») : la face U tourne sur elle-même, puis les 4 bandes tournent en cercle. Attention au sens de `np.rot90` (notion 3.4) et aux vues (notion 3.5).
- [ ] Écrire `move(name)`, qui pour l'instant ne connaît que `"U"`.
- [ ] `uv run pytest -v` : `test_quarter_turn_four_times_is_identity[U]` doit passer, et ton test de référence aussi.
- [ ] Commit : `feat: ajoute le mouvement U`.

### Étape H — Les inverses, les demi-tours et les mouvements inconnus

- [ ] `U'` et `U2` : le plus simple est de **répéter** le quart de tour (3 fois pour `U'`, 2 fois pour `U2`). C'est un peu moins rapide, mais impossible de se tromper, et ça divise le travail par trois : seuls 6 quarts de tour sont à écrire.
- [ ] `move` doit lire le nom : la première lettre donne la face, la suite (rien, `'` ou `2`) donne le nombre de quarts de tour (notion 2).
- [ ] Un nom inconnu (`"X"`, `"R3"`, `"r"`, `""`) doit lever une `ValueError` avec un message clair. Test : `test_unknown_move_raises`, paramétré sur plusieurs noms invalides, avec `pytest.raises`.
- [ ] Commit : `feat: ajoute les inverses et les demi-tours`.

### Étape I — Les 5 autres faces

Pour **chaque** face, dans l'ordre **D**, puis **R** et **L**, puis **F** et **B** :

- [ ] écrire son test de référence (rouge) : un mouvement depuis le cube résolu, puis les couleurs observées sur un vrai cube ;
- [ ] écrire le quart de tour ;
- [ ] `uv run pytest -v` : regarder les tests paramétrés passer au vert, face après face ;
- [ ] commit : `feat: ajoute le mouvement D` (etc.). Un commit par face, ou par paire (`R` et `L`) si tu préfères.

  <details>
  <summary>Quelques repères pour les tests de référence (vérifie d'abord sur un vrai cube)</summary>

  Depuis le cube résolu, blanc en haut, vert devant :

  - après `R`, la colonne de droite de U est **verte** ;
  - après `L`, la colonne de gauche de F est **blanche** ;
  - après `F`, la colonne de gauche de R est **blanche**.
  </details>

Quand `R` et `U` fonctionnent, `test_sexy_move_six_times_is_identity` passe au vert. Quand les 6 faces sont là, ajoute ces tests, qui attrapent les bugs les plus sournois :

- [ ] `test_quarter_turn_moves_twenty_stickers` : sur le cube numéroté, un quart de tour change exactement 20 cases (notion 3.6 : compter les cases différentes) ;
- [ ] `test_centers_never_move` : après n'importe quel mouvement, les 6 centres sont toujours à leur place ;
- [ ] `test_opposite_faces_commute` : faire `U` puis `D` donne le même cube que `D` puis `U` (et pareil pour `R`/`L`, `F`/`B`). Deux faces opposées ne touchent aucune case commune ;
- [ ] (bonus) généraliser le test « sexy move » : pour **toute** paire de faces voisines X et Y, `X Y X' Y'` répété 6 fois ramène à l'état de départ.

**Pourquoi les tests de référence sont indispensables.** Imagine un cube où tous les mouvements tournent dans le mauvais sens (`R` fait en réalité `R'`, etc.). Les 4 tests clés du cadrage passent tous ! Quatre quarts de tour dans le mauvais sens font toujours un tour complet, et `R' U' R U` répété 6 fois ramène aussi au départ. Seul un test qui compare à un **vrai** cube attrape ce bug.

### Étape J — Appliquer une suite de mouvements : `apply`

- [ ] `apply("R U R' U'")` découpe la chaîne et applique chaque mouvement avec `move`.
- [ ] Tests :
  - `apply("R U R' U'")` donne le même cube que les 4 `move` à la main ;
  - `apply("")` ne change rien ;
  - une suite contenant un mouvement inconnu lève `ValueError`.
- [ ] Simplifier le test « sexy move » avec `apply`, s'il ne l'utilise pas déjà.
- [ ] Commit : `feat: ajoute apply pour les suites de mouvements`.

### Étape K — Mélanger : `scramble`

- [ ] Définir la constante des **18 mouvements**, dans un ordre fixe.
- [ ] `scramble(n)` tire `n` mouvements au hasard parmi les 18, les applique, et renvoie la liste des mouvements joués.
- [ ] Prévoir un moyen de rendre le mélange **reproductible** (notion 4). À toi de choisir comment ; indice : `random.Random(graine)`.
- [ ] Écrire une petite fonction qui calcule la **suite inverse** d'une suite de mouvements. Principe de la chaussette et de la chaussure : pour défaire « chaussette puis chaussure », on enlève d'abord la chaussure. On inverse l'ordre, et on inverse chaque mouvement (`X` ↔ `X'`, et `X2` reste `X2`).
- [ ] Tests :
  - `scramble(n)` renvoie `n` mouvements, tous parmi les 18 ;
  - même graine, même mélange ;
  - après un mélange de 100 coups, il y a toujours 9 cases de chaque couleur ;
  - **mélanger, puis appliquer la suite inverse, redonne un cube résolu** (le test le plus satisfaisant de la phase).
- [ ] Commit : `feat: ajoute scramble et le calcul de la suite inverse`.

### Étape L — Nettoyer

- [ ] Depuis la **racine** du repo (regarde l'invite : `/c/rubiks-rl`) :

  ```bash
  uv run pytest -v
  uv run ruff check .
  uv run ruff format --check .
  ```

  Si `ruff format --check` signale des fichiers, lance `uv run ruff format .`, puis `git diff` pour voir ce qui a changé.
- [ ] Relire `cube.py` : chaque méthode a-t-elle une docstring en français ? Des annotations de type (`-> bool`, `-> None`, `-> list[str]`) ? Des noms clairs ?
- [ ] Jouer avec le cube dans la console (`uv run python`) : `from rubiks.cube import Cube`, puis `c = Cube()`, `c.apply("R U")`, `print(c)`…
- [ ] Mettre à jour la ligne « Avancement » du `README.md`, et y ajouter un exemple d'utilisation du cube (3 ou 4 lignes).
- [ ] Commit(s) : `style: …`, `refactor: …` ou `docs: …` selon ce que tu as changé.

### Étape M — La Pull Request et la relecture

- [ ] `git push` (le lien avec GitHub existe depuis l'étape B, grâce à `-u`).
- [ ] Sur GitHub : **Pull requests** → **New pull request** → *base* : `main`, *compare* : `feature/cube-model`.
- [ ] Titre : au format des commits, par exemple `feat: cube logique (phase 1)`. Description :

  ```markdown
  ## Ce que fait cette PR
  - classe Cube : état, 18 mouvements, apply, scramble, is_solved, copy
  - tests : identités du cadrage, tests de référence, mélange reproductible

  ## Comment tester
  uv sync
  uv run pytest -v
  ```

- [ ] Parcourir l'onglet **Files changed** : c'est l'occasion de te relire une dernière fois.
- [ ] Me demander une relecture (donne-moi le lien de la PR). Pour chaque correction : un nouveau commit sur la branche, `git push`, et la PR se met à jour.
- [ ] Une fois la relecture terminée, dernier commit sur la branche : dans `docs/cadrage.md`, annexe B, passer la phase 1 à « Terminé » avec la date ; dans `CLAUDE.md`, section « Phase en cours », passer à la phase 2. Commit : `docs: clôture la phase 1`, puis `git push`.

### Étape N — Merger, ranger, taguer

- [ ] Sur GitHub, dans la PR : **Create a merge commit** → **Confirm merge**. Puis cliquer sur **Delete branch** (supprime la branche sur GitHub seulement).
- [ ] Sur ton ordinateur :

  ```bash
  git switch main
  git pull                                  # récupère le commit de merge
  git log --oneline --graph --all           # admire le graphe
  git branch -d feature/cube-model          # supprime la branche locale
  git fetch --prune                         # oublie origin/feature/cube-model
  git branch -a                             # vérifier qu'il ne reste que main
  ```

  **Question :** pourquoi `git pull` doit-il venir **avant** `git branch -d` ? (Indice : avant de supprimer, `-d` vérifie que le travail de la branche est bien arrivé dans `main`.)
- [ ] Vérifier que tout est vert sur `main` : `uv sync`, puis `uv run pytest`.
- [ ] Poser et envoyer le tag :

  ```bash
  git tag -a v0.1.0 -m "Phase 1 : cube logique"
  git push origin v0.1.0
  git show v0.1.0
  ```

- [ ] Sur GitHub, vérifier que le tag apparaît (menu des branches → onglet **Tags**).
- [ ] Me demander la fiche de la phase 2.

---

## Comment vérifier que c'est bon

- [ ] `uv run pytest -v` : tout est vert, y compris les tests paramétrés sur les 6 faces.
- [ ] Depuis la racine : `uv run ruff check .` → `All checks passed!` et `uv run ruff format --check .` ne signale rien.
- [ ] Les tests couvrent : les 4 tests clés du cadrage, au moins un test de référence par face, les mouvements inconnus, `copy`, `apply`, `scramble` (reproductible, 9 cases par couleur, suite inverse).
- [ ] `git log --oneline --graph --all` montre la branche `feature/cube-model` qui part de `main` et y revient par un commit de merge, avec le tag `v0.1.0`.
- [ ] Sur GitHub : la PR n°1 est marquée **Merged** (en violet), la branche est supprimée, le tag `v0.1.0` est visible.
- [ ] Sur `main`, `pyproject.toml` contient `numpy` et `uv.lock` a été commité avec lui.
- [ ] Je sais expliquer avec mes mots :
  - ce qu'est une branche, une Pull Request, un merge et un tag ;
  - la différence entre une vue et une copie numpy, et pourquoi elle compte pendant un mouvement ;
  - pourquoi les 4 tests clés ne suffisent pas, et ce qu'ajoutent les tests de référence ;
  - pourquoi on fixe une graine dans les tests de mélange.

---

## Pièges fréquents

| Symptôme | Cause | Solution |
|---|---|---|
| `ValueError: The truth value of an array … is ambiguous` | `assert a == b` sur deux tableaux | `assert np.array_equal(a, b)` |
| une face tourne dans le mauvais sens | `np.rot90` tourne dans le sens **anti-horaire** par défaut | vérifier le sens sur la grille 1 à 9 (notion 3.4) |
| la forme du tableau change après une rotation, les faces se mélangent | `np.rot90` appliqué au tableau `(6, 3, 3)` entier | tourner une seule face : `state[i]` |
| après un mouvement, une bande de 3 cases est dupliquée et une autre a disparu | une vue gardée « de côté » a été écrasée pendant le cycle des bandes | mettre de côté avec `.copy()` (notion 3.5) |
| modifier la copie d'un cube modifie aussi l'original | `copy()` réutilise le même tableau, ou `c2 = c1` au lieu de `c2 = c1.copy()` | `copy()` doit copier le tableau ; tester avec `test_copy_is_independent` |
| les 4 tests clés passent, mais le cube ne se comporte pas comme un vrai | tous les mouvements tournent à l'envers, ou le cube est « en miroir » | tests de référence, vérifiés sur un vrai cube |
| `F` ou `B` semblent justes seuls, mais `F U F' U'` ×6 échoue | l'ordre d'une bande devait s'inverser (ou pas) au passage ligne ↔ colonne | reprendre le patron plié ; tester avec le cube numéroté |
| `L` « tourne à l'envers » | horaire se juge en regardant **la face L**, donc depuis la gauche | revoir la section « Notation » |
| `ValueError` sur `R'` alors que le code a l'air juste | apostrophe typographique `’` (copiée d'un site ou d'un traitement de texte) au lieu de `'` | retaper l'apostrophe au clavier ; afficher le nom avec `!r` dans le message d'erreur pour la repérer |
| un test de mélange échoue « de temps en temps » | le hasard change à chaque exécution | fixer la graine |
| `ModuleNotFoundError: No module named 'numpy'` | `uv add numpy` oublié, ou `python` lancé sans `uv run` | `uv add numpy` (étape C) ; toujours `uv run` |
| `ruff check .` ne signale rien alors qu'il y a une erreur dans `src/` | commande lancée depuis `tests/` : `.` veut dire « le dossier courant » | toujours lancer les commandes depuis la racine du repo |
| `ruff format .` modifie un fichier `.md` | ruff met aussi en forme les blocs de code Python des fichiers Markdown | normal : relire avec `git diff`, puis commiter (`style: …`) |
| `no changes added to commit` | `git add` oublié avant `git commit` | `git status` avant chaque commit ; `git add <fichier>` puis recommencer |
| un fichier manque dans le commit que je viens de faire | `git add` oublié pour ce fichier | s'il n'est **pas encore poussé** : `git add <fichier>` puis `git commit --amend --no-edit` (remplace le dernier commit). S'il est déjà poussé : un nouveau commit, tout simplement |
| `fatal: The current branch … has no upstream branch` | premier `git push` d'une nouvelle branche | `git push -u origin feature/cube-model` (Git affiche lui-même la commande) |
| j'ai fait un commit sur `main` par erreur | oubli de `git switch -c` | ne rien pousser, et me demander : on le déplacera sur une branche ensemble |
| `git switch` refuse de changer de branche | des modifications non commitées seraient écrasées | commiter d'abord (ou me demander : on verra `git stash`) |
| `error: the branch 'feature/cube-model' is not fully merged` (ou l'avertissement *not yet merged to HEAD*) | ton `main` local n'a pas encore le commit de merge (`git pull` oublié), ou la PR a été mergée avec *Squash* | `git switch main` puis `git pull`, et réessayer. Ne pas utiliser `-D` sans comprendre pourquoi |
| le tag n'apparaît pas sur GitHub | `git push` n'envoie pas les tags | `git push origin v0.1.0` |
| le tag est sur le mauvais commit | tag posé avant `git pull` | s'il n'est pas encore poussé : `git tag -d v0.1.0`, `git pull`, puis recréer le tag |
| Git Bash affiche `>` et attend | apostrophe dans un message entre apostrophes : `-m 'feat: ajoute l'inverse'` | `Ctrl+C`, puis mettre le message entre **guillemets doubles** |

---

## Pour aller plus loin (optionnel)

- **Les permutations, gratuitement.** Prends un cube numéroté (0 à 53), applique `R`, et regarde le tableau obtenu, mis à plat : il dit, pour chaque case, d'où vient son contenu. C'est exactement la permutation de l'option B, fabriquée par ton code de l'option A, sans rien écrire à la main. Avec l'indexation avancée de numpy (`state[perm]`), un mouvement devient une seule opération. Mesure le gain :

  ```bash
  uv run python -m timeit -s "from rubiks.cube import Cube; c = Cube()" "c.move('R')"
  ```

  En phase 5, l'agent jouera des millions de coups : chaque microseconde compte.
- **L'ordre d'une séquence.** Combien de fois faut-il répéter `R U` pour revenir au cube résolu ? (Réponse surprenante : 105.) Et `R U'` ? Écris une petite fonction qui le calcule, et un test pour `R U` = 105.
- **Un meilleur mélange.** `R` suivi de `R'` s'annule, et `R` suivi de `R2` fait `R'` : ces coups sont gaspillés. Interdis deux mouvements de suite sur la même face.
- **`__eq__` et `__repr__`.** Définis `__eq__` pour pouvoir écrire `assert cube_a == cube_b` dans les tests, et `__repr__` pour un affichage lisible dans les messages d'erreur de pytest.
- **Les fixtures pytest.** Une fonction marquée `@pytest.fixture` fabrique un objet (par exemple un cube numéroté) que plusieurs tests reçoivent en paramètre. Documentation : <https://docs.pytest.org/en/stable/how-to/fixtures.html>.
- **Découper le module.** Le cadrage prévoit `moves.py` et `scramble.py`. Si `cube.py` devient long, déplace le code, lance les tests : s'ils sont toujours verts, le découpage n'a rien cassé. C'est à ça que servent les tests. Commit : `refactor: …`.
- **Protéger `main` sur GitHub.** *Settings* → *Rules* → *Rulesets* : exiger une Pull Request avant tout merge dans `main`. Un `git push` direct sur `main` sera alors refusé : l'erreur de la phase 0 devient impossible.
- **Ne plus taper `-u`.** `git config --global push.autoSetupRemote true` : le premier `git push` d'une nouvelle branche crée automatiquement le lien avec GitHub.
- **Aligner la version du projet sur les tags.** `uv version` affiche la version de `pyproject.toml` ; `uv version --bump minor` la fait passer de `0.1.0` à `0.2.0`. À faire au moment de préparer le tag de la phase 2.
- **Une « release » GitHub.** Sur la page du tag `v0.1.0`, GitHub propose de créer une *release* avec des notes de version : un résumé de ce que fait cette version.
