git branch# rubiks-rl

Un Rubik's Cube 3x3 recréé en Python, jouable au clavier dans une vue 3D manipulable à la souris, puis résolu par un agent de **reinforcement learning** (apprentissage par renforcement).

C'est un projet d'apprentissage : il sert à pratiquer Python, Git et le reinforcement learning, étape par étape. Le plan complet est décrit dans le [document de cadrage](docs/cadrage.md).

> **Avancement :** phase 2 : On peut lancer une fenêtre pygame, jouer sur un rubiks cube en 2d avec le clavier, et si on devine les mouvements inverses du mélange, on peut réussir le jeu!

## Installation

### Prérequis

- [Git](https://git-scm.com/downloads)
- [uv](https://docs.astral.sh/uv/getting-started/installation/), le gestionnaire de projet Python. Pas besoin d'installer Python à part : uv télécharge lui-même la bonne version (3.12).

### Récupérer le projet

```bash
git clone https://github.com/leonardgst/rubiks-rl.git
cd rubiks-rl
uv sync
```

`uv sync` crée l'environnement virtuel `.venv/` et y installe les versions exactes des dépendances, listées dans `uv.lock`.

Pour vérifier que tout fonctionne :

```bash
uv run python -c "import rubiks; print('ok')"
```

## Commandes utiles

| Commande | À quoi ça sert |
|---|---|
| `uv run pytest` | lancer les tests |
| `uv run ruff check .` | chercher les erreurs probables dans le code (linter) |
| `uv run ruff format .` | remettre le code en forme |
| `uv run rubiks` | lancer le programme |

## Documentation

- [Document de cadrage](docs/cadrage.md) : objectifs, choix techniques, découpage en phases
- [Cours sur uv](docs/cours/uv.md)
- [Fiches récap](docs/fiches/), une par étape
