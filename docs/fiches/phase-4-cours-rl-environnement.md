# Fiche — Phase 4 : Cours de RL et environnement Gymnasium

> **Emplacement dans le repo :** `docs/fiches/phase-4-cours-rl-environnement.md`
> **Durée indicative :** 12 à 18 h, en plusieurs séances : 3 à 5 h de cours et d'exercices sur papier, puis le code. Chaque étape se termine par un commit, chaque branche par une Pull Request.
> **Documents liés :** le cours `docs/cours/rl-1-les-bases.md` (**à lire en premier**), `docs/cadrage.md` (section 6 « Phase 4 », section 9 « Décisions »), `docs/fiches/bilan-v1.md` (section 5 « Ce qui est prêt pour le RL »).

## Objectif

À la fin de cette phase, j'ai :

- **compris** les notions de base du RL, et je sais les expliquer avec le cube : agent, environnement, état, action, récompense, épisode, politique, valeur, équation de Bellman, exploration / exploitation ;
- **résolu à la main, puis en code** un mini-casse-tête à 3 jetons, avec l'itération de valeur ;
- un **environnement Gymnasium** `RubiksEnv`, validé par le vérificateur officiel de Gymnasium et par mes tests ;
- un **agent aléatoire** qui joue dans cet environnement, et un **tableau de mesures** : sa réussite selon la profondeur du mélange ;
- (recommandé) un **parcours en largeur** qui compte les états à chaque distance, jusqu'à 5 coups ;
- un **court rapport écrit avec mes mots** : pourquoi l'agent aléatoire échoue, et ce qu'il faudra pour la phase 5.

**Terminé quand** (cadrage) : un agent aléatoire tourne dans l'environnement et je comprends pourquoi il n'y arrive pas.

---

## Comment travailler cette phase

Cette phase est différente des précédentes : **la moitié du travail se fait sans ordinateur**. Trois habitudes vont t'aider, ici et pour toute la suite du RL.

1. **Le cours d'abord, avec un crayon.** Lis `docs/cours/rl-1-les-bases.md` et fais les exercices sur papier **avant** de coder. Le code de cette phase est court ; ce qui compte, c'est de comprendre ce qu'il fait.
2. **Prédire avant de mesurer.** Avant chaque expérience, écris ce que tu t'attends à voir (un nombre, une tendance). Puis mesure. Quand la mesure te surprend, c'est là que tu apprends le plus. Tes prédictions iront dans ton rapport (étape G), même fausses : surtout fausses.
3. **Expliquer avec tes mots.** Le rapport final n'est pas une formalité : si tu arrives à expliquer à quelqu'un pourquoi l'agent aléatoire échoue, tu as compris le cœur du problème des phases 5 et 6.

**Rappel :** à partir de cette phase, c'est de nouveau toi qui codes (`CLAUDE.md`). Si tu bloques, demande-moi un indice : (1) une question ou une piste, (2) l'explication de la notion, (3) un petit exemple hors projet, (4) la solution, seulement si tu la demandes.

---

## Décisions de début de phase

Le cadrage (section 9) laisse plusieurs choix pour la phase 4. Tes décisions se notent dans `docs/cadrage.md`, section 9 (étape B).

### 1. Comment l'agent voit le cube (l'observation)

| | 54 cases | Les cubies (positions + orientations) |
|---|---|---|
| Ce que c'est | les couleurs des 54 cases, un vecteur de 54 entiers de 0 à 5 | 8 coins et 12 arêtes : où est chacun, et dans quel sens |
| Déjà disponible | oui : `cube.state`, mis à plat | non : il faudrait tout écrire |
| Taille | 54 nombres | 40 nombres environ |
| Lisible pour toi | oui, comme `print(cube)` | moins |

**Je recommande les 54 cases.** Elles sont déjà là, rapides (un coup ≈ 1 µs), et elles suffisent : la propriété de Markov est respectée (cours, section 4). Dans Gymnasium, ce sera un espace `MultiDiscrete([6] * 54)` : 54 cases, chacune avec 6 valeurs possibles.

Pour un réseau de neurones (phase 5), on transformera ces 54 nombres en 54 × 6 = 324 « 0 ou 1 » (le *one-hot*). Ce sera une préparation **à côté** de l'environnement, pas dans l'environnement. On en reparlera.

### 2. La récompense

| | -1 par coup (γ = 1) | +1 quand c'est résolu, 0 sinon (γ < 1) |
|---|---|---|
| Ce que vaut le retour | moins le nombre de coups | 0,9 puissance (nombre de coups - 1), si résolu |
| Ce que vaut V\* | **moins la distance** (cours, section 6) | 0,9 puissance (distance - 1) |
| Pousse à aller vite | oui, chaque coup coûte | oui, grâce à γ |
| Lisibilité | très bonne | moyenne |

**Je recommande -1 par coup, avec γ = 1.** Le retour se lit directement (« -7 » = 7 coups), et la valeur parfaite est la distance, ce qui fera le lien avec DeepCubeA (phase 6). L'exercice 5 du cours montre que les deux choix mènent à la même meilleure politique.

### 3. PyTorch : maintenant ou en phase 5 ?

Le cadrage prévoyait d'ajouter `torch` dès la phase 4. **Je recommande d'attendre le début de la phase 5**, pour trois raisons :

