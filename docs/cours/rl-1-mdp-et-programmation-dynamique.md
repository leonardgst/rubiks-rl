# Cours de RL — 1. MDP, programmation dynamique, et pourquoi le cube est difficile

> **Emplacement dans le repo :** `docs/cours/rl-1-mdp-et-programmation-dynamique.md`
> **Niveau :** master (statistique, ML, DL). Prérequis : probabilités, chaînes de Markov finies, algèbre linéaire, optimisation. Aucun prérequis en RL.
> **Durée :** 4 à 6 h de lecture, plus les exercices (section 12, corrigés en section 13).
> **Fiche associée :** `docs/fiches/phase-4-cours-rl-environnement.md`.
> **Correspondances :** ce chapitre couvre Sutton et Barto, chapitres 3 et 4, avec un peu de Puterman et de Bertsekas pour les preuves. Il y ajoute une analyse propre au cube : groupe, chaîne de Markov, exploration.
> **Les maths** sont écrites en LaTeX (`$…$`), affiché correctement par GitHub et par l'aperçu Markdown de VS Code.

---

## 0. Plan

Trois chapitres accompagnent les phases RL du projet :

| Chapitre | Phase | Contenu |
|---|---|---|
| **1. MDP et programmation dynamique** (ce document) | 4 | formalisme, équations et opérateurs de Bellman, programmation dynamique et convergence, le cube comme plus court chemin sur un graphe de Cayley, la politique aléatoire comme marche aléatoire, l'exploration, la conception de la récompense, l'évaluation statistique |
| 2. Apprendre sans modèle | 5 | Monte-Carlo et TD, Q-learning et approximation stochastique, approximation de fonctions et « triade mortelle », DQN et variantes, curriculum |
| 3. Programmation dynamique approchée et recherche | 6 | itération de valeur ajustée (DAVI), A\* pondéré, recherche en faisceau, MCTS, DeepCube, DeepCubeA, EfficientCube |

La section 9 donne déjà la feuille de route des chapitres 2 et 3, avec leurs équations clés.

### Notations

