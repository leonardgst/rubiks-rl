# Cours de RL — 1. Les bases, avec un Rubik's Cube

> **Emplacement dans le repo :** `docs/cours/rl-1-les-bases.md`
> **Pour qui :** quelqu'un qui n'a jamais fait de reinforcement learning (RL). Pas de maths au-delà des moyennes et des puissances.
> **Durée :** 2 à 3 heures de lecture, plus 1 à 2 heures d'exercices, en plusieurs fois.
> **Comment le lire :** dans l'ordre, avec un crayon. Les encadrés « Pour les curieux » sont facultatifs : saute-les à la première lecture. Les exercices sont en section 15 et leurs corrigés en section 16. Essaie vraiment avant de regarder.
> **Fiche associée :** `docs/fiches/phase-4-cours-rl-environnement.md`.

---

## 0. La carte du cours

```
 1. Apprendre par essais et erreurs        ← l'idée
 2. La boucle agent / environnement         ← le vocabulaire
 3. Le retour : ce que l'agent cherche à maximiser
 4. La politique : sa stratégie
 5. Un mini-casse-tête à 3 jetons           ← notre laboratoire, entièrement à la main
 6. La valeur : « combien vaut cette position ? »
 7. L'équation de Bellman                   ← LA relation du RL
 8. Calculer la valeur : l'itération de valeur
 9. Explorer ou exploiter
10. Qui a mérité la récompense ?
11. Pourquoi le Rubik's Cube est si difficile
12. Ce qui va nous sauver (phases 5 et 6)
13. Résumé en 10 phrases
14. Glossaire français / anglais
15. Exercices
16. Corrigés
17. Pour aller plus loin
```

Le fil rouge : à la fin, tu dois pouvoir expliquer à quelqu'un **pourquoi un agent qui joue au hasard ne résoudra jamais un Rubik's Cube**, et **ce qu'il faudrait pour qu'un agent apprenne**.

---

## 1. Apprendre par essais et erreurs

### L'idée

Personne ne t'a appris à faire du vélo en te donnant, à chaque instant, l'angle exact du guidon. Tu as essayé, tu es tombé, tu as recommencé. Petit à petit, tu as gardé ce qui marchait. Le seul « professeur » était le résultat : **je roule** ou **je tombe**.

Le reinforcement learning (en français : **apprentissage par renforcement**), c'est exactement ça, pour un programme :

- il **essaie** des actions ;
- il reçoit un **score** (une récompense) qui dit si c'était bien ;
- il **ajuste** sa façon de jouer pour obtenir plus de points la prochaine fois.

On parle de « renforcement » comme en dressage : on renforce les comportements qui rapportent une récompense.

### Ce qui le distingue des autres apprentissages

| | Apprentissage supervisé | Reinforcement learning |
|---|---|---|
| Ce qu'on donne au programme | des exemples **avec la bonne réponse** (« ici, il fallait jouer R' ») | seulement un **score**, souvent tardif (« résolu en 12 coups », ou « pas résolu ») |
| Quand arrive l'information | tout de suite, pour chaque exemple | parfois très tard, après une longue suite d'actions |
| D'où viennent les données | d'un jeu de données fixé à l'avance | **de l'agent lui-même** : ce qu'il voit dépend de ce qu'il a joué |
| Exemple | reconnaître un chat sur une photo | apprendre à jouer à un jeu vidéo en ne voyant que le score |

La troisième ligne est importante : en RL, un agent qui joue mal **ne voit que des situations de mauvais joueur**. Il ne peut pas apprendre ce qu'il ne rencontre jamais. On y reviendra (section 9).

### Une remarque honnête sur le cube

Il existe déjà d'excellents programmes qui résolvent le Rubik's Cube sans aucun apprentissage (par exemple la bibliothèque `kociemba`, notre référence de la phase 7). Le RL n'est donc pas le moyen le plus simple de résoudre un cube. Mais c'est un **terrain d'entraînement idéal** pour apprendre le RL :

- les règles sont parfaitement connues et simulées par `cube.py` ;
- on sait toujours vérifier si l'agent a réussi ;
- la difficulté est réglable : un cube mélangé de 1 coup est facile, de 20 coups extrêmement dur.

---

## 2. La boucle agent / environnement

### Le schéma

Tout le RL tient dans une boucle :

```
                    action  (ex. « R' »)
        ┌──────────────────────────────────────────┐
        │                                          ▼
   ┌─────────┐                             ┌───────────────┐
   │  AGENT  │                             │ ENVIRONNEMENT │
   │ (choisit│                             │ (le cube, ses │
   │ le coup)│                             │ règles, et le │
   └─────────┘                             │    juge)      │
        ▲                                  └───────────────┘
        │                                          │
        └──────────────────────────────────────────┘
          nouvel état (le cube après le coup)
          + récompense (ex. -1)
          + « c'est fini ? »
```

À chaque **pas de temps** (numéroté t = 0, 1, 2…) :

1. l'agent regarde l'**état** du monde ;
2. il choisit une **action** ;
3. l'environnement applique l'action et renvoie le **nouvel état** et une **récompense** ;
4. on recommence, jusqu'à la fin de l'**épisode**.

### Le vocabulaire, avec le cube

| Notion | En mots simples | Pour notre cube | Dans le code (Gymnasium) |
|---|---|---|---|
| **Agent** | celui qui décide | le « cerveau » qui choisit le prochain coup. **Ce n'est pas le cube !** | une classe à toi, avec une méthode du genre `act(observation)` |
| **Environnement** | tout le reste : le monde, ses règles, le juge | le cube, les 18 mouvements, la règle « résolu = gagné » | une classe qui hérite de `gymnasium.Env` |
| **État** | la situation à un instant | les couleurs des 54 cases | l'**observation** renvoyée par `reset` et `step` |
| **Action** | un choix possible | un des 18 mouvements `U U' U2 R R' R2 …` | un entier de 0 à 17 |
| **Récompense** | un nombre qui note le dernier pas | -1 par coup joué (notre choix, section 3) | le 2ᵉ élément renvoyé par `step` |
| **Transition** | ce que devient l'état après une action | `cube.move("R")` : le cube après R | le travail de `step` |
| **Épisode** | une partie complète | du mélange jusqu'à « résolu » ou jusqu'à l'abandon | de `reset()` jusqu'à la fin |