- la phase 4 ne s'en sert pas (aucun réseau de neurones) ; règle du cadrage : chaque dépendance arrive **au moment où on en a besoin** ;
- `torch` est très lourd (plusieurs centaines de Mo, voire plusieurs Go) ;
- le choix CPU / GPU dépend de ta machine : sous Windows et macOS, la version de PyPI est la version « CPU » (sur un Mac à puce Apple, elle sait aussi utiliser la puce graphique) ; sous Linux, c'est une version pour carte NVIDIA (CUDA), beaucoup plus grosse. La documentation d'uv explique comment choisir (guide « PyTorch » d'uv : <https://docs.astral.sh/uv/guides/integration/pytorch/>).

Question à préparer pour la phase 5 : **quel système as-tu, et as-tu une carte graphique NVIDIA ?**

### 4. La limite de coups par épisode

Sans limite, un agent aléatoire pourrait jouer pendant 1,4 million d'années (cours, section 11.4). Il faut donc **tronquer** les épisodes après `max_steps` coups. Fais-en un paramètre de l'environnement, avec une valeur par défaut raisonnable (par exemple 20). Tu verras en étape E si la valeur change quelque chose.

---

## Notions Python à connaître

Comme d'habitude : noms en anglais, commentaires en français, et des mini-exemples **hors projet**. Pour essayer les exemples Gymnasium, il faut d'abord ajouter la bibliothèque au projet (étape C), puis lancer le fichier d'essai avec `uv run python essai.py` (sans le commiter).

### 1. Gymnasium en 5 minutes

**Gymnasium** est la bibliothèque standard des environnements de RL. Elle ne contient pas d'agent : elle définit **une interface commune**, que tous les environnements respectent. Avantage : n'importe quel algorithme écrit pour Gymnasium (les tiens, ou ceux de bibliothèques comme Stable-Baselines3) peut jouer dans n'importe quel environnement Gymnasium, sans rien changer.

L'interface tient en deux méthodes :

```python
observation, info = env.reset(seed=0)        # commence un épisode
observation, reward, terminated, truncated, info = env.step(action)   # joue un pas
```

| Valeur | Ce que c'est | Pour le cube |
|---|---|---|
| `observation` | ce que voit l'agent | les 54 cases |
| `reward` | la récompense de ce pas | -1 |
| `terminated` | `True` si l'épisode est **vraiment fini** | le cube est résolu |
| `truncated` | `True` si on arrête **par limite de temps** | `max_steps` coups joués sans résoudre |
| `info` | un dictionnaire libre, pour **toi** (débogage, mesures) | par exemple le mélange utilisé |

L'épisode s'arrête dès que `terminated` **ou** `truncated` vaut `True`.

Mini-exemple complet (hors projet) : un robot dans un couloir de 6 cases. La sortie est tout à droite. Il paie -1 par pas.

```python
import gymnasium as gym
from gymnasium import spaces

LEFT, RIGHT = 0, 1  # les deux actions


class CorridorEnv(gym.Env):
    """Un robot dans un couloir de `length` cases ; la sortie est tout à droite.

    État : la case du robot (0 à length - 1). Actions : 0 = gauche, 1 = droite.
    Récompense : -1 par pas. Fin : sortie atteinte (terminated) ou trop de pas
    (truncated).
    """

    metadata = {"render_modes": ["ansi"], "render_fps": 4}

    def __init__(self, length: int = 6, max_steps: int = 20, render_mode: str | None = None):
        self.length = length
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Discrete(length)
        self.position = 0
        self.steps = 0

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)  # prépare self.np_random avec la graine
        options = options or {}
        # départ au hasard, sauf sur la sortie (ou imposé par options)
        start = options.get("start")
        if start is None:
            start = int(self.np_random.integers(0, self.length - 1))
        self.position = start
        self.steps = 0
        return self.position, {}  # (observation, info)

    def step(self, action: int):
        move = 1 if action == RIGHT else -1
        self.position = min(max(self.position + move, 0), self.length - 1)
        self.steps += 1
        terminated = self.position == self.length - 1  # sortie : vraie fin
        truncated = not terminated and self.steps >= self.max_steps  # chrono écoulé
        reward = -1.0
        return self.position, reward, terminated, truncated, {"steps": self.steps}

    def render(self) -> str:
        cells = ["R" if i == self.position else "." for i in range(self.length)]
        return "".join(cells) + "|"  # | = la sortie


if __name__ == "__main__":
    from gymnasium.utils.env_checker import check_env

    env = CorridorEnv(render_mode="ansi")
    check_env(env)  # vérifie que l'environnement respecte l'API

    observation, info = env.reset(seed=0, options={"start": 0})
    env.action_space.seed(0)  # le hasard des actions a sa propre graine (notion 4)
    total, done = 0.0, False
    while not done:
        action = env.action_space.sample()  # un agent qui joue au hasard
        observation, reward, terminated, truncated, info = env.step(action)
        total += reward
        print(env.render(), action, reward)
        done = terminated or truncated
    print("retour :", total, "| terminé :", terminated, "| tronqué :", truncated)
```

Ce qu'il affiche avec ces graines : le robot avance de trois cases, recule jusqu'au mur, y piétine, repart, et sort au 14ᵉ pas. L'épisode est **terminé**, avec un retour de -14, alors que 5 pas suffisaient. `check_env` affiche aussi un avertissement sans gravité (notion 2).

**À essayer :**
- change les deux graines (celle de `reset` et celle de `action_space.seed`) : avec certaines, le robot n'atteint pas la sortie en 20 pas, et l'épisode est **tronqué** (retour -20). Un premier aperçu de ce qui t'attend avec le cube ;
- supprime la ligne `env.action_space.seed(0)` et relance deux fois : les résultats changent à chaque fois. Pourquoi ? (notion 4) ;
- remplace `env.action_space.sample()` par `RIGHT` : quel retour obtiens-tu ? C'est la politique optimale de ce couloir.

### 2. Écrire son propre environnement : la liste de contrôle

Un environnement est une classe qui **hérite** de `gymnasium.Env` (comme `CubeView` héritait d'`Entity` en phase 3). Il doit avoir :

| Élément | Rôle | Piège |
|---|---|---|
| `metadata` | les modes d'affichage acceptés | ajoute `"render_fps"` pour éviter un avertissement |
| `__init__(..., render_mode=None)` | crée `action_space` et `observation_space` | accepte **toujours** `render_mode`, même si tu ne t'en sers pas |
| `reset(self, *, seed=None, options=None)` | commence un épisode ; renvoie `(observation, info)` | **appelle `super().reset(seed=seed)` en premier** |
| `step(self, action)` | joue un pas ; renvoie **5** valeurs | `terminated` et `truncated` séparés |
| `render(self)` (facultatif) | montre l'état | |

Le `*` dans `reset(self, *, seed=None, options=None)` est une syntaxe Python : tout ce qui suit **doit** être donné par son nom. On écrit `env.reset(seed=3)`, jamais `env.reset(3)`. C'est voulu : on ne peut pas confondre la graine et les options.

**Le vérificateur officiel.** `check_env(env)` (de `gymnasium.utils.env_checker`) joue quelques épisodes et vérifie que ton environnement respecte l'interface. Ses messages sont clairs. Par exemple, si tu oublies `super().reset(seed=seed)`, il te dit : *« Most likely the environment reset function does not call `super().reset(seed=seed)` »*. Lance-le dans un test : il deviendra ton premier filet de sécurité.

Il affiche parfois un avertissement inoffensif, *« Not able to test alternative render modes due to the environment not having a spec »*. Il veut dire : « je n'ai pas pu tester les autres modes d'affichage, car l'environnement n'a pas été créé avec `gymnasium.make` ». Tu peux l'ignorer, ou passer `skip_render_check=True` (voir aussi « Pour aller plus loin »).

### 3. Les espaces : décrire les actions et les observations

Un **espace** décrit l'ensemble des valeurs possibles :

```python
from gymnasium import spaces

actions = spaces.Discrete(18)               # un entier de 0 à 17
observations = spaces.MultiDiscrete([6] * 54)  # 54 entiers, chacun de 0 à 5

actions.sample()          # un élément au hasard, par exemple 11
actions.n                 # 18
observations.contains(x)  # True si x est une observation valable
```

Pour le cube : **l'action i est le mouvement `MOVES[i]`** (`rubiks.moves.MOVES`, dans l'ordre `U U' U2 R R' R2 F …`). L'agent ne manipule que des entiers ; c'est l'environnement qui les traduit en mouvements.

### 4. Le hasard reproductible

En RL, presque tout est aléatoire : les mélanges, les choix de l'agent, plus tard l'initialisation des réseaux. Pour pouvoir **refaire une expérience** et **déboguer**, il faut des graines.

numpy fournit des **générateurs** de nombres aléatoires :

```python
import numpy as np

rng = np.random.default_rng(42)   # un générateur, avec sa graine
rng.integers(0, 18)               # un entier de 0 à 17 (18 exclu)
rng.integers(0, 18, size=5)       # cinq entiers d'un coup
rng.choice(["G", "D"])            # un élément au hasard

# deux générateurs avec la même graine donnent la même suite
a = np.random.default_rng(7)
b = np.random.default_rng(7)
print(a.integers(0, 100, size=3), b.integers(0, 100, size=3))   # identiques
```

Dans ton projet, il y aura **trois** sources de hasard. Il faut les relier :

| Source | Où | Comment la rendre reproductible |
|---|---|---|
| l'environnement (le mélange) | `self.np_random`, créé par `super().reset(seed=seed)` | `env.reset(seed=...)` |
| ton `Cube` | `cube.scramble(n, seed=...)` attend une graine entière | **tire cette graine avec `self.np_random`** : ainsi, une seule graine (celle de `reset`) décide de tout |
| l'agent | son propre générateur | donne-lui une graine à sa création |

Attention : `env.action_space.sample()` a **son propre** générateur, qui **n'est pas** réglé par `env.reset(seed=...)`. Si tu t'en sers, appelle aussi `env.action_space.seed(...)`. Plus simple : donne à ton agent son propre générateur.

### 5. Vue ou copie : ne pas prêter son cube

Avec numpy, `reshape` ne copie pas les données : il crée une **vue**, une autre façon de regarder **le même tableau**.

```python
import numpy as np

a = np.zeros((2, 3), dtype=int)
b = a.reshape(6)          # une VUE : les mêmes données, une autre forme
c = a.reshape(6).copy()   # une COPIE : des données indépendantes

b[0] = 7
print(a[0, 0])  # 7 : modifier b a modifié a !
c[1] = 9
print(a[0, 1])  # 0 : c est indépendant
```

Pour l'environnement : si l'observation renvoyée est une vue sur `cube.state`, un agent qui modifie son observation (par erreur, ou pour la préparer) **modifie le cube de l'environnement**. Renvoie toujours une **copie**. Le test qui le prouve : modifier l'observation reçue, puis vérifier que l'environnement n'a pas changé.

### 6. `options` et `info` : deux dictionnaires

- `options` entre dans `reset` : des réglages pour **cet** épisode. Pour le cube : `env.reset(seed=0, options={"scramble_depth": 3})`. Dans `reset`, `options` peut valoir `None` : l'astuce `options = options or {}` le remplace par un dictionnaire vide, puis `options.get("scramble_depth", self.scramble_depth)` donne la valeur demandée, ou celle par défaut.
- `info` sort de `reset` et de `step` : des informations pour **toi**, jamais pour l'agent. Y mettre le mélange est très pratique pour les tests, mais un agent qui le lirait serait l'oracle tricheur (cours, section 4 et exercice 12).

C'est ainsi que Gymnasium traduit le `reset(scramble_depth)` du cadrage.

### 7. Mesurer correctement : combien d'épisodes ?

Un agent aléatoire est… aléatoire. Une seule partie ne dit rien ; il faut **beaucoup d'épisodes** et des **moyennes**.

- **Taux de réussite** = nombre d'épisodes résolus / nombre d'épisodes.
- **Longueur moyenne** des épisodes réussis, et **retour moyen**.
- **Combien d'épisodes ?** Un pourcentage p mesuré sur n épisodes est précis à environ **± 2 × racine( p × (1 - p) / n )**. Exemple : 7 % mesuré sur 1 000 épisodes est précis à ± 1,6 point. Règle simple : **attends d'avoir au moins une dizaine de succès** avant de croire un pourcentage. « 0 succès sur 100 » ne veut pas dire « 0 % ».
- **La vitesse** : `time.perf_counter()` avant et après, pour compter les pas par seconde.

### 8. Le parcours en largeur (BFS) : dictionnaires et clés

Pour compter les cubes à chaque distance (étape F), on explore « vague par vague » : le cube résolu, puis ses voisins, puis les voisins des voisins… en retenant ceux déjà vus, pour ne pas les compter deux fois.

- **Retenir ce qu'on a vu** : un `set` (ou un `dict` état → distance). Un test « déjà vu ? » y prend le même temps, qu'il contienne 10 éléments ou 10 millions.
- **Une clé doit être « hashable »** (non modifiable). Un tableau numpy ne l'est pas : `TypeError: unhashable type: 'numpy.ndarray'`. Utilise `cube.facelets()` (une chaîne de 54 lettres, lisible) ou `cube.state.tobytes()` (plus rapide).
- **Vague par vague** : garde une liste des états de la distance actuelle ; la suivante se construit à partir d'elle.

Mini-exemple (hors projet) : les distances dans un petit réseau de villes.

```python
neighbours = {
    "Paris": ["Lyon", "Lille"],
    "Lyon": ["Paris", "Marseille"],
    "Lille": ["Paris"],
    "Marseille": ["Lyon"],
}
distance = {"Paris": 0}
frontier = ["Paris"]  # la vague actuelle
d = 0
while frontier:
    d += 1
    next_frontier = []
    for city in frontier:
        for other in neighbours[city]:
            if other not in distance:  # jamais vue : elle est à distance d
                distance[other] = d
                next_frontier.append(other)
    frontier = next_frontier
print(distance)  # {'Paris': 0, 'Lyon': 1, 'Lille': 1, 'Marseille': 2}
```

C'est l'itération de valeur du cours (section 8), quand chaque pas coûte 1.

### 9. Tester du code aléatoire

On ne peut pas tester « le résultat » d'un tirage au hasard. On teste :

- la **reproductibilité** : même graine, même mélange ; graines différentes, mélanges différents ;
- des **propriétés** toujours vraies : l'observation est dans l'espace d'observations, le cube n'est pas résolu après `reset`, l'épisode est tronqué exactement au bout de `max_steps` coups ;
- un **chemin connu** : dans un **test**, tu as le droit de lire le mélange dans `info` et de jouer sa suite inverse (`rubiks.moves.inverse_sequence`). L'épisode doit alors se terminer, au dernier coup exactement, avec le bon retour. C'est l'oracle, utilisé là où il est permis : pour vérifier l'environnement ;
- `check_env(env)`, dans un test.

### 10. Lancer un module : `python -m`

Pour lancer ton évaluation sans ajouter de commande au projet :

```bash
uv run python -m rubiks.rl.evaluate
```

`-m` lance un module **par son nom de paquet**, ce qui fait marcher les imports `from rubiks…`. Le module doit se terminer par le bloc `if __name__ == "__main__":`, que tu connais depuis la phase 2.

---

## Notions Git de l'étape

Tu maîtrises le cycle des branches. Quatre choses nouvelles, ou devenues utiles.

### 1. Quand la coche de la CI est rouge

`main` est protégé : une PR ne se merge que si la CI est verte. Si elle est rouge :

1. dans la PR, onglet **Checks**, ouvre l'étape en échec et lis le message (comme une erreur de pytest) ;
2. reproduis en local : `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest`, `uv lock --check` ;
3. corrige, commit, `git push` **sur la même branche** : la PR se met à jour toute seule, et la CI repart.

Piège classique : `uv add` en local, mais `uv.lock` oublié dans le commit. `uv lock --check` le détecte.

### 2. Expériences et reproductibilité

En RL, on fait beaucoup d'expériences. Règle : **on commite ce qui permet de refaire l'expérience** (le code, la graine, la commande), **pas les gros fichiers de résultats**. Les chiffres importants vont dans ton rapport, en Markdown. Si tu écris des fichiers de résultats (CSV…), range-les dans un dossier `runs/` et ajoute-le au `.gitignore`.

### 3. `git stash` : mettre de côté une expérience

Tu es en train d'essayer une idée sur ta branche, ce n'est pas fini, et tu dois corriger autre chose d'abord (la CI d'une autre PR, par exemple).

