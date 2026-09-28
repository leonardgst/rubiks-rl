# Cours — uv : gérer Python, l'environnement et les dépendances

> **Pour qui :** quelqu'un qui débute en Python et veut comprendre ce qui se passe « sous le capot », pas seulement taper des commandes.
> **Durée :** environ 1 h de lecture + 30 min d'exercices.
> **Vérifié avec :** uv 0.12 (septembre 2026). Les commandes de base changent rarement ; en cas de doute, `uv help <commande>` ou la [documentation officielle](https://docs.astral.sh/uv/).
> **Emplacement dans le repo :** `docs/cours/uv.md`

## Sommaire

1. Le problème : pourquoi on a besoin d'un outil
2. La brique de base : l'environnement virtuel
3. uv en deux mots
4. Installer uv
5. Les 4 éléments d'un projet uv
6. Le mécanisme central : verrouiller, puis synchroniser
7. Les commandes du quotidien
8. Gérer Python lui-même
9. Pourquoi `import rubiks` marche : le projet « empaqueté »
10. uv et Git
11. Outils hors projet : `uvx` et `uv tool`
12. Pour plus tard : PyTorch (phase 4)
13. Application : mettre en place `rubiks-rl` (phase 0)
14. Pièges fréquents
15. Aide-mémoire
16. Exercices et quiz

---

## 1. Le problème : pourquoi on a besoin d'un outil

Python arrive avec sa **bibliothèque standard** : `random`, `math`, `json`… Tout le reste (`numpy`, `pytest`, `pygame`, `torch`) est **externe**. Ce sont des **paquets** qu'il faut télécharger depuis **PyPI** (*Python Package Index*), une sorte de magasin d'applications pour les bibliothèques Python.

Si on installe tous ces paquets au même endroit, pour tout l'ordinateur, on tombe vite sur trois problèmes :

1. **Les conflits.** Le projet A veut `numpy` 1.26, le projet B veut `numpy` 2.3. Un seul emplacement = un seul `numpy`. L'un des deux projets casse.
2. **La reproductibilité.** « Ça marche sur ma machine. » Mais dans six mois, ou sur un autre ordinateur, quelles versions exactes avais-je installées ? Personne ne s'en souvient.
3. **La version de Python.** Le projet a besoin de Python 3.12, l'ordinateur a 3.10… ou rien du tout.

Historiquement, on résolvait ça avec **quatre outils différents** :

| Problème | Outil classique |
|---|---|
| Installer la bonne version de Python | installateur de python.org, `pyenv` |
| Créer une « boîte » isolée par projet | `python -m venv` |
| Installer des paquets dans la boîte | `pip` |
| Noter les versions exactes | `requirements.txt`, `pip-tools`, `poetry`… |

**uv fait les quatre**, avec une seule commande de départ.

---

## 2. La brique de base : l'environnement virtuel

uv ne remplace pas l'idée d'environnement virtuel : il l'**automatise**. Il faut donc d'abord comprendre ce qu'est cette « boîte ».

Un **environnement virtuel** est un simple **dossier**, qu'on appelle par convention `.venv`. Il contient « un Python rien que pour ce projet » et les paquets de ce projet.

```
.venv/
├── pyvenv.cfg                 # carte d'identité : « mon vrai Python est là-bas, version 3.12.x »
├── bin/                       # (Scripts\ sous Windows)
│   ├── python                 # un lien vers le vrai Python
│   ├── activate               # script d'activation (voir plus bas)
│   └── pytest, ruff…          # commandes fournies par les paquets installés
└── lib/python3.12/site-packages/     # (Lib\site-packages\ sous Windows)
    ├── numpy/                 # le code des paquets installés
    └── …
```

**Le « truc » est très simple.** Python n'est pas copié : `bin/python` est juste un lien vers le vrai Python (sous Windows, un petit lanceur). Quand on lance ce `python`-là, il lit `pyvenv.cfg`, comprend qu'il est dans un environnement virtuel, et va chercher les paquets dans **le `site-packages` de la boîte** au lieu du dossier global de l'ordinateur. C'est tout.

Conséquence : chaque projet a son propre `site-packages`, donc ses propres versions. Les conflits disparaissent.

**Et « activer », alors ?** Activer un environnement (`source .venv/bin/activate`) modifie temporairement le `PATH` du terminal, c'est-à-dire la liste des dossiers où le terminal cherche les commandes. Après activation, taper `python` lance `.venv/bin/python` au lieu du Python global. Rien de plus magique. `deactivate` annule.

Avec uv, on n'a presque jamais besoin d'activer : `uv run` fait la même chose, mais **pour une seule commande** (voir section 7).

---

## 3. uv en deux mots

**uv** est un outil unique, écrit en Rust, créé par Astral — la même équipe que `ruff`, que le projet utilise déjà. Il remplace toute la chaîne de la section 1 :

| Avant | À quoi ça sert | Avec uv |
|---|---|---|
| installateur python.org, `pyenv` | installer Python | automatique, ou `uv python install` |
| `python -m venv .venv` | créer la boîte | automatique (`uv sync`, `uv run`) |
| `pip install numpy` | installer un paquet | `uv add numpy` |
| `requirements.txt`, `pip-tools` | noter les versions exactes | `uv.lock`, automatique |
| `source .venv/bin/activate` puis `pytest` | lancer une commande dans la boîte | `uv run pytest` |
| `pipx` | installer des outils pour tout l'ordinateur | `uv tool install`, `uvx` |

### Pourquoi uv est si rapide

1. **Rust et téléchargements en parallèle.** Là où `pip` fait les choses une par une, uv en fait beaucoup en même temps.
2. **Un cache global.** Chaque version de chaque paquet n'est téléchargée **qu'une seule fois pour tout l'ordinateur**. Elle est rangée dans le cache d'uv : `~/.cache/uv` sous macOS/Linux, `%LOCALAPPDATA%\uv\cache` sous Windows. La commande `uv cache dir` affiche l'emplacement exact.
3. **Pas de copie.** Pour « installer » un paquet dans `.venv`, uv ne recopie pas les fichiers. Il crée des liens vers le cache : des clones *copy-on-write* sous macOS/Linux, des liens physiques (*hardlinks*) sous Windows. C'est quasi instantané et presque gratuit en espace disque.

**Conséquence importante :** `.venv` est **jetable**. Le supprimer et le recréer ne prend que quelques secondes. On ne le « répare » jamais : au pire, on le supprime et on relance `uv sync`.

---

## 4. Installer uv

uv s'installe **une fois par ordinateur**, pas dans chaque projet. Pas besoin d'avoir Python installé avant : uv s'en chargera.

**macOS / Linux** (dans un terminal) :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (dans PowerShell) :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Autres possibilités : `brew install uv` (macOS) ou `winget install --id=astral-sh.uv -e` (Windows).

**Vérifier :** ferme et rouvre ton terminal, puis :

```bash
uv --version
```

**Mettre à jour uv plus tard :** `uv self update` si tu as utilisé l'installateur officiel ; sinon, passe par `brew` ou `winget`.

---

## 5. Les 4 éléments d'un projet uv

C'est **le cœur du cours**. Un projet uv repose sur quatre éléments. Une analogie aide à les retenir :

| Élément | Analogie | Rôle |
|---|---|---|
| `pyproject.toml` | la **liste de courses** | ce que je **veux** (en gros) |
| `uv.lock` | le **ticket de caisse** | ce qui a été **acheté**, exactement |
| `.venv/` | le **frigo** | ce qui est **réellement installé** |
| `.python-version` | l'**étiquette** sur le frigo | quelle version de Python utiliser |

### 5.1 `pyproject.toml` — la liste de courses

C'est le fichier **standard** de description d'un projet Python : tous les outils Python savent le lire. Voici à quoi il ressemble pour un petit projet d'exemple `demo-uv` (les numéros de version seront différents chez toi) :

```toml
[project]
name = "demo-uv"                    # nom du projet
version = "0.1.0"                   # version de MON projet
description = "Add your description here"
readme = "README.md"
authors = [                         # rempli à partir de ta configuration Git
    { name = "Ton Nom", email = "toi@example.com" }
]
requires-python = ">=3.12"          # versions de Python acceptées
dependencies = [                    # ce dont le code a besoin pour tourner
    "numpy>=2.5.3",
]

[project.scripts]                   # commandes créées par le projet (voir section 9)
demo-uv = "demo_uv:main"

[dependency-groups]                 # outils qui ne servent qu'à développer
dev = [
    "pytest>=9.1.1",
    "ruff>=0.16.9",
]

[build-system]                      # comment « emballer » le projet (voir section 9)
requires = ["uv_build>=0.12.19,<0.13.0"]
build-backend = "uv_build"
```

À retenir :

- `numpy>=2.5.3` veut dire « **au moins** cette version ». C'est une contrainte **large**, et c'est voulu : on dit ce qu'on accepte, pas exactement ce qu'on installe. Par défaut, `uv add` met la version du jour comme minimum.
- `[project]` est standard. Les sections `[tool.xxx]` (par exemple `[tool.pytest.ini_options]` ou `[tool.ruff]`) servent à configurer les outils. On en ajoutera dans la fiche de la phase 0.
- On peut éditer ce fichier à la main. Mais pour les dépendances, on passe plutôt par `uv add` et `uv remove`, qui font tout le travail autour.

### 5.2 `uv.lock` — le ticket de caisse

`pyproject.toml` dit « numpy, au moins 2.5.3 ». Mais quelle version a **vraiment** été installée ? 2.5.3 ? 2.6.0 ? C'est `uv.lock` qui le dit. Voici un extrait simplifié :

```toml
[[package]]
name = "numpy"
version = "2.5.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/…/numpy-2.5.3.tar.gz", hash = "sha256:…", size = … }
wheels = [
    { url = "https://files.pythonhosted.org/…/numpy-2.5.3-cp312-cp312-macosx_14_0_arm64.whl", hash = "sha256:…", size = … },
    { url = "https://files.pythonhosted.org/…/numpy-2.5.3-cp312-cp312-win_amd64.whl", hash = "sha256:…", size = … },
    # … des dizaines d'autres : un fichier par système et par version de Python
]
```

Ce fichier contient :

- la **version exacte** de **chaque** paquet, y compris les paquets dont tes paquets ont besoin (voir section 6) ;
- l'**empreinte** (`hash`) de chaque fichier téléchargé. C'est une sorte d'empreinte digitale : si le fichier a été modifié, l'empreinte ne correspond plus et uv refuse de l'installer. C'est une garantie de sécurité ;
- les fichiers pour **toutes les plateformes** à la fois (Windows, macOS, Linux). Le même `uv.lock` sert partout : on dit qu'il est **universel**.

Une **wheel** (`.whl`) est un paquet précompilé, prêt à être installé. C'est ce que uv télécharge.

**Règles :** `uv.lock` est **généré par uv**, on ne le modifie **jamais à la main**, et on le **commite** dans Git.

### 5.3 `.python-version` — l'étiquette

Un fichier d'une ligne, par exemple :

```
3.12
```

Il dit à uv quelle version de Python utiliser pour créer `.venv`.

Ne pas confondre avec `requires-python` :

- `requires-python = ">=3.12"` est une **promesse** : « le projet fonctionne avec 3.12 ou plus ». C'est une plage.
- `.python-version` est un **choix** : « ici, on travaille avec 3.12 ». C'est une version précise, qui doit se trouver dans la plage.

### 5.4 `.venv/` — le frigo

C'est l'environnement virtuel de la section 2, **rempli par uv à partir de `uv.lock`**. Chaque ordinateur a le sien. Il est jetable et ne va **jamais** dans Git.

Petit détail astucieux : uv place dans `.venv` un fichier `.gitignore` qui contient seulement `*` (« ignore tout ce dossier »). Git ignore donc `.venv` automatiquement. On ajoute quand même `.venv/` au `.gitignore` du repo, par sécurité et pour que ce soit explicite.

### Récapitulatif

| Élément | Qui l'écrit ? | Dans Git ? |
|---|---|---|
| `pyproject.toml` | moi (souvent via `uv add`) | oui |
| `uv.lock` | uv, jamais à la main | oui |
| `.python-version` | `uv init` ou `uv python pin` | oui |
| `.venv/` | uv | **non** |

---

## 6. Le mécanisme central : verrouiller, puis synchroniser

Toute la logique d'uv tient dans ce schéma :

```
   pyproject.toml              uv.lock                    .venv/
  (ce que je veux)   ──────►  (versions exactes)  ──────►  (paquets installés)
                     « lock »                     « sync »
                    = résoudre                   = installer
```

### 6.1 Verrouiller (*lock*) = résoudre le puzzle

Quand tu ajoutes `pytest`, tu n'ajoutes pas qu'un seul paquet. `pytest` a lui-même besoin d'autres paquets pour fonctionner, par exemple `pluggy` et `iniconfig`. On distingue :

- les **dépendances directes** : celles que **tu** as demandées (`pytest`) ;
- les **dépendances transitives** : celles dont tes dépendances ont besoin (`pluggy`, `iniconfig`…).

Chaque paquet impose ses propres contraintes de version. **Résoudre**, c'est trouver un ensemble de versions qui satisfait **toutes** les contraintes en même temps : ta liste, les contraintes de chaque paquet, et `requires-python`. uv choisit la version la plus récente possible pour chacun. Si c'est impossible (deux paquets exigent des versions incompatibles d'un troisième), uv s'arrête avec un message qui explique le conflit.

Le résultat est écrit dans `uv.lock`.

**Point important :** le lockfile ne bouge pas tout seul. Si une nouvelle version de `numpy` sort demain, ton projet continue d'utiliser la version verrouillée. Mettre à jour est une **décision explicite** :

```bash
uv lock --upgrade-package numpy   # met à jour numpy seulement (dans les limites de pyproject.toml)
uv lock --upgrade                 # met à jour tout ce qui peut l'être
```

C'est exactement ce qu'on veut : le code ne casse pas « tout seul » un matin.

### 6.2 Synchroniser (*sync*) = remplir le frigo

`uv sync` rend `.venv` **identique** à `uv.lock` :

- il crée `.venv` s'il n'existe pas (et télécharge Python si besoin) ;
- il installe ce qui manque et met à jour ce qui a changé ;
- il **retire ce qui n'est pas dans le lockfile**. On dit que la synchronisation est **exacte**.

Par défaut, `uv sync` installe aussi ton propre projet (voir section 9) et le groupe `dev`. `uv sync --no-dev` installe tout sauf les outils de développement.

### 6.3 C'est automatique

En pratique, tu tapes rarement `uv lock` ou `uv sync` toi-même :

- `uv add` et `uv remove` modifient `pyproject.toml`, puis verrouillent, puis synchronisent ;
- `uv run` vérifie **avant chaque commande** que `uv.lock` correspond à `pyproject.toml` et que `.venv` correspond à `uv.lock`, corrige si besoin, puis lance la commande. Nuance : `uv run` ajoute ce qui manque mais ne retire pas les paquets en trop, contrairement à `uv sync`.

Deux options utiles pour **vérifier sans rien modifier** :

```bash
uv lock --check          # uv.lock est-il à jour par rapport à pyproject.toml ?
uv run --locked pytest   # lance pytest, mais échoue si uv.lock n'est pas à jour
```

Elles serviront surtout plus tard, pour les vérifications automatiques sur GitHub.

---

## 7. Les commandes du quotidien

### `uv add` — ajouter une dépendance

Voici ce qui se passe quand tu tapes `uv add numpy` :

1. uv cherche le projet : un `pyproject.toml` dans le dossier courant ou dans un dossier parent.
2. Il demande à PyPI quelles versions de `numpy` existent et choisit la plus récente compatible.
3. Il écrit `"numpy>=…"` dans `dependencies`.
4. Il résout tout et met à jour `uv.lock`.
5. Il synchronise `.venv`.

Pour un outil de développement :

```bash
uv add --dev pytest ruff      # va dans [dependency-groups] dev
```

Pourquoi séparer ? Le jeu n'a pas besoin de `pytest` pour tourner. Si un jour on distribue le projet, les outils de développement ne font pas partie de ce qu'on distribue.

### `uv remove` — retirer une dépendance

```bash
uv remove numpy
uv remove --dev ruff
```

### `uv run` — lancer une commande dans l'environnement

```bash
uv run pytest                 # les tests
uv run ruff check .           # le linter
uv run python                 # une console Python interactive
uv run python mon_script.py   # un script (équivalent : uv run mon_script.py)
```

Ce qui se passe à chaque `uv run` :

1. uv trouve le projet ;
2. il vérifie et met à jour `uv.lock` si besoin ;
3. il vérifie et met à jour `.venv` si besoin ;
4. il lance la commande avec le Python de `.venv`, comme si l'environnement était activé, mais seulement pour cette commande.

Les options d'uv se placent **avant** la commande. Tout ce qui vient après appartient à la commande : dans `uv run pytest -v`, le `-v` est pour pytest.

### `uv sync`, `uv lock`, `uv tree`

```bash
uv sync      # aligner .venv sur uv.lock (après un git clone, un git pull…)
uv lock      # mettre à jour uv.lock sans rien installer
uv tree      # afficher l'arbre des dépendances (directes et transitives)
```

### Et si je préfère activer l'environnement ?

C'est possible, et ça ne pose aucun problème :

```bash
source .venv/bin/activate     # macOS / Linux
.venv\Scripts\activate        # Windows (PowerShell)
```

Ensuite, `python` et `pytest` fonctionnent directement. Seul piège : si les dépendances changent (après un `git pull`, par exemple), pense à lancer `uv sync`. `uv run`, lui, le fait tout seul. Dans les fiches du projet, on écrira `uv run`.

**Éditeur de code :** dans VS Code ou PyCharm, choisis l'interpréteur Python situé dans `.venv` (commande « Python: Select Interpreter » dans VS Code). Sinon, l'éditeur soulignera tes imports en rouge.

### Et `pip` ?

Le `.venv` créé par uv **ne contient pas `pip`**, et c'est voulu. Un `pip install` n'écrirait rien dans `pyproject.toml` ni dans `uv.lock`, et le paquet disparaîtrait au prochain `uv sync`. Il existe une commande `uv pip install`, un mode de compatibilité pour les anciens projets, mais elle contourne aussi `pyproject.toml` et `uv.lock`. **Dans ce projet : toujours `uv add`.**

---

## 8. Gérer Python lui-même

uv distingue deux sortes de Python :

- **Python « système » :** celui qui est déjà sur l'ordinateur (installé par toi, par le système, par `pyenv`…) ;
- **Python « géré » :** celui qu'uv a téléchargé lui-même. Il provient du projet `python-build-standalone`, des versions précompilées et portables de Python.

Par défaut, uv utilise un Python système s'il convient. Sinon, il **télécharge automatiquement** la version demandée. Tu n'as rien à faire.

**Comment uv choisit la version**, du plus prioritaire au moins prioritaire :

1. l'option `--python` d'une commande, si tu la donnes ;
2. le fichier `.python-version` ;
3. sinon, la première version compatible avec `requires-python`.

Commandes utiles :

```bash
uv python list            # versions installées et disponibles au téléchargement
uv python install 3.12    # installer une version (rarement nécessaire : c'est automatique)
uv python pin 3.12        # écrire « 3.12 » dans .python-version
uv python find            # afficher le chemin du Python qu'uv utiliserait ici
uv python upgrade 3.12    # passer au dernier correctif (3.12.x le plus récent)
```

Changer de version plus tard est facile : `uv python pin 3.13`, et au prochain `uv run`, uv reconstruit `.venv` avec la nouvelle version. Passer à une nouvelle version mineure (3.12 → 3.13) reste une **décision** à prendre, car certaines bibliothèques peuvent ne pas encore la supporter. Les correctifs (3.12.10 → 3.12.11) sont sans risque.

---

## 9. Pourquoi `import rubiks` marche : le projet « empaqueté »

Depuis uv 0.12, `uv init` crée cette structure :

```
demo-uv/
├── pyproject.toml
├── .python-version
├── README.md
└── src/
    └── demo_uv/
        └── __init__.py
```

Et il ajoute au `pyproject.toml` une section `[build-system]`. Elle indique quel outil sait « emballer » le projet en paquet installable, ici `uv_build`, qu'uv télécharge tout seul.

**Conséquence :** lors de la synchronisation, uv installe **ton propre projet** dans `.venv`, en mode **éditable**. Au lieu de copier ton code, `.venv` contient un simple pointeur vers `src/`. Donc :

- `import demo_uv` fonctionne partout, y compris dans les tests (`tests/test_cube.py` pourra faire `from rubiks.cube import Cube`) ;
- tes modifications dans `src/` sont prises en compte **immédiatement**, sans rien réinstaller.

**Pourquoi un dossier `src/` ?** Il sépare le code du paquet du reste (docs, tests, scripts) et évite d'importer par accident un fichier qui traîne à la racine au lieu du paquet installé.

**Tiret ou tiret bas ?** Le projet s'appelle `demo-uv`, mais le dossier s'appelle `demo_uv`. Python n'accepte pas les tirets dans les noms de modules : uv les remplace donc par des tirets bas.

**Les commandes du projet.** La ligne `demo-uv = "demo_uv:main"` de `[project.scripts]` crée une commande `demo-uv` dans `.venv`. `uv run demo-uv` appelle alors la fonction `main()` de `src/demo_uv/__init__.py`. Plus tard, on pourra lancer le jeu avec `uv run rubiks`.

> Pour info : l'option `uv init --no-package` crée l'ancienne structure (un `main.py` à plat, sans `[build-system]`, sans installation du projet). Ce n'est pas ce qu'on veut ici.

---

## 10. uv et Git

**Ce qu'on commite :** `pyproject.toml`, `uv.lock`, `.python-version`, `src/`.
**Ce qu'on ignore** (dans `.gitignore`) : `.venv/`, `__pycache__/`.

**Règle d'or : `pyproject.toml` et `uv.lock` partent ensemble, dans le même commit.** Sinon, l'historique contient un état où la liste de courses et le ticket de caisse ne correspondent pas. Exemple de message : `build: ajoute numpy aux dépendances`.

### Le scénario qui montre tout l'intérêt d'uv

Tu changes d'ordinateur, ou quelqu'un veut essayer ton projet :

```bash
git clone https://github.com/<toi>/rubiks-rl.git
cd rubiks-rl
uv sync          # Python 3.12 téléchargé si besoin, .venv créé, versions EXACTES du lockfile
uv run pytest    # et c'est parti
```

Trois commandes, et l'environnement est **identique** au tien, au fichier près. Sans uv, il faudrait installer la bonne version de Python, créer l'environnement, l'activer, lancer `pip install`… et espérer obtenir les mêmes versions.

### Après un `git pull` ou un changement de branche

Si les dépendances ont changé, lance `uv sync`. Ou lance directement `uv run …`, qui s'en occupe.

### Conflit de merge sur `uv.lock` (ça arrivera peut-être en phase 3)

On ne résout **jamais** un conflit dans `uv.lock` à la main. La méthode :

1. résoudre le conflit dans `pyproject.toml`, à la main (ce fichier est lisible) ;
2. reprendre l'une des deux versions de `uv.lock`, par exemple la tienne : `git checkout --ours uv.lock` ;
3. lancer `uv lock` : uv regénère le lockfile à partir du `pyproject.toml` fusionné ;
4. `git add pyproject.toml uv.lock`, puis terminer le merge.

---

## 11. Outils hors projet : `uvx` et `uv tool`

Parfois, on veut juste **essayer** un outil, sans l'ajouter au projet :

```bash
uvx pycowsay "Salut"      # lance l'outil dans un environnement temporaire
```

`uvx` est un raccourci pour `uv tool run`. Et pour installer un outil disponible partout sur l'ordinateur : `uv tool install <outil>`.

**Dans ce projet**, `pytest` et `ruff` restent dans le groupe `dev`. Ainsi, leur version est verrouillée dans `uv.lock`, identique pour tout le monde, et plus tard pour les vérifications automatiques sur GitHub. `uvx`, c'est pour les essais.

---

## 12. Pour plus tard : PyTorch (phase 4)

PyTorch est un cas particulier. Il existe en plusieurs variantes : pour processeur seul (CPU) ou pour carte graphique NVIDIA (CUDA). Elles sont publiées sur des index séparés.

- `uv add torch` fonctionne directement. Depuis PyPI, on obtient la version CPU sous Windows et macOS, et une version CUDA sous Linux.
- Pour choisir une variante (par exemple CPU partout, beaucoup plus légère à télécharger), on déclare l'index de PyTorch dans `pyproject.toml` :

```toml
[tool.uv.sources]
torch = [{ index = "pytorch-cpu" }]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true        # cet index ne sert QUE pour les paquets qui le demandent
```

Cette décision est prévue au début de la phase 4 (cadrage, section 9). Le guide officiel détaille toutes les variantes : <https://docs.astral.sh/uv/guides/integration/pytorch/>.

---

## 13. Application : mettre en place `rubiks-rl` (phase 0)

Voici un aperçu, que la fiche de la phase 0 détaillera. C'est toi qui tapes les commandes.

```bash
# dans le dossier du repo (cloné depuis GitHub, ou créé avec git init)
uv init --name rubiks --python 3.12
git status                                      # regarde ce qu'uv a créé ou modifié
uv add --dev pytest ruff
uv run python -c "import rubiks; print('ok')"
```

Pourquoi ces options :

- **`--name rubiks`** : sans elle, le nom viendrait du dossier. `rubiks-rl` donnerait un paquet `rubiks_rl`. Avec elle, on obtient `src/rubiks/`, comme prévu dans le cadrage, et on écrira `from rubiks.cube import Cube`.
- **`--python 3.12`** : fixe `requires-python = ">=3.12"` et écrit `3.12` dans `.python-version`.
- **Pas de `numpy` maintenant** : on l'ajoutera en phase 1, quand on en aura besoin.

Ce qu'il faut savoir :

- **Dans un repo qui existe déjà**, `uv init` ne touche ni au `README.md` ni au `.gitignore` existants. Il ajoute seulement `pyproject.toml`, `.python-version` et `src/rubiks/__init__.py`. Le `.gitignore` tout prêt d'uv n'est créé que lorsqu'uv crée lui-même le dépôt Git.
- **Complète donc ton `.gitignore` toi-même** avec au moins `.venv/` et `__pycache__/`.
- **`git status` juste après `uv init`** : c'est le bon réflexe avant tout `git add`. Tu vois exactement quels fichiers uv a créés.

Si `uv init` refuse de s'exécuter avec le message *Project is already initialized*, c'est qu'un `pyproject.toml` existe déjà dans le dossier (un reste d'essai, par exemple).

---

## 14. Pièges fréquents

| Symptôme | Cause | Solution |
|---|---|---|
| `uv: command not found` | le terminal a été ouvert avant l'installation | fermer et rouvrir le terminal |
| `ModuleNotFoundError: No module named 'numpy'` avec `python fichier.py` | c'est le Python global qui a été lancé, pas celui de `.venv` | `uv run python fichier.py` (ou activer l'environnement) |
| un paquet installé « à la main » disparaît | `uv sync` retire tout ce qui n'est pas dans `uv.lock` | toujours passer par `uv add` |
| `uv.lock` a changé alors que je n'ai « rien fait » | `pyproject.toml` a été modifié à la main, uv a re-verrouillé | normal : commiter les deux ensemble |
| `__pycache__/` apparaît dans `git status` | il manque dans le `.gitignore` du repo | ajouter `__pycache__/` (et `.venv/`) au `.gitignore` |
| l'activation est refusée sous Windows | politique d'exécution de PowerShell | utiliser `uv run`, qui n'a pas besoin d'activation |
| l'éditeur souligne les imports en rouge | l'éditeur utilise un autre Python | choisir l'interpréteur de `.venv` |
| `uv init` dans un sous-dossier crée un « workspace » | uv a trouvé un `pyproject.toml` dans un dossier parent | faire ses essais **en dehors** du repo |