### Un épisode, pas à pas

L'environnement mélange le cube avec `F R`. **L'agent ne voit pas ce mélange** : il voit seulement le cube mélangé.

```
t = 0   état s0 = cube mélangé
        l'agent joue U    → récompense -1, état s1        (mauvais coup)
t = 1   l'agent joue U'   → récompense -1, état s2 = s0   (il annule son erreur)
t = 2   l'agent joue R'   → récompense -1, état s3
t = 3   l'agent joue F'   → récompense -1, état s4 = RÉSOLU → fin de l'épisode
```

Total des récompenses : **-4**. Le meilleur possible était **-2** (R' puis F').

### Deux façons de finir : « terminé » ou « tronqué »

Un épisode peut s'arrêter pour deux raisons très différentes :

- **terminé** (*terminated*) : le jeu est vraiment fini. Le cube est résolu. Il n'y a plus rien à faire, plus aucun coup à payer.
- **tronqué** (*truncated*) : on arrête parce que **le temps est écoulé** (par exemple 20 coups au maximum). Le cube, lui, n'est pas résolu : si on continuait, il faudrait encore jouer des coups.

Comparaison : un marathonien qui franchit la ligne d'arrivée a **terminé**. Un marathonien qu'on arrête au kilomètre 30 parce que la route rouvre aux voitures a été **arrêté** : sa course n'est pas finie, il lui restait 12 km.

Pourquoi c'est important ? Quand l'agent apprendra (phase 5), il se demandera « combien vaut la position où je suis arrivé ? ». Après un épisode **terminé**, la réponse est simple : rien, c'est fini. Après un épisode **tronqué**, la position a encore une valeur : il restait du chemin. Confondre les deux fausse l'apprentissage. Gymnasium renvoie donc deux informations séparées : `terminated` et `truncated`.

---

## 3. Le retour : ce que l'agent cherche à maximiser

### Pas la récompense du prochain coup, mais le total

L'agent ne cherche pas à gagner le plus de points **tout de suite** : il cherche à gagner le plus de points **au total, sur tout l'épisode**. Ce total s'appelle le **retour** (*return*), noté G :

```text
G = r1 + r2 + r3 + … + rT        (la somme des récompenses jusqu'à la fin)
```

Pourquoi le total ? Parce qu'un bon coup peut **sembler** mauvais sur le moment. Au cube, il faut souvent « défaire » une partie déjà rangée pour pouvoir tout ranger ensuite. Un agent qui ne regarde que le coup suivant est un agent à courte vue.

### Notre choix : -1 par coup

Avec une récompense de **-1 à chaque coup** :

| Ce qui arrive | Retour G |
|---|---|
| résolu en 5 coups | -5 |
| résolu en 12 coups | -12 |
| pas résolu, arrêté après 20 coups (tronqué) | -20 |

**Maximiser G revient donc à résoudre en le moins de coups possible.** C'est exactement l'objectif du projet. Et G est très lisible : c'est « moins le nombre de coups ».

### L'autre choix classique : +1 quand c'est résolu

On pourrait aussi donner **+1** au coup qui résout, et 0 sinon. Problème : résoudre en 5 coups ou en 500 coups donne le même retour, G = 1. L'agent n'a **aucune raison d'être rapide**.

La solution habituelle est l'**actualisation** (*discount*) : une récompense obtenue plus tard compte un peu moins. On choisit un nombre γ (« gamma ») un peu plus petit que 1, par exemple 0,9, et :

```text
G = r1 + γ·r2 + γ²·r3 + γ³·r4 + …
```

Avec γ = 0,9 et +1 au coup qui résout :

| Résolu au coup n° | G |
|---|---|
| 1 | 1 |
| 2 | 0,9 |
| 3 | 0,81 |
| 10 | 0,9⁹ ≈ 0,39 |

Plus c'est rapide, plus ça rapporte. Image : un bonbon tout de suite vaut un peu plus qu'un bonbon dans une semaine.

> **Pour les curieux.** γ sert aussi à garantir que G reste un nombre fini quand un épisode pourrait durer indéfiniment : avec γ < 1, la somme 1 + γ + γ² + … vaut 1 / (1 - γ), soit 10 pour γ = 0,9. Avec notre choix « -1 par coup », on peut garder γ = 1 : nos épisodes sont toujours limités (tronqués après un nombre maximum de coups).

**Dans ce projet, on prend -1 par coup et γ = 1** (ou très proche de 1). La fiche de la phase 4 en discute.

---

## 4. La politique : la stratégie de l'agent

### Définition

Une **politique** (*policy*), notée π (« pi »), c'est **la règle qui dit à l'agent quoi jouer dans chaque état**. C'est sa stratégie, sa façon de jouer.

Une politique peut être :

- **une table** : pour chaque état, le coup à jouer (possible seulement s'il y a peu d'états) ;
- **une règle écrite à la main** : « si la croix blanche n'est pas faite, faire… » (c'est ce que fait un humain qui suit une méthode) ;
- **une fonction apprise** : un réseau de neurones qui reçoit les 54 cases et propose un coup (phase 5).

Elle peut être **déterministe** (toujours le même coup dans le même état) ou **aléatoire** (des probabilités : « 70 % R, 30 % U »).

### Trois politiques pour le cube

| Politique | Comment elle joue | Ce qu'on en pense |
|---|---|---|
| **aléatoire** | chacun des 18 coups avec probabilité 1/18 | la plus bête ; c'est notre **point de départ** (et celle de la phase 4) |
| **méthode humaine** | une méthode couche par couche, écrite à la main | marche toujours, mais en ~100 coups ; personne ne l'a « apprise » |
| **l'oracle tricheur** | rejoue à l'envers le mélange qu'il a vu | parfait, mais il **triche** : il utilise une information que l'agent n'a pas |