| Commande | À quoi ça sert |
|---|---|
| `git stash push -m "essai max_steps 100"` | range tes modifications non commitées dans une « réserve » ; ton dossier redevient propre |
| `git stash list` | liste ce qui est en réserve |
| `git stash pop` | ressort la dernière réserve et la supprime de la liste |
| `git stash drop` | jette la dernière réserve |

Scénario d'entraînement : modifie `max_steps` dans ton environnement, `git stash push -m "essai"`, vérifie avec `git status` que tout est propre, change de branche et reviens, puis `git stash pop`.

### 4. `git rm` : supprimer un fichier suivi

Un double de `CLAUDE.md` s'est glissé dans `tests/` lors de la mise à jour v1.0 (`git log --oneline -- tests/CLAUDE.md` montre le commit). `git rm tests/CLAUDE.md` supprime le fichier **et** prépare la suppression pour le prochain commit (un simple `rm` ferait la première moitié seulement). Cousin : `git mv ancien nouveau` pour renommer.

(Facultatif) L'exercice du conflit de merge de la phase 3 (fiche 3, étape D) est toujours disponible.

---

## Tâches (dans l'ordre)

**À chaque branche, le même cycle** : `main` à jour → `git switch -c …` → commits → `uv run pytest` + `uv run ruff check .` → `git push` → PR → CI verte → merge → Delete branch → `git switch main` → `git pull` → `git branch -d …`.

