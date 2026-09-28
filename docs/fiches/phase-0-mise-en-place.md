# Fiche — Phase 0 : Mise en place

> **Emplacement dans le repo :** `docs/fiches/phase-0-mise-en-place.md`
> **Durée indicative :** 2 à 4 h, lecture du cours `uv` comprise.
> **Documents liés :** `docs/cadrage.md` (section 6, phase 0) et `docs/cours/uv.md`.

## Objectif

À la fin de cette phase, j'ai :

- un repo `rubiks-rl` sur GitHub, avec un historique de commits clairs ;
- un projet Python géré par `uv`, que n'importe qui peut réinstaller à l'identique ;
- les outils de développement (`pytest`, `ruff`) installés, configurés et qui fonctionnent ;
- le cycle Git de base dans les doigts : `status` → `add` → `commit` → `push`.

On ne code **pas encore** le cube. On prépare l'atelier avant de construire.

---

## Notions Python à connaître

### 1. Environnement virtuel et `uv`

Un environnement virtuel (`.venv/`) est une « boîte » qui contient le Python et les paquets d'**un seul** projet. `uv` crée et remplit cette boîte pour toi.

Tout est expliqué dans `docs/cours/uv.md`. **Lis les sections 1 à 10 avant de commencer les tâches**, puis fais les exercices de la section 16.

Les quatre éléments à retenir :

| Élément | Analogie | Dans Git ? |
|---|---|---|
| `pyproject.toml` | la liste de courses | oui |
| `uv.lock` | le ticket de caisse | oui |
| `.python-version` | l'étiquette « Python 3.12 » | oui |
| `.venv/` | le frigo | **non** |

### 2. Module, paquet et `import`

- Un **module** est un fichier `.py`. Exemple : `cube.py` est le module `cube`.
- Un **paquet** est un dossier qui regroupe des modules et qui contient un fichier `__init__.py`. Exemple : `src/rubiks/` est le paquet `rubiks`.
- `import rubiks` demande à Python de trouver et de charger ce paquet.

Mini-exemple (hors projet) :

```python
import math  # module de la bibliothèque standard

print(math.sqrt(16))  # 4.0
```

Dans notre projet, `uv` installe le paquet `rubiks` en mode « éditable » (cours `uv`, section 9). C'est pour ça que `import rubiks` fonctionnera partout, y compris dans les tests.

### 3. Lancer une ligne de Python sans fichier : `python -c`

```bash
uv run python -c "print('bonjour')"
```

`-c` veut dire « exécute ce code ». Pratique pour une vérification rapide, comme `import rubiks`.

### 4. Un test avec `pytest`

Un **test** est une fonction dont le nom commence par `test_`, dans un fichier dont le nom commence par `test_`. Elle vérifie quelque chose avec `assert`. Si l'`assert` est faux ou si le code plante, le test échoue.

Mini-exemple (hors projet) :

```python
# fichier : test_calcul.py
def test_addition():
    assert 1 + 1 == 2
```

`pytest` trouve tout seul les fichiers et les fonctions `test_…`, les lance, et affiche un résumé. Pour l'instant, c'est tout ce qu'il faut savoir.

### 5. Linter et formateur : `ruff`

- **`ruff check .`** (le linter) cherche les erreurs probables : un import inutilisé, une variable jamais utilisée, un nom mal écrit…
- **`ruff format .`** (le formateur) remet en forme le code : espaces, indentation, guillemets. Comme ça, on ne discute jamais de style.

---

## Notions Git de l'étape

### Les 3 zones (le plus important de la phase)

```
 dossier de travail  ──git add──►  zone de préparation  ──git commit──►  historique local  ──git push──►  GitHub
 (mes fichiers)                    (« staging » :                          (les commits)                  (copie en ligne)
                                    ce qui partira dans
                                    le prochain commit)
```

- Je modifie des fichiers : ils sont dans le **dossier de travail**.
- `git add` les place dans la **zone de préparation** : je choisis ce qui fera partie de la prochaine « photo ».
- `git commit` prend la photo et l'ajoute à l'**historique**, sur mon ordinateur uniquement.
- `git push` envoie mes nouveaux commits sur **GitHub**.

### Les commandes de la phase