### L'agent ne voit que l'état

C'est une règle fondamentale : l'agent prend sa décision **en regardant seulement l'état actuel**. Il ne sait pas comment le cube a été mélangé.

C'est possible parce que, pour le cube, **l'état contient tout ce qu'il faut savoir** : peu importe le chemin par lequel le cube est arrivé dans cette position, les coups qui le résolvent sont les mêmes. Cette propriété s'appelle la **propriété de Markov** : « le futur ne dépend que du présent, pas du passé ».

Contre-exemple : si l'agent ne voyait que la face avant du cube, l'état ne suffirait plus. Deux cubes avec la même face avant peuvent avoir besoin de solutions différentes. Il faudrait se souvenir du passé pour deviner le reste. Heureusement, notre agent voit les 54 cases.

### Le but du RL

**Trouver la meilleure politique**, notée π\* (« pi étoile ») : celle qui donne le plus grand retour possible, depuis n'importe quel état. Pour le cube : celle qui résout en le moins de coups possible.

---

## 5. Un mini-casse-tête à 3 jetons : notre laboratoire

Le cube a beaucoup trop d'états pour qu'on fasse les calculs à la main. Alors on va tout comprendre sur un casse-tête **minuscule**, qui fonctionne exactement comme lui.

### Les règles

Trois jetons A, B, C sont posés en ligne, dans le désordre. Deux actions :

- **G** : échanger les deux jetons de **gauche** ;
- **D** : échanger les deux jetons de **droite**.

But : obtenir **ABC**.

```
   B C A  --G-->  C B A           B C A  --D-->  B A C
```

C'est un « mini Rubik's Cube » : un casse-tête où des coups **permutent des pièces**, et où chaque coup s'annule en le rejouant (comme U2 au cube).

### Tous les états

Il y a 3 × 2 × 1 = **6** façons de ranger 3 jetons. En reliant chaque état à ceux qu'on atteint en un coup, on obtient un **cercle** :

```
                 ABC          ← résolu
              G /   \ D
             BAC     ACB      ← à 1 coup
           D  |       |  G
             BCA     CAB      ← à 2 coups
              G \   / D
                 CBA          ← à 3 coups (le plus loin)
```

Vérifie une flèche ou deux : depuis BAC, G échange B et A → ABC ; D échange A et C → BCA.

La **distance** d'un état, c'est le nombre minimum de coups pour le résoudre : 0 pour ABC, 1 pour BAC et ACB, 2 pour BCA et CAB, 3 pour CBA.

### Et si on jouait au hasard ?

Un agent aléatoire joue G ou D à pile ou face. Combien de coups lui faut-il, en moyenne, pour arriver à ABC ?

| Départ | Distance (le minimum) | Coups en moyenne au hasard |
|---|---|---|
| BAC ou ACB | 1 | 5 |
| BCA ou CAB | 2 | 8 |
| CBA | 3 | 9 |

(Tu pourras vérifier ces nombres en section 7, et en les mesurant avec ton code en phase 4.)

Au hasard, c'est **lent** (9 coups au lieu de 3), mais **ça marche** : avec 20 coups au maximum, l'agent aléatoire parti de CBA réussit environ **92 fois sur 100**. Avec seulement 6 états, on finit toujours par tomber sur le bon.

Retiens bien ce résultat : sur le cube, ce sera **complètement différent** (section 11).

---

## 6. La valeur : « combien vaut cette position ? »

### L'intuition

Ton GPS affiche « **temps restant : 2 h 15** ». Ce nombre résume toute la suite du trajet en une seule information, pour l'endroit où tu es. Il te permet de comparer deux routes sans les parcourir.

La **valeur** d'un état, notée V(s), c'est la même idée : **le retour que l'agent peut espérer à partir de cet état**. Avec notre récompense de -1 par coup, c'est « moins le nombre de coups qu'il reste ».

### La valeur dépend de la façon de jouer

Le temps restant dépend du conducteur ! On distingue donc :

- V^π(s) : la valeur de s **si on joue avec la politique π**. Par exemple, avec la politique aléatoire, V^aléatoire(CBA) = -9 (en moyenne, 9 coups) ;
- V\*(s) : la valeur de s **si on joue parfaitement**. V\*(CBA) = -3.

Pour le mini-casse-tête (récompense -1 par coup, γ = 1) :

| État | Distance | V\* (jeu parfait) | V^aléatoire |
|---|---|---|---|
| ABC | 0 | 0 | 0 |
| BAC, ACB | 1 | -1 | -5 |
| BCA, CAB | 2 | -2 | -8 |
| CBA | 3 | -3 | -9 |

Tu remarques : **V\*(s) = - distance(s)**. Ce n'est pas un hasard.

### La valeur d'une action : Q

On a souvent besoin d'une information un peu plus fine : **combien vaut le coup a, joué dans l'état s ?** C'est la **valeur d'action**, notée Q(s, a). C'est le retour espéré si on joue a maintenant, puis qu'on continue (parfaitement, pour Q\*).

Exemple dans l'état BCA :

```text
Q*(BCA, G) = -1 (le coup G)  + V*(CBA) = -1 + (-3) = -4
Q*(BCA, D) = -1 (le coup D)  + V*(BAC) = -1 + (-1) = -2     ← le meilleur
```

### Pourquoi c'est la clé

Si l'agent connaît Q\*, jouer parfaitement devient trivial : **dans chaque état, il prend l'action qui a la plus grande valeur**. On dit qu'il joue de façon **gloutonne** (*greedy*).

Tout le problème du RL se ramène donc souvent à : **apprendre la valeur**.

### Ce que ça veut dire pour le cube

Avec -1 par coup et γ = 1, la valeur parfaite d'un cube est :