---

## 15. Aide-mémoire

| Je veux… | Commande |
|---|---|
| vérifier / mettre à jour uv | `uv --version` / `uv self update` |
| créer un projet | `uv init` |
| ajouter une dépendance | `uv add numpy` |
| ajouter un outil de développement | `uv add --dev pytest` |
| retirer une dépendance | `uv remove numpy` |
| lancer une commande dans l'environnement | `uv run pytest` |
| tout installer (après un clone, un pull) | `uv sync` |
| voir l'arbre des dépendances | `uv tree` |
| mettre à jour un paquet | `uv lock --upgrade-package numpy` |
| tout mettre à jour | `uv lock --upgrade` |
| vérifier que `uv.lock` est à jour | `uv lock --check` |
| voir les versions de Python | `uv python list` |
| choisir la version de Python du projet | `uv python pin 3.12` |
| essayer un outil sans l'installer | `uvx <outil>` |
| obtenir de l'aide | `uv help add` ou `uv add --help` |

---

## 16. Exercices et quiz

Fais ces exercices dans un dossier d'entraînement **en dehors** de `rubiks-rl` (par exemple `~/sandbox/`), que tu supprimeras ensuite. Si tu les fais à l'intérieur du repo, uv croira que `demo-uv` fait partie du projet `rubiks` (voir la dernière ligne des pièges fréquents).

