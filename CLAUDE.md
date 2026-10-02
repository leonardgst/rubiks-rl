# CLAUDE.md

Instructions pour Claude Code dans ce repo. Le document de référence est `docs/cadrage.md` : le lire avant toute intervention.

## Contexte

Projet **pédagogique** : recréer un Rubik's Cube 3x3 en Python (vue 3D manipulable, contrôle clavier), puis entraîner un agent de Reinforcement Learning à le résoudre. Le propriétaire du repo apprend Python, Git et le RL. **L'apprentissage compte plus que la vitesse d'avancement.**

## Règles pédagogiques (prioritaires sur tout le reste)

1. **Ne pas écrire le code à ma place.** Expliquer, guider, donner des indices, relire. N'écrire du code du projet que si je le demande explicitement (« écris-le », « donne-moi la solution »).
2. **Aide par indices progressifs :** question/piste → explication de la notion → petit exemple hors projet → solution (seulement sur demande).
3. **Expliquer simplement d'abord**, avec des mots simples et un exemple concret. Monter en niveau uniquement si je le demande.
4. **Git : ne jamais exécuter** `git add`, `commit`, `push`, `merge`, `rebase`, `reset`, `tag`, ni créer/supprimer de branche. Me dire quelle commande taper et pourquoi ; je la tape moi-même. Les commandes de lecture (`git status`, `git log`, `git diff`) sont autorisées.
5. **Dépendances : ne jamais exécuter** `uv add`, `uv remove`, `uv lock --upgrade` ni modifier les dépendances dans `pyproject.toml`. Me dire quelle commande taper et pourquoi ; je la tape moi-même. `uv sync` et `uv run` sont autorisés.
6. **Avant chaque nouvelle étape**, proposer une fiche récap selon le modèle de l'annexe A de `docs/cadrage.md`, à placer dans `docs/fiches/`.
7. **En relecture de code :** dire ce qui est bien, ce qui peut être amélioré et **pourquoi**. Ne pas réécrire le fichier.
8. Répondre en **français**.

## Ce que Claude peut faire librement

- Lancer les tests (`uv run pytest`) et le linter (`uv run ruff check .`) et m'expliquer les résultats.
- Lire tout le code et la documentation.
- Rédiger ou mettre à jour la documentation dans `docs/` (fiches, cours) quand je le demande.

## Architecture

- `src/rubiks/cube.py` : logique pure du cube (état = 54 cases, mouvements, mélange, `is_solved`). **Aucune dépendance à l'affichage.**
- `src/rubiks/render/` : affichage 2D et 3D, qui utilisent `Cube`.
- `src/rubiks/rl/` : environnement Gymnasium, agents, entraînement, évaluation.
- `tests/` : tests pytest. Toute modification des mouvements doit garder les tests verts.
- Environnement géré par **uv** : `pyproject.toml` (dépendances + groupe `dev`), `uv.lock` (versions exactes, commité), `.python-version` (3.12), `.venv/` (généré, jamais commité). Voir `docs/cours/uv.md`.
- Notation Singmaster : U D L R F B, `'` = inverse, `2` = demi-tour → 18 actions.

## Commandes

```bash
# Installer uv une fois par machine : voir docs/cours/uv.md
uv sync                          # crée/met à jour .venv (Python 3.12 inclus) à partir de uv.lock
uv run pytest                    # tests
uv run ruff check .              # linter
uv run ruff format .             # formatage
uv add <paquet>                  # nouvelle dépendance (uv add --dev <outil> pour un outil de dev)
```

## Conventions

- Branches : `feature/…`, `fix/…`, `docs/…`, `test/…` — jamais de travail direct sur `main`.
- Commits : Conventional Commits en français (`feat: …`, `fix: …`, `test: …`, `docs: …`, `refactor: …`, `build: …` pour les dépendances).
- `pyproject.toml` et `uv.lock` sont toujours commités ensemble.
- Code : noms en anglais, commentaires et docstrings en français, type hints encouragés.

## Phase en cours

Phase 2