| Commande | À quoi ça sert |
|---|---|
| `git config --global …` | se présenter à Git (nom, email) une fois par ordinateur |
| `git clone <url>` | copier un repo GitHub sur mon ordinateur |
| `git status` | voir l'état des 3 zones. **À taper tout le temps**, surtout avant `add` et `commit` |
| `git diff` | voir les modifications pas encore préparées |
| `git diff --staged` | voir ce qui est préparé, donc ce qui partira dans le commit |
| `git add <fichier>` | préparer un fichier |
| `git restore --staged <fichier>` | retirer un fichier de la préparation (sans perdre mes modifications) |
| `git commit -m "type: message"` | enregistrer un commit |
| `git log --oneline` | voir l'historique, une ligne par commit |
| `git push` | envoyer mes commits sur GitHub |

### `origin` et `main`

- **`origin`** est le surnom donné automatiquement au repo GitHub quand on fait `git clone`. `git remote -v` affiche son adresse.
- **`main`** est la branche principale. Les branches arrivent en phase 1.

### Exception de la phase 0

Le cadrage dit : « on ne code jamais directement sur `main` ». En phase 0, on fait **exception** : il n'y a encore rien à protéger, et les branches ne sont pas encore au programme. Dès la phase 1, chaque changement passera par une branche et une Pull Request.

### Le fichier `.gitignore`

C'est une liste de fichiers et de dossiers que Git doit **faire semblant de ne pas voir**. Ils n'apparaissent plus dans `git status` et ne peuvent pas être commités par erreur.

---

## Tâches (dans l'ordre)

### Étape A — Préparer l'ordinateur (une seule fois)

- [ ] Vérifier que Git est installé : `git --version`.
  S'il manque, l'installer : <https://git-scm.com/downloads>.
- [ ] Se présenter à Git :

  ```bash
  git config --global user.name "Ton Nom"
  git config --global user.email "ton-email@example.com"
  git config --global init.defaultBranch main
  git config --list          # vérifier
  ```

  Astuce : pour ne pas rendre ton email public, GitHub fournit une adresse du type `12345678+pseudo@users.noreply.github.com` (GitHub → Settings → Emails).
- [ ] (Recommandé) Choisir l'éditeur que Git ouvre quand il a besoin d'un message. Avec VS Code :
  `git config --global core.editor "code --wait"`
- [ ] Configurer l'accès à GitHub. GitHub **n'accepte pas le mot de passe** du compte pour `git push`. Deux solutions :
  - **clé SSH** (recommandé : une seule fois, et on comprend ce qu'on fait) → guide officiel : <https://docs.github.com/fr/authentication/connecting-to-github-with-ssh>. Test : `ssh -T git@github.com` doit répondre avec ton pseudo ;
  - **HTTPS** avec le gestionnaire d'identifiants (inclus dans Git pour Windows) ou GitHub CLI (`gh auth login`).
- [ ] Installer `uv` (cours `uv`, section 4) et vérifier : `uv --version`.

### Étape B — Faire les exercices du cours `uv`

- [ ] Lire les sections 1 à 10 de `docs/cours/uv.md`.
- [ ] Faire les exercices 1 à 7 de la section 16, dans un dossier **en dehors** du futur repo (par exemple `~/sandbox/`).
- [ ] Répondre au quiz sans regarder les réponses.

### Étape C — Créer le repo et le récupérer

- [ ] Sur GitHub : **New repository**, nom `rubiks-rl`, cocher **uniquement** « Add a README file ». Pas de `.gitignore` ni de licence : on les écrira nous-mêmes.
- [ ] Copier l'adresse du repo (bouton **Code** → SSH ou HTTPS selon ton choix de l'étape A), puis :

  ```bash
  git clone <adresse-du-repo>
  cd rubiks-rl
  git status
  git log --oneline
  ```

  **Question :** combien de commits y a-t-il déjà ? Qui les a faits ?

### Étape D — Premier commit : la documentation

- [ ] Créer les dossiers `docs/`, `docs/fiches/` et `docs/cours/`.
- [ ] Y placer les documents du projet : `docs/cadrage.md`, `docs/cours/uv.md`, et cette fiche dans `docs/fiches/phase-0-mise-en-place.md`.
- [ ] Placer `CLAUDE.md` à la **racine** du repo.
- [ ] `git status` : **devine** d'abord ce qui va s'afficher, puis vérifie.
- [ ] Préparer, vérifier, commiter, envoyer :

  ```bash
  git add docs CLAUDE.md
  git status                 # tout est en vert ?
  git commit -m "docs: ajoute le cadrage, le cours uv, la fiche de la phase 0 et CLAUDE.md"
  git push
  ```

- [ ] Rafraîchir la page GitHub : les fichiers y sont.

### Étape E — Le `.gitignore`

