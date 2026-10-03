# Bilan de la v1.0 — phases 0 à 3 et leurs « pour aller plus loin »

> **Emplacement dans le repo :** `docs/fiches/bilan-v1.md`
> **Date :** 02/10/2026 — version `1.0.0`, tag `v1.0.0`.
> **Pourquoi ce document :** la phase 3 et les bonus ont été codés par Claude, à ta demande, pour attaquer la phase 4 sereinement. Ce bilan dit **ce qui a été fait, où le lire, et ce qu'il te reste à faire à la main** (réglages GitHub). Il propose aussi un ordre de lecture du code.

---

## 1. Ordre de lecture conseillé (une soirée)

Du plus simple au plus riche ; chaque fichier n'utilise que les précédents.

| Ordre | Fichier | Ce qu'il faut y voir |
|---|---|---|
| 1 | `src/rubiks/moves.py` | la notation en chaînes : `parse_move`, `inverse_move`, `simplify` (une pile : on regarde le dernier coup gardé) |
| 2 | `src/rubiks/scramble.py` | un mélange sans coups gaspillés, en 10 lignes |
| 3 | `src/rubiks/geometry.py` | cubie + normale, rotation d'un quart de tour, **permutation fabriquée par la géométrie**, glisser à la souris (produit vectoriel) |
| 4 | `src/rubiks/cube.py` | ton code de la phase 1, gardé comme référence ; les permutations construites au chargement ; `__eq__`, `__repr__`, `facelets`, `sequence_order` |
| 5 | `src/rubiks/game.py` | `Command`, `Game` (chrono avec horloge injectable, annulation, solution) et `Player` (jouer, animer, repeindre) |
| 6 | `src/rubiks/render/view2d.py` | ta vue 2D, avec Ctrl, le chrono et F12 |
| 7 | `src/rubiks/render/scene.py` puis `view3d_pygame.py` | la 3D **à la main** : projection, faces de dos, peintre, clic sur une case |
| 8 | `src/rubiks/render/view3d.py` | la même chose avec ursina : bien plus court, car ursina fait la partie 7 pour toi |
| 9 | `tests/conftest.py`, `tests/test_geometry.py`, `tests/test_game.py` | fixtures, le grand test, une fausse horloge |

Astuce : lance `uv run pytest -v tests/test_geometry.py` en lisant `geometry.py` ; chaque nom de test raconte une propriété.

---

## 2. Tous les « pour aller plus loin », un par un

Légende : **Fait** (dans le code), **À toi** (une commande ou un réglage sur GitHub, voir section 4), **Réponse** (une question de réflexion, réponse en section 3).

### Phase 0

| Bonus | Statut | Où |
|---|---|---|
| `git log --oneline --graph --all`, `git show` | À toi | commandes de lecture, à utiliser librement |
| Alias `git lg` | À toi | `git config --global alias.lg "log --oneline --graph --all"` |
| `uv lock --check` | Fait | README, `CLAUDE.md`, et dans la CI (`.github/workflows/tests.yml`) |
| Licence MIT | Fait | `LICENSE` |
| Règles ruff `B` et `UP` | Fait | `pyproject.toml` ; le code passe sans erreur |

### Phase 1

| Bonus | Statut | Où |
|---|---|---|
| Les permutations, gratuitement | Fait | `cube.py` : `_face_permutation`, `PERMUTATIONS`. Mesuré : **14 µs → 0,8 µs** par coup (≈ 18 fois plus rapide) |
| L'ordre d'une séquence (`R U` = 105) | Fait | `cube.sequence_order` ; tests `test_sequence_order` (`R U'` = 63) |
| Un meilleur mélange | Fait | `scramble.py` : jamais deux fois la même face de suite |
| `__eq__` et `__repr__` | Fait | `cube.py` ; `repr` donne `Cube.from_facelets('UUU…')`, recopiable |
| Fixtures pytest | Fait | `tests/conftest.py` : `numbered_cube`, `clock` |
| Découper le module | Fait | `moves.py`, `scramble.py`, `geometry.py` ; `cube.py` ne garde que le `Cube` |
| Protéger `main` | À toi | section 4 |
| `push.autoSetupRemote` | À toi | `git config --global push.autoSetupRemote true` |
| Version alignée sur les tags | À toi | `uv version --bump major` (0.2.0 → 1.0.0), dans le script de mise à jour |
| Une release GitHub | À toi | section 4 |

### Phase 2

| Bonus | Statut | Où |
|---|---|---|
| Annuler (Ctrl+Z) | Fait | `Game.undo` ; dans les 3 fenêtres |
| Compteur et chronomètre | Fait | `Game.moves_played`, `Game.elapsed` (horloge injectable pour les tests) |
| Demi-tours au clavier (Ctrl + lettre) | Fait | `key_to_move(..., ctrl=True)` |
| Second affichage dans le terminal | Fait | `render/terminal.py`, `uv run rubiks-terminal` |
| Test automatique « pas de pygame dans le cube » | Fait | `tests/test_render.py`, étendu à ursina et à tous les modules purs |
| Capture d'écran dans le README | Fait | `docs/images/`, et F12 dans les vues pygame |
| Alias Git pour le graphe | À toi | (même alias que la phase 0) |
| Protéger `main` | À toi | section 4 |
| Release GitHub `v0.2.0` | À toi | section 4 |
| pygame-ce | Rien à faire | on garde `pygame` : bon à savoir pour lire de la doc récente |