```text
V*(cube) = - (nombre minimum de coups pour le résoudre)
```

Elle va de 0 (résolu) à -20 : on sait depuis 2010 que tout cube se résout en 20 coups au plus (le « nombre de Dieu »).

Autrement dit : **apprendre la valeur du cube, c'est apprendre à estimer combien de coups il reste**. Et savoir estimer ça, c'est savoir résoudre : on joue le coup qui mène au cube le plus proche de la solution. C'est exactement l'idée de DeepCubeA, le travail de recherche qui inspire notre phase 6.

---

## 7. L'équation de Bellman

C'est **la** relation du RL. Elle a l'air technique, mais elle dit quelque chose de très simple.

### En mots

> **La valeur d'ici = ce que je gagne en faisant le meilleur pas + la valeur de là où j'arrive.**

Retour au GPS. Tu vas de Paris à Marseille en passant par Lyon. Alors :

```text
temps restant depuis Paris = temps Paris → Lyon + temps restant depuis Lyon
```

…à condition que Lyon soit sur **le meilleur** chemin. Si tu ne sais pas encore par où passer, tu regardes toutes les villes voisines et tu prends la meilleure :

```text
temps restant depuis Paris = le minimum, parmi les villes voisines V,
                             de  ( temps Paris → V  +  temps restant depuis V )
```

### En formule

Notre environnement est **déterministe** : une action donne toujours le même résultat. L'équation de Bellman s'écrit :

```text
V*(s) = le maximum, sur toutes les actions a,  de  [ r(s, a) + γ · V*(s') ]

    où s' est l'état obtenu en jouant a dans s,
    et  V*(état terminal) = 0   (une fois résolu, il n'y a plus rien à gagner ni à perdre).
```

Et pour Q :

```text
Q*(s, a) = r(s, a) + γ · V*(s')        et        V*(s) = le maximum des Q*(s, a)
```

### Vérification sur le mini-casse-tête

Pour BCA (r = -1, γ = 1) :

```text
V*(BCA) = max( -1 + V*(CBA) ,  -1 + V*(BAC) )
        = max( -1 + (-3)    ,  -1 + (-1)    )
        = max( -4 , -2 )  =  -2      ✓
```

### Pour le cube

Avec r = -1 et γ = 1, l'équation devient :

```text
distance(cube) = 1 + le minimum des distances de ses 18 voisins
```

C'est presque une évidence : « pour résoudre en n coups, il faut un premier coup qui mène à un cube résoluble en n - 1 coups ». Et pourtant, c'est l'outil qui va nous permettre de **calculer** puis d'**apprendre** les valeurs.

### Bellman pour une politique donnée

L'équation existe aussi pour une politique quelconque, par exemple aléatoire. On ne prend plus le meilleur coup, mais **la moyenne** sur les coups que la politique joue :

```text
V^aléatoire(s) = la moyenne, sur les actions a, de [ r(s, a) + γ · V^aléatoire(s') ]
```

Sur le mini-casse-tête :

```text
V^aléatoire(BAC) = -1 + ½ · ( V(ABC) + V(BCA) ) = -1 + ½ · ( 0 + (-8) ) = -5     ✓
```

C'est ainsi qu'on calcule les « 5, 8, 9 coups en moyenne » de la section 5 (exercice 6).