- [ ] Créer un fichier `.gitignore` à la racine et y écrire, une ligne par entrée, ce qu'on ne veut **jamais** commiter :

  | Entrée | Pourquoi |
  |---|---|
  | `.venv/` | l'environnement virtuel, reconstructible avec `uv sync` |
  | `__pycache__/` | fichiers compilés que Python crée tout seul |
  | `.pytest_cache/` | cache de pytest |
  | `.ruff_cache/` | cache de ruff |
  | `models/` | les futurs modèles RL entraînés (gros fichiers) |
  | `.DS_Store` | fichier caché que macOS crée partout (utile même sous Windows, si tu changes un jour d'ordinateur) |

  Une ligne qui commence par `#` est un commentaire : tu peux regrouper les entrées par catégorie.
- [ ] Commit : `chore: ajoute le .gitignore` puis `git push`.
  (`chore` = tâche de maintenance, qui ne touche ni au code ni à la doc.)

### Étape F — Initialiser le projet Python

- [ ] Dans le repo :

  ```bash
  uv init --name rubiks --python 3.12
  git status
  ```

  **Devine avant de regarder :** quels fichiers uv a-t-il créés ? A-t-il modifié le `README.md` ?
  (Réponse dans le cours, section 13.)
- [ ] Ouvrir `pyproject.toml` et `src/rubiks/__init__.py`. Pour chaque ligne, être capable de dire à quoi elle sert (cours, sections 5.1 et 9). S'il reste une ligne mystérieuse, demande-moi.
- [ ] Remplacer `"Add your description here"` par une vraie description du projet.
- [ ] Vérifier que le paquet s'importe :

  ```bash
  uv run python -c "import rubiks; print('ok')"
  uv run rubiks
  ```

  **Question :** d'où vient le message affiché par `uv run rubiks` ?
- [ ] `git status` : `.venv/` apparaît-il ? Pourquoi ? Et `uv.lock` ?
- [ ] Commit (tous les fichiers du projet ensemble) :

  ```bash
  git add pyproject.toml uv.lock .python-version src
  git commit -m "build: initialise le projet Python avec uv"
  git push
  ```

### Étape G — Ajouter et configurer les outils de développement

- [ ] Ajouter les outils :

  ```bash
  uv add --dev pytest ruff
  git diff pyproject.toml    # qu'est-ce qui a changé ?
  uv tree                    # d'où viennent tous ces paquets ?
  ```

- [ ] Commit : `pyproject.toml` **et** `uv.lock` ensemble → `build: ajoute pytest et ruff aux outils de développement`.
- [ ] Configurer les outils : ajouter ces sections à la fin de `pyproject.toml` (les éditer à la main est normal ici : ce n'est pas une dépendance, c'est un réglage).

  ```toml
  [tool.pytest.ini_options]
  testpaths = ["tests"]          # pytest cherche les tests uniquement dans tests/

  [tool.ruff.lint]
  select = ["E", "F", "I"]       # E : style, F : erreurs probables, I : ordre des imports
  ```

- [ ] Lancer `uv run pytest`. **Devine :** que va-t-il se passer alors qu'il n'y a encore aucun test ? Lis bien le message.
- [ ] Commit : `build: configure pytest et ruff`.

### Étape H — Premier test

- [ ] Créer le dossier `tests/` et un fichier `tests/test_import.py`.
- [ ] Y écrire **toi-même** un test qui vérifie que le paquet `rubiks` s'importe. Indice : si `import rubiks` échoue, le test échoue tout seul ; il suffit donc d'importer le paquet dans une fonction `test_…`. Pour aller un cran plus loin, vérifie avec `assert` qu'il possède bien une fonction `main` (cherche ce que fait `hasattr`).
- [ ] Vérifier :

  ```bash
  uv run pytest              # 1 passed ?
  uv run ruff check .        # All checks passed! ?
  uv run ruff format --check .
  ```

  Si `ruff format --check` signale un fichier, lance `uv run ruff format .` et regarde ce qui a changé avec `git diff`.
- [ ] Commit : `test: vérifie que le paquet rubiks s'importe`.

### Étape I — Le README

- [ ] Compléter `README.md` avec :
  - une ou deux phrases de présentation du projet ;
  - une section « Installation » : prérequis (Git, uv), puis `git clone`, `uv sync` ;
  - une section « Commandes utiles » : lancer les tests, le linter ;
  - un lien vers `docs/cadrage.md`.
- [ ] Commit : `docs: complète le README`, puis `git push`.

### Étape J — Vérification finale et clôture

- [ ] Faire le test du « nouvel ordinateur » **en dehors** du repo :

  ```bash
  cd ~/sandbox
  git clone <adresse-du-repo> rubiks-rl-test
  cd rubiks-rl-test
  uv sync
  uv run python -c "import rubiks; print('ok')"
  uv run pytest
  ```

  Puis supprimer le dossier `rubiks-rl-test`.
- [ ] Dans `docs/cadrage.md`, annexe B : passer la phase 0 à « Terminé » avec la date.
- [ ] Dans `CLAUDE.md`, section « Phase en cours » : passer à la phase 1.
- [ ] Commit : `docs: clôture la phase 0`, puis `git push`.
- [ ] Me demander une relecture du repo, puis la fiche de la phase 1.

---

## Comment vérifier que c'est bon

- [ ] `git log --oneline` affiche une suite de commits clairs (au moins 3, sans compter celui de GitHub), au format `type: description`.
- [ ] Sur GitHub, on voit : `README.md`, `CLAUDE.md`, `.gitignore`, `.python-version`, `pyproject.toml`, `uv.lock`, `docs/`, `src/rubiks/`, `tests/`.
- [ ] Sur GitHub, on ne voit **pas** : `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`.
- [ ] `uv run pytest` → `1 passed`.
- [ ] `uv run ruff check .` → `All checks passed!`.
- [ ] Le test du clone (étape J) fonctionne du premier coup.
- [ ] Je sais expliquer avec mes mots :
  - les 3 zones de Git et le rôle de `add`, `commit` et `push` ;
  - la différence entre `pyproject.toml` et `uv.lock`, et pourquoi on les commite ensemble ;
  - pourquoi `.venv/` n'est jamais commité ;
  - ce que fait `uv run` avant de lancer une commande.

---

## Pièges fréquents

| Symptôme | Cause | Solution |
|---|---|---|
| `Author identity unknown` au moment du commit | nom et email pas configurés | étape A, `git config --global …` |
| `Password authentication is not supported` au `push` | GitHub refuse le mot de passe du compte | configurer une clé SSH ou le gestionnaire d'identifiants (étape A) |
| `git commit` sans `-m` ouvre un éditeur étrange (souvent Vim) | aucun éditeur configuré | pour sortir de Vim : `Échap`, puis taper `:q!` et `Entrée` (abandon). Ensuite, configurer `core.editor` |
| `.venv/` ou `__pycache__/` apparaissent dans `git status` | `.gitignore` absent, mal placé ou mal écrit | le `.gitignore` doit être à la **racine** du repo ; vérifier l'orthographe |
| un fichier a été commité avant d'être ajouté au `.gitignore` | le `.gitignore` n'agit que sur les fichiers **pas encore suivis** | me demander : on verra `git rm --cached` ensemble |
| `git add .` a préparé des fichiers non voulus | `.` veut dire « tout le dossier » | préférer nommer les fichiers ; en cas d'erreur, `git restore --staged <fichier>` |
| `uv run pytest` affiche `no tests ran` | normal tant qu'aucun test n'existe | c'est l'étape H qui règle ça |
| `Project is already initialized` | un `pyproject.toml` existe déjà | vérifier qu'on n'a pas lancé `uv init` deux fois |
| `uv init` crée un « workspace » dans le sandbox | le dossier d'essai est à l'intérieur du repo | faire les exercices **en dehors** de `rubiks-rl` |
| `LF will be replaced by CRLF` (Windows) | Windows et macOS/Linux ne marquent pas les fins de ligne de la même façon | simple avertissement, sans danger pour l'instant |
| l'éditeur souligne `import rubiks` en rouge | il utilise un autre Python | choisir l'interpréteur de `.venv` (cours `uv`, section 7) |

---

## Pour aller plus loin (optionnel)

- `git log --oneline --graph --all` : l'historique sous forme de graphe (il deviendra intéressant en phase 1, avec les branches).
- `git show <identifiant>` : le détail d'un commit.
- Créer un alias : `git config --global alias.lg "log --oneline --graph --all"`, puis `git lg`.
- `uv lock --check` : vérifier que `uv.lock` est à jour sans rien modifier.
- Ajouter une licence (MIT par exemple) avec le bouton « Add file » de GitHub, puis récupérer ce commit avec `git pull`. Bon premier contact avec `pull`.
- Activer plus de règles `ruff` : `B` (pièges fréquents) et `UP` (syntaxe Python moderne). Lance `uv run ruff check .` pour voir si ça change quelque chose.