### Étape A — Le cours, sur papier (pas de code, pas de branche)

- [ ] Lire `docs/cours/rl-1-les-bases.md`, sections 1 à 10. Faire les exercices 1 à 8 dans un cahier. Comparer avec les corrigés. Noter les questions qui restent : on en parle avant de coder.
- [ ] Lire les sections 11 à 14, faire les exercices 9 à 13.
- [ ] **Tes prédictions**, écrites avant toute mesure (elles iront dans le rapport) :
  1. l'agent aléatoire, sur un cube mélangé de **1** coup, avec 20 coups maximum : quel pourcentage de réussite ?
  2. même question pour des mélanges de **3** coups ;
  3. si on lui donne **100** coups au lieu de 20, le pourcentage est-il multiplié par 5 ? par combien ?
  4. parmi des mélanges de 3 coups, quelle proportion est **vraiment** à 3 coups de la solution ?
  5. combien de temps et de mémoire pour compter tous les cubes jusqu'à la distance 5 sur ton ordinateur ? et jusqu'à 6 ?

### Étape B — Branche `docs/fiche-phase-4`

- [ ] Ajouter cette fiche dans `docs/fiches/` et le cours dans `docs/cours/`. Commit : `docs: ajoute la fiche et le cours de la phase 4`.
- [ ] `docs/cadrage.md`, section 9, noter les décisions : représentation de l'état (« Décidé : 54 cases »), version de PyTorch (« Reportée au début de la phase 5 »), et une nouvelle ligne « Récompense » (« Décidé : -1 par coup, γ = 1 »). Section 6, phase 4 : remplacer « `gymnasium` et `torch` ajoutés » par « `gymnasium` ajouté (`torch` en phase 5) ». Commit : `docs: décisions de début de phase 4`.
- [ ] `git rm tests/CLAUDE.md`. Commit : `docs: supprime le double de CLAUDE.md dans tests/`.
- [ ] Push, PR, merge, rangement.