> **Pour les curieux : la forme générale.** Quand l'environnement est aléatoire (une même action peut mener à plusieurs états, avec des probabilités P(s' | s, a)), on fait la moyenne sur les états d'arrivée :
>
> V\*(s) = max sur a de  Σ sur s' de  P(s' | s, a) · [ r + γ · V\*(s') ]
>
> Le cube est déterministe : la somme n'a qu'un seul terme, de probabilité 1. L'ensemble « états, actions, transitions, récompenses, γ » s'appelle un **processus de décision markovien** (*MDP*) : c'est le cadre mathématique de tout le RL.

### Pourquoi c'est si important

La valeur parle de **tout le futur** (des dizaines de coups). L'équation de Bellman la ramène à une relation **entre voisins** (un seul coup). On n'a plus besoin de jouer des parties entières pour vérifier une valeur : il suffit de regarder un pas plus loin.

---

## 8. Calculer la valeur : l'itération de valeur

### L'algorithme, en mots

On ne connaît pas V\*. Alors :

1. on part de **V = 0 partout** (on ne sait rien) ;
2. pour chaque état, on recalcule V(s) avec l'équation de Bellman, **en utilisant les anciennes valeurs** des voisins ;
3. on recommence l'étape 2 jusqu'à ce que plus rien ne change.

C'est l'**itération de valeur** (*value iteration*).

### À la main, sur le mini-casse-tête

Chaque colonne est un tour. ABC est terminal : sa valeur reste 0.

| État | Tour 0 | Tour 1 | Tour 2 | Tour 3 | Tour 4 |
|---|---|---|---|---|---|
| ABC | 0 | 0 | 0 | 0 | 0 |
| BAC | 0 | -1 | -1 | -1 | -1 |
| ACB | 0 | -1 | -1 | -1 | -1 |
| BCA | 0 | -1 | **-2** | -2 | -2 |
| CAB | 0 | -1 | **-2** | -2 | -2 |
| CBA | 0 | -1 | -2 | **-3** | -3 |

Détail d'une case, BCA au tour 2 : max( -1 + V₁(CBA), -1 + V₁(BAC) ) = max( -1 - 1, -1 - 1 ) = -2.

Au tour 4, plus rien ne change : on a trouvé V\* (et les distances).

### Ce qu'on voit : une vague

Regarde les cases en gras : **la bonne nouvelle part de l'état résolu et s'étend d'un anneau par tour**, comme une onde dans l'eau. Après le tour k, tous les états à distance k ou moins ont leur valeur exacte.

Pour le cube, cette vague, c'est un **parcours en largeur** (*BFS*) : on part du cube résolu, on trouve ses 18 voisins (distance 1), puis leurs voisins (distance 2), etc. Tu la programmeras dans l'étape F de la fiche.

### Pourquoi on ne peut pas faire ça pour le cube

L'itération de valeur doit **passer sur tous les états** à chaque tour, et **retenir une valeur par état**. Pour le cube :

- 43 252 003 274 489 856 000 états ;
- même avec **un seul octet** par état, il faudrait 43 milliards de gigaoctets de mémoire ;
- et une table Q (18 nombres de 4 octets par état) : environ 3 milliards de téraoctets.

C'est impossible. Il faudra une autre idée (section 12).

---

## 9. Explorer ou exploiter

### Le dilemme du restaurant

Tu connais un bon restaurant. Ce soir, tu y retournes (tu **exploites** ce que tu sais) ou tu en essaies un nouveau, peut-être meilleur, peut-être pire (tu **explores**) ?

- Si tu n'explores jamais, tu ne découvriras jamais mieux que ton restaurant actuel.
- Si tu explores tout le temps, tu manges souvent mal.

L'agent a le même problème. Il apprend **de sa propre expérience** (section 1) : s'il joue toujours le coup qu'il croit le meilleur, il ne découvre jamais que d'autres coups étaient meilleurs.

### La solution la plus simple : ε-glouton

On choisit un petit nombre ε (« epsilon »), par exemple 0,1 :

- avec une probabilité ε, l'agent joue un coup **au hasard** (il explore) ;
- sinon, il joue le coup qu'il croit **le meilleur** (il exploite).

En général, on commence avec ε grand (beaucoup d'exploration, car on ne sait rien) et on le diminue au fil de l'apprentissage.

### Le piège du cube

Au tout début, l'agent ne sait rien : toutes ses valeurs sont égales. Exploiter ou explorer, c'est pareil : **il joue au hasard**. C'est l'agent aléatoire.

Or, sur le cube, le hasard ne trouve presque jamais la solution (section 11). L'agent ne reçoit donc **jamais** l'information « résolu ». Il n'a rien à exploiter. C'est le problème de la poule et de l'œuf :

> pour apprendre, il faut réussir de temps en temps ; pour réussir, il faut avoir appris.

---

## 10. Qui a mérité la récompense ?

Une équipe de foot gagne 1-0. Qui a mérité la victoire : le buteur ? le passeur ? le défenseur qui a bloqué un tir à la 10ᵉ minute ? Le gardien ?

L'agent a le même problème, qu'on appelle l'**attribution du mérite** (*credit assignment*). Il joue 15 coups, et seule la fin de l'épisode dit si c'était bien. **Lequel de ces 15 coups était bon ?** Lequel était inutile ?

L'équation de Bellman est la réponse : épisode après épisode, la valeur de l'état final « remonte » vers les états d'avant, un pas à la fois (comme la vague de la section 8). Un coup qui mène à un état de grande valeur devient un bon coup. Mais pour que ça marche, il faut **de nombreux épisodes qui atteignent la récompense**.

---

## 11. Pourquoi le Rubik's Cube est si difficile

Cinq raisons, du plus évident au plus subtil.

### 11.1 Le nombre d'états

Le cube a **43 252 003 274 489 856 000** états, soit environ 4,3 × 10¹⁹ (43 milliards de milliards).

Même à **un million de coups par seconde** (l'ordre de grandeur de `cube.move`), visiter chaque état une seule fois prendrait environ **1,4 million d'années**.

### 11.2 L'explosion autour de la solution

Combien d'états à chaque distance de la solution ? (Sources : cube20.org ; les lignes 0 à 5 ont été vérifiées avec notre `cube.py`.)

| Distance | Nombre d'états | Multiplié par |
|---|---|---|
| 0 | 1 | |
| 1 | 18 | ×18 |
| 2 | 243 | ×13,5 |
| 3 | 3 240 | ×13,3 |
| 4 | 43 239 | ×13,3 |
| 5 | 574 908 | ×13,3 |
| 6 | 7 618 438 | ×13,3 |
| 7 | 100 803 036 | ×13,2 |
| 10 | environ 232 milliards | |
| 15 | environ 91 millions de milliards | |
| 20 (le maximum) | quelques centaines de millions | (des cas très rares) |

À chaque coup de plus, **environ 13 fois plus d'états**. La plupart des cubes mélangés sont à 17 ou 18 coups de la solution.

Pourquoi « ×13 » et pas « ×18 » ? Parce que certains coups reviennent en arrière (R puis R') ou se combinent (R puis R donne R2), et que des faces opposées commutent (R L = L R).

### 11.3 La pente : au hasard, on s'éloigne

C'est la raison la plus importante. Prends un cube à distance d (entre 1 et 4) et regarde ses 18 voisins. En moyenne :

| Le coup… | Combien sur 18 | Proportion |
|---|---|---|
| rapproche de la solution (distance d - 1) | environ 1,1 | ≈ 6 % |
| laisse à la même distance | environ 2,2 | ≈ 12 % |
| **éloigne** (distance d + 1) | **environ 14,7** | **≈ 82 %** |

(Mesuré avec `cube.py` sur tous les états jusqu'à la distance 4. À distance 1, c'est exactement 1, 2 et 15.)

Un coup au hasard t'éloigne donc **plus de 8 fois sur 10**. Imagine un arbre immense : depuis la racine (le cube résolu), chaque branche se divise en 13. Une fourmi qui marche au hasard sur cet arbre s'éloigne de la racine presque à chaque pas.

Compare avec le mini-casse-tête : à distance 1 ou 2, **un coup sur deux** rapproche. Le cercle ne permet pas de s'éloigner beaucoup.

### 11.4 Le retour au point de départ

Un résultat mathématique (le lemme de Kac) dit : pour une marche au hasard comme la nôtre, **le nombre moyen de coups pour revenir à l'état de départ est égal au nombre d'états**.

- Mini-casse-tête : 6 états → on revient à ABC en **6 coups** en moyenne (exercice 10).
- Cube : 4,3 × 10¹⁹ états → il faut **4,3 × 10¹⁹ coups** en moyenne. À un million de coups par seconde : **1,4 million d'années**.

Un agent aléatoire qui part d'un cube résolu et s'en éloigne d'un seul coup ne revient pratiquement jamais.

### 11.5 La récompense ne dit rien

Avec -1 par coup, l'agent reçoit -1 **que son coup soit bon ou mauvais**. La seule information utile, c'est d'arriver à l'état résolu, et c'est justement ce qui n'arrive presque jamais au hasard. On dit que la récompense est **rare** (*sparse reward*) : elle n'est pas absente, mais elle ne porte aucune information sur la qualité des coups.

Tu mesureras toi-même, en phase 4, combien de fois l'agent aléatoire réussit, selon le nombre de coups du mélange. **Écris ta prédiction avant de mesurer** (fiche, étape A).

### 11.6 Le piège de la récompense « maison »

Idée tentante : récompenser l'agent selon le **nombre de cases bien placées** (une case est bien placée si elle a la couleur du centre de sa face). Plus il y en a, mieux c'est, non ?

Voici des mesures faites avec `cube.py` :

| Cube | Cases mal placées | Distance réelle |
|---|---|---|
| après `R` | 12 | 1 |
| après `R U R' U'` | 12 | 4 |
| après `R L` | 24 | 2 |
| le **superflip** (toutes les arêtes retournées sur place) | 24 | **20** (le maximum !) |

Le superflip a **autant** de cases mal placées que `R L`, mais il est à 20 coups au lieu de 2. Et à 4 ou 5 coups de la solution, on trouve des cubes avec seulement 12 cases mal placées, autant qu'après un seul coup.

**Le nombre de cases bien placées ne dit presque rien de la distance.** Un agent récompensé comme ça apprendrait à rendre le cube « joli », pas à le résoudre. C'est un exemple de **mauvaise conception de récompense**, un piège très courant en RL : l'agent optimise **exactement** ce qu'on lui demande, pas ce qu'on voulait.

---

## 12. Ce qui va nous sauver (aperçu des phases 5 et 6)

Les difficultés de la section 11 ont des réponses. Ce sont les idées des prochaines phases.

| Difficulté | Idée | Phase |
|---|---|---|
| au hasard, on ne trouve jamais la solution | **le curriculum** : commencer par des cubes mélangés de 1 coup (là, le hasard réussit parfois), puis 2, puis 3… comme à l'école | 5 |
| la valeur s'apprend sur les états visités | **Q-learning** : l'équation de Bellman, appliquée non pas à tous les états, mais aux seules expériences que l'agent vit, une par une | 5 |
| trop d'états pour une table | **généraliser** : un réseau de neurones qui *estime* Q à partir des 54 cases ; deux cubes semblables reçoivent des valeurs semblables | 5 (DQN) |
| le hasard s'éloigne de la solution | **partir de la solution** : on fabrique des états d'entraînement en mélangeant un cube résolu ; on sait toujours d'où ils viennent | 6 |
| une estimation n'est jamais parfaite | **chercher** : combiner la valeur apprise avec une recherche (A\*) qui essaie plusieurs suites de coups | 6 |

> **Pour les curieux : avec ou sans modèle.** Q-learning et DQN sont dits « sans modèle » (*model-free*) : ils apprennent seulement de l'expérience, sans savoir prévoir ce que fera une action. Mais nous avons un avantage énorme : le **modèle** de l'environnement est connu et parfait. C'est `cube.move` ! On peut donc **planifier** : essayer des coups « dans sa tête » (sur une copie du cube) avant de jouer. C'est la clé de la phase 6, et c'est aussi ce que fait AlphaGo.

---

## 13. Résumé en 10 phrases

1. En RL, un **agent** apprend par essais et erreurs, guidé seulement par des **récompenses**.
2. À chaque pas, il observe un **état**, choisit une **action**, reçoit une récompense et un nouvel état ; une partie complète est un **épisode**.
3. Un épisode est **terminé** (le cube est résolu) ou **tronqué** (le temps est écoulé) : ce n'est pas la même chose.
4. L'agent maximise le **retour**, la somme des récompenses ; avec -1 par coup, cela revient à résoudre en peu de coups.
5. Sa stratégie s'appelle une **politique** ; il décide en ne regardant que l'état (propriété de Markov).
6. La **valeur** V(s) est le retour qu'on peut espérer depuis s ; Q(s, a) est celui d'un coup précis.
7. Pour le cube, la valeur parfaite est **moins la distance à la solution**.
8. L'**équation de Bellman** relie la valeur d'un état à celle de ses voisins ; l'**itération de valeur** l'applique en boucle, comme une vague qui part de la solution.
9. L'agent doit équilibrer **exploration** et **exploitation**, et attribuer le mérite aux bons coups.
10. Le cube est dur : **trop d'états**, une **pente** qui éloigne au hasard (82 % des coups), et une récompense qui n'arrive **presque jamais** ; d'où le curriculum, les réseaux de neurones et la recherche.

---

## 14. Glossaire français / anglais

Presque toute la documentation est en anglais : voici les correspondances.

| Français | Anglais | En une phrase |
|---|---|---|
| apprentissage par renforcement | reinforcement learning (RL) | apprendre par essais et erreurs, guidé par des récompenses |
| agent | agent | celui qui choisit les actions |
| environnement | environment | le monde, ses règles et le juge |
| état / observation | state / observation | la situation que voit l'agent |
| action | action | un choix possible (un des 18 coups) |
| espace d'actions / d'observations | action space / observation space | l'ensemble des actions / observations possibles |
| récompense | reward | le nombre qui note un pas |
| récompense rare | sparse reward | une récompense qui n'apporte presque jamais d'information |
| épisode | episode | une partie complète |
| terminé / tronqué | terminated / truncated | vraie fin / arrêt par limite de temps |
| retour | return | la somme (actualisée) des récompenses |
| facteur d'actualisation | discount factor (γ) | combien vaut une récompense future |
| politique | policy (π) | la stratégie de l'agent |
| politique gloutonne | greedy policy | jouer l'action de plus grande valeur |
| valeur d'état | state value, V(s) | ce que vaut un état |
| valeur d'action | action value, Q(s, a) | ce que vaut une action dans un état |
| équation de Bellman | Bellman equation | valeur d'ici = gain d'un pas + valeur de là-bas |
| itération de valeur | value iteration | appliquer Bellman en boucle sur tous les états |
| exploration / exploitation | exploration / exploitation | essayer du nouveau / utiliser ce qu'on sait |
| ε-glouton | ε-greedy | explorer avec une probabilité ε |
| attribution du mérite | credit assignment | savoir quelles actions ont mené à la récompense |
| processus de décision markovien | Markov decision process (MDP) | le cadre mathématique du RL |
| parcours en largeur | breadth-first search (BFS) | explorer distance par distance |
| conception de la récompense | reward shaping / reward design | choisir les récompenses (avec ses pièges) |

---

## 15. Exercices

Sur papier. Les corrigés sont en section 16.

**Exercice 1 — Le vocabulaire.** Un robot aspirateur doit nettoyer une pièce. Donne : l'agent, l'environnement, un exemple d'état, les actions, une idée de récompense, une fin « terminée » et une fin « tronquée ».

**Exercice 2 — Terminé ou tronqué ?** Pour chaque situation, dis si l'épisode est terminé, tronqué, ou pas fini.
a) Le cube est résolu au 7ᵉ coup, la limite était de 20.
b) Le 20ᵉ coup est joué, la limite était de 20, le cube n'est pas résolu.
c) Le 20ᵉ coup résout le cube, la limite était de 20.
d) Le robot aspirateur n'a plus de batterie au milieu de la pièce.
e) La démonstration du robot s'arrête au bout de 5 minutes, comme prévu.

