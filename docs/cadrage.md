# Document de cadrage — Rubik's Cube & Reinforcement Learning

> **Statut :** v1.1 — document vivant, à mettre à jour à la fin de chaque phase.
> **Historique :** v1.1 (28/09/2026) — `uv` remplace `venv` + `pip` dès la phase 0.
> **Emplacement dans le repo :** `docs/cadrage.md`

---

## 1. En une phrase

Recréer un Rubik's Cube 3x3 jouable en Python (vue 3D manipulable, contrôle au clavier), puis entraîner un agent de **Reinforcement Learning** (RL) qui apprend à le résoudre, d'abord simplement, puis avec le moins de mouvements possible.

## 2. Pourquoi ce projet ?

C'est un projet **formateur** avant tout. Le cube est le prétexte ; l'objectif réel est d'apprendre :

| Domaine | Ce que je veux savoir faire à la fin |
|---|---|
| **Python** | Structurer un vrai projet (modules, classes, tests), gérer son environnement et ses dépendances avec `uv`, utiliser numpy, écrire du code lisible |
| **Git / GitHub** | Faire mes commits et push à la main, comprendre et utiliser les branches, les merges, les Pull Requests, les tags |
| **3D / interface** | Afficher un objet 3D, gérer caméra, clavier, souris et animations |
| **Reinforcement Learning** | Comprendre les bases (agent, état, action, récompense), implémenter un algorithme de A à Z avec PyTorch |

### Principes pédagogiques (non négociables)

1. **C'est moi qui code.** Claude explique, guide, donne des indices et relit — il n'écrit pas le code à ma place, sauf si je le demande explicitement.
2. **Du plus simple au plus complexe.** Chaque notion est d'abord expliquée avec des mots simples et un exemple concret. On monte en niveau ensuite, à ma demande.
3. **Une fiche récap avant chaque étape** (modèle en annexe A).
4. **Git fait partie de l'apprentissage** : je fais tous mes `add`, `commit`, `push`, `merge` moi-même.
5. **Pour la partie RL**, un vrai cours d'abord, puis implémentation guidée pas à pas.

## 3. Périmètre

**Dans le périmètre**
- Modèle logique complet du cube 3x3 (état, 18 mouvements, mélange, détection « résolu »).
- Affichage 2D simple (patron déplié) pour valider la logique.
- Vue 3D manipulable à la souris, faces tournées au clavier, avec animation.
- Environnement RL compatible Gymnasium.
- Un ou plusieurs agents RL capables de résoudre le cube, du plus simple au plus performant.
- Comparaison des solutions (nombre de coups, temps de calcul, taux de réussite).

**Hors périmètre (au moins au départ)**
- Cubes 2x2, 4x4 et plus (possible en bonus plus tard).
- Reconnaissance d'un vrai cube par webcam.
- Application web ou mobile.
- Coder les algorithmes humains « à la main » comme objectif principal (possible en bonus pour comparer).

## 4. Choix techniques proposés

Chaque choix est justifié simplement. Ils peuvent être rediscutés au début de la phase concernée.

| Sujet | Choix proposé | Pourquoi |
|---|---|---|
| Langage | Python 3.12 | Version mûre et bien supportée par les bibliothèques du projet ; installée et épinglée par `uv` (fichier `.python-version`) |
| Environnement et dépendances | `uv` | Un seul outil, très rapide, pour installer Python, créer l'environnement virtuel (`.venv`), ajouter les dépendances et les verrouiller (`uv.lock`) : le projet se réinstalle à l'identique sur n'importe quelle machine. Cours : `docs/cours/uv.md` |
| Calcul | `numpy` | Manipuler le cube comme un tableau, rapide et indispensable pour le RL |
| Tests | `pytest` | Vérifier automatiquement que les mouvements sont corrects |
| Qualité du code | `ruff` | Un seul outil pour le style et les erreurs courantes |
| Affichage 2D | Terminal (couleurs) ou `pygame` | Voir le cube vite, sans la complexité de la 3D |
| Affichage 3D | **À décider en phase 3** : `ursina` (simple, souris/clavier intégrés) ou `pygame` + `PyOpenGL` (plus formateur, plus dur) | Voir section 9 |
| RL | `PyTorch` + `gymnasium` | Standards du domaine, très bien documentés |
| Solveur de référence | `kociemba` (bibliothèque) | Point de comparaison : un solveur classique qui trouve ~20 coups |