### Phase 3

| Bonus | Statut | Où |
|---|---|---|
| Demi-tours animés | Fait | `Player._start_move` : une animation de 180°, 1,5 fois plus longue |
| Annuler avec animation | Fait | Ctrl+Z passe par la file de `Player` |
| Tourner tout le cube (`x y z`) | Fait + Réponse | touches X Y Z ; permutations de `geometry.permutation` |
| Tranches du milieu (`M E S`) | Fait + Réponse | touches M E S |
| Tourner une face à la souris | Fait | `geometry.move_for_drag`, `best_direction` ; `view3d.py` et `view3d_pygame.py` |
| Rejouer une solution | Fait | Entrée : `Game.solution` (inverse simplifié), jouée coup par coup ; « Résolu (avec aide) » |
| Vue OpenGL à la main | Fait autrement | `scene.py` + `view3d_pygame.py` : la même idée **sans OpenGL**, avec pygame seul (voir section 3) |
| Release `v1.0.0` | À toi | section 4 |

En plus, sans être dans les fiches :

- **Maj + Espace** : long mélange de 25 coups ;
- **CI GitHub** : tests, ruff et `uv lock --check` à chaque push et PR ;
- **`Cube.facelets()`** : le format de la bibliothèque `kociemba`, prêt pour la comparaison de la phase 7 ;
- correction du `.gitignore` (`.pytest_cahce` → `.pytest_cache`) et d'une ligne « git branch » collée par erreur en haut du README.

---

## 3. Les questions de réflexion, avec leurs réponses

**Tourner tout le cube (`x y z`) : juste la caméra, ou pas ?** Dans la vue 3D, on *pourrait* tourner la caméra et rien d'autre. Mais `x` change vraiment `cube.state` : la face verte n'est plus en F. C'est pour ça que `is_solved` compare chaque case au **centre de sa face**, et pas à une couleur fixe : un cube résolu reste résolu quand on le tient autrement (test `test_a_rotated_cube_is_still_solved`). Et c'est pour ça que les rotations ne comptent pas dans le nombre de coups.

**Pourquoi `M E S` ne sont pas de bonnes actions pour le RL ?** Une tranche déplace **4 centres** (test `test_slice_moves_the_centers`) : après `M`, le cube est « le même » mais tenu autrement. Un même casse-tête aurait alors 24 écritures différentes de `cube.state` (une par façon de le tenir), et l'agent devrait apprendre 24 fois la même chose. Avec seulement les 18 mouvements de faces, les centres ne bougent jamais : **un état = une seule écriture**. Et on ne perd rien : `M` = `L' R x'`, donc toute position atteinte avec des tranches l'est aussi sans.

**Pourquoi pas PyOpenGL ?** L'idée du bonus était de « comprendre ce qu'ursina fait pour toi ». `scene.py` le montre sans ajouter de dépendance : projection en perspective (diviser par la distance), élimination des faces de dos (produit scalaire avec la direction de l'œil), algorithme du peintre (trier par profondeur), et sélection d'une case au clic (point dans un polygone). OpenGL ferait la même chose sur la carte graphique, avec en plus des matrices 4 × 4, des shaders et un tampon de profondeur : un très bon sujet plus tard, mais un projet à lui seul.

**Comment la vue 3D sait-elle quel mouvement animer ?** (Question de conception de la notion 6.) `Game.execute` renvoie la liste des coups qu'il vient de jouer ; `Player` s'en sert pour démarrer l'animation. La vue 2D l'ignore simplement : rien n'a cassé.

---

## 4. Ce qu'il te reste à faire à la main sur GitHub

1. **Protéger `main`** : *Settings* → *Rules* → *Rulesets* → *New branch ruleset*. Cible : la branche par défaut. Coche *Require a pull request before merging* et *Require status checks to pass* (choisis le contrôle `tests`, il apparaît après le premier passage de la CI). Un `git push` direct sur `main` sera alors refusé.
2. **Releases** : onglet *Releases* → *Draft a new release* → choisir le tag `v0.1.0`, titre « Phase 1 : cube logique », quelques lignes de notes. Pareil pour `v0.2.0` (« Phase 2 : affichage 2D et clavier ») et `v1.0.0` (« Phase 3 : le jeu est fini », avec la capture `docs/images/vue-3d.png`).

---

## 5. Avant la phase 4 : ce qui est prêt pour le RL

- **Les 18 actions** : `rubiks.moves.MOVES`, dans un ordre fixe : l'action numéro `i` sera `MOVES[i]`.
- **Un coup ≈ 1 µs** grâce aux permutations : un million de coups prend environ une seconde.
- **Un état** : `cube.state` (54 entiers de 0 à 5). Pour un réseau de neurones, on le transformera en « one-hot » (54 × 6 = 324 zéros et uns) : ce sera une décision de la phase 4 (cadrage, section 9).
- **Un mélange de `n` coups** : `cube.scramble(n, seed=...)`, sans coups gaspillés, reproductible. Exactement ce qu'il faut pour le *curriculum learning* (phase 5).
- **Aucun affichage chargé** quand on importe `rubiks.cube` : vérifié par les tests.