**Exercice 3 — Calculer un retour.**
a) Récompenses -1, -1, -1, -1 (résolu au 4ᵉ coup), γ = 1. Que vaut G ?
b) Récompenses 0, 0, 0, +1 (résolu au 4ᵉ coup), γ = 0,9. Que vaut G ?
c) Avec la récompense « +1 à la résolution » et γ = 1, que vaut G pour un cube résolu en 3 coups ? En 30 coups ? Quel est le problème ?

**Exercice 4 — Les Q du mini-casse-tête.** Avec -1 par coup et γ = 1, calcule Q\*(s, G) et Q\*(s, D) pour les 5 états non résolus. En déduire la politique gloutonne (le meilleur coup dans chaque état). Y a-t-il un état où les deux coups se valent ?

**Exercice 5 — L'itération de valeur avec +1.** Refais le tableau de la section 8 avec la récompense « +1 au coup qui résout, 0 sinon » et γ = 0,9 (ABC reste terminal, de valeur 0). Quelles valeurs obtiens-tu ? La politique gloutonne est-elle la même qu'à l'exercice 4 ?

**Exercice 6 — L'agent aléatoire du mini-casse-tête.** Vérifie, avec l'équation de Bellman pour la politique aléatoire, que les valeurs -5 (BAC), -8 (BCA) et -9 (CBA) sont cohérentes. (Indice : par symétrie, ACB vaut comme BAC et CAB comme BCA.)