**Dépendances du projet vs outils de développement.** Les bibliothèques dont le code a besoin pour tourner (`numpy`, `pygame`, `torch`…) vont dans les dépendances principales : `uv add numpy`. Les outils qui servent seulement à développer (`pytest`, `ruff`) vont dans le groupe `dev` : `uv add --dev pytest ruff`. Chaque dépendance est ajoutée **au moment où on en a besoin**, pas toutes dès le début.

### Notation du cube (Singmaster)

On utilise la notation standard, qui servira partout (clavier, code, RL) :

- **U** (haut), **D** (bas), **L** (gauche), **R** (droite), **F** (devant), **B** (derrière)
- `R` = quart de tour horaire de la face droite, `R'` = anti-horaire, `R2` = demi-tour
- → **18 mouvements possibles** (6 faces × 3 variantes) : ce seront les **actions** de l'agent RL.

### Idée clé d'architecture : séparer la logique de l'affichage

Le cube « logique » (un tableau de 54 cases colorées) ne sait rien de l'affichage. L'affichage 2D, la vue 3D **et** l'agent RL utilisent tous le même objet `Cube`. Conséquence : l'agent RL peut s'entraîner des millions de fois sans rien afficher, donc très vite.

```
            ┌──────────────┐
            │  Cube        │  ← logique pure (état + mouvements)
            │  (cube.py)   │
            └──────┬───────┘
      ┌────────────┼─────────────┐
      ▼            ▼             ▼
 Affichage 2D   Vue 3D      Environnement RL
                (clavier,   (gymnasium)
                 souris)        │
                                ▼
                            Agents RL
```

## 5. Arborescence cible du repo

Elle se construira petit à petit, phase par phase.

```
rubiks-rl/
├── README.md               # présentation du projet
├── CLAUDE.md               # instructions pour Claude Code
├── pyproject.toml          # description du projet, dépendances, config (pytest, ruff)
├── uv.lock                 # versions exactes des dépendances (généré par uv, commité)
├── .python-version         # version de Python du projet (3.12)
├── .gitignore
├── .venv/                  # environnement virtuel (généré par uv, ignoré par git)
├── docs/
│   ├── cadrage.md          # ce document
│   ├── fiches/             # fiches récap, une par étape
│   └── cours/              # cours (uv, RL…)
├── src/
│   └── rubiks/
│       ├── __init__.py     # créé par `uv init`
│       ├── cube.py         # classe Cube : état, mouvements, is_solved
│       ├── moves.py        # définition des 18 mouvements
│       ├── scramble.py     # mélanges aléatoires
│       ├── render/
│       │   ├── view2d.py   # patron déplié
│       │   └── view3d.py   # vue 3D manipulable
│       └── rl/
│           ├── env.py      # environnement Gymnasium
│           ├── agents/     # un fichier par algorithme
│           ├── train.py    # entraînement
│           └── evaluate.py # mesures de performance
├── tests/                  # tests pytest
└── models/                 # modèles entraînés (ignoré par git)
```

## 6. Découpage en phases

Chaque phase = une branche Git principale (voire plusieurs sous-branches) + une fiche récap + un tag à la fin.

### Phase 0 — Mise en place

- **Objectif :** avoir un repo propre, un environnement Python reproductible, et savoir faire le cycle Git de base.
- **Python / uv :** installer `uv` ; créer le projet avec `uv init` (uv installe Python 3.12 lui-même si besoin) ; ajouter les outils de développement (`uv add --dev pytest ruff`) ; lancer des commandes avec `uv run`. Comprendre les rôles de `pyproject.toml`, `uv.lock`, `.python-version` et `.venv/`. Cours : `docs/cours/uv.md`.
- **Git :** `init` / `clone`, `status`, `add`, `commit`, `push`, `log`. Comprendre les 3 zones : dossier de travail → zone de préparation (staging) → historique.
- **Livrables :** repo GitHub, `README.md`, `.gitignore`, `pyproject.toml`, `uv.lock`, `.python-version`, `src/rubiks/__init__.py`, `CLAUDE.md`, `docs/cadrage.md`, `docs/cours/uv.md`.
- **Terminé quand :** le repo est sur GitHub avec au moins 3 commits clairs, et après un `git clone` dans un autre dossier, `uv sync` puis `uv run python -c "import rubiks"` fonctionnent sans erreur.

**Phase 0 terminée**

### Phase 1 — Le cube logique

