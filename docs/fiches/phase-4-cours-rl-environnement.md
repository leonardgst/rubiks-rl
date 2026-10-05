# Fiche — Phase 4 : MDP, programmation dynamique et environnement Gymnasium

> **Emplacement dans le repo :** `docs/fiches/phase-4-cours-rl-environnement.md`
> **Niveau :** le RL est traité au niveau master (formalisme, preuves, modèles probabilistes). Python, Gymnasium et Git restent expliqués pas à pas.
> **Durée indicative :** 15 à 25 h, en plusieurs séances : 5 à 8 h de cours et d'exercices, puis le code. Chaque étape se termine par un commit, chaque branche par une Pull Request.
> **Documents liés :** le cours `docs/cours/rl-1-mdp-et-programmation-dynamique.md` (**à lire en premier**), `docs/cadrage.md` (section 6 « Phase 4 », section 9 « Décisions »), `docs/fiches/bilan-v1.md` (section 5 « Ce qui est prêt pour le RL »).

## Objectif

À la fin de cette phase, j'ai :

- **maîtrisé le formalisme** (MDP, plus court chemin stochastique, opérateurs de Bellman, itération de politique et de valeur) et je sais le spécialiser au cube : graphe de Cayley, $V^* = -d$, itération de valeur = parcours en largeur ;
- une **boîte à outils tabulaire** (évaluation exacte et itérative, itération de valeur et de politique, chaînes absorbantes), validée sur le mini-casse-tête à 3 jetons contre les résultats exacts du cours ;
- un **environnement Gymnasium** `RubiksEnv`, validé par le vérificateur officiel et par mes tests ;
- la **structure exacte** du problème : les sphères du 3×3 jusqu'à la distance 5, la « pente », l'écart entre profondeur de mélange et distance, et le **2×2 résolu exactement** (3 674 160 états), qui servira de vérité terrain en phase 5 ;
- un **agent aléatoire mesuré avec des intervalles de confiance**, et confronté à trois modèles : la ruine du joueur, une chaîne agrégée sur les distances, et un calcul exact sur le 2×2 ;
- un **rapport** qui explique l'échec de l'agent aléatoire, chiffres et modèles à l'appui, et qui en tire les conséquences pour la phase 5.

**Terminé quand** (cadrage) : un agent aléatoire tourne dans l'environnement et je comprends pourquoi il n'y arrive pas. Ici, « comprendre » veut dire : **savoir prédire son taux de réussite** avant de le mesurer, et expliquer l'écart.

---

## Comment travailler cette phase

1. **Le cours d'abord, avec un crayon.** Sections 1 à 8 en détail, la section 9 en survol. Les exercices théoriques (1, 2, 3, 5, 6, 8, 9, 10, 12, 13, 14) se font sur papier, avant de coder. Les exercices marqués [code] (4, 7, 11) se font dans les étapes C à F.
2. **Prédire, mesurer, puis modéliser l'écart.** Avant chaque expérience, écris ta prédiction (un nombre, avec son incertitude). Mesure, avec un intervalle de confiance. Puis explique l'écart entre les deux : c'est là qu'on apprend. Tout ira dans ton rapport (étape G).
3. **Écrire.** Le rapport n'est pas une formalité. Si tu peux expliquer à quelqu'un, chiffres à l'appui, pourquoi l'agent aléatoire échoue et ce qu'il faudrait changer, tu as compris le cœur des phases 5 et 6.

**Rappel :** c'est de nouveau toi qui codes (`CLAUDE.md`). Si tu bloques, demande-moi un indice : (1) une question ou une piste, (2) l'explication de la notion, (3) un petit exemple hors projet, (4) la solution, seulement si tu la demandes. Pour les questions de cours, je peux aller aussi loin que tu veux dans les preuves.

---

## Décisions de début de phase

Le cadrage (section 9) laisse plusieurs choix pour la phase 4. Tes décisions se notent dans `docs/cadrage.md`, section 9 (étape B).

### 1. L'observation

| | 54 cases | Les cubies (positions + orientations) |
|---|---|---|
| Ce que c'est | les couleurs des 54 cases, un vecteur de 54 entiers de 0 à 5 | 8 coins et 12 arêtes : où est chacun, et dans quel sens |
| Déjà disponible | oui : `cube.state`, mis à plat | non : il faudrait tout écrire |
| Taille | 54 nombres | 40 nombres |
| État complet (Markov) | oui : l'application groupe → couleurs est injective (cours, section 2.4) | oui |

**Je recommande les 54 cases.** Elles sont déjà là et rapides (un coup ≈ 1 µs). C'est aussi l'entrée de DeepCubeA, en *one-hot* 54 × 6 = 324 (cours, section 9.5). Dans Gymnasium : `MultiDiscrete([6] * 54)`. Le *one-hot* sera une préparation **à côté** de l'environnement, en phase 5.