**Exercice 7 — Profondeur de mélange ou distance ?** Pour chaque mélange, donne la distance réelle du cube obtenu.
a) `R L R'`
b) `R L R' L'`
c) `U D U' D2`
d) Que retenir pour un environnement qui « mélange de n coups » ?

**Exercice 8 — Les voisins d'un cube à 1 coup.** Le cube a subi `R`. Parmi les 18 coups possibles, lesquels mènent à un cube à distance 0 ? à distance 1 ? à distance 2 ? Compare avec le tableau de la section 11.3.

**Exercice 9 — La mémoire d'une table.** Combien d'octets faut-il pour stocker une table Q pour le mini-casse-tête (2 actions, un nombre de 4 octets par case) ? Et pour le cube (18 actions) ? Donne l'ordre de grandeur.

**Exercice 10 — Le lemme de Kac à la main.** Dans le mini-casse-tête, l'agent aléatoire part de ABC (on ne s'arrête pas) et joue au hasard. En utilisant le tableau de la section 5, combien de coups lui faut-il en moyenne pour revenir à ABC ? Compare avec le nombre d'états.

**Exercice 11 — La récompense « maison ».** Un camarade propose : « récompense = nombre de cases bien placées après le coup ». Donne deux raisons, avec des exemples de la section 11.6, pour lesquelles c'est une mauvaise idée.

**Exercice 12 — L'oracle tricheur.** L'environnement renvoie, dans un dictionnaire `info`, la liste des coups du mélange (pratique pour les tests). Pourquoi un agent ne doit-il **jamais** s'en servir ? Que mesurerait-on si on le laissait faire ?

**Exercice 13 — Le signe de la récompense.** Par erreur, l'environnement donne **+1** à chaque coup joué (au lieu de -1), et l'épisode s'arrête quand le cube est résolu. Qu'est-ce qu'un bon agent apprendrait à faire ?

---

## 16. Corrigés

**Exercice 1.** Agent : le programme qui pilote l'aspirateur. Environnement : la pièce, les meubles, la poussière, la batterie. État : la position du robot, une carte des zones sales, le niveau de batterie. Actions : avancer, tourner à gauche, tourner à droite, aspirer. Récompense : +1 par zone nettoyée, -1 par choc contre un meuble, par exemple. Terminé : la pièce est propre (succès), ou la batterie est vide (échec). Tronqué : on arrête l'expérience au bout d'un temps fixé.