Pour chaque exercice, **devine le résultat avant de lancer la commande**, puis vérifie. C'est là qu'on apprend vraiment.

### Exercice 1 — Créer un projet

```bash
uv init demo-uv --python 3.12
cd demo-uv
```

Liste **tous** les fichiers, y compris les fichiers cachés (`ls -a` sous macOS/Linux, `Get-ChildItem -Force` sous Windows).
**Devine :** y a-t-il un `.venv` ? un `uv.lock` ?
Puis lance `uv run demo-uv` et liste à nouveau les fichiers.
**À constater :** `.venv` et `uv.lock` n'apparaissent qu'au premier `uv run`. uv les crée seulement quand il en a besoin.

### Exercice 2 — Regarder dans la boîte

```bash
uv run python -c "import sys; print(sys.executable); print(sys.prefix)"
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

(Sous macOS/Linux, la seconde commande s'appelle peut-être `python3`. Si aucun Python n'est installé sur ta machine, elle échouera : c'est normal, et c'est même instructif.)
**À constater :** avec `uv run`, les chemins pointent dans `.venv`.
Ouvre ensuite `.venv/pyvenv.cfg` avec un éditeur de texte. **Question :** quelle ligne indique à Python où se trouve son « vrai » interpréteur ?

### Exercice 3 — Liste de courses et ticket de caisse

```bash
uv add numpy
```

Ouvre `pyproject.toml` : qu'est-ce qui a été ajouté ? Cherche `name = "numpy"` dans `uv.lock` : quelle est la version exacte ? À peu près combien de fichiers `wheels` sont listés, et pourquoi autant ?
**Question :** pourquoi `pyproject.toml` dit `>=` alors que `uv.lock` donne une version précise ?

### Exercice 4 — Dépendances transitives

```bash
uv add --dev pytest
uv tree
```

**Question :** quels paquets sont des dépendances directes ? Lesquels sont arrivés « avec » pytest ?

### Exercice 5 — La synchronisation est exacte

```bash
uv pip list          # liste ce qui est installé dans .venv (en lecture seule, sans danger)
uv sync --no-dev
uv pip list
uv sync
uv pip list
```

**Devine :** que va contenir la deuxième liste ?
**À constater :** `uv sync --no-dev` a **retiré** pytest et ses dépendances de `.venv`, puis `uv sync` les a remis. `.venv` suit toujours `uv.lock`.
**Bonus :** dans la liste, la colonne *Editable project location* de `demo-uv` pointe vers ton dossier. C'est l'installation « éditable » de la section 9.

### Exercice 6 — `.venv` est jetable

Supprime `.venv` (`rm -rf .venv` sous macOS/Linux, `Remove-Item -Recurse -Force .venv` sous Windows), puis lance `uv sync` en surveillant le temps que ça prend.
**À constater :** c'est très rapide, car rien n'est retéléchargé. Lance `uv cache dir` pour voir où se trouve le cache.

### Exercice 7 — Changer de Python

```bash
uv python list
uv python pin 3.13
uv run python --version
uv python pin 3.11
```

**À constater :** avec 3.13, uv télécharge la version si besoin et reconstruit `.venv`. Avec 3.11, lis bien le message.
**Question :** pourquoi 3.13 est-il accepté, mais pas 3.11 ?
Termine par `uv python pin 3.12` pour revenir à la normale.

### Quiz d'auto-vérification

<details>
<summary>1. Quelle est la différence entre <code>pyproject.toml</code> et <code>uv.lock</code> ?</summary>

`pyproject.toml` dit ce que je **veux**, avec des contraintes larges (`numpy>=2.5.3`). `uv.lock` dit ce qui est **réellement installé** : versions exactes de toutes les dépendances, transitives comprises, avec leurs empreintes.
</details>

<details>
<summary>2. Pourquoi ne commite-t-on pas <code>.venv</code> ?</summary>

Il est lourd, propre à chaque machine (système, chemins) et entièrement reconstructible à partir de `uv.lock` avec `uv sync`.
</details>

<details>
<summary>3. Que fait <code>uv run pytest</code> avant de lancer pytest ?</summary>

Il vérifie que `uv.lock` correspond à `pyproject.toml` (et re-verrouille si besoin), puis que `.venv` correspond à `uv.lock` (et synchronise si besoin). Ensuite seulement, il lance pytest avec le Python de `.venv`.
</details>

<details>
<summary>4. J'ajoute <code>"numpy"</code> à la main dans <code>pyproject.toml</code>. Que se passe-t-il au prochain <code>uv run</code> ?</summary>

uv voit que `uv.lock` n'est plus à jour : il re-verrouille, installe numpy, puis lance la commande. Il faudra commiter `pyproject.toml` **et** `uv.lock`.
</details>

<details>
<summary>5. Quelqu'un clone mon repo. Quelle commande installe tout ?</summary>

`uv sync`. Au besoin, uv télécharge même Python 3.12.
</details>

<details>
<summary>6. Pourquoi pytest est-il dans le groupe <code>dev</code> et pas dans <code>dependencies</code> ?</summary>

Le jeu n'a pas besoin de pytest pour tourner : c'est un outil de développement. Il ne ferait pas partie d'une version distribuée du projet.
</details>

<details>
<summary>7. Quelle est la différence entre <code>requires-python</code> et <code>.python-version</code> ?</summary>

`requires-python` est une promesse sous forme de plage (« 3.12 ou plus »). `.python-version` est la version précise choisie pour travailler, qui doit être dans la plage.
</details>

<details>
<summary>8. Une nouvelle version de numpy sort demain. Mon projet l'utilise-t-il automatiquement ?</summary>

Non. `uv.lock` garde la version verrouillée. Pour mettre à jour : `uv lock --upgrade-package numpy`, puis lancer les tests, puis commiter.
</details>

---

## Pour aller plus loin

- Documentation officielle : <https://docs.astral.sh/uv/>
- Guide « Working on projects » : <https://docs.astral.sh/uv/guides/projects/>
- Concepts « Locking and syncing » : <https://docs.astral.sh/uv/concepts/projects/sync/>
- Gestion des versions de Python : <https://docs.astral.sh/uv/concepts/python-versions/>
- uv et PyTorch (phase 4) : <https://docs.astral.sh/uv/guides/integration/pytorch/>