- **Objectif :** un cube qui tourne correctement, sans aucun affichage.
- **Python :** classes, méthodes, numpy (ajouté avec `uv add numpy` ; tableaux, `np.rot90`, indexation), `random`, tests `pytest` (lancés avec `uv run pytest`).
- **Git :** première branche `feature/cube-model`, merge dans `main`, première Pull Request sur GitHub.
- **Livrables :** classe `Cube` avec `move("R")`, `apply("R U R' U'")`, `scramble(n)`, `is_solved()`, `copy()`.
- **Tests clés (le cube se vérifie tout seul !) :**
  - un même mouvement fait 4 fois = cube inchangé ;
  - un mouvement suivi de son inverse = cube inchangé ;
  - `R U R' U'` répété 6 fois = cube inchangé ;
  - chaque couleur apparaît toujours exactement 9 fois.
- **Terminé quand :** tous les tests passent. Tag `v0.1.0`.

**Phase 1 terminée - 2026/10/02**

### Phase 2 — Affichage 2D et contrôle clavier

- **Objectif :** jouer au cube dans une fenêtre simple (patron déplié en croix).
- **Python :** boucle de jeu, gestion d'événements clavier, dessin 2D.
- **Git :** plusieurs petites branches, commits fréquents, lire l'historique (`git log --graph`).
- **Livrables :** touches U/D/L/R/F/B (+ Maj pour l'inverse), touche de mélange, touche de réinitialisation, message « Résolu ! ».
- **Terminé quand :** je peux mélanger puis refaire le cube au clavier. Tag `v0.2.0`.

**Phase 2 terminée - 2026/10/02**

### Phase 3 — Vue 3D manipulable

- **Objectif :** le même jeu, mais en 3D.
- **Notions :** coordonnées 3D, les 26 petits cubes (« cubies »), rotation de caméra à la souris, animation d'une face qui tourne.
- **Git :** provoquer volontairement un **conflit de merge** et apprendre à le résoudre.
- **Livrables :** fenêtre 3D, caméra orbitale à la souris, rotations animées au clavier, synchronisation avec le `Cube` logique.
- **Terminé quand :** le jeu 3D est jouable et reste cohérent avec les tests de la phase 1. Tag `v1.0.0` (le jeu est fini !).

### Phase 4 — Cours de RL et environnement

- **Objectif :** comprendre le RL et transformer le cube en « terrain de jeu » pour un agent.
- **Cours (dans `docs/cours/`) :** agent, environnement, état, action, récompense, épisode, politique, fonction de valeur, exploration vs exploitation, équation de Bellman — toujours avec le cube comme exemple.
- **Pourquoi c'est dur :** le cube a environ 43 × 10¹⁸ états possibles, et au hasard on ne tombe quasiment jamais sur l'état résolu → la récompense est **extrêmement rare**.
- **Livrables :** `gymnasium` et `torch` ajoutés au projet avec `uv add` (version CPU ou GPU : voir section 9) ; `RubiksEnv` (gymnasium) avec `reset(scramble_depth)`, `step(action)`, récompense, fin d'épisode.
- **Terminé quand :** un agent aléatoire tourne dans l'environnement et je comprends pourquoi il n'y arrive pas.

### Phase 5 — Premier agent : résoudre des cubes peu mélangés

- **Objectif :** un agent qui résout des cubes mélangés de 1, 2, 3… coups.
- **Idée clé : le curriculum learning** — comme à l'école, on commence par des exercices faciles (1 coup de mélange) et on augmente la difficulté quand l'agent réussit.
- **Algorithmes, dans l'ordre :**
  1. Q-learning tabulaire (un tableau qui retient la valeur de chaque couple état/action) → marche pour 2–4 coups, puis explose en mémoire. On comprend pourquoi.
  2. Deep Q-Network (DQN) : on remplace le tableau par un réseau de neurones.
- **Terminé quand :** l'agent résout de façon fiable des mélanges de ~5–7 coups et je sais expliquer ce qu'il fait.

### Phase 6 — Résolution complète

- **Objectif :** résoudre n'importe quel cube mélangé.
- **Approche envisagée :** inspirée de **DeepCubeA** (Agostinelli et al., 2019), un travail de recherche qui a résolu le cube par apprentissage :
  - on part du cube résolu et on « remonte » : un réseau apprend à estimer *combien de coups il reste* depuis un état donné ;
  - on combine ce réseau avec une **recherche** (A* ou beam search) qui explore les coups les plus prometteurs.
- **À savoir :** le RL « pur » sans recherche résout très rarement un cube complètement mélangé. Combiner apprentissage + recherche est la clé — c'est aussi ce que fait AlphaGo.
- **Terminé quand :** taux de réussite élevé sur des mélanges aléatoires de 100 coups, avec un temps de calcul raisonnable sur mon ordinateur.

### Phase 7 — Résoudre le plus vite possible

- **Objectif :** optimiser et comparer.
- **Deux sens de « vite » à distinguer :**
  - **le moins de coups possible** — référence : le « nombre de Dieu » est 20 (tout cube se résout en 20 coups maximum, démontré en 2010) ;
  - **le moins de temps de calcul possible.**
- **Pistes :** réseau plus grand ou mieux entraîné, réglages de la recherche, comparaison avec le solveur `kociemba` et avec une méthode humaine (couche par couche, ~100 coups ; CFOP, ~55 coups).
- **Livrables :** script `evaluate.py` qui produit un tableau comparatif (taux de réussite, coups moyens, temps moyen).
- **Terminé quand :** j'ai un tableau de résultats et je sais expliquer les compromis.

### Bonus possibles (plus tard)

- Visualiser dans la vue 3D l'agent en train de résoudre le cube.
- Cube 2x2 (beaucoup plus petit, idéal pour tester des idées RL).
- Faire apprendre une méthode humaine étape par étape (sous-objectifs).

## 7. Méthode de travail avec Git

### Règles

- `main` est **toujours stable** : on n'y code jamais directement.
- Une branche par fonctionnalité, nommée selon son type :
  - `feature/...` — nouvelle fonctionnalité (`feature/cube-model`)
  - `fix/...` — correction de bug
  - `docs/...` — documentation
  - `test/...` — ajout de tests
- Merge dans `main` via une **Pull Request sur GitHub**, même en travaillant seul (c'est là que Claude peut relire).
- Petits commits fréquents : un commit = une idée.
- Quand une dépendance change, `pyproject.toml` et `uv.lock` partent **ensemble, dans le même commit**. Le dossier `.venv/` n'est jamais commité.
- Un **tag** à la fin de chaque phase (`v0.1.0`, `v0.2.0`, …).

### Messages de commit

Format « Conventional Commits » : `type: description courte`, en français.

```
feat: ajoute le mouvement R et son inverse
fix: corrige l'orientation de la face B
test: vérifie que R fait 4 fois revient à l'état initial
docs: ajoute la fiche de la phase 1
refactor: déplace les mouvements dans moves.py
build: ajoute numpy aux dépendances
```

### Cycle type d'une fonctionnalité

```bash
git switch main
git pull                              # récupérer la dernière version
uv sync                               # mettre .venv à jour si uv.lock a changé
git switch -c feature/ma-fonctionnalite
# ... je code ...
uv run pytest                         # les tests passent ?
uv run ruff check .                   # le code est propre ?
git status                            # qu'est-ce qui a changé ?
git add fichier.py
git commit -m "feat: ..."
git push -u origin feature/ma-fonctionnalite
# → ouvrir une Pull Request sur GitHub, relire, merger
git switch main
git pull
git branch -d feature/ma-fonctionnalite
```

Les notions Git sont introduites progressivement : les bases en phase 0, les branches en phase 1, les conflits en phase 3, et des outils plus avancés (`rebase`, `stash`, `cherry-pick`) quand l'occasion se présente.

## 8. Comment je travaille avec Claude

- **Avant chaque étape :** Claude me fournit une fiche récap (modèle en annexe A), enregistrée dans `docs/fiches/`.
- **Pendant l'étape :** je code. Si je bloque, je demande de l'aide. Claude répond par **indices progressifs** :
  1. une question ou une piste ;
  2. une explication de la notion ;
  3. un petit exemple *hors du projet* ;
  4. la solution, seulement si je la demande.
- **Après l'étape :** Claude relit mon code (via la Pull Request ou le repo), explique ce qui est bien, ce qui peut être amélioré, et pourquoi.
- **Niveau des explications :** simple par défaut. Je peux demander « plus simple » ou « plus technique » à tout moment.
- **Git :** Claude me dit quelle commande taper et pourquoi, mais c'est moi qui les exécute.
- **Claude Code :** si je l'utilise, il suit les mêmes règles, décrites dans `CLAUDE.md`.

## 9. Décisions à prendre plus tard

| Décision | Quand | Options |
|---|---|---|
| Bibliothèque 3D | Début phase 3 | `ursina` (simple) ou `pygame` + `PyOpenGL` (formateur mais exigeant) |
| Affichage 2D - Décidé: `pygame` | 2026-10-02 | Terminal coloré ou fenêtre `pygame` |
| Représentation de l'état pour le RL | Phase 4 | 54 cases colorées (simple) ou positions/orientations des cubies (compact) |
| Version de PyTorch (CPU ou GPU) | Début phase 4 | Version par défaut de PyPI, ou index PyTorch dédié (CPU seul, CUDA…) déclaré dans `pyproject.toml` — voir `docs/cours/uv.md` |
| Métrique de coups | Phase 7 | Demi-tour compte pour 1 coup (HTM) ou 2 (QTM) |
| Matériel d'entraînement | Phase 6 | CPU local, GPU local, ou Google Colab |

## 10. Risques et points d'attention

| Risque | Parade |
|---|---|
| La 3D prend beaucoup plus de temps que prévu | Phase 2 d'abord : le jeu fonctionne en 2D avant de toucher la 3D |
| Un bug dans les mouvements fausse tout le RL | Tests solides en phase 1, relancés à chaque changement |
| Une mise à jour de bibliothèque casse le code | `uv.lock` est commité : les versions ne changent que quand je le décide (`uv lock --upgrade-package …`), et Git permet de revenir en arrière |
| L'entraînement RL est trop long sur mon ordinateur | Curriculum, petits réseaux, tester d'abord sur un cube 2x2, Colab si besoin |
| Vouloir tout faire d'un coup | Une phase à la fois, des objectifs « terminé quand » clairs |
| Perte de motivation sur une phase longue | Petites victoires fréquentes : un commit, un test qui passe, un tag |

## 11. Glossaire

- **Environnement virtuel (`.venv`) :** un dossier qui contient un Python et les paquets d'un seul projet, isolé du reste de l'ordinateur.
- **Dépendance :** une bibliothèque externe dont le projet a besoin (par exemple `numpy`).
- **Lockfile (`uv.lock`) :** la liste exacte des versions installées, pour réinstaller le projet à l'identique partout.
- **Commit :** une photo enregistrée de mon code, avec un message.
- **Branche :** une ligne de travail parallèle, pour tester sans casser `main`.
- **Merge :** fusionner une branche dans une autre.
- **Pull Request (PR) :** une demande de merge sur GitHub, qui permet de relire avant d'intégrer.
- **Cubie :** un des 26 petits cubes visibles qui composent le Rubik's Cube.
- **Agent :** le programme qui apprend et choisit les actions.
- **État :** la configuration actuelle du cube.
- **Action :** un des 18 mouvements.
- **Récompense :** le signal numérique qui dit à l'agent si c'était bien.
- **Épisode :** une partie complète, du mélange jusqu'à la résolution (ou l'abandon).
- **Politique :** la « stratégie » de l'agent — quelle action choisir dans quel état.

---

## Annexe A — Modèle de fiche récap

Chaque fiche est enregistrée dans `docs/fiches/phase-X-titre.md`.

```markdown
# Fiche — Phase X : titre

## Objectif
Ce que j'aurai à la fin, en une ou deux phrases.

## Notions Python à connaître
- Notion 1 — explication simple + mini-exemple
- Notion 2 — ...

## Notions Git de l'étape
- Commande / concept + à quoi ça sert

## Tâches (dans l'ordre)
- [ ] Tâche 1
- [ ] Tâche 2

## Comment vérifier que c'est bon
- Tests à écrire / à faire passer
- Ce que je dois voir à l'écran

## Pièges fréquents
- ...

## Pour aller plus loin (optionnel)
- ...
```

## Annexe B — Suivi d'avancement

| Phase | Statut | Tag | Date de fin |
|---|---|---|---|
| 0 — Mise en place | Fait | — | 30/09/2026 |
| 1 — Cube logique | Fait | v0.1.0 | 02/10/2026 |
| 2 — Affichage 2D | Fait | v0.2.0 | 02/10/2026 |
| 3 — Vue 3D | À faire | v1.0.0 | — |
| 4 — Cours RL + environnement | À faire | — | — |
| 5 — Premier agent | À faire | — | — |
| 6 — Résolution complète | À faire | — | — |
| 7 — Optimisation | À faire | — | — |