**Exercice 2.** a) Terminé. b) Tronqué. c) **Terminé** : le cube est résolu, c'est une vraie fin, même si c'était le dernier coup permis. d) Terminé (un échec, mais une vraie fin : le robot ne peut plus rien faire). e) Tronqué (arrêt artificiel).

**Exercice 3.** a) G = -4. b) G = 0,9³ = 0,729 (la récompense arrive au 4ᵉ coup, elle est actualisée trois fois). c) G = 1 dans les deux cas : l'agent n'a aucune raison de préférer 3 coups à 30. D'où γ < 1, ou une récompense de -1 par coup.

**Exercice 4.**

| État | Q\*(s, G) | Q\*(s, D) | Meilleur coup |
|---|---|---|---|
| BAC | -1 (→ ABC) | -3 (→ BCA) | G |
| ACB | -3 (→ CAB) | -1 (→ ABC) | D |
| BCA | -4 (→ CBA) | -2 (→ BAC) | D |
| CAB | -2 (→ ACB) | -4 (→ CBA) | G |
| CBA | -3 (→ BCA) | -3 (→ CAB) | les deux se valent |

**Exercice 5.** V\* = 0 pour ABC, 1 pour BAC et ACB, 0,9 pour BCA et CAB, 0,81 pour CBA. Autrement dit, V\*(s) = 0,9 puissance (distance - 1). Les valeurs sont différentes, mais **leur ordre est le même** : la politique gloutonne est identique. Deux récompenses différentes peuvent mener à la même meilleure politique.

**Exercice 6.**
- V(BAC) = -1 + ½ · ( V(ABC) + V(BCA) ) = -1 + ½ · ( 0 - 8 ) = -5 ✓
- V(BCA) = -1 + ½ · ( V(CBA) + V(BAC) ) = -1 + ½ · ( -9 - 5 ) = -8 ✓
- V(CBA) = -1 + ½ · ( V(BCA) + V(CAB) ) = -1 + ½ · ( -8 - 8 ) = -9 ✓

**Exercice 7.** a) R et L commutent : `R L R'` = `L`, distance 1. b) Identité : distance 0, le cube est résolu ! c) U et D commutent : `U U' D D2` = `D'`, distance 1. d) **Un mélange de n coups donne un cube à distance n au plus**, parfois moins, parfois même 0. L'environnement doit relancer le mélange s'il redonne un cube résolu. Et une « profondeur de mélange » n'est pas une « distance ».

**Exercice 8.** Distance 0 : `R'` (1 coup). Distance 1 : `R` (on obtient R2) et `R2` (on obtient R') (2 coups). Distance 2 : les 15 autres. C'est la ligne « distance 1 » de la section 11.3 : 1, 2 et 15.

**Exercice 9.** Mini-casse-tête : 6 états × 2 actions × 4 octets = 48 octets. Cube : 4,3 × 10¹⁹ × 18 × 4 ≈ 3 × 10²¹ octets, soit environ 3 milliards de téraoctets. Il faudrait 3 milliards de disques durs de 1 To.

**Exercice 10.** Depuis ABC, le premier coup mène à BAC ou ACB (1 coup), puis il faut en moyenne 5 coups pour revenir (section 5) : 1 + 5 = **6 coups**, exactement le nombre d'états. Pour le cube : 4,3 × 10¹⁹ coups.

**Exercice 11.** 1) Des cubes très proches de la solution ont beaucoup de cases mal placées (`R L` : 24 cases, 2 coups). 2) Des cubes très loin en ont peu (le superflip : 24 cases, 20 coups ; `R U R' U'` : 12 cases, 4 coups, autant que `R`). La récompense ne mesure donc pas la vraie distance : l'agent apprendrait à faire des cubes « jolis », et il resterait bloqué, car il faut souvent défaire ce qui est rangé pour avancer.

**Exercice 12.** Parce qu'en vrai, un cube mélangé n'arrive pas avec la liste de ses coups de mélange : l'agent ne verra jamais cette information quand il devra résoudre un cube qu'on lui donne. Un agent qui lit `info` est l'oracle tricheur de la section 4. On mesurerait sa capacité à lire une liste, pas à résoudre un cube. `info` sert au débogage et aux tests, jamais à la décision.

**Exercice 13.** Il apprendrait à **ne jamais résoudre le cube**, pour jouer le plus de coups possible et accumuler les +1. Un signe inversé suffit à faire apprendre le contraire de ce qu'on veut. Toujours vérifier le signe de la récompense, et ce que « maximiser le retour » veut dire concrètement.

---

## 17. Pour aller plus loin

- **Le livre de référence, gratuit :** Richard Sutton et Andrew Barto, *Reinforcement Learning: An Introduction* (2ᵉ édition), en anglais : <http://incompleteideas.net/book/the-book-2nd.html>. Chapitre 1 (l'idée), chapitre 3 (MDP, valeurs, Bellman), chapitre 4 (itération de valeur). Ce cours en est une version simplifiée.
- **Un cours en ligne, gratuit et progressif :** Hugging Face Deep RL Course, unités 1 et 2 (introduction, Q-learning) : <https://huggingface.co/learn/deep-rl-course/unit0/introduction>.
- **Gymnasium**, la bibliothèque des environnements : « Basic Usage » <https://gymnasium.farama.org/introduction/basic_usage/> et « Create a Custom Environment » <https://gymnasium.farama.org/introduction/create_custom_env/>.
- **Les nombres du cube** (nombre d'états, distances, superflip) : <https://www.cube20.org/>.
- **Pour la phase 6 :** Agostinelli, McAleer, Shmakov et Baldi, *Solving the Rubik's cube with deep reinforcement learning and search*, Nature Machine Intelligence, 2019 (DeepCubeA). Version gratuite : <https://deepcube.igb.uci.edu/static/files/SolvingTheRubiksCubeWithDeepReinforcementLearningAndSearch_Final.pdf>.

Le prochain chapitre (`rl-2-…`, en phase 5) partira de la section 12 : Q-learning, le curriculum, puis les réseaux de neurones.