### 2. La récompense

| | $r = -1$ par coup, $\gamma = 1$ | $r = \mathbb 1[s' = e]$, $\gamma < 1$ |
|---|---|---|
| Cadre | plus court chemin (SSP) | actualisé |
| $V^*$ | $-d$ | $\gamma^{d-1}$ |
| Lisibilité du retour | « -7 » = 7 coups | moyenne |
| Lien avec DeepCubeA (coût restant) | direct | indirect |

**Je recommande $r = -1$, $\gamma = 1$.** Les deux choix ont les mêmes politiques optimales (cours, section 7.1 et exercice 9). Le premier rend les valeurs directement interprétables, et permet de comparer une valeur apprise à la distance exacte (2×2, phase 5).

### 3. PyTorch : maintenant ou en phase 5 ?

Le cadrage prévoyait d'ajouter `torch` dès la phase 4. **Je recommande d'attendre le début de la phase 5** :

- la phase 4 ne s'en sert pas ; règle du cadrage : chaque dépendance arrive **au moment où on en a besoin** ;
- `torch` est très lourd (plusieurs centaines de Mo, voire plusieurs Go) ;
- le choix CPU / GPU dépend de ta machine. Sous Windows et macOS, la version de PyPI est la version « CPU » (sur un Mac à puce Apple, elle sait aussi utiliser la puce graphique). Sous Linux, c'est une version pour carte NVIDIA (CUDA), beaucoup plus grosse. Le guide « PyTorch » d'uv explique comment choisir l'index : <https://docs.astral.sh/uv/guides/integration/pytorch/>.

Question à préparer pour la phase 5 : **quel système as-tu, et as-tu une carte graphique NVIDIA ?**

### 4. La limite de coups par épisode

La troncature est un artefact de collecte, pas une propriété de la tâche (cours, section 2.3). Fais-en un paramètre `max_steps` de l'environnement (par défaut 20, par exemple). Rappelle-toi deux choses :

- un épisode tronqué n'est **pas** terminé : `terminated=False, truncated=True` ;
- avec une troncature à $H$ coups, la valeur optimale est $-\min(d, H)$ (cours, section 4.6). Toutes les positions au-delà de $H$ se ressemblent pour un agent qui n'a jamais réussi.

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
- `info` sort de `reset` et de `step` : des informations pour **toi**, jamais pour l'agent. Y mettre le mélange est très pratique pour les tests. Mais un agent qui le lirait ne résoudrait rien : il recopierait l'inverse du mélange. C'est un « oracle », utile pour vérifier l'environnement, interdit pour décider.

C'est ainsi que Gymnasium traduit le `reset(scramble_depth)` du cadrage.

### 7. Un MDP tabulaire en numpy

Pour un petit MDP (le mini-casse-tête : 6 états, 2 actions), tout tient dans des tableaux :

- `P` de forme `(A, S, S)` : `P[a, s, t]` est la probabilité d'aller de `s` à `t` avec l'action `a` (pour un MDP déterministe, une seule case vaut 1 par ligne) ;
- `R` de forme `(S, A)` : la récompense espérée ;
- `terminal` de forme `(S,)` : des booléens.

Les opérations du cours s'écrivent alors en une ligne chacune (exemple hors projet, sur un MDP aléatoire) :

```python
import numpy as np

S, A, gamma = 4, 2, 0.9
rng = np.random.default_rng(0)
P = rng.random((A, S, S))
P /= P.sum(axis=2, keepdims=True)              # chaque ligne somme à 1
R = rng.random((S, A))
V = np.zeros(S)

pi = np.full((S, A), 1 / A)                    # politique uniforme : pi[s, a]
P_pi = np.einsum("sa,ast->st", pi, P)          # P^pi[s, t] = somme sur a de pi(a|s) P(t|s,a)
r_pi = (pi * R).sum(axis=1)                    # r^pi[s]
Q = R + gamma * np.einsum("ast,t->sa", P, V)   # Q(s, a) = r(s, a) + gamma * somme sur t de P(t|s,a) V(t)
V_new = Q.max(axis=1)                          # une application de l'opérateur T

V_pi = np.linalg.solve(np.eye(S) - gamma * P_pi, r_pi)   # évaluation exacte (gamma < 1)
```

`np.einsum` écrit une somme sur des indices exactement comme sur papier : `"sa,ast->st"` veut dire « pour chaque `s` et `t`, somme sur `a` de `pi[s, a] * P[a, s, t]` ».

Avec $\gamma = 1$, on restreint le système aux états **non terminaux** (cours, section 3.2). Si la politique est **impropre** (elle ne termine jamais depuis certains états), la matrice est singulière : `numpy.linalg.LinAlgError: Singular matrix`. Ce n'est pas un bug numérique, c'est la théorie du plus court chemin stochastique qui se manifeste (section 2.2). Ta fonction doit le détecter et lever une erreur qui le dit.

### 8. Mesurer : des intervalles, pas des points

Cours, section 8. En pratique :

- écris toi-même une fonction pure `wilson_interval(successes, n, z=1.96)`, et teste-la sur des valeurs connues (tableau 8.1 du cours : 6 824 succès sur 100 000 donnent [6,67 % ; 6,98 %]) ;
- 0 succès sur $n$ : la borne supérieure à 95 % vaut environ $3/n$ (règle de trois) ;
- taille d'échantillon : $n \approx 4(1-p)/(\delta^2 p)$ pour une précision relative $\delta$ ;
- une ligne de tableau de résultats = estimation, intervalle, $n$, graine ;
- pour comparer deux agents : **les mêmes cubes** (mêmes graines de mélange) pour les deux ;
- la vitesse : `time.perf_counter()` avant et après, puis des pas par seconde.

### 9. Le parcours en largeur, simple puis vectorisé

**Version simple** (le 3×3 jusqu'à la distance 5). On explore « vague par vague », en retenant ce qui a déjà été vu.

- Retenir ce qu'on a vu : un `dict` état → distance. Le test « déjà vu ? » y prend un temps constant.
- Une clé doit être **hashable** (non modifiable). Un tableau numpy ne l'est pas (`TypeError: unhashable type: 'numpy.ndarray'`) : utilise `cube.facelets()` (54 lettres, lisible) ou `cube.state.tobytes()` (plus rapide).

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

**Version vectorisée** (le 2×2, 3,7 millions d'états). Une boucle Python par état serait trop lente : on traite une vague entière à la fois, avec des opérations numpy sur des tableaux.

- **Un état = un entier.** Les 24 cases de coins, chacune de 0 à 5, s'encodent en $\sum_i c_i 6^i$. Comme $6^{24} \approx 4{,}7 \times 10^{18} < 2^{63}$, cela tient dans un `int64`. Attention : pour les 54 cases du 3×3, $6^{54}$ dépasse, et il faut garder des octets.
- **Une vague = un tableau** `(n, 24)`. Ses voisins par un coup : `frontier[:, perm]`, avec la permutation du coup restreinte aux 24 cases (l'indexation avancée de `cube.move`).
- **Dédoublonner, retirer le déjà-vu, ajouter** : `np.unique`, `np.isin`, `np.union1d` (tableaux triés).
- **Retrouver l'indice d'un état** : `np.searchsorted` sur le tableau **trié** des codes.

```python
import numpy as np

w = 6 ** np.arange(4, dtype=np.int64)              # poids pour 4 cases
states = np.array([[0, 1, 2, 3], [3, 2, 1, 0], [0, 1, 2, 3]])
codes = states.astype(np.int64) @ w                # un entier par ligne : [726, 51, 726]
uniq, first = np.unique(codes, return_index=True)  # codes triés sans doublon, et où les trouver
seen = np.array([51])
new = ~np.isin(uniq, seen)                         # ceux qu'on n'a jamais vus
print(states[first[new]])                          # [[0 1 2 3]]
print(np.searchsorted(uniq, codes))                # indice de chaque état dans uniq : [1 0 1]
```

L'itération de valeur du cube, c'est exactement ce parcours (cours, section 4.6).

### 10. Tester du code aléatoire

On ne peut pas tester « le résultat » d'un tirage au hasard. On teste :

- la **reproductibilité** : même graine, même mélange ; graines différentes, mélanges différents ;
- des **propriétés** toujours vraies : l'observation est dans l'espace d'observations, le cube n'est pas résolu après `reset`, l'épisode est tronqué exactement au bout de `max_steps` coups ;
- un **chemin connu** : dans un **test**, tu as le droit de lire le mélange dans `info` et de jouer sa suite inverse (`rubiks.moves.inverse_sequence`). L'épisode doit alors se terminer, au dernier coup exactement, avec le bon retour. C'est l'oracle, utilisé là où il est permis : pour vérifier l'environnement ;
- `check_env(env)`, dans un test.

### 11. Lancer un module : `python -m`

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

- [ ] Lire le cours, sections 1 à 8 ; survoler la section 9.
- [ ] Exercices 1, 2, 3, 5, 6, 8, 9, 10, 12, 13, 14, sur papier. Comparer avec les corrigés. Noter les questions qui restent : on en parle avant de coder.
- [ ] **Tes prédictions**, écrites avant toute mesure, **avec une incertitude** (elles iront dans le rapport) :
  1. l'agent aléatoire sur le 3×3, mélange de **1** coup, 20 coups au maximum. Tu as maintenant de quoi le **calculer** (ruine du joueur, cours section 5.4). Fais-le ;
  2. mêmes questions pour des mélanges de **2** et **3** coups ;
  3. avec **100** coups au lieu de 20 : quel facteur de gain ?
  4. le même agent sur le **2×2** (9 actions ; à distance 1 ou 2, chaque état a 1 coup qui rapproche, 2 qui laissent à la même distance et 6 qui éloignent) : réussite depuis la distance 1 ?
  5. temps et mémoire pour le BFS du 3×3 jusqu'à la distance 5, et pour le 2×2 complet.

### Étape B — Branche `docs/fiche-phase-4`

- [ ] Ajouter cette fiche dans `docs/fiches/` et le cours dans `docs/cours/`. Commit : `docs: ajoute la fiche et le cours de la phase 4`.
- [ ] `docs/cadrage.md`, section 9 : représentation de l'état (« Décidé : 54 cases »), version de PyTorch (« Reportée au début de la phase 5 »), et une nouvelle ligne « Récompense » (« Décidé : -1 par coup, γ = 1 »). Section 6, phase 4 : « `gymnasium` ajouté (`torch` en phase 5) », et ajouter le 2×2 exact aux livrables. Commit : `docs: décisions de début de phase 4`.
- [ ] `CLAUDE.md`, règle 3 : préciser ton niveau, par exemple « Pour le RL et les maths : niveau master (formalisme, preuves). Pour Python, Git et les bibliothèques : progressif. » Commit dans la même PR.
- [ ] `git rm tests/CLAUDE.md` (notions Git). Commit : `docs: supprime le double de CLAUDE.md dans tests/`.
- [ ] Push, PR, merge, rangement.

### Étape C — Branche `feature/tabular-dp` : la boîte à outils tabulaire

- [ ] Ajouter Gymnasium (dépendance **principale** : le paquet `rubiks.rl` en aura besoin pour tourner) :

  ```bash
  uv add gymnasium
  ```

  Commit avec `pyproject.toml` **et** `uv.lock` : `build: ajoute gymnasium aux dépendances`.
- [ ] Créer le sous-paquet `src/rubiks/rl/` (avec son `__init__.py` et une docstring).
- [ ] `src/rubiks/rl/tabular.py` : numpy seulement, sans Gymnasium (notion 7). Une représentation d'un MDP fini (par exemple une `dataclass` avec `P`, `R`, `terminal`, `gamma`), puis :
  - l'évaluation **exacte** d'une politique (système linéaire restreint aux états non terminaux, cours section 3.2), qui lève une erreur claire (`ValueError`) si la politique est impropre ;
  - l'évaluation **itérative**, qui renvoie aussi l'historique des écarts $\lVert V_{k+1} - V_k \rVert_\infty$ ;
  - l'**itération de valeur**, avec le critère d'arrêt de la section 4.4 (et un arrêt exact quand plus rien ne change, pour $\gamma = 1$) ;
  - l'**itération de politique** ;
  - la **politique gloutonne** associée à une valeur ;
  - pour une chaîne absorbante : la **matrice fondamentale**, et la probabilité d'absorption en au plus $T$ pas.
- [ ] `src/rubiks/rl/mini_puzzle.py` : le mini-casse-tête (cours, section 2.5). Une fonction qui construit son MDP tabulaire, et une classe `MiniPuzzleEnv(gym.Env)` (observation `Discrete(6)`, action `Discrete(2)`, -1 par coup, terminé sur ABC, tronqué après `max_steps`, départ imposable par `options={"start": "CBA"}`).
- [ ] Tests (`tests/test_tabular.py`, `tests/test_mini_puzzle.py`) :
  - $V^*$ et $Q^*$ égaux au tableau de la section 3.5 ;
  - $V^{\text{alea}} = -(5, 5, 8, 8, 9)$, par l'évaluation exacte **et** par la matrice fondamentale ;
  - probabilité de résoudre CBA en au plus 20 coups au hasard ≈ 0,925 (exercice 4) ;
  - l'itération de valeur avec $\gamma = 1$ se stabilise à l'itération $D + 1 = 4$, et ses itérés valent $-\min(d, k)$ (section 4.6) ;
  - l'itération de politique, partie de la politique uniforme, converge en 2 itérations ;
  - l'évaluation de « toujours G » avec $\gamma = 1$ lève l'erreur prévue (politique impropre : depuis ACB, elle boucle entre ACB et CAB) ;
  - `check_env` passe ; et les transitions de l'environnement sont celles du MDP tabulaire (pour chaque état et chaque action).
- [ ] **Vitesse de convergence** (dans un test ou un petit script) : évalue la politique uniforme de façon itérative, avec $\gamma = 1$ puis $\gamma = 0{,}9$. Mesure le rapport des erreurs **sur deux itérations**, et compare-le à $\gamma^2$ (la borne de contraction) et à $\rho(\gamma Q)^2$ (le rayon spectral, `np.linalg.eigvals`). Lequel décrit la réalité ? Pourquoi mesurer sur deux itérations ?
- [ ] Commits, push, PR, merge, rangement.

### Étape D — Branche `feature/rubiks-env` : l'environnement du cube

Dans `src/rubiks/rl/env.py`, une classe `RubiksEnv(gym.Env)`, sur le modèle du couloir et du mini-casse-tête :

- [ ] `__init__(self, scramble_depth=3, max_steps=20, render_mode=None)` ; `action_space = Discrete(18)` ; `observation_space = MultiDiscrete([6] * 54)`.
- [ ] `reset(self, *, seed=None, options=None)` :
  - `super().reset(seed=seed)` en premier ;
  - la profondeur vient de `options` (ou de la valeur par défaut) ;
  - un cube neuf, mélangé avec une graine **tirée de `self.np_random`** (notion 4) ;
  - si le mélange redonne le cube résolu (cours, section 5.5), on recommence ;
  - renvoie une **copie** des 54 cases, et un `info` (profondeur, mélange : pour les tests et les mesures, jamais pour l'agent).
- [ ] `step(self, action)` : joue `MOVES[action]`, compte le coup, et renvoie l'observation (copie), -1, `terminated` (résolu), `truncated` (limite atteinte **sans** être résolu), `info`.
- [ ] (Facultatif) `render` en mode `"ansi"` avec `rubiks.render.terminal.to_ansi`.
- [ ] Tests (`tests/test_env.py`), avec la notion 10 :
  - `check_env` passe ;
  - même graine → même observation ; graines différentes → observations différentes ;
  - après `reset`, le cube n'est pas résolu, et l'observation est dans `observation_space` ;
  - modifier l'observation reçue ne change pas l'environnement (notion 5) ;
  - l'action 3 joue bien `R` ;
  - **l'oracle de test** : jouer la suite inverse du mélange termine l'épisode au dernier coup, avec un retour de -(longueur de la suite) ;
  - un épisode sans solution est tronqué **exactement** au coup `max_steps` ;
  - un cube résolu au dernier coup permis est **terminé**, pas tronqué.
- [ ] Dans `tests/test_render.py`, ajouter les modules de `rubiks.rl` à `PURE_MODULES` : l'entraînement ne doit charger ni pygame ni ursina.
- [ ] Commits, push, PR, merge, rangement.

### Étape E — Branche `feature/exact-structure` : la structure exacte du problème

- [ ] `src/rubiks/rl/bfs.py` : les sphères du 3×3 jusqu'à une distance donnée (notion 9, version simple avec un `dict`). Test : 1, 18, 243, 3 240 jusqu'à la distance 3 (pas plus loin dans les tests : ils doivent rester rapides). Lancer jusqu'à 5 à la main, en mesurant temps et mémoire. **Ne pas lancer 6** sans avoir estimé le coût.
- [ ] Avec les distances obtenues, mesurer **toi-même** :
  - la pente (cours, section 5.4) : pour chaque distance de 1 à 4, la moyenne du nombre de voisins à $d-1$, $d$, $d+1$ ;
  - profondeur ≠ distance (section 5.5) : la loi de la distance réelle de 10 000 mélanges de 3, 4 et 5 coups ;
  - (bonus) $d(s^{-1}) = d(s)$ sur des mélanges courts : $s^{-1}$ s'obtient en appliquant au cube neuf la suite inverse du mélange (cours, exercice 13).
- [ ] `src/rubiks/rl/two_by_two.py` : le 2×2, vu comme **les 24 cases de coins** du 3×3, avec les 9 mouvements U, R, F (et variantes), ce qui fixe le coin DBL (cours, section 4.7). Un BFS **vectorisé** (notion 9) qui calcule la distance des 3 674 160 états.
  - Tests rapides : les premières sphères (1, 9, 54, 321).
  - À la main : la distribution complète (tableau du cours, section 4.7), le diamètre 11, le temps.
  - Enregistrer les codes triés et leurs distances dans `models/2x2_distances.npz` (dossier ignoré par Git), avec une fonction qui les recalcule s'ils manquent. Ce sera la vérité terrain de la phase 5.
- [ ] Commits, push, PR, merge, rangement.

### Étape F — Branche `feature/random-agent` : mesurer, puis modéliser

- [ ] `src/rubiks/rl/agents/random_agent.py` : `RandomAgent`, avec `act(observation) -> int` et **son propre générateur** (notion 4).
- [ ] `src/rubiks/rl/stats.py` : `wilson_interval(successes, n, z=1.96)`, testée contre le tableau 8.1 du cours.
- [ ] `src/rubiks/rl/evaluate.py` :
  - jouer **un** épisode avec un agent → résolu ou non, nombre de coups, retour ;
  - jouer **n** épisodes → taux de réussite **avec son intervalle de Wilson**, longueur moyenne des réussites, retour moyen ;
  - un bloc `if __name__ == "__main__":` qui affiche le tableau : profondeur 1 à 6, `max_steps = 20`, puis profondeurs 1 à 3 avec `max_steps = 100`. Lancement : `uv run python -m rubiks.rl.evaluate`.
- [ ] Tests (`tests/test_evaluate.py`), sur le mini-casse-tête : un agent glouton par rapport à $V^*$ (étape C) réussit 100 % des épisodes, avec une longueur moyenne égale à la distance moyenne des départs.
- [ ] **Mesurer** (assez d'épisodes pour avoir au moins une dizaine de succès par case : notion 8), et **stratifier par distance réelle** jusqu'à 5 grâce à l'étape E. Mesurer aussi la vitesse de l'environnement (pas par seconde).
- [ ] **Modéliser** et comparer aux mesures :
  1. la **ruine du joueur** pour la distance 1 (cours, section 5.4, exercice 6) ;
  2. la **chaîne agrégée** sur les distances (exercice 7) pour les distances 1 à 3, puis le **mélange** sur la distance réelle pour les mélanges de 3 coups ;
  3. **le 2×2 exact** : avec la table des voisins (l'indice de chacun des 9 voisins de chaque état, par `np.searchsorted`), calcule la probabilité **exacte** de résoudre en au plus 20 coups au hasard depuis chaque état. Il suffit de 20 itérations vectorisées de $u \leftarrow$ moyenne de $u$ sur les voisins, avec $u = 1$ sur l'état résolu. Moyenne par distance. Compare avec la ruine du joueur pour 9 actions, et avec une simulation.
- [ ] Commits, push, PR, merge, rangement.

### Étape G — Le rapport

- [ ] Créer `docs/rapports/phase-4-agent-aleatoire.md` :

  ```markdown
  # Rapport — Phase 4 : pourquoi l'agent aléatoire échoue

  ## 1. Prédictions (écrites avant de mesurer, avec leur incertitude)
  ## 2. Protocole (environnement, max_steps, nombre d'épisodes, graines, commit, commande)
  ## 3. Mesures (tableaux avec intervalles de Wilson, stratifiés par distance réelle)
  ## 4. Modèles et écarts (ruine du joueur, chaîne agrégée, mélange, 2×2 exact)
  ## 5. Pourquoi ça échoue (au moins quatre raisons, chacune chiffrée)
  ## 6. Conséquences pour la phase 5 (loi initiale, curriculum, rôle du 2×2)
  ```

- [ ] Section 4 : pour chaque écart entre modèle et mesure, une explication testable (agrégeabilité, tirage non uniforme des états par le générateur de mélanges, horizon fini…).
- [ ] Section 6 : quelle loi initiale $\rho_0$ pour commencer à apprendre, et pourquoi ? Quelles mesures de la phase 5 seront possibles sur le 2×2 et pas sur le 3×3 ?
- [ ] Me demander une relecture. Commit : `docs: rapport de la phase 4 sur l'agent aléatoire`.

### Étape H — Clore la phase (branche `docs/cloture-phase-4`)

- [ ] `uv run ruff check .`, `uv run ruff format .`, `uv run pytest`.
- [ ] Relire `src/rubiks/rl/` : docstrings, annotations de type, aucun nombre magique.
- [ ] `README.md` : avancement, et la commande `uv run python -m rubiks.rl.evaluate`.
- [ ] `docs/cadrage.md` : annexe B (phase 4 « Fait », date) et « Phase 4 terminée » dans la section 6. `CLAUDE.md` : phase en cours = phase 5, et `src/rubiks/rl/` dans l'architecture.
- [ ] (Optionnel) `uv version --bump minor` (1.0.0 → 1.1.0), et un tag `v1.1.0` après le merge.
- [ ] Commit, push, PR, merge, rangement.
- [ ] Me demander la fiche de la phase 5 et le chapitre 2 du cours.

---

## Comment vérifier que c'est bon

- [ ] `uv run pytest` : tout est vert, et rapide (les calculs longs, comme le 2×2 complet, sont hors des tests ou marqués à part).
- [ ] `check_env` passe pour `MiniPuzzleEnv` et `RubiksEnv`.
- [ ] `uv run ruff check .`, `uv run ruff format --check .` et la CI sont verts.
- [ ] `import rubiks.rl.env` ne charge ni pygame ni ursina.
- [ ] `uv run python -m rubiks.rl.evaluate` est **reproductible** : deux lancements, mêmes chiffres.
- [ ] Mes prédictions, mes mesures et mes modèles sont dans le rapport, avec leurs intervalles.
- [ ] Je sais, sans notes :
  - démontrer que $T$ est une contraction pour $\gamma < 1$, et dire pourquoi le cas $\gamma = 1$ demande le cadre SSP (politiques propres) ;
  - démontrer $T^k 0 = -\min(d, k)$ pour le cube, et en déduire le lien entre itération de valeur, BFS et nombre de Dieu ;
  - expliquer pourquoi la vitesse observée de l'évaluation itérative est $\rho(\gamma Q)$ et non $\gamma$ ;
  - retrouver le temps de retour $\lvert \mathcal G \rvert$ (Kac) et la probabilité d'environ 6,7 % (ruine du joueur) ;
  - écrire la cible de *bootstrap* correcte après un épisode terminé et après un épisode tronqué ;
  - énoncer le théorème du *shaping* par potentiel, et dire pourquoi « le nombre de cases bien placées » est une mauvaise récompense ;
  - justifier un nombre d'épisodes avec un intervalle de Wilson ou la règle de trois ;
  - dire quel levier rend le cube apprenable malgré l'exploration exponentielle (le choix de $\rho_0$).

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
| de temps en temps, `reset` donne un cube déjà résolu | un mélange comme `R L R' L'` s'annule (cours, section 5.5) | recommencer le mélange tant que le cube est résolu |
| un épisode résolu au dernier coup est marqué « tronqué » | `truncated` calculé sans regarder `terminated` | tronqué = limite atteinte **et pas** résolu |
| `LinAlgError: Singular matrix` en évaluant une politique avec $\gamma = 1$ | politique **impropre** : depuis certains états, elle ne termine jamais | c'est la théorie du SSP : lever une erreur explicite, ou évaluer avec $\gamma < 1$ |
| l'itération de valeur « ne s'arrête pas » avec $\gamma = 1$ | critère d'arrêt de la section 4.4 (il divise par $1 - \gamma$) | pour $\gamma = 1$ : s'arrêter quand $V_{k+1} = V_k$ exactement |
| l'erreur de l'évaluation itérative oscille d'une itération à l'autre | valeurs propres de signes opposés ($\pm\sqrt3/2$ sur l'hexagone) | mesurer le taux sur deux itérations |
| codes du BFS faux ou négatifs | encodage des 54 cases du 3×3 en int64 : $6^{54}$ dépasse $2^{63}$ | int64 seulement pour les 24 cases du 2×2 ; `tobytes()` pour le 3×3 |
| `np.searchsorted` renvoie des indices absurdes | le tableau des codes n'est pas trié | trier une fois (`np.argsort`), et réordonner les distances avec le même ordre |
| `MemoryError` ou ordinateur qui rame | BFS du 3×3 au-delà de 5, ou table des voisins du 2×2 en int64 (265 Mo) | s'arrêter à 5 ; indices en `int32` (132 Mo) |
| « 0 % de réussite » à la profondeur 4 | trop peu d'épisodes pour un événement rare | règle de trois, plus d'épisodes (notion 8) |
| les tests sont parfois rouges, parfois verts | un test dépend du hasard sans graine | graines partout ; tester des propriétés (notion 10) |
| `PytestUnknownMarkWarning` | un marqueur `@pytest.mark.slow` non déclaré | le déclarer dans `pyproject.toml`, section `[tool.pytest.ini_options]`, clé `markers` |
| `TypeError: unhashable type: 'numpy.ndarray'` | un tableau numpy comme clé de `dict` ou élément de `set` | `cube.facelets()` ou `state.tobytes()` (notion 9) |
| la CI est rouge alors que tout passe en local | `uv.lock` pas commité avec `pyproject.toml` | `uv lock --check`, puis commiter les deux ensemble |

---

## Pour aller plus loin (optionnel)

- **Un agent qui cherche.** Un agent « à $k$ coups d'avance » essaie toutes les suites de $k$ coups sur une copie du cube (18, puis 324, puis 5 832 suites), et joue la première d'une suite qui résout. Mesure sa réussite par distance : c'est un BFS borné, la forme la plus simple de **planification avec le modèle** (cours, section 9.5).
- **La programmation linéaire.** Avec `uv add --dev scipy`, résous le mini-casse-tête par `scipy.optimize.linprog` (cours, section 4.5), puis le problème dual. Interprète les variables duales comme des mesures d'occupation.
- **Les symétries.** Implémente les 24 rotations du cube sur l'état (une rotation `x`, `y` ou `z`, plus un renommage des couleurs pour remettre les centres à leur place). Vérifie que la distance est invariante sur les sphères connues. Combien de classes d'états à distance 2 reste-t-il ?
- **Kac, mesuré.** Sur le mini-casse-tête, puis sur le 2×2 avec la table des voisins : temps moyen de retour à l'état résolu. Sur le 2×2, Kac prédit 3 674 160. Combien d'épisodes faut-il pour l'estimer à 10 % près ? (La loi du temps de retour est proche d'une géométrique.)
- **Un casse-tête à 4 jetons** ($S_4$, 3 transpositions adjacentes, 24 états) : ta boîte à outils tabulaire marche-t-elle sans rien changer ? Quel diamètre ?
- **Enregistrer l'environnement** : `gymnasium.register(id="rubiks/RubiksCube-v0", entry_point="rubiks.rl.env:RubiksEnv")`, puis `gymnasium.make("rubiks/RubiksCube-v0", scramble_depth=2)`. `make` ajoute des vérifications, et l'avertissement « no spec » de `check_env` disparaît.
- **La troncature par un *wrapper*** : `gymnasium.wrappers.TimeLimit`. Compare avec ta troncature faite à la main.
- **Des graphiques** : `uv add --dev matplotlib`. Réussite en fonction de la distance (échelle logarithmique, barres d'erreur), et loi des distances du 2×2.
- **Lectures** : Sutton et Barto, chapitres 3 et 4 ; Puterman, chapitre 6 (critères d'arrêt, itération de politique) ; Bertsekas et Tsitsiklis (1991) pour le SSP ; Levin, Peres et Wilmer pour les marches aléatoires sur les groupes.

---

## Pour vérifier tes mesures (à lire APRÈS les étapes E et F)

Mesures faites avec le code du dépôt (mélanges sans deux coups de suite sur la même face, relancés s'ils redonnent le cube résolu). Les tiennes peuvent varier selon tes graines et tes choix, mais elles doivent être compatibles avec ces valeurs, compte tenu des intervalles.

**Agent aléatoire, 3×3, `max_steps = 20`** (100 000 épisodes par profondeur) :

| Profondeur du mélange | Réussite | Wilson 95 % |
|---|---|---|
| 1 | 6,82 % | [6,67 ; 6,98] |
| 2 | 0,605 % | [0,56 ; 0,66] |
| 3 | 0,165 % | |
| 4 | 0,051 % | |
| 5 | 0,020 % | |
| 6 | 0,007 % (7 sur 100 000) | [0,0034 ; 0,0145] |

**Avec `max_steps = 100`** (20 000 épisodes) : environ 6,7 %, 0,48 % et 0,14 % pour les profondeurs 1 à 3. **Pas mieux** : la marche part vers les distances 17-18 et ne revient pas (cours, sections 5.2 et 5.4).

**Les modèles :**

| | Distance 1 | Distance 2 | Distance 3 | Mélanges de 3 coups |
|---|---|---|---|---|
| ruine du joueur | 6,72 % | | | |
| chaîne agrégée (20 coups) | 6,73 % | 0,51 % | 0,038 % | 0,14 % (mélange sur la distance réelle) |
| mesure | 6,82 % | 0,605 % (profondeur 2 = distance 2) | | 0,165 % |

À la distance 1, le modèle est exact aux fluctuations près : toutes les sphères de rayon 1 ont la même pente (1, 2, 15). Au-delà, il sous-estime, pour deux raisons. L'agrégation n'est pas exacte, et le générateur de mélanges favorise les états qui ont plusieurs coups « rapprochants » (`R L` et `L R` donnent le même état). Aux profondeurs 3 et plus, la plupart des réussites viennent de mélanges « effondrés » : 96,0 % des mélanges de 3 coups sont à distance 3, 2,7 % à distance 2 et 1,3 % à distance 1.

**Le 2×2 exact** (probabilité de résoudre en au plus 20 coups au hasard, moyenne par distance, calculée sur les 3 674 160 états) :

| Distance | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| réussite | 16,69 % | 2,81 % | 0,49 % | 0,09 % | 0,017 % |

Pente du 2×2 : exactement 1, 2 et 6 voisins (sur 9) aux distances 1 et 2. La ruine du joueur donne alors $a = 1/6$ et $h = \frac{1/7}{1 - \frac{6}{7} \cdot \frac{1}{6}} = \frac{1}{6} \approx 16{,}67\ \%$, presque exactement la valeur calculée.

**Le mini-casse-tête** : $V^{\text{alea}} = -(5, 5, 8, 8, 9)$ ; 92,5 % de réussite en au plus 20 coups depuis CBA ; l'itération de politique converge en 2 itérations depuis la politique uniforme. Taux de convergence de l'évaluation itérative, mesuré sur deux itérations : 0,75 pour $\gamma = 1$ et 0,6075 pour $\gamma = 0{,}9$, soit exactement $\rho(\gamma Q)^2$ avec $\rho(Q) = \sqrt 3 / 2$. C'est mieux que la borne $\gamma^2$ (1 et 0,81).

**Vitesses et tailles** : environ 100 000 pas par seconde pour l'environnement, contre environ 1 million de coups par seconde pour `cube.move` seul. BFS du 3×3 avec des objets `Cube` et `facelets()` : distance 5 en moins d'une minute et environ 500 Mo (6 : une dizaine de minutes et plusieurs Go, à ne pas lancer). BFS vectorisé du 2×2 : environ 20 s, 29 Mo pour les codes ; table des voisins : 132 Mo en int32.