### Étape C — Branche `feature/mini-puzzle` : le laboratoire

Le mini-casse-tête à 3 jetons du cours (section 5), d'abord en code. Six états : on peut **tout** vérifier à la main.

- [ ] Ajouter Gymnasium (dépendance **principale** : le paquet `rubiks.rl` en aura besoin pour tourner) :

  ```bash
  uv add gymnasium
  ```

  Commit avec `pyproject.toml` **et** `uv.lock` : `build: ajoute gymnasium aux dépendances`.
- [ ] Créer le sous-paquet `src/rubiks/rl/` (avec son `__init__.py` et une docstring) et `src/rubiks/rl/mini_puzzle.py` :
  - les 6 états (par exemple une constante `STATES = ("ABC", "BAC", …)`) et les 2 actions (0 = G, 1 = D) ;
  - une fonction pure `next_state(state, action)` ;
  - une classe `MiniPuzzleEnv(gym.Env)` : observation = le **numéro** de l'état (`spaces.Discrete(6)`), action `spaces.Discrete(2)`, -1 par coup, terminé sur ABC, tronqué après `max_steps`, départ au hasard (jamais ABC) ou imposé par `options={"start": "CBA"}`.
- [ ] Dans `src/rubiks/rl/value_iteration.py`, une fonction `value_iteration(...)` qui applique l'équation de Bellman en boucle (cours, section 8) jusqu'à ce que plus rien ne change. Essaie de l'écrire **pour n'importe quel petit problème** : elle reçoit la liste des états, des actions, une fonction de transition, et sait quels états sont terminaux. Elle renvoie les valeurs (et, pourquoi pas, le nombre de tours).
- [ ] Tests (`tests/test_mini_puzzle.py`) :
  - `check_env` passe ;
  - G puis G revient à l'état de départ ; depuis BAC, G termine l'épisode avec une récompense de -1 ;
  - `value_iteration` trouve 0, -1, -1, -2, -2, -3, comme ton tableau de la section 8 (où les valeurs ne bougent plus après le tour 3 : le tour 4 le confirme) ;
  - un agent **glouton** qui suit ces valeurs résout CBA en 3 coups exactement.
- [ ] Une petite mesure : l'agent aléatoire, depuis CBA, avec une grande limite (par exemple 1 000 coups) : longueur moyenne sur 10 000 épisodes ? Et la réussite avec 20 coups maximum ? Compare avec le cours (9 coups ; environ 92 %).
- [ ] Commits, push, PR, merge, rangement.

### Étape D — Branche `feature/rubiks-env` : l'environnement du cube