| Symbole | Sens |
|---|---|
| $\mathcal S, \mathcal A$ | ensembles d'états et d'actions (finis ici) |
| $P(s' \mid s, a)$ | noyau de transition |
| $r(s, a)$ | récompense espérée (déterministe pour le cube) |
| $\gamma \in [0, 1]$ | facteur d'actualisation |
| $\pi(a \mid s)$ | politique (stochastique) ; $\pi(s)$ si déterministe |
| $G_t = \sum_{k \ge 0} \gamma^k R_{t+k+1}$ | retour à partir de $t$ |
| $V^\pi, Q^\pi, A^\pi = Q^\pi - V^\pi$ | valeur d'état, d'action, avantage |
| $V^*, Q^*$ | valeurs optimales |
| $T^\pi, T$ | opérateurs de Bellman (d'évaluation, d'optimalité) |
| $d(s)$ | distance de $s$ à l'état résolu, en nombre de coups (métrique demi-tour, 18 actions) |
| $\mathcal G$ | le groupe du cube, $\lvert \mathcal G \rvert = 43\,252\,003\,274\,489\,856\,000$ |

---

## 1. Le RL vu par un statisticien

Ce qui change par rapport à l'apprentissage supervisé :

1. **Les données ne sont pas i.i.d.** Les états d'une trajectoire sont corrélés, et surtout **leur loi dépend de la politique** : changer de politique change la distribution des données. C'est un problème de *distribution shift* permanent, et endogène.
2. **Pas d'étiquette, un signal différé.** On n'observe jamais « la bonne action ». On observe un scalaire, éventuellement nul presque partout, et le mérite de ce scalaire doit être réparti sur les actions passées (*credit assignment*).
3. **La collecte des données fait partie du problème.** Un agent qui n'explore pas ne voit jamais les états qui lui apprendraient à mieux faire (section 6). Il n'existe pas d'équivalent supervisé de cet arbitrage exploration / exploitation.
4. **L'évaluation est elle-même un problème d'estimation.** Le retour d'une politique est une espérance, estimée par Monte-Carlo, avec ses intervalles de confiance, ses événements rares et ses biais de sélection (section 8).

On distingue quatre problèmes :

| Problème | Donné | Cherché |
|---|---|---|
| **planification** | le modèle $(P, r)$ | $V^*$, $\pi^*$ (programmation dynamique, recherche) |
| **prédiction** (évaluation) | une politique $\pi$, des trajectoires | $V^\pi$ ou $Q^\pi$ |
| **contrôle** | des trajectoires | $\pi^*$ |
| **exploration** | la possibilité d'agir | des données qui rendent le contrôle possible |

**Le cube est un cas très particulier : le modèle est connu, exact et gratuit** (`cube.move`, environ 1 µs). Tout le RL « sans modèle » y est donc, en un sens, un choix pédagogique. La phase 6 exploitera le modèle pour planifier (chapitre 3).

---

## 2. Le formalisme : processus de décision markovien

### 2.1 Définition

Un **processus de décision markovien** (MDP) est un tuple $(\mathcal S, \mathcal A, P, r, \gamma, \rho_0)$ : états, actions, transitions, récompenses, actualisation, loi de l'état initial. Un sous-ensemble $\mathcal S_T \subset \mathcal S$ d'états **absorbants** (terminaux) peut terminer les épisodes ; par convention, ils ont une récompense nulle et bouclent sur eux-mêmes.

Une politique $\pi$ et $\rho_0$ définissent une loi sur les trajectoires $\tau = (S_0, A_0, R_1, S_1, A_1, \dots)$ :

$$
\mathbb P^\pi(\tau) = \rho_0(S_0) \prod_{t \ge 0} \pi(A_t \mid S_t) \, P(S_{t+1} \mid S_t, A_t).
$$

La **propriété de Markov** est l'hypothèse $\mathbb P(S_{t+1} \mid S_0, A_0, \dots, S_t, A_t) = P(S_{t+1} \mid S_t, A_t)$ : l'état résume tout le passé utile.

**Classes de politiques.** On peut autoriser une politique à dépendre de tout l'historique, et à être aléatoire. Résultat classique (Puterman, chapitre 6) : pour un MDP fini actualisé, il existe une politique optimale **markovienne, stationnaire et déterministe**. On peut donc chercher $\pi^* : \mathcal S \to \mathcal A$ sans perte de généralité. Les politiques stochastiques resteront utiles pour explorer et pour les méthodes de gradient (chapitre 2).

### 2.2 Trois façons de rendre le retour fini

| Cadre | Retour | Remarque |
|---|---|---|
| actualisé, horizon infini | $\sum_{t \ge 0} \gamma^t R_{t+1}$, $\gamma < 1$ | borné par $R_{\max} / (1-\gamma)$ ; le cadre des théorèmes de contraction |
| horizon fini $H$ | $\sum_{t=0}^{H-1} R_{t+1}$ | la politique optimale est **non stationnaire** (elle dépend du temps restant) |
| plus court chemin stochastique (SSP) | $\sum_{t \ge 0} R_{t+1}$, $\gamma = 1$, jusqu'à l'absorption | suppose qu'au moins une politique atteint la cible presque sûrement (*politique propre*) ; Bertsekas et Tsitsiklis (1991) |

**Le cube relève du troisième cadre** : $\gamma = 1$, récompense $-1$ par coup, état résolu absorbant. Le retour d'une politique qui résout vaut moins le nombre de coups. Une politique qui ne résout jamais (*impropre*) a une valeur de $-\infty$.

### 2.3 Terminé ou tronqué : une distinction de modélisation

Un environnement réel impose souvent une **limite de temps** $H$ (notre `max_steps`). Deux lectures sont possibles :

- **le temps fait partie de la tâche** : le temps restant doit alors faire partie de l'état, sinon le processus n'est plus markovien (deux situations identiques avec 1 ou 19 coups restants n'ont pas la même valeur) ;
- **la limite est un artefact de collecte** (le cas du cube : on veut résoudre, quel que soit le temps) : l'état atteint à la limite **n'est pas terminal**, et sa valeur n'est pas nulle.

Gymnasium sépare donc `terminated` (absorption dans $\mathcal S_T$) et `truncated` (fin artificielle). En apprentissage par *bootstrap* (chapitre 2), la cible doit être $r + \gamma V(s')$ si l'épisode est tronqué, et $r$ seulement s'il est terminé. Confondre les deux biaise les valeurs vers 0 près de la limite (Pardo et al., *Time Limits in Reinforcement Learning*, ICML 2018).

### 2.4 Le cube comme MDP

| Élément | Le cube |
|---|---|
| $\mathcal S$ | le **groupe du cube** $\mathcal G$ : les permutations des 54 cases atteignables depuis l'état résolu, $\lvert \mathcal G \rvert \approx 4{,}3 \times 10^{19}$ |
| $\mathcal A$ | $\{U, U', U2, R, \dots, B2\}$, 18 générateurs, **fermé par inverse** ($\mathcal A = \mathcal A^{-1}$) |
| $P$ | déterministe : $s' = s \cdot a$ (on applique le coup) |
| $r$ | $-1$ par coup |
| $\mathcal S_T$ | $\{e\}$, l'état résolu (l'élément neutre) |
| $\gamma$ | 1 |
| $\rho_0$ | **à choisir** : mélanges de profondeur $k$, loi uniforme sur $\mathcal G$… C'est un levier majeur (section 6.4) |

Le MDP est un **plus court chemin déterministe** sur le **graphe de Cayley** $\mathrm{Cay}(\mathcal G, \mathcal A)$ : les sommets sont les éléments de $\mathcal G$, avec une arête entre $g$ et $g \cdot a$ pour chaque $a \in \mathcal A$. Comme $\mathcal A = \mathcal A^{-1}$, le graphe est non orienté et 18-régulier. Donc :

$$
V^*(s) = -d(s), \qquad Q^*(s, a) = -1 - d(s \cdot a).
$$

**Observation.** L'environnement montre la coloration des 54 cases, et non l'élément de $\mathcal G$. Cette application $\mathcal G \to \{0, \dots, 5\}^{54}$ est **injective** quand les centres sont fixes (et ils le sont, avec les 18 mouvements de faces) : chaque cubie est identifié par son ensemble de couleurs, et son orientation par la face où se trouve chaque couleur. L'observation est donc un état complet ; il n'y a pas d'observabilité partielle. À l'inverse, n'observer que la face avant donnerait un POMDP.

**Le groupe, en une ligne.** Un état est déterminé par la permutation et l'orientation des 8 coins et des 12 arêtes, avec trois contraintes : somme des orientations des coins $\equiv 0 \pmod 3$, somme des orientations des arêtes $\equiv 0 \pmod 2$, parité de la permutation des coins égale à celle des arêtes. D'où

$$
\lvert \mathcal G \rvert = \frac{8! \cdot 3^8 \cdot 12! \cdot 2^{12}}{3 \cdot 2 \cdot 2} = 8! \cdot 3^7 \cdot 12! \cdot 2^{10} = 43\,252\,003\,274\,489\,856\,000.
$$

Un cube démonté puis remonté au hasard n'a qu'**une chance sur 12** d'être résoluble (exercice 8).

### 2.5 L'exemple fil rouge : $S_3$, un « cube » à 6 états

Trois jetons A, B, C. Deux actions, chacune une transposition : **G** échange les deux jetons de gauche, **D** échange les deux de droite. Cible : ABC. C'est $\mathrm{Cay}(S_3, \{(1\,2), (2\,3)\})$, un **hexagone** :

```
                 ABC          d = 0
              G /   \ D
             BAC     ACB      d = 1
           D  |       |  G
             BCA     CAB      d = 2
              G \   / D
                 CBA          d = 3
```

Mêmes ingrédients que le cube (groupe de permutations, générateurs involutifs, plus court chemin), mais tout se calcule à la main. On s'en sert comme banc d'essai pour chaque notion.

---

## 3. Fonctions de valeur et équations de Bellman

### 3.1 Définitions

$$
V^\pi(s) = \mathbb E^\pi \big[ G_t \mid S_t = s \big], \qquad
Q^\pi(s, a) = \mathbb E^\pi \big[ G_t \mid S_t = s, A_t = a \big], \qquad
A^\pi = Q^\pi - V^\pi.
$$

$V^*(s) = \sup_\pi V^\pi(s)$ et $Q^*(s, a) = \sup_\pi Q^\pi(s, a)$.

### 3.2 Équation d'évaluation (Bellman pour une politique)

En conditionnant sur le premier pas :

$$
V^\pi(s) = \sum_a \pi(a \mid s) \Big[ r(s, a) + \gamma \sum_{s'} P(s' \mid s, a) \, V^\pi(s') \Big].
$$

Sous forme matricielle, avec $r^\pi(s) = \sum_a \pi(a \mid s) r(s, a)$ et $P^\pi(s, s') = \sum_a \pi(a \mid s) P(s' \mid s, a)$ :

$$
V^\pi = r^\pi + \gamma P^\pi V^\pi \quad \Longrightarrow \quad V^\pi = (I - \gamma P^\pi)^{-1} r^\pi \quad (\gamma < 1).
$$

Pour $\gamma = 1$ et une politique propre, on restreint aux états transitoires : si $Q$ est la sous-matrice de $P^\pi$ entre états non terminaux, $N = (I - Q)^{-1}$ est la **matrice fondamentale** de la chaîne absorbante (Kemeny et Snell). Avec $r = -1$ par pas, $V^\pi = -N \mathbf 1$ : **moins le temps moyen d'absorption**.

### 3.3 Équations d'optimalité

$$
V^*(s) = \max_a \Big[ r(s, a) + \gamma \sum_{s'} P(s' \mid s, a) V^*(s') \Big], \qquad
Q^*(s, a) = r(s, a) + \gamma \sum_{s'} P(s' \mid s, a) \max_{a'} Q^*(s', a').
$$

Toute politique **gloutonne** par rapport à $Q^*$, $\pi(s) \in \arg\max_a Q^*(s, a)$, est optimale. C'est pourquoi tant de méthodes se ramènent à **estimer $Q^*$**.

### 3.4 Opérateurs et contraction

Définissons, pour $V \in \mathbb R^{\mathcal S}$ :

$$
(T^\pi V)(s) = \sum_a \pi(a \mid s) \big[ r(s,a) + \gamma \, \mathbb E_{s'} V(s') \big], \qquad
(T V)(s) = \max_a \big[ r(s,a) + \gamma \, \mathbb E_{s'} V(s') \big].
$$

**Monotonie.** $V \le W$ (composante par composante) implique $T V \le T W$ et $T^\pi V \le T^\pi W$.

**Contraction.** Pour $\gamma < 1$, $\lVert T V - T W \rVert_\infty \le \gamma \lVert V - W \rVert_\infty$.

*Preuve.* Pour tout $s$, $\lvert \max_a f(a) - \max_a g(a) \rvert \le \max_a \lvert f(a) - g(a) \rvert$. Donc
$\lvert (TV)(s) - (TW)(s) \rvert \le \gamma \max_a \sum_{s'} P(s' \mid s, a) \lvert V(s') - W(s') \rvert \le \gamma \lVert V - W \rVert_\infty$. $\square$

Par le théorème du point fixe de Banach, $T$ a un unique point fixe, $V^*$, et $\lVert T^k V_0 - V^* \rVert_\infty \le \gamma^k \lVert V_0 - V^* \rVert_\infty$. Même chose pour $T^\pi$ et $V^\pi$.

**Garantie d'une politique gloutonne approchée** (Singh et Yee, 1994). Si $\lVert V - V^* \rVert_\infty \le \varepsilon$ et que $\pi$ est gloutonne par rapport à $V$, alors

$$
\lVert V^\pi - V^* \rVert_\infty \le \frac{2 \gamma \varepsilon}{1 - \gamma}.
$$

Le facteur $1/(1-\gamma)$ dit qu'une petite erreur sur la valeur peut coûter cher sur un long horizon. Pour $\gamma = 1$, la borne ne dit plus rien. Pour le cube, on cherchera d'autres garanties, du côté de la recherche (chapitre 3) : une heuristique **cohérente** ou **admissible** garantit l'optimalité d'A\*.

### 3.5 Le mini-casse-tête, entièrement résolu

Avec $r = -1$, $\gamma = 1$ :

| État | $d$ | $V^*$ | $Q^*(\cdot, \mathrm G)$ | $Q^*(\cdot, \mathrm D)$ | $V^{\text{alea}}$ |
|---|---|---|---|---|---|
| ABC | 0 | 0 | — | — | 0 |
| BAC | 1 | $-1$ | $-1$ | $-3$ | $-5$ |
| ACB | 1 | $-1$ | $-3$ | $-1$ | $-5$ |
| BCA | 2 | $-2$ | $-4$ | $-2$ | $-8$ |
| CAB | 2 | $-2$ | $-2$ | $-4$ | $-8$ |
| CBA | 3 | $-3$ | $-3$ | $-3$ | $-9$ |

La colonne $V^{\text{alea}}$ est $-N\mathbf 1$ pour la politique uniforme. Les états transitoires sont pris dans l'ordre (BAC, ACB, BCA, CAB, CBA), et $Q$ vaut $\tfrac12$ sur chaque arête de l'hexagone qui ne mène pas à ABC :

$$
N = (I - Q)^{-1} =
\begin{pmatrix}
5/3 & 1/3 & 4/3 & 2/3 & 1 \\
1/3 & 5/3 & 2/3 & 4/3 & 1 \\
4/3 & 2/3 & 8/3 & 4/3 & 2 \\
2/3 & 4/3 & 4/3 & 8/3 & 2 \\
1 & 1 & 2 & 2 & 3
\end{pmatrix},
\qquad N \mathbf 1 = (5, 5, 8, 8, 9)^\top.
$$

C'est aussi le temps d'atteinte classique d'une marche simple sur un cycle de longueur $n = 6$, depuis la distance $k$ : $k(n - k)$, soit $1 \cdot 5$, $2 \cdot 4$ et $3 \cdot 3$.

---

## 4. Programmation dynamique

### 4.1 Évaluation de politique

- **Exacte** : résoudre le système linéaire, en $O(\lvert \mathcal S \rvert^3)$.
- **Itérative** : $V_{k+1} = T^\pi V_k$, en $O(\lvert \mathcal S \rvert^2)$ par itération (ou $O(\lvert \mathcal S \rvert \cdot \lvert \mathcal A \rvert)$ pour un MDP déterministe), avec une convergence géométrique de taux $\gamma$.

### 4.2 Théorème d'amélioration de politique

Soit $\pi'$ telle que $Q^\pi(s, \pi'(s)) \ge V^\pi(s)$ pour tout $s$. Alors $V^{\pi'} \ge V^\pi$.

*Preuve.* $V^\pi(s) \le Q^\pi(s, \pi'(s)) = \mathbb E[R_1 + \gamma V^\pi(S_1) \mid S_0 = s, A_0 = \pi'(s)]$. On applique à nouveau l'inégalité à $V^\pi(S_1)$, et ainsi de suite. En dépliant $k$ fois, on obtient $V^\pi(s) \le \mathbb E^{\pi'}[\sum_{t < k} \gamma^t R_{t+1} + \gamma^k V^\pi(S_k)]$, qui tend vers $V^{\pi'}(s)$. $\square$

La politique gloutonne par rapport à $Q^\pi$ vérifie l'hypothèse. Si elle n'améliore rien, $V^\pi$ satisfait l'équation d'optimalité, donc $\pi$ est optimale.

### 4.3 Itération de politique

On alterne évaluation exacte et amélioration gloutonne. La suite $V^{\pi_k}$ est croissante, et il n'y a qu'un nombre fini de politiques déterministes : l'algorithme **termine en un nombre fini d'itérations**, en pratique très petit. Il s'interprète comme une méthode de Newton sur l'équation $V = TV$.

### 4.4 Itération de valeur

$V_{k+1} = T V_k$. Convergence géométrique (section 3.4). Critère d'arrêt classique (Puterman, théorème 6.3.1) : si $\lVert V_{k+1} - V_k \rVert_\infty < \varepsilon (1 - \gamma) / (2\gamma)$, la politique gloutonne par rapport à $V_{k+1}$ est $\varepsilon$-optimale.

### 4.5 Formulation par programmation linéaire

$V^*$ est la plus petite fonction qui domine son image par $T$ :

$$
\min_V \sum_s \mu(s) V(s) \quad \text{sous} \quad V(s) \ge r(s,a) + \gamma \sum_{s'} P(s' \mid s, a) V(s') \quad \forall (s, a),
$$

pour toute pondération $\mu > 0$. Le problème dual porte sur les **mesures d'occupation** $x(s, a)$. Ce point de vue nourrit des méthodes modernes (RL hors ligne, RL sous contraintes), mais ne nous servira pas pour le cube.

### 4.6 Le cas du cube : l'itération de valeur est un parcours en largeur

**Proposition.** Pour le cube ($r = -1$, $\gamma = 1$, $V(e) = 0$), partant de $V_0 = 0$ :

$$
V_k(s) = (T^k V_0)(s) = -\min\big(d(s), k\big).
$$

*Preuve, par récurrence.* Pour $s \ne e$ :
$V_{k+1}(s) = \max_a [-1 + V_k(s a)] = -1 - \min_a \min(d(sa), k) = -1 - \min(d(s) - 1, k) = -\min(d(s), k+1)$,
car $\min_a d(sa) = d(s) - 1$. $\square$

Conséquences :

1. L'itération de valeur atteint $V^*$ en $D$ itérations, où $D = \max_s d(s)$ est le **diamètre** du graphe vu depuis $e$ (le « nombre de Dieu » : 20 pour le 3×3 en métrique demi-tour), et se stabilise visiblement à l'itération $D + 1$.
2. À l'itération $k$, seuls les états à distance $k$ changent de valeur : c'est une **vague** qui part de la solution. On n'a donc pas besoin de balayer tout $\mathcal S$ : un **parcours en largeur** (BFS) depuis $e$ calcule exactement la même chose, sphère par sphère. C'est Bellman-Ford dans le cas des coûts unitaires.
3. **Horizon fini.** Avec une troncature à $H$ coups, la valeur optimale est $V^*_H(s) = -\min(d(s), H)$ : au-delà de la distance $H$, toutes les positions se valent ($-H$). Un agent tronqué à 20 coups ne « voit » aucune différence entre deux cubes à distance 25 et 40.

Sur le mini-casse-tête ($D = 3$) :

| État | $V_0$ | $V_1$ | $V_2$ | $V_3$ | $V_4$ |
|---|---|---|---|---|---|
| ABC | 0 | 0 | 0 | 0 | 0 |
| BAC, ACB | 0 | $-1$ | $-1$ | $-1$ | $-1$ |
| BCA, CAB | 0 | $-1$ | $-2$ | $-2$ | $-2$ |
| CBA | 0 | $-1$ | $-2$ | $-3$ | $-3$ |

### 4.7 La malédiction de la dimension (le terme est de Bellman)

Une table de $V$ pour le cube, à un octet par état, occuperait $4{,}3 \times 10^{19}$ octets, soit 43 milliards de Go. Une table $Q$ en `float32` en occuperait 3 milliards de To. Même énumérer les états à $10^6$ par seconde prendrait 1,4 million d'années. La programmation dynamique exacte est hors de portée, d'où les deux voies des chapitres suivants :

- **échantillonner** au lieu de balayer (méthodes sans modèle, chapitre 2) ;
- **approximer** $V$ par une fonction paramétrée qui généralise, et **chercher** autour de l'estimation (chapitre 3).

**Une vérité terrain de taille raisonnable : le 2×2.** Le cube 2×2×2 a le même groupe que les coins du 3×3. En fixant un coin (mouvements U, R, F seulement, 9 actions), il a $7! \cdot 3^6 = 3\,674\,160$ états. Un BFS vectorisé le résout **exactement** en une vingtaine de secondes, avec quelques dizaines de Mo (fiche, étape E) :

| $d$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| états | 1 | 9 | 54 | 321 | 1 847 | 9 992 | 50 136 | 227 536 | 870 072 | 1 887 748 | 623 800 | 2 644 |

Le diamètre est 11. Avec $V^*$ connu partout, le 2×2 sera notre banc d'essai en phase 5 : on pourra mesurer l'erreur d'une valeur **apprise** contre la valeur **exacte**, ce qui est impossible sur le 3×3.

---

## 5. La politique aléatoire comme marche aléatoire

L'agent aléatoire de la phase 4 induit une chaîne de Markov sur $\mathcal G$ : la **marche aléatoire sur le graphe de Cayley**. C'est un objet probabiliste très étudié, et il explique quantitativement l'échec de l'agent.

### 5.1 Propriétés de la chaîne

- **Matrice symétrique.** $P(g, g a) = 1/18$ pour $a \in \mathcal A$, et $\mathcal A = \mathcal A^{-1}$, donc $P(g, h) = P(h, g)$. Elle est bistochastique : **la loi stationnaire est uniforme** sur $\mathcal G$.
- **Irréductible** : $\mathcal A$ engendre $\mathcal G$, par définition de $\mathcal G$.
- **Apériodique** : il y a des cycles de longueur 2 ($R R'$) et de longueur 3 ($R\,R\,R2$), et $\mathrm{pgcd}(2, 3) = 1$.

### 5.2 Le lemme de Kac

Pour une chaîne irréductible récurrente positive, de loi stationnaire $\pi$, le temps moyen de retour en $x$ vaut

$$
\mathbb E_x\big[\tau_x^+\big] = \frac{1}{\pi(x)}.
$$

*Intuition.* Sur une longue trajectoire, la fraction du temps passée en $x$ tend vers $\pi(x)$ (théorème ergodique). Les visites successives découpent le temps en cycles i.i.d. de longueur moyenne $\mathbb E_x[\tau_x^+]$. Une visite par cycle donne la fraction $1 / \mathbb E_x[\tau_x^+]$.

Ici $\pi$ est uniforme, donc $\mathbb E_e[\tau_e^+] = \lvert \mathcal G \rvert$. Le premier pas mène à l'un des 18 états à distance 1, tiré uniformément. On en déduit que **le temps moyen pour résoudre au hasard un cube mélangé d'un seul coup (en moyenne sur ce coup) est $\lvert \mathcal G \rvert - 1 \approx 4{,}3 \times 10^{19}$ coups**, soit environ 1,4 million d'années à un million de coups par seconde. Sur l'hexagone, les deux voisins de ABC sont symétriques : $\mathbb E[\tau^+] = 6 = 1 + 5$.

### 5.3 La croissance des sphères

Nombre d'états à distance $d$ (métrique demi-tour ; cube20.org, lignes 0 à 5 vérifiées avec `cube.py`) :

| $d$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| états | 1 | 18 | 243 | 3 240 | 43 239 | 574 908 | 7 618 438 | 100 803 036 |
| rapport | | 18 | 13,5 | 13,33 | 13,35 | 13,30 | 13,25 | 13,23 |

Le rapport tend vers le **facteur de branchement effectif** des séquences canoniques : environ 13,35. On l'obtient après élimination des coups successifs sur la même face, et en ordonnant les paires de faces opposées, qui commutent (Korf, 1997). La loi des distances d'un état **uniforme** est très concentrée : environ 67 % des états sont à distance 18, 28 % à 17, 3,5 % à 19, 2,5 % à 16 (estimations de cube20.org). Le maximum, 20, ne concerne qu'environ 490 millions d'états.

Pour l'apprentissage, cela veut dire qu'un « cube mélangé » typique est **à 17 ou 18 coups**. Une méthode entraînée sur des mélanges courts subit un fort **décalage de distribution** à l'évaluation.

### 5.4 La dérive vers l'extérieur

Pour un état à distance $d$, on compte combien des 18 coups mènent à $d - 1$, $d$ et $d + 1$. Mesures exhaustives jusqu'à $d = 4$, avec `cube.py` :

| $d$ | vers $d-1$ | vers $d$ | vers $d+1$ |
|---|---|---|---|
| 1 | 1 | 2 | 15 |
| 2 | 1,11 | 2,22 | 14,67 |
| 3 | 1,10 | 2,20 | 14,70 |
| 4 | 1,10 | 2,21 | 14,69 |

(Moyennes sur tous les états de la sphère.) **82 % des coups éloignent**, 6 % rapprochent. En projetant la marche sur la distance, on obtient (approximativement) une chaîne de naissance et de mort à **forte dérive vers l'extérieur**.

**Calcul par la ruine du joueur.** Pour $d \ge 2$, on prend des probabilités constantes : $p \approx 1{,}10/18$ vers l'intérieur et $q \approx 14{,}69/18$ vers l'extérieur. Pour une chaîne infinie de ce type, la probabilité d'atteindre un jour $d - 1$ depuis $d$ vaut $a = p/q \approx 0{,}075$. Depuis la distance 1, en ignorant les pas « sur place » :

$$
h = \frac{1}{16} + \frac{15}{16}\, a\, h \quad \Longrightarrow \quad h = \frac{1/16}{1 - \tfrac{15}{16} a} \approx 6{,}7\ \%.
$$

C'est la probabilité de résoudre **avant de se perdre**. Le reste du temps, la marche part vers les distances 17 et 18 et ne revient qu'au bout d'environ $\lvert \mathcal G \rvert$ coups (section 5.2). Le processus est récurrent au sens mathématique, mais transient à toute échelle de temps utile.

**Limites du modèle agrégé.** La projection sur la distance n'est pas exactement **agrégeable** (*lumpable*, au sens de Kemeny et Snell). Les états d'une même sphère n'ont pas tous le même nombre de coups qui rapprochent : par exemple, `R L` en a deux, car R et L commutent. De plus, les mélanges ne tirent pas ces états uniformément. L'exercice 7 te fait quantifier ces écarts contre tes propres mesures.

### 5.5 Profondeur de mélange et distance

Un mélange de $k$ coups donne un état à distance $\le k$, et la loi de la distance réelle dépend du générateur de mélanges. Avec le nôtre (jamais deux fois la même face de suite), mesuré sur 20 000 mélanges :

| Profondeur $k$ | $P(d = k)$ | $P(d = k-1)$ | $P(d \le k - 2)$ |
|---|---|---|---|
| 3 | 96,0 % | 2,7 % | 1,3 % |
| 4 | 93,0 % | 4,3 % | 2,7 % (dont 0,1 % résolus) |
| 5 | 89,7 % | 5,9 % | 4,5 % |

Les causes sont algébriques : $R L R' = L$ (commutation), $R L R' L' = e$. Pour l'évaluation, il faudra donc **stratifier par distance réelle** quand on la connaît (BFS jusqu'à 5, 2×2 exact), et ne pas confondre « profondeur » et « difficulté ».

---

## 6. L'exploration

### 6.1 Les stratégies classiques

| Stratégie | Principe | Limite |
|---|---|---|
| ε-glouton | une action uniforme avec probabilité ε | exploration « non dirigée » |
| Boltzmann (softmax) | $\pi(a \mid s) \propto \exp(Q(s,a)/\tau)$ | non dirigée aussi |
| optimisme (UCB, R-max, bonus de comptage) | surestimer ce qui est peu visité | demande de reconnaître le « déjà vu » |
| échantillonnage de Thompson, valeurs aléatoires (*randomized value functions*) | agir selon un tirage de la loi a posteriori | exploration « profonde », mais coûteuse |

### 6.2 Le cadenas à combinaison

Considérons une chaîne de $H$ états où une seule action sur $\lvert \mathcal A \rvert$ fait avancer, et où les autres renvoient au départ. La récompense n'est qu'au bout. Une exploration non dirigée (uniforme, ou ε-gloutonne avec des valeurs initiales constantes) a une probabilité $\lvert \mathcal A \rvert^{-H}$ de voir la récompense par épisode. Il lui faut donc **un nombre d'épisodes exponentiel en $H$**. Ce type de construction est à la base des bornes inférieures sur l'exploration non dirigée (voir par exemple Osband et al., 2019).

Le cube est un cadenas de ce genre, encore aggravé par la croissance des sphères. Depuis la distance $d$, réussir en $d$ coups demande de suivre un plus court chemin, ce qui arrive avec une probabilité de l'ordre de $(\text{nombre de plus courts chemins}) / 18^d$.

### 6.3 Pourquoi l'optimisme ne sauve pas

Les bonus de comptage supposent que l'on revisite des états. Ici, presque **chaque état rencontré est nouveau**. Sans généralisation entre états voisins, tous les bonus sont égaux et l'optimisme dégénère en marche aléatoire. Il faut une **structure** : de la généralisation (réseau, chapitre 2) et, surtout, un choix intelligent de $\rho_0$.

### 6.4 Le vrai levier : choisir d'où l'on part

En simulation, **la loi de l'état initial est un paramètre de conception**. C'est rarement le cas dans la vraie vie, mais c'est le cas ici :

- **curriculum** : mélanges de profondeur 1, puis 2, puis 3…, au rythme de la réussite de l'agent (phase 5) ;
- **curriculum inverse** : partir près de la cible, puis s'en éloigner (Florensa et al., 2017) ;
- **échantillonner depuis la cible** : DeepCubeA génère ses états d'entraînement en mélangeant l'état résolu de $k \sim \mathcal U\{1, \dots, K\}$ coups. On n'attend jamais la récompense : on la fabrique (chapitre 3) ;
- **ré-étiquetage des buts** (*hindsight experience replay*, Andrychowicz et al., 2017) : en RL conditionné par un but, un échec vers $g$ est un succès vers l'état atteint. Le groupe rend l'idée triviale. Rejoindre $b$ depuis $a$, c'est résoudre $b^{-1}a$, car $d(a \to b) = d(b^{-1} a)$. Toute trajectoire est donc une démonstration de résolution d'un autre cube.

---

## 7. Concevoir la récompense

### 7.1 Deux récompenses, une même politique optimale

- $r = -1$ par coup, $\gamma = 1$ : $V^*(s) = -d(s)$.
- $r = \mathbb 1[s' = e]$, $\gamma < 1$ : $V^*(s) = \gamma^{d(s) - 1}$ pour $s \ne e$.

Dans les deux cas, $V^*$ est une fonction **strictement décroissante** de $d$, donc les politiques gloutonnes coïncident. Avec $r = \mathbb 1[s' = e]$ et $\gamma = 1$, en revanche, toutes les politiques propres ont la même valeur : il n'y a plus de pression vers les solutions courtes.

### 7.2 Le théorème du *shaping* par potentiel

On veut ajouter une récompense « d'aide » $F$ sans changer les politiques optimales. Théorème (Ng, Harada et Russell, 1999) : si

$$
F(s, a, s') = \gamma \Phi(s') - \Phi(s)
$$

pour une fonction **potentiel** $\Phi : \mathcal S \to \mathbb R$ (avec $\Phi = 0$ sur les états terminaux), alors le MDP modifié a les mêmes politiques optimales. Et, sans hypothèse supplémentaire sur le MDP, cette forme est la seule qui garantisse cette invariance.

*Idée de la preuve.* Le long d'une trajectoire, $\sum_t \gamma^t F = \gamma^{T}\Phi(S_T) - \Phi(S_0)$ : la somme est **télescopique**. Donc $Q'^{\pi}(s, a) = Q^\pi(s, a) - \Phi(s)$ pour toute politique. Le terme retranché ne dépend pas de l'action : l'argmax est inchangé. $\square$

Wiewiora (2003) a montré que ce *shaping* équivaut à **initialiser** $Q$ avec $\Phi$. Avec $\Phi = -h$, où $h$ est une heuristique de distance, on retrouve l'idée d'A\* : guider la recherche avec une estimation du coût restant.

### 7.3 Un mauvais *shaping* : « le nombre de cases bien placées »

Soit $c(s)$ le nombre de cases de la couleur de leur centre. Deux usages possibles :

**(a) Comme récompense, $r = c(s')$.** Les récompenses positives créent des **cycles profitables**. Depuis l'état `R` ($c = 42$), l'agent peut jouer `R2`, `R2`, `R2`… et ne visiter que `R'` et `R` (42 cases bien placées chacun). Avec $\gamma = 0{,}99$, ce cycle rapporte $42/(1-\gamma) = 4200$, contre 54 pour la résolution (épisode terminé). **La politique optimale ne résout jamais.** C'est un cas d'école de *reward hacking*.

**(b) Comme potentiel, $\Phi = c$.** Sans danger, d'après le théorème. Mais est-ce utile ? Mesures avec `cube.py` :

| Cube | Cases mal placées ($54 - c$) | $d$ |
|---|---|---|
| `R` | 12 | 1 |
| `R U R' U'` | 12 | 4 |
| `R L` | 24 | 2 |
| superflip | 24 | 20 |

Moyenne de $54 - c$ par sphère : 21,8 ; 28,5 ; 31,6 ; 33,9 pour $d = 2, \dots, 5$. Mais le **minimum** reste à 12 jusqu'à $d = 5$, et le superflip (le premier état dont on a prouvé qu'il est à 20 coups) ne vaut pas mieux que `R L`. $\Phi = c$ est un potentiel **faiblement informatif** : il ne nuit pas, mais il n'aide guère. **Un bon potentiel, c'est une bonne estimation de $-d$**, et c'est précisément ce qu'on cherche à apprendre.

---

## 8. Évaluer un agent : de la statistique, pas des anecdotes

### 8.1 Un taux de réussite est une proportion binomiale

Avec $k$ succès sur $n$ épisodes i.i.d., l'intervalle de **Wilson** à 95 % ($z = 1{,}96$) vaut

$$
\frac{\hat p + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat p (1 - \hat p)}{n} + \frac{z^2}{4 n^2}}}{1 + \frac{z^2}{n}}.
$$

Contrairement à l'intervalle de Wald $\hat p \pm z \sqrt{\hat p(1-\hat p)/n}$, il reste valide pour des $\hat p$ proches de 0, ce qui est notre cas. Exemples :

| $k / n$ | $\hat p$ | Wilson 95 % |
|---|---|---|
| 6 824 / 100 000 | 6,82 % | [6,67 % ; 6,98 %] |
| 605 / 100 000 | 0,605 % | [0,56 % ; 0,66 %] |
| 7 / 100 000 | 0,007 % | [0,0034 % ; 0,0145 %] |

**Règle de trois.** Avec 0 succès sur $n$ essais, la borne supérieure unilatérale à 95 % vaut environ $3/n$.

**Taille d'échantillon.** Pour une précision relative $\delta$ (par exemple ±30 %) à 95 %, il faut $n \approx 4(1 - p) / (\delta^2 p)$. Pour $p = 0{,}05\ \%$ et $\delta = 0{,}3$, cela donne environ 89 000 épisodes.

### 8.2 Stratifier et comparer

- **Stratifier par difficulté réelle** (distance, si on la connaît) plutôt que par profondeur de mélange : la loi de mélange de la section 5.5 suffit à expliquer une grande partie des réussites « aux grandes profondeurs ».
- **Comparer deux agents sur les mêmes cubes** (nombres aléatoires communs) : l'appariement réduit fortement la variance de la différence. En phase 7, un **jeu de test fixe** de cubes mélangés, versionné, servira à tous les agents.
- **Plusieurs graines d'entraînement.** La variabilité entre graines est souvent du même ordre que les écarts entre méthodes. Il faut la rapporter, et agréger proprement : moyenne interquartile, intervalles par bootstrap stratifié (Henderson et al., 2018 ; Agarwal et al., 2021).

### 8.3 Reproductibilité

Une expérience est définie par un commit, une commande et des graines. Toute source d'aléa (environnement, agent, `action_space.sample`, initialisation des réseaux) doit être contrôlée.

---

## 9. Feuille de route : ce que les chapitres 2 et 3 développeront

### 9.1 Prédiction sans modèle (chapitre 2)

- **Monte-Carlo** : $V(s) \leftarrow V(s) + \alpha\,(G_t - V(s))$. Estimateur sans biais de $V^\pi$, mais de forte variance (somme de nombreux termes aléatoires).
- **TD(0)** : $V(s) \leftarrow V(s) + \alpha\,\big(r + \gamma V(s') - V(s)\big)$. La cible utilise l'estimation courante (*bootstrap*) : elle est biaisée, mais de variance bien plus faible. C'est une version stochastique de $T^\pi$.
- $n$ pas, TD(λ) : un continuum biais / variance entre les deux.

### 9.2 Contrôle sans modèle (chapitre 2)

- **SARSA** (on-policy) : cible $r + \gamma Q(s', a')$ avec $a' \sim \pi$.
- **Q-learning** (off-policy) : cible $r + \gamma \max_{a'} Q(s', a')$. Version stochastique de $T$ appliquée à $Q$.

  Convergence presque sûre vers $Q^*$ en tabulaire (Watkins et Dayan, 1992). Il faut que chaque couple $(s,a)$ soit visité infiniment souvent, et que les pas vérifient les conditions de Robbins-Monro : $\sum_t \alpha_t = \infty$, $\sum_t \alpha_t^2 < \infty$.
- **Biais de maximisation** : $\mathbb E[\max_a \hat Q] \ge \max_a \mathbb E[\hat Q]$ (Jensen). Le Q-learning surestime. **Double Q-learning** (van Hasselt, 2010) découple le choix de l'action et son évaluation.

### 9.3 Approximation de fonctions (chapitre 2)

- **TD semi-gradient** avec $Q_\theta$ : on ne dérive pas à travers la cible.
- **La triade mortelle** (Sutton et Barto, chapitre 11) : approximation + bootstrap + off-policy peut **diverger** (contre-exemple de Baird, 1995).
- **DQN** (Mnih et al., 2015) stabilise par un *replay buffer* (données moins corrélées) et un **réseau cible** gelé. Puis viennent Double DQN, perte de Huber, etc.
- **Le point de vue du statisticien : *fitted Q-iteration*** (Ernst et al., 2005 ; Riedmiller, 2005). Chaque itération est une **régression supervisée** de la cible de Bellman, calculée avec le modèle précédent : $Q_{k+1} = \arg\min_Q \sum_i \big(Q(s_i, a_i) - r_i - \gamma \max_{a'} Q_k(s'_i, a')\big)^2$. C'est l'itération de valeur où l'on remplace $T$ par « $T$ puis projection sur une classe de fonctions ». La convergence n'est plus garantie : la projection n'est pas une contraction en norme infinie.

### 9.4 Gradient de politique (pour la culture : peu adapté au cube)

- **Théorème du gradient de politique** (Sutton et al., 2000) : $\nabla_\theta J(\theta) = \mathbb E^{\pi_\theta}\big[\sum_t \nabla_\theta \log \pi_\theta(A_t \mid S_t)\,(G_t - b(S_t))\big]$.
- **REINFORCE** (Williams, 1992) : c'est l'**estimateur du score**, ou du rapport de vraisemblance, bien connu en statistique. La *baseline* $b$ est une **variable de contrôle** : elle ne change pas l'espérance et réduit la variance.
- **Acteur-critique**, **GAE** (Schulman et al., 2016), **PPO** (Schulman et al., 2017).

Pourquoi pas pour le cube ? Les gradients de politique brillent avec des actions continues, des modèles inconnus et des récompenses denses. Ici, tout est discret et déterministe, le modèle est parfait, et la récompense est terminale et rare. Les méthodes par valeur combinées à la recherche dominent.

### 9.5 Planifier avec une valeur apprise (chapitre 3)

- **A\*** avec $f = g + h$. Si $h$ est **admissible** ($h \le d$), la solution est optimale. **A\* pondéré** ($f = g + w h$, $w > 1$) : coût au plus $w$ fois l'optimum si $h$ est admissible, et beaucoup moins de nœuds explorés. **Recherche en faisceau**, **MCTS / UCT** (Kocsis et Szepesvári, 2006 ; la famille AlphaZero).
- **DeepCube** (McAleer et al., 2018) : *autodidactic iteration* (ADI) puis MCTS.
- **DeepCubeA** (Agostinelli et al., 2019) : *deep approximate value iteration* (DAVI), une itération de valeur ajustée sur des états tirés en mélangeant l'état résolu, avec un réseau cible. On le combine avec un A\* pondéré par lots (BWAS, $f = \lambda g + h$ avec $\lambda = 0{,}6$, $N = 10\,000$ nœuds développés par itération). Entrée : *one-hot* 54 × 6 = 324. Résultats : **100 %** des cubes de test résolus, et un plus court chemin trouvé dans **60,3 %** des cas.
- **EfficientCube** (Takano, TMLR 2023) : un réseau prédit simplement **le dernier coup d'un mélange aléatoire** (classification supervisée, donc auto-supervisée), et une recherche en faisceau utilise ces probabilités. Les auteurs rapportent un meilleur compromis que DeepCubeA : 69,6 % de solutions optimales contre 65,0 %, avec environ deux fois moins de nœuds développés. Ces deux travaux utilisent la métrique « quart de tour » (12 actions). Leçon : sur un problème au modèle connu, un apprentissage **supervisé sur des données générées depuis la cible** peut battre une procédure de RL plus élaborée.

| Idée | Où dans le projet |
|---|---|
| Q-learning tabulaire, curriculum | phase 5 (et sa limite mémoire, mesurable sur le 2×2) |
| DQN sur le 3×3, mélanges courts | phase 5 |
| DAVI + A\* pondéré | phase 6 |
| prédiction du dernier coup + faisceau | phase 6 ou 7, en comparaison |
| statistiques d'évaluation, jeu de test fixe | phase 7 |

---

## 10. Résumé

1. Un MDP est un tuple $(\mathcal S, \mathcal A, P, r, \gamma, \rho_0)$. Pour un MDP fini, il existe une politique optimale markovienne, stationnaire et déterministe.
2. Le cube est un **plus court chemin déterministe sur le graphe de Cayley** de son groupe ($\lvert \mathcal G \rvert \approx 4{,}3 \times 10^{19}$, 18 générateurs, $\gamma = 1$, récompense $-1$) : $V^* = -d$.
3. Les équations de Bellman caractérisent $V^\pi$ (système linéaire) et $V^*$ (point fixe d'un opérateur monotone, contractant pour $\gamma < 1$).
4. Itération de politique et itération de valeur convergent. Pour le cube, $T^k 0 = -\min(d, k)$ : l'itération de valeur **est** un BFS, et le nombre de Dieu (20) est le nombre d'itérations utiles.
5. Terminé et tronqué sont deux objets différents : la troncature n'est pas une absorption.
6. La politique aléatoire est une marche aléatoire de loi stationnaire uniforme. Le lemme de Kac donne $\lvert \mathcal G \rvert$ coups en moyenne pour revenir à la solution.
7. Les sphères croissent d'un facteur d'environ 13,35, 82 % des coups éloignent, et la probabilité de résoudre « avant de se perdre » depuis la distance 1 est d'environ 6,7 % (ruine du joueur).
8. L'exploration non dirigée coûte un temps exponentiel en la profondeur. Le levier propre au cube est le **choix de la loi initiale** (curriculum, échantillonnage depuis la cible, ré-étiquetage).
9. Seul le *shaping* par potentiel préserve les politiques optimales. « Le nombre de cases bien placées » comme récompense mène au *reward hacking*, et comme potentiel il est peu informatif.
10. Évaluer, c'est estimer : intervalles de Wilson, règle de trois, stratification, appariement, plusieurs graines.

---

## 11. Glossaire français / anglais

| Français | Anglais |
|---|---|
| processus de décision markovien | Markov decision process (MDP) |
| plus court chemin stochastique | stochastic shortest path (SSP) |
| politique propre / impropre | proper / improper policy |
| retour, facteur d'actualisation | return, discount factor |
| fonction de valeur d'état / d'action, avantage | state-value / action-value function, advantage |
| opérateur de Bellman, contraction | Bellman operator, contraction |
| évaluation, amélioration, itération de politique | policy evaluation, improvement, iteration |
| itération de valeur | value iteration |
| matrice fondamentale | fundamental matrix |
| graphe de Cayley | Cayley graph |
| temps de retour, temps d'atteinte | return time, hitting time |
| facteur de branchement effectif | effective branching factor |
| exploration non dirigée / profonde | undirected (dithering) / deep exploration |
| cadenas à combinaison | combination lock |
| ré-étiquetage a posteriori | hindsight relabeling (HER) |
| *shaping* par potentiel | potential-based reward shaping |
| détournement de récompense | reward hacking |
| amorçage (cible estimée) | bootstrapping |
| triade mortelle | deadly triad |
| itération Q ajustée | fitted Q-iteration |
| estimateur du score | score-function / likelihood-ratio estimator |
| heuristique admissible / cohérente | admissible / consistent heuristic |

---

## 12. Exercices

Les exercices marqués **[code]** se font avec le code de la phase 4 (fiche, étapes C à F).

**1. Contraction.** Montre que $T^\pi$ est une $\gamma$-contraction en norme infinie, et que $T^\pi$ et $T$ sont monotones. En déduire l'unicité de $V^\pi$.

**2. Amélioration de politique.** Rédige la preuve complète du théorème 4.2, en justifiant le passage à la limite. Montre que si l'amélioration gloutonne laisse $\pi$ inchangée, alors $V^\pi = V^*$.

**3. Itération de valeur sur le cube.** Démontre $T^k 0 = -\min(d, k)$. Combien d'itérations utiles pour le 3×3 (métrique demi-tour) ? pour le 2×2 à coin fixé ? Que vaut $V^*_H$ pour une troncature à $H$ coups, et quelle conséquence pour un agent tronqué à 20 coups ?

**4. Matrice fondamentale.** [code] Pour le mini-casse-tête et la politique uniforme, calcule $N = (I - Q)^{-1}$ avec numpy et retrouve $(5, 5, 8, 8, 9)$. Calcule ensuite, par puissances de la matrice de transition, la probabilité de résoudre CBA en au plus 20 coups. Compare avec une simulation.

**5. Kac.** Vérifie le lemme sur l'hexagone (temps de retour moyen 6). Pour le cube, déduis-en le temps moyen d'atteinte de $e$ depuis la distance 1, en moyenne sur les 18 états à distance 1. Ces 18 états sont-ils tous équivalents par symétrie ? (Indice : un quart de tour peut-il être l'image d'un demi-tour par une symétrie du cube ?)

**6. Ruine du joueur.** Pour une chaîne de naissance et de mort sur $\mathbb N$, de probabilités constantes $p$ (vers le bas) et $q > p$ (vers le haut), montre que la probabilité d'atteindre $d - 1$ depuis $d$ vaut $p/q$. Retrouve $h \approx 6{,}7\ \%$, et compare avec la mesure de la phase 4.

**7. Modèle agrégé et ses limites.** [code] Construis la chaîne sur les distances avec les probabilités du tableau 5.4. Pour $d \ge 5$, reprends celles de $d = 4$. Calcule la probabilité de résoudre en au plus 20 coups depuis $d = 1, 2, 3$. Prédis ensuite la réussite pour des **mélanges** de 3 coups, comme un mélange sur la distance réelle (tableau 5.5). Compare avec tes mesures, et explique l'écart résiduel : agrégeabilité, et tirage non uniforme des états d'une sphère par le générateur de mélanges.

**8. L'ordre du groupe.** Justifie la formule de $\lvert \mathcal G \rvert$. Pourquoi un cube remonté au hasard n'est-il résoluble qu'avec probabilité $1/12$ ?

**9. Récompenses équivalentes.** Montre que $r = -1, \gamma = 1$ et $r = \mathbb 1[s' = e], \gamma \in (0, 1)$ ont les mêmes politiques optimales. Qu'est-ce qui casse pour $r = \mathbb 1[s' = e], \gamma = 1$ ?

**10. *Shaping*.** (a) Démontre l'invariance de l'argmax sous un *shaping* par potentiel. (b) Avec $r = c(s')$ et $\gamma = 0{,}99$, compare la valeur du cycle `R2` répété depuis l'état `R` à celle de la résolution par `R'`. (c) Pourquoi $\Phi = c$ est-il sans danger, mais peu utile ?

**11. Statistique.** (a) Intervalle de Wilson pour 7 succès sur 100 000. (b) 0 succès sur 2 000 épisodes : que peux-tu affirmer ? (c) Combien d'épisodes pour mesurer $p \approx 0{,}02\ \%$ à ±25 % près ?

**12. Troncature et *bootstrap*.** Écris la cible TD correcte pour une transition qui termine l'épisode, puis pour une transition qui le tronque. Quel biais introduirait $V(s') = 0$ dans le second cas ?

**13. Symétries.** Montre que $d(s^{-1}) = d(s)$. Les 48 symétries du cube agissent par conjugaison et préservent $d$. Quel facteur d'augmentation de données cela offre-t-il au plus pour l'apprentissage de $V$ ? Comment le traduire en contrainte sur l'architecture (équivariance) ?

**14. Décalage de distribution.** On entraîne une estimation de $V$ sur des mélanges de profondeur uniforme dans $\{1, \dots, 30\}$, puis on l'évalue sur des états uniformes de $\mathcal G$. Quelle est la loi des distances dans chacun des cas ? Quels risques, et quelles parades ?

---

## 13. Corrigés

**1.** $\lvert (T^\pi V - T^\pi W)(s) \rvert = \gamma \lvert \sum_{a, s'} \pi(a \mid s) P(s' \mid s, a) (V - W)(s') \rvert \le \gamma \lVert V - W \rVert_\infty$, car les poids somment à 1. Monotonie : les poids sont positifs (et, pour $T$, le max est croissant). Unicité : deux points fixes $V, W$ vérifient $\lVert V - W \rVert \le \gamma \lVert V - W \rVert$, donc $V = W$.

**2.** En itérant, $V^\pi(s) \le \mathbb E^{\pi'}\big[\sum_{t<k} \gamma^t R_{t+1}\big] + \gamma^k \mathbb E^{\pi'}[V^\pi(S_k)]$. Le second terme est borné par $\gamma^k \lVert V^\pi \rVert_\infty \to 0$ ; le premier tend vers $V^{\pi'}(s)$ par convergence dominée. Si $\pi$ est stable par amélioration gloutonne, alors $V^\pi(s) = \max_a Q^\pi(s, a)$ : $V^\pi$ est un point fixe de $T$, donc $V^\pi = V^*$.

**3.** Récurrence de la section 4.6. Itérations utiles : $D = 20$ pour le 3×3, stabilité constatée à la 21ᵉ ; $D = 11$ pour le 2×2, stabilité à la 12ᵉ. $V^*_H = -\min(d, H)$ : avec $H = 20$, tous les états à distance $\ge 20$ ont la même valeur. Et surtout, un agent qui n'a jamais résolu observe $-H$ partout : aucun signal pour distinguer les états.

**4.** $N\mathbf 1 = (5, 5, 8, 8, 9)$. Avec la matrice de transition $6 \times 6$ (ABC absorbant), la probabilité d'absorption en au plus 20 pas depuis CBA vaut environ 0,925.

**5.** Hexagone : 6. Cube : $\mathbb E_e[\tau_e^+] = 1 + \frac{1}{18}\sum_{a \in \mathcal A} \mathbb E_{a}[\tau_e] = \lvert \mathcal G \rvert$, donc la moyenne des 18 temps d'atteinte vaut $\lvert \mathcal G \rvert - 1$. Les 18 états à distance 1 forment **deux** classes. Les 48 symétries du cube agissent par conjugaison, préservent $e$ et l'ensemble des générateurs, donc la loi de la marche. Les rotations envoient une face sur n'importe quelle autre, et les réflexions échangent $X$ et $X'$ : les 12 quarts de tour sont équivalents. Mais une conjugaison préserve l'ordre d'un élément : un demi-tour (ordre 2) n'est jamais l'image d'un quart de tour (ordre 4). Les 6 demi-tours forment l'autre classe. Les deux temps moyens sont tous deux de l'ordre de $\lvert \mathcal G \rvert$.

**6.** Soit $a$ la probabilité cherchée, qui ne dépend pas de $d$ par homogénéité. Après un pas vers le haut, il faut redescendre deux fois ; les pas sur place ne changent rien. Donc $a = \tfrac{p}{p+q} + \tfrac{q}{p+q} a^2$, dont les racines sont $1$ et $p/q$. Pour $q > p$, la bonne racine est la plus petite, $p/q$ (car la marche est transiente). Avec $p/q \approx 1{,}10/14{,}69$, on trouve $h \approx 0{,}0672$, cohérent avec une mesure d'environ 6,8 % (intervalle de Wilson [6,67 ; 6,98] sur 100 000 épisodes).

**7.** Le modèle donne environ 6,7 %, 0,51 % et 0,038 % pour $d = 1, 2, 3$. Pour des mélanges de 3 coups : $0{,}013 \times 6{,}7 + 0{,}027 \times 0{,}51 + 0{,}96 \times 0{,}038 \approx 0{,}14\ \%$. Les mesures typiques sont d'environ 0,6 % à la profondeur 2 et 0,17 % à la profondeur 3. Le modèle explique l'essentiel (la contribution des mélanges « effondrés » domine à la profondeur 3), mais il sous-estime. En effet, les états à fort nombre de coups « rapprochants » (paires qui commutent, comme `R L`) sont **plus probables** sous le générateur de mélanges (`R L` et `L R` mènent au même état), et l'agrégation suppose à tort une sphère homogène.

**8.** 8 coins : $8!$ permutations, $3^8$ orientations ; 12 arêtes : $12!$ et $2^{12}$. Les mouvements de faces préservent trois invariants : la somme des torsions des coins mod 3, la somme des retournements des arêtes mod 2, et l'égalité des parités des permutations des coins et des arêtes. Chacun divise l'ensemble atteignable par 3, 2 et 2. Inversement, on montre que tout état vérifiant les trois invariants est atteignable. Un remontage uniforme satisfait les trois avec probabilité $1/(3 \cdot 2 \cdot 2) = 1/12$.

**9.** Les deux $V^*$ sont des fonctions strictement décroissantes de $d$, et $Q^*(s, a)$ est une fonction strictement décroissante de $d(sa)$ dans les deux cas : mêmes argmax. Avec $\gamma = 1$ et une récompense terminale seule, $V^* \equiv 1$ sur les états d'où une politique propre existe, donc toutes les actions qui ne rendent pas la politique impropre se valent.

**10.** (a) Section 7.2. (b) Le cycle rapporte $42/(1 - 0{,}99) = 4200$ ; la résolution rapporte 54, puis s'arrête. L'agent optimal ne résout jamais. (c) Avec un potentiel, les retours modifiés diffèrent des retours originaux de $-\Phi(S_0)$ (plus un terme nul à l'absorption) : mêmes politiques optimales. Mais $c$ est mal corrélé à $d$ (minimum de 12 cases mal placées jusqu'à $d = 5$, superflip), donc l'aide à l'exploration est faible.

**11.** (a) Environ [0,0034 % ; 0,0145 %]. (b) $p < 3/2000 = 0{,}15\ \%$ à 95 % (unilatéral). (c) $n \approx 4(1-p)/(\delta^2 p) = 4 / (0{,}0625 \times 0{,}0002) \approx 320\,000$.

**12.** Terminée : $y = r$. Tronquée : $y = r + \gamma V(s')$, car l'état $s'$ n'est pas absorbant. Prendre $V(s') = 0$ dans le cas tronqué revient à prétendre que l'épisode s'arrête « naturellement ». Avec $r = -1$, comme $V(s') < 0$, cela **surestime** la valeur des états souvent rencontrés à la limite de temps : l'agent serait attiré par des états qui ne sont bons qu'en apparence.

**13.** Si $s \cdot w = e$ avec $\lvert w \rvert = d$, alors $s^{-1} = w$, donc $s^{-1} \cdot w^{-1} = e$ avec $\lvert w^{-1} \rvert = d$ : par symétrie, $d(s^{-1}) = d(s)$. Le groupe engendré par les 48 symétries et l'inversion a au plus $48 \times 2 = 96$ éléments, d'où une augmentation d'au plus un facteur 96 (moins pour les états symétriques). On peut aussi contraindre le réseau à être invariant, par exemple en moyennant sur les symétries ou par une architecture équivariante.

**14.** Entraînement : un mélange des lois « distance d'un mélange de $k$ coups », avec une masse importante aux petites distances et une saturation vers 17-18 au-delà de $k \approx 20$. Test : environ 67 % à 18, 28 % à 17. Risques : un réseau mal calibré dans la zone 15-20, qui est pourtant celle qui compte, et une erreur d'estimation qui se propage à la recherche. Parades : tirer $k$ jusqu'à 30 (comme DeepCubeA), surpondérer les grandes profondeurs, mesurer l'erreur **par distance** sur le 2×2 où $d$ est connue.

---

## 14. Références

**Manuels**
- R. Sutton, A. Barto, *Reinforcement Learning: An Introduction*, 2ᵉ éd., MIT Press, 2018. Gratuit : <http://incompleteideas.net/book/the-book-2nd.html>. Chapitres 3-4 ici ; 5-6, 9-11 et 13 pour la suite.
- M. Puterman, *Markov Decision Processes*, Wiley, 1994 (preuves, critères d'arrêt).
- D. Bertsekas, J. Tsitsiklis, *An analysis of stochastic shortest path problems*, Math. of Operations Research, 1991 ; D. Bertsekas, *Reinforcement Learning and Optimal Control*, 2019.
- J. Kemeny, J. L. Snell, *Finite Markov Chains*, 1960 (chaînes absorbantes, agrégeabilité) ; D. Levin, Y. Peres, E. Wilmer, *Markov Chains and Mixing Times* (lemme de Kac, marches sur les groupes).

**Articles cités**
- S. Singh, R. Yee, *An upper bound on the loss from approximate optimal-value functions*, Machine Learning, 1994.
- A. Ng, D. Harada, S. Russell, *Policy invariance under reward transformations*, ICML 1999 ; E. Wiewiora, *Potential-based shaping and Q-value initialization are equivalent*, JAIR, 2003.
- F. Pardo et al., *Time Limits in Reinforcement Learning*, ICML 2018.
- R. Korf, *Finding optimal solutions to Rubik's Cube using pattern databases*, AAAI 1997.
- I. Osband et al., *Deep Exploration via Randomized Value Functions*, JMLR, 2019.
- C. Florensa et al., *Reverse Curriculum Generation for Reinforcement Learning*, CoRL 2017 ; M. Andrychowicz et al., *Hindsight Experience Replay*, NeurIPS 2017.
- C. Watkins, P. Dayan, *Q-learning*, Machine Learning, 1992 ; H. van Hasselt, *Double Q-learning*, NeurIPS 2010 ; L. Baird, *Residual algorithms*, ICML 1995.
- V. Mnih et al., *Human-level control through deep reinforcement learning*, Nature, 2015 ; D. Ernst et al., *Tree-based batch mode RL*, JMLR, 2005 ; M. Riedmiller, *Neural fitted Q iteration*, ECML 2005.
- R. Williams, *Simple statistical gradient-following algorithms*, Machine Learning, 1992 ; R. Sutton et al., *Policy gradient methods for RL with function approximation*, NeurIPS 2000 ; J. Schulman et al., *GAE*, ICLR 2016, et *PPO*, 2017.
- L. Kocsis, C. Szepesvári, *Bandit based Monte-Carlo planning*, ECML 2006.
- S. McAleer et al., *Solving the Rubik's Cube Without Human Knowledge*, 2018, <https://arxiv.org/abs/1805.07470>.
- F. Agostinelli et al., *Solving the Rubik's cube with deep reinforcement learning and search*, Nature Machine Intelligence, 2019, <https://doi.org/10.1038/s42256-019-0070-z>. Version libre : <https://deepcube.igb.uci.edu/static/files/SolvingTheRubiksCubeWithDeepReinforcementLearningAndSearch_Final.pdf>.
- K. Takano, *Self-Supervision is All You Need for Solving Rubik's Cube*, TMLR 2023, <https://arxiv.org/abs/2106.03157>.
- P. Henderson et al., *Deep Reinforcement Learning that Matters*, AAAI 2018 ; R. Agarwal et al., *Deep RL at the Edge of the Statistical Precipice*, NeurIPS 2021.
- T. Rokicki, H. Kociemba, M. Davidson, J. Dethridge : nombre de Dieu et distribution des distances, <https://www.cube20.org/>.

**Outils**
- Gymnasium : <https://gymnasium.farama.org/introduction/basic_usage/> et <https://gymnasium.farama.org/introduction/create_custom_env/>.