Dans `src/rubiks/rl/env.py`, une classe `RubiksEnv(gym.Env)`, sur le modèle du mini-casse-tête et du couloir :

- [ ] `__init__(self, scramble_depth=3, max_steps=20, render_mode=None)` ; `action_space = Discrete(18)` ; `observation_space = MultiDiscrete([6] * 54)`.
- [ ] `reset(self, *, seed=None, options=None)` :
  - `super().reset(seed=seed)` en premier ;
  - la profondeur vient de `options` (ou de la valeur par défaut) ;
  - un cube neuf, mélangé avec une graine **tirée de `self.np_random`** (notion 4) ;
  - si le mélange redonne un cube résolu (cours, exercice 7), on recommence ;
  - renvoie une **copie** des 54 cases, et un `info` (par exemple la profondeur et le mélange, pour les tests).
- [ ] `step(self, action)` : joue `MOVES[action]`, compte le coup, et renvoie l'observation (copie), -1, `terminated` (résolu), `truncated` (limite atteinte **sans** être résolu), `info`.
- [ ] (Facultatif) `render` en mode `"ansi"` : `rubiks.render.terminal.to_ansi` existe déjà. Réutiliser du code, c'est aussi ça, l'architecture du cadrage.
- [ ] Tests (`tests/test_env.py`), en t'aidant de la notion 9 :
  - `check_env` passe ;
  - même graine → même observation ; graines différentes → observations différentes ;
  - après `reset`, le cube n'est pas résolu, et l'observation est dans `observation_space` ;
  - modifier l'observation reçue ne change pas l'environnement (notion 5) ;
  - l'action 3 joue bien `R` (compare avec un `Cube` sur lequel tu fais `move("R")`) ;
  - **l'oracle de test** : jouer la suite inverse du mélange termine l'épisode au dernier coup, avec un retour de - (longueur de la suite) ;
  - un épisode sans solution est tronqué **exactement** au coup `max_steps`, pas avant ;
  - un cube résolu au dernier coup permis est **terminé**, pas tronqué (cours, exercice 2c).
- [ ] Dans `tests/test_render.py`, ajouter `"rubiks.rl.env"` et `"rubiks.rl.mini_puzzle"` à la liste `PURE_MODULES` : l'entraînement ne doit charger ni pygame ni ursina.
- [ ] Commits, push, PR, merge, rangement.

### Étape E — Branche `feature/random-agent` : mesurer l'échec

- [ ] `src/rubiks/rl/agents/__init__.py` et `src/rubiks/rl/agents/random_agent.py` : une classe `RandomAgent` avec une méthode `act(observation) -> int`, qui choisit un coup au hasard **avec son propre générateur** (notion 4). Elle ignore complètement l'observation : c'est le principe.
- [ ] `src/rubiks/rl/evaluate.py` :
  - une fonction qui joue **un** épisode avec un agent et renvoie : résolu ou non, nombre de coups, retour ;
  - une fonction qui en joue **n** et renvoie le taux de réussite, la longueur moyenne des réussites, le retour moyen ;
  - un bloc `if __name__ == "__main__":` qui affiche un **tableau** : profondeur de mélange 1 à 6, réussite de l'agent aléatoire, avec `max_steps = 20`. Lancement : `uv run python -m rubiks.rl.evaluate`.
- [ ] Tests (`tests/test_evaluate.py`) : utilise le mini-casse-tête, où tout est connu. Un agent glouton qui suit `value_iteration` doit réussir **100 %** des épisodes, avec une longueur moyenne égale à la distance moyenne des départs. Pas besoin de tester l'agent aléatoire au pourcentage près.
- [ ] Mesurer (au moins 10 000 épisodes par profondeur, plus pour les grandes profondeurs : notion 7) :
  - le tableau de réussite de l'agent aléatoire, profondeurs 1 à 6, `max_steps = 20` ;
  - le même pour les profondeurs 1 à 3 avec `max_steps = 100` ;
  - la vitesse de ton environnement, en pas par seconde.
  Compare avec tes prédictions de l'étape A. **Puis seulement**, lis la section « Pour vérifier tes mesures » en fin de fiche.
- [ ] Commits, push, PR, merge, rangement.

### Étape F (recommandée) — Branche `feature/bfs` : voir l'explosion

- [ ] `src/rubiks/rl/bfs.py` : une fonction qui compte les cubes à chaque distance, de 0 à `max_distance`, par un parcours en largeur (notion 8). Les voisins d'un cube : `copy()` puis `move(m)` pour chacun des 18 mouvements de `MOVES`.
- [ ] Test : les comptes jusqu'à la distance 3 sont 1, 18, 243, 3 240 (le tableau du cours, section 11.2). Pas plus loin dans les tests : ils doivent rester rapides.
- [ ] À la main : lancer jusqu'à la distance 4, puis 5, en mesurant le temps (`time.perf_counter`). Regarde la mémoire utilisée par Python dans le gestionnaire des tâches. **Ne lance pas la distance 6** sans avoir estimé, avec un « × 13 », le temps et la mémoire nécessaires.
- [ ] (Bonus) Avec les distances calculées, mesure toi-même deux chiffres du cours : la **pente** (section 11.3 : combien des 18 voisins d'un cube à distance 3 sont plus proches, à la même distance, plus loin ?) et la **profondeur ≠ distance** (exercice 7 : parmi 10 000 mélanges de 3 coups, combien sont vraiment à distance 3 ?).
- [ ] Commits, push, PR, merge, rangement.

### Étape G — Le rapport : pourquoi l'agent aléatoire échoue

- [ ] Créer `docs/rapports/phase-4-agent-aleatoire.md`, avec ce plan :

  ```markdown
  # Rapport — Phase 4 : pourquoi l'agent aléatoire échoue

  ## 1. Mes prédictions (écrites avant de mesurer)
  ## 2. Le protocole (environnement, max_steps, nombre d'épisodes, graines, commande)
  ## 3. Les mesures (tableaux)
  ## 4. Pourquoi ça échoue (avec mes mots, chiffres à l'appui)
  ## 5. Ce que j'en conclus pour la phase 5
  ```

- [ ] Section 4 : au moins **quatre raisons**, chacune appuyée sur **un chiffre que tu as mesuré** ou calculé. Le cours (section 11) t'aide, mais écris-les à ta façon.
- [ ] Section 5 : d'après tes mesures, **à quelle profondeur de mélange** un agent qui apprend devrait-il commencer ? Pourquoi ?
- [ ] Me demander une relecture. Commit : `docs: rapport de la phase 4 sur l'agent aléatoire`.

### Étape H — Clore la phase (branche `docs/cloture-phase-4`)

- [ ] `uv run ruff check .`, `uv run ruff format .`, `uv run pytest`.
- [ ] Relire `src/rubiks/rl/` : une docstring par module, classe et fonction, des annotations de type, aucun nombre magique (profondeur et `max_steps` par défaut, nombre d'épisodes… en constantes).
- [ ] `README.md` : avancement, et la commande `uv run python -m rubiks.rl.evaluate`.
- [ ] `docs/cadrage.md` : annexe B (phase 4 « Fait », date) et « Phase 4 terminée » dans la section 6. `CLAUDE.md` : phase en cours = phase 5, et `src/rubiks/rl/` dans l'architecture.
- [ ] (Optionnel) `uv version --bump minor` (1.0.0 → 1.1.0) et un tag `v1.1.0` après le merge.
- [ ] Commit, push, PR, merge, rangement.
- [ ] Me demander la fiche de la phase 5 (et le chapitre 2 du cours : Q-learning).

---

## Comment vérifier que c'est bon

- [ ] `uv run pytest` : tout est vert, y compris `test_mini_puzzle.py`, `test_env.py`, `test_evaluate.py` (et `test_bfs.py`).
- [ ] `check_env` passe pour `MiniPuzzleEnv` et `RubiksEnv`.
- [ ] `uv run ruff check .`, `uv run ruff format --check .` et la CI sont verts.
- [ ] `import rubiks.rl.env` ne charge ni pygame ni ursina (test de `test_render.py`).
- [ ] `uv run python -m rubiks.rl.evaluate` affiche le tableau de réussite, de façon **reproductible** (deux lancements, mêmes chiffres).
- [ ] Mon rapport est écrit, relu, et commité.
- [ ] Je sais expliquer avec mes mots :
  - la boucle agent / environnement, et le rôle de chacune des 5 valeurs de `step` ;
  - la différence entre terminé et tronqué, et pourquoi elle compte ;
  - pourquoi « -1 par coup » fait chercher les solutions courtes ;
  - ce que sont V et Q, et pourquoi V\*(cube) = - distance ;
  - l'équation de Bellman avec l'exemple du GPS, et l'itération de valeur comme une « vague » ;
  - pourquoi l'agent ne doit jamais lire `info` ;
  - au moins quatre raisons de l'échec de l'agent aléatoire, avec des chiffres ;
  - pourquoi on ne peut pas faire une table de valeurs pour le cube.

---

## Pièges fréquents

| Symptôme | Cause | Solution |
|---|---|---|
| un tutoriel en ligne écrit `import gym` et `obs, reward, done, info = env.step(a)` | c'est l'**ancienne** bibliothèque `gym` (avant 2022), remplacée par Gymnasium | `import gymnasium as gym` ; `step` renvoie **5** valeurs |
| `ValueError: not enough values to unpack (expected 5, got 4)` | `step` renvoie 4 valeurs (un seul `done`) | séparer `terminated` et `truncated` |
| `check_env` : *« The result returned by `env.reset()` was not a tuple of the form `(obs, info)` »* | `reset` renvoie seulement l'observation | `return observation, info` |
| `check_env` : *« … does not call `super().reset(seed=seed)` »* | oubli de la première ligne de `reset` | `super().reset(seed=seed)` en premier |
| `TypeError: … unexpected keyword argument 'render_mode'` (avec `gymnasium.make`) | `__init__` n'accepte pas `render_mode` | ajouter `render_mode=None` aux paramètres |
| deux lancements avec la même graine donnent des résultats différents | une source de hasard non réglée : `random` sans graine, ou `action_space.sample()` | tirer la graine du mélange avec `self.np_random` ; un générateur à graine pour l'agent (notion 4) |
| le cube de l'environnement change quand l'agent modifie son observation | l'observation est une vue sur `cube.state` | renvoyer une copie (notion 5) |
| de temps en temps, `reset` donne un cube déjà résolu | un mélange comme `R L R' L'` s'annule (cours, exercice 7) | recommencer le mélange tant que le cube est résolu |
| un épisode résolu au dernier coup est marqué « tronqué » | `truncated` calculé sans regarder `terminated` | tronqué = limite atteinte **et pas** résolu |
| l'agent apprend à ne jamais finir (en phase 5) | récompense positive à chaque coup (cours, exercice 13) | -1 par coup ; vérifier le signe |
| « 0 % de réussite » à la profondeur 4 | trop peu d'épisodes pour voir un événement rare | plus d'épisodes, au moins 10 succès (notion 7) |
| les tests sont parfois rouges, parfois verts | un test dépend du hasard sans graine | graines partout dans les tests ; tester des propriétés (notion 9) |
| `TypeError: unhashable type: 'numpy.ndarray'` | un tableau numpy comme clé de `dict` ou élément de `set` | `cube.facelets()` ou `state.tobytes()` (notion 8) |
| l'ordinateur rame, puis `MemoryError` pendant le BFS | distance 6 ou plus : des millions d'états en mémoire | s'arrêter à 5 ; estimer avant de lancer (« × 13 ») |
| `ModuleNotFoundError: No module named 'gymnasium'` | `uv add gymnasium` oublié, ou lancement sans `uv run` | étape C ; toujours `uv run` |
| la CI est rouge alors que tout passe en local | `uv.lock` pas commité avec `pyproject.toml` | `uv lock --check`, puis commiter les deux ensemble |

---

## Pour aller plus loin (optionnel)

- **Un agent qui cherche, au lieu d'apprendre.** Un agent « à un coup d'avance » : il essaie les 18 coups sur une **copie** du cube et joue celui qui résout, s'il existe (sinon au hasard). Quelle réussite à la profondeur 1 ? Puis « à deux coups d'avance » (18 × 18 = 324 suites) : quelles profondeurs résout-il toujours ? C'est un avant-goût de la phase 6 : nous connaissons le **modèle** du cube (cours, section 12, encadré).
- **Évaluer la politique aléatoire par le calcul.** Adapte `value_iteration` pour qu'elle fasse **la moyenne** sur les actions au lieu du maximum (cours, section 7, « Bellman pour une politique donnée »). Sur le mini-casse-tête, tu dois retrouver -5, -8 et -9, exactement les longueurs moyennes mesurées à l'étape C.
- **Le lemme de Kac, mesuré.** Sur le mini-casse-tête, mesure le nombre moyen de coups pour revenir à ABC en partant de ABC (cours, exercice 10). Tu dois trouver environ 6.
- **Un casse-tête à 4 jetons** : 24 états, 3 actions (échanger les jetons 1-2, 2-3 ou 3-4). Ta `value_iteration` générique marche-t-elle sans rien changer ? Quelle est la distance maximale ? Combien de coups pour l'agent aléatoire ?
- **Enregistrer l'environnement** auprès de Gymnasium : `gymnasium.register(id="rubiks/RubiksCube-v0", entry_point="rubiks.rl.env:RubiksEnv")`, puis `env = gymnasium.make("rubiks/RubiksCube-v0", scramble_depth=2)`. `make` ajoute automatiquement des vérifications, et l'avertissement « no spec » de `check_env` disparaît.
- **La troncature par un « wrapper ».** Gymnasium fournit `gymnasium.wrappers.TimeLimit`, qui tronque n'importe quel environnement après n pas. Un *wrapper* est un environnement qui en enveloppe un autre pour modifier son comportement. Compare avec ta troncature faite à la main.
- **Un graphique.** `uv add --dev matplotlib`, puis la réussite en fonction de la profondeur, avec une échelle logarithmique (`plt.yscale("log")`). Tu en feras beaucoup en phase 5 (les courbes d'apprentissage).
- **Lire la suite**, en anglais : Sutton et Barto, chapitres 3 et 4 (<http://incompleteideas.net/book/the-book-2nd.html>) ; le cours Hugging Face, unités 1 et 2 (<https://huggingface.co/learn/deep-rl-course/unit0/introduction>).

---

## Pour vérifier tes mesures (à lire APRÈS l'étape E)

Mesures faites avec le code du dépôt (mélanges sans deux coups de suite sur la même face, relancés s'ils redonnent un cube résolu). Les tiennes peuvent varier un peu selon tes graines et tes choix, mais l'ordre de grandeur doit être le même.

**L'agent aléatoire sur le cube, `max_steps = 20`** (100 000 épisodes par profondeur) :

| Profondeur du mélange | Réussite |
|---|---|
| 1 | environ 6,8 % |
| 2 | environ 0,6 % |
| 3 | environ 0,17 % |
| 4 | environ 0,05 % |
| 5 | environ 0,02 % |
| 6 | environ 0,007 % (7 réussites sur 100 000) |

**Avec `max_steps = 100`** : environ 6,7 %, 0,5 % et 0,14 % pour les profondeurs 1, 2, 3. **Pas mieux** : un agent qui s'est éloigné ne revient pas. Plus de temps ne sert à rien.

**D'où viennent les rares réussites aux grandes profondeurs ?** Leur longueur moyenne est de 2 à 3 coups seulement, même pour des mélanges de 6 coups. Ce sont surtout des mélanges qui « s'effondrent » (cours, exercice 7) : parmi les mélanges de 3 coups, environ 96 % sont vraiment à distance 3, 2,7 % à distance 2 et 1,3 % à distance 1. Aux profondeurs 4 et 5, environ 90 % sont vraiment à la distance du mélange.

**Le mini-casse-tête** : depuis CBA, environ 9 coups en moyenne au hasard, et environ 92 % de réussite avec 20 coups maximum.

**La vitesse** : de l'ordre de **100 000 pas par seconde** pour l'environnement, contre environ 1 million de coups par seconde pour `cube.move` seul. La différence vient de tout ce que fait `step` en plus : copier l'observation, vérifier si le cube est résolu, construire le tuple.

**Le BFS** (avec des objets `Cube` et `facelets()`) : distance 4 en quelques secondes ; distance 5 en moins d'une minute, avec environ 500 Mo de mémoire. Distance 6, avec « × 13 » : une dizaine de minutes et plusieurs Go. Distance 7 : plusieurs dizaines de Go. Pas lancée : c'est le but de l'exercice.
