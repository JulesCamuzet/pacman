# Gestion de projet - Pacman

Dernière mise à jour : 28 juillet 2026.

## 1. Objectif

Le projet consiste à livrer un Pacman complet, jouable et installable,
écrit en Python avec Pygame, tout en respectant les contraintes du sujet :

- configuration JSON avec commentaires et valeurs par défaut ;
- labyrinthes créés par le package A-Maze-ing imposé ;
- au moins 10 niveaux ;
- joueur, fantômes, pacgums et super-pacgums ;
- score, vies, chronomètre, pause et cheat mode ;
- menus, HUD, écrans de victoire et de défaite ;
- highscores persistants ;
- tests, documentation et package déployé sur Itch.io ;
- aucune erreur Python affichée à l'utilisateur.

Le projet est réalisé par deux développeurs :

- **Mind-alia** : données, règles du jeu, stockage et tests de logique ;
- **JulesCamuzet** : Pygame, rendu, contrôles, sprites et écrans.

Les interfaces communes, la documentation finale, les tests d'acceptation
et le déploiement sont réalisés à deux.

## 2. État vérifié au 28 juillet 2026

| Élément | État | Preuve |
| --- | --- | --- |
| Configuration Pydantic | Terminé | `tests/test_config.py` |
| Adaptation de MazeGenerator | Terminé | `tests/test_game.py` |
| Stockage des highscores | Terminé côté données | `tests/test_highscores.py` |
| CLI `pac-man.py config.json` | Terminé | tests CLI |
| Fenêtre et boucle Pygame | Première version terminée | `pacman/ui/ui.py` |
| Écran d'accueil et menu | Première version terminée | `pacman/ui/pages/` |
| Écran des scores | En cours d'intégration | utilise encore `data/scores.json` |
| Sprites et animation d'accueil | Première version terminée | `pacman/ui/sprites/` |
| Moteur de jeu | À faire | `pacman/game.py` est vide |
| Entités du jeu | À faire | `pacman/entities.py` est vide |
| Jeu complet et package | À faire | dépend des tâches ci-dessous |

État des contrôles au début de ce plan :

```text
make test : 19 tests réussis
make lint : flake8 et mypy réussis sur 24 fichiers Python
```

## 3. Organisation de l'équipe

### 3.1 Propriété des fichiers

| Zone | Responsable principal | Relecteur |
| --- | --- | --- |
| `pacman/config.py` | Mind-alia | JulesCamuzet |
| `pacman/maze.py` | Mind-alia | JulesCamuzet |
| `pacman/highscores.py` | Mind-alia | JulesCamuzet |
| `pacman/entities.py` | Mind-alia | JulesCamuzet |
| `pacman/game.py` | Mind-alia | JulesCamuzet |
| `tests/test_*.py` pour la logique | Mind-alia | JulesCamuzet |
| `pacman/ui/` | JulesCamuzet | Mind-alia |
| `pacman/constants.py` | JulesCamuzet | Mind-alia |
| `pacman/tick.py` | JulesCamuzet | Mind-alia |
| `assets/` | JulesCamuzet | Mind-alia |
| `MLX_MAPPING.md` | JulesCamuzet | Mind-alia |
| `pacman/app.py` et `pac-man.py` | Partagé | Relecture croisée |
| `Makefile`, `requirements.txt` | Partagé | Relecture croisée |
| `README.md` et `docs/` | Partagé | Relecture croisée |
| Packaging et Itch.io | Partagé | Test sur les deux machines |

Règle : une seule personne modifie un fichier partagé à la fois. Avant de
commencer une tâche partagée, son propriétaire temporaire est annoncé dans
le canal de communication de l'équipe.

### 3.2 Contrat entre logique et interface

La logique du jeu ne doit jamais importer Pygame. L'interface peut lire
l'état du jeu, mais elle ne doit pas recalculer les collisions, les scores
ou les règles.

Les objets déjà disponibles pour l'interface sont :

```python
app.config       # GameConfig
app.maze         # MazeData
app.highscores   # list[HighscoreEntry]
```

Le futur moteur de jeu devra proposer une interface simple :

```python
game = Game(config)
game.start()
game.set_direction(direction)
game.update(delta_time)
game.toggle_pause()
game.apply_cheat(cheat)
state = game.state
```

`state` devra contenir uniquement les informations nécessaires au rendu :
positions, directions, score, vies, niveau, temps restant, pacgums,
fantômes, pause et résultat de la partie.

## 4. Méthode Git

Pour chaque tâche :

1. partir de la dernière version de `main` ;
2. créer une branche courte, par exemple `feat/player-movement` ;
3. écrire ou mettre à jour les tests associés ;
4. exécuter `make test` puis `make lint` ;
5. créer un commit au nom explicite ;
6. pousser la branche et ouvrir une pull request ;
7. faire relire la pull request par l'autre développeur ;
8. fusionner uniquement lorsque les contrôles passent.

Il ne faut pas développer directement sur `main` ni mélanger plusieurs
fonctionnalités indépendantes dans le même commit.

## 5. Planning

Les durées sont indicatives. Une phase ne commence que lorsque ses
dépendances indispensables sont disponibles.

| Phase | Durée | Mind-alia | JulesCamuzet | Résultat attendu |
| --- | ---: | --- | --- | --- |
| 0. Fondations | Terminé | Config, maze, highscores, tests | Fenêtre, pages, sprites | Données et UI initiale |
| 1. Contrat du jeu | 1 jour | État et entités | Écran de jeu vide et renderer du maze | Une carte visible |
| 2. Joueur et objets | 2 jours | Mouvement, collisions, pacgums, score | Contrôles, sprites, HUD | Niveau jouable sans fantômes |
| 3. Fantômes et vies | 2 jours | IA, collisions, états edible | Animations et rendu des fantômes | Défaite et respawn fonctionnels |
| 4. Progression complète | 2 jours | Niveaux, temps, victoire, cheat | Pause, game over, victoire, saisie du nom | Boucle complète du jeu |
| 5. Stabilisation | 1 jour | Tests de logique et erreurs | Tests manuels et finition visuelle | Version candidate |
| 6. Livraison | 1 jour | README technique et package | Instructions et validation des assets | Build Itch.io testable |

## 6. Tâches de Mind-alia

### M01 - Configuration robuste - Terminé

- [x] Modèles `LevelConfig` et `GameConfig`.
- [x] Commentaires `#` acceptés.
- [x] Valeurs absentes ou invalides remplacées par des valeurs sûres.
- [x] Clés inconnues ignorées.
- [x] Erreurs de fichier gérées sans traceback.
- [x] Tests de configuration.

Critère d'acceptation :

```bash
.venv/bin/python -m pytest tests/test_config.py -v
```

### M02 - Génération et validation du labyrinthe - Terminé

- [x] Utilisation du wheel imposé sans le modifier.
- [x] `perfect=False`.
- [x] `MazeData` validé avec Pydantic.
- [x] Vérification des dimensions, valeurs, entrée et sortie.
- [x] Seed fixe pour le premier niveau et seeds aléatoires ensuite.
- [x] Erreur du générateur convertie en erreur métier propre.

Critère d'acceptation :

```bash
make maze-check
```

### M03 - Stockage des highscores - Terminé côté données

- [x] Nom limité à 10 caractères.
- [x] Lettres, nombres et espaces uniquement.
- [x] Score entier positif ou nul.
- [x] Tri décroissant et conservation du top 10.
- [x] Chargement et sauvegarde JSON.
- [x] Fichier absent ou cassé géré sans traceback.

Il reste une tâche partagée : connecter cette API à l'écran des scores et
à la fin de partie.

### M04 - Entités et état du jeu - À faire

Fichiers : `pacman/entities.py`, `pacman/game.py`.

- [ ] Créer les types `Direction`, `Position` et `GameStatus`.
- [ ] Créer les modèles `Player`, `Ghost`, `Pacgum` et `SuperPacgum`.
- [ ] Créer `GameState` avec score, vies, niveau, temps et pause.
- [ ] Initialiser le joueur au centre du labyrinthe.
- [ ] Initialiser quatre fantômes dans les quatre coins.
- [ ] Garder toute cette logique indépendante de Pygame.

Critères d'acceptation :

- les modèles peuvent être créés sans ouvrir de fenêtre ;
- leurs positions sont à l'intérieur de la grille ;
- quatre fantômes sont présents ;
- le joueur possède le nombre de vies de `GameConfig`.

### M05 - Déplacements et collisions avec le maze - À faire

Fichiers : `pacman/game.py`, `tests/test_game.py`.

- [ ] Convertir les entrées en directions nord, est, sud et ouest.
- [ ] Utiliser les bits `1`, `2`, `4`, `8` de `MazeData.grid`.
- [ ] Interdire un mouvement lorsqu'un mur est présent.
- [ ] Autoriser le mouvement dans un corridor ouvert.
- [ ] Empêcher toute position hors de la grille.
- [ ] Garder une vitesse indépendante du nombre d'images par seconde.

Critères d'acceptation :

- un test existe pour chaque direction ;
- un mur bloque le joueur et un corridor l'autorise ;
- le résultat est identique à 30, 60 ou 120 FPS.

### M06 - Pacgums, super-pacgums et score - À faire

- [ ] Placer les pacgums dans la majorité des corridors accessibles.
- [ ] Placer quatre super-pacgums dans les coins accessibles.
- [ ] Ne rien placer sur le joueur, les fantômes ou les cellules fermées.
- [ ] Retirer un objet lorsqu'il est mangé.
- [ ] Ajouter les points définis par `GameConfig`.
- [ ] Ne jamais diminuer le score.
- [ ] Terminer le niveau lorsqu'il ne reste plus de pacgum.

Critères d'acceptation :

- chaque objet ne peut être mangé qu'une fois ;
- les trois valeurs de score viennent de la configuration ;
- un niveau vide de pacgums est déclaré gagné.

### M07 - Fantômes et collisions - À faire

- [ ] Déplacer automatiquement les quatre fantômes.
- [ ] Les faire poursuivre le joueur lorsqu'ils sont normaux.
- [ ] Les faire fuir lorsqu'ils sont `edible`.
- [ ] Activer l'état `edible` après une super-pacgum.
- [ ] Restaurer l'état normal après une durée définie.
- [ ] Faire perdre une vie au joueur lors d'une collision normale.
- [ ] Faire gagner les points configurés lors d'une collision edible.
- [ ] Faire réapparaître un fantôme mangé dans son coin.
- [ ] Replacer le joueur au centre après la perte d'une vie.

Critères d'acceptation :

- les fantômes ne traversent pas les murs ;
- une collision normale retire exactement une vie ;
- une collision edible ne retire aucune vie et ajoute les points ;
- zéro vie déclenche le game over.

### M08 - Progression, temps et pause - À faire

- [ ] Enchaîner au moins 10 niveaux.
- [ ] Conserver le score et les vies entre les niveaux.
- [ ] Respecter `level_max_time`.
- [ ] Choisir un comportement clair à la fin du temps : perdre une vie
  et recommencer le niveau.
- [ ] Arrêter le chronomètre et les entités pendant la pause.
- [ ] Déclarer la victoire après le dernier niveau.
- [ ] Déclarer la défaite lorsque les vies atteignent zéro.
- [ ] Retourner au menu après l'enregistrement du score.

### M09 - Cheat mode - À faire

- [ ] Ajouter une commande d'invincibilité.
- [ ] Ajouter une commande pour passer le niveau.
- [ ] Ajouter une commande pour figer les fantômes.
- [ ] Ajouter une commande pour gagner une vie.
- [ ] Exposer clairement l'état du cheat mode dans le HUD.
- [ ] Documenter les touches dans l'écran d'instructions.

Critère d'acceptation : chaque cheat permet au correcteur de tester une
fonction sans modifier le fichier de configuration.

### M10 - Tests de logique - À faire

- [ ] Tester les déplacements et les murs.
- [ ] Tester la collecte des deux types de pacgums.
- [ ] Tester les scores configurables.
- [ ] Tester les collisions avec les fantômes.
- [ ] Tester la perte et le respawn.
- [ ] Tester le chronomètre et la pause.
- [ ] Tester les 10 niveaux, la victoire et la défaite.
- [ ] Tester chaque cheat.
- [ ] Tester une panne simulée du générateur.

## 7. Tâches de JulesCamuzet

### J01 - Base Pygame et sprites - Première version terminée

- [x] Initialisation de Pygame et création de la fenêtre.
- [x] Boucle d'événements principale.
- [x] Limiteur de FPS compatible avec les contraintes MLX.
- [x] Découpage de la spritesheet.
- [x] Animation Pacman sur l'écran d'accueil.
- [x] Première navigation Welcome, Menu et Scores.

### J02 - Unifier les highscores avec la couche de données - À faire

Fichiers : `pacman/ui/pages/scores.py`, `pacman/highscores.py`.

- [ ] Supprimer la lecture JSON dupliquée dans `ScoresPage`.
- [ ] Recevoir `list[HighscoreEntry]` depuis `AppMain`.
- [ ] Afficher uniquement les 10 scores déjà triés.
- [ ] Afficher une liste vide sans lever d'exception.
- [ ] Utiliser `highscore_filename` au lieu de `SCORES_PATH`.
- [ ] Supprimer la divergence entre `data/scores.json` et
  `highscores.json`.

Critère d'acceptation : l'UI et la logique lisent exactement le même
fichier de scores.

### J03 - Affichage du labyrinthe - À faire

- [ ] Créer l'écran de jeu.
- [ ] Calculer la taille d'une cellule depuis la fenêtre et `MazeData`.
- [ ] Dessiner les murs avec les bits nord, est, sud et ouest.
- [ ] Dessiner correctement des labyrinthes rectangulaires.
- [ ] Conserver une zone dédiée au HUD.
- [ ] Ne jamais modifier `MazeData` pendant le rendu.

Critère d'acceptation : une carte `21x21` et une carte rectangulaire sont
affichées sans mur manquant ou décalé.

### J04 - Contrôles du joueur et animations - À faire

- [ ] Lire les flèches et les touches WASD.
- [ ] Transmettre une `Direction` au moteur sans déplacer directement le
  joueur dans l'UI.
- [ ] Choisir l'animation selon la direction.
- [ ] Afficher l'animation de mort lorsque le joueur perd une vie.
- [ ] Garder le rendu fluide lorsque le moteur refuse un mouvement.

### J05 - Rendu des objets et des fantômes - À faire

- [ ] Ajouter les sprites des quatre fantômes.
- [ ] Afficher leur état normal, edible et mangé.
- [ ] Afficher les pacgums et super-pacgums.
- [ ] Retirer visuellement un objet dès que `GameState` ne le contient
  plus.
- [ ] Afficher le respawn des fantômes dans leur coin.

### J06 - HUD permanent - À faire

- [ ] Afficher le score.
- [ ] Afficher les vies restantes.
- [ ] Afficher le niveau courant sur le total.
- [ ] Afficher le temps restant.
- [ ] Afficher l'état de pause.
- [ ] Afficher si le cheat mode est actif.

Critère d'acceptation : le HUD reste visible pendant toute la partie et
reflète `GameState` sans retard.

### J07 - Menu principal complet - À faire

Le sujet demande exactement :

- [ ] Start Game.
- [ ] View Highscores.
- [ ] Instructions.
- [ ] Exit.

Le bouton `Settings` actuel doit devenir `Instructions`, sauf si un écran
Settings supplémentaire est conservé sans remplacer une entrée obligatoire.

### J08 - Pause et navigation - À faire

- [ ] Ouvrir le menu de pause avec Échap.
- [ ] Reprendre la partie.
- [ ] Retourner au menu principal.
- [ ] Empêcher le jeu de continuer derrière le menu de pause.
- [ ] Gérer la fermeture de fenêtre depuis chaque page.

### J09 - Game over, victoire et saisie du nom - À faire

- [ ] Écran Game Over avec score final.
- [ ] Écran Victory avec score final et message de félicitations.
- [ ] Champ de saisie limité à 10 caractères.
- [ ] Refuser les caractères non autorisés avec un message compréhensible.
- [ ] Appeler `add_highscore()` puis `save_highscores()`.
- [ ] Revenir au menu après la sauvegarde.

### J10 - Finition visuelle et compatibilité MLX - À faire

- [ ] Vérifier que chaque fonction Pygame utilisée possède un équivalent
  documenté dans `MLX_MAPPING.md`.
- [ ] Retirer toute fonction Pygame sans équivalent acceptable.
- [ ] Vérifier le contraste, l'alignement et la lisibilité.
- [ ] Vérifier le redimensionnement ou choisir une taille de fenêtre fixe
  cohérente.
- [ ] Ajouter les instructions minimales dans le package.
- [ ] Tester le clavier sur les deux machines de l'équipe.

## 8. Tâches partagées

### S01 - Intégration AppMain, Game et Ui

- [ ] `AppMain` construit `Game` après la configuration.
- [ ] `AppMain` transmet les données validées à `Ui`.
- [ ] `Ui` transmet seulement les intentions du joueur au moteur.
- [ ] `Game` expose un état lisible par l'UI.
- [ ] Aucun second parser JSON n'existe dans l'UI.
- [ ] Une erreur métier affiche un message propre et retourne au menu.

### S02 - Tests d'intégration et sessions manuelles

- [ ] Tester une partie complète jusqu'à la victoire.
- [ ] Tester une partie complète jusqu'au game over.
- [ ] Tester une configuration modifiée pendant l'exécution.
- [ ] Tester un fichier absent, cassé et contenant des commentaires.
- [ ] Tester seed `42`, seed `0` et une carte rectangulaire.
- [ ] Tester le top 10 après victoire et après défaite.
- [ ] Tester la pause et chaque cheat.
- [ ] Tester le lancement depuis un environnement virtuel neuf.

Après chaque session, ajouter une ligne dans le journal de progression et
créer un ticket pour chaque bug reproductible.

### S03 - README final en anglais

- [ ] Première ligne en italique avec les deux logins 42.
- [ ] Description du projet.
- [ ] Instructions d'installation et de lancement.
- [ ] Ressources utilisées.
- [ ] Explication de l'utilisation de l'IA.
- [ ] Configuration et valeurs par défaut.
- [ ] Fonctionnement des highscores.
- [ ] Intégration de MazeGenerator.
- [ ] Résumé technique de l'implémentation.
- [ ] Architecture générale.
- [ ] Résumé de la gestion de projet avec lien vers ce dossier.
- [ ] Contrôles, cheat mode et exemples d'utilisation.

### S04 - Packaging et Itch.io

Plateforme retenue pour le plan : **Itch.io**, en build gratuit et non
listé.

- [ ] Choisir PyInstaller et ajouter le fichier `.spec` à la racine.
- [ ] Inclure la spritesheet, la configuration et les ressources.
- [ ] Gérer les chemins des ressources dans le build.
- [ ] Régénérer le package uniquement avec une commande documentée.
- [ ] Tester le package sur les deux machines.
- [ ] Vérifier qu'aucun environnement virtuel n'est inclus.
- [ ] Ajouter les instructions minimales dans le package.
- [ ] Publier un build privé ou non listé sur Itch.io.
- [ ] Tester le téléchargement et le lancement du build publié.

### S05 - Préparation de la soutenance

- [ ] Cloner le dépôt dans un dossier neuf.
- [ ] Exécuter `make install`, `make test`, `make lint`, `make run`.
- [ ] Réinstaller le wheel A-Maze-ing fourni.
- [ ] Modifier une valeur de configuration et vérifier son effet.
- [ ] Expliquer chaque modèle Pydantic.
- [ ] Expliquer le bitmask du labyrinthe.
- [ ] Expliquer la boucle de jeu et le delta time.
- [ ] Démontrer les cheats.
- [ ] Régénérer le package.
- [ ] Préparer chacun une petite modification réalisable en quelques
  minutes.

## 9. Kanban immédiat

### À faire maintenant

1. **Mind-alia - M04** : créer les entités et `GameState`.
2. **JulesCamuzet - J02** : connecter `ScoresPage` aux highscores validés.
3. **Partagé - S01** : valider le contrat exact entre `Game` et `Ui`.

### Ensuite

1. **Mind-alia - M05 et M06** : mouvements, murs, pacgums et score.
2. **JulesCamuzet - J03 et J04** : renderer du maze, contrôles et Pacman.
3. Faire une première intégration : niveau jouable sans fantômes.

### Après la première version jouable

1. **Mind-alia - M07 à M09** : fantômes, progression et cheat mode.
2. **JulesCamuzet - J05 à J09** : HUD et tous les écrans de fin.
3. **Partagé** : tests complets, documentation et packaging.

## 10. Plan de tests d'acceptation

| ID | Fonction testée | Résultat attendu | Responsable |
| --- | --- | --- | --- |
| A01 | Lancement avec un JSON valide | Le menu apparaît sans traceback | Partagé |
| A02 | Configuration commentée | Les commentaires sont ignorés | Mind-alia |
| A03 | Valeur absente ou invalide | Valeur sûre et message clair | Mind-alia |
| A04 | Clé inconnue | La clé est ignorée | Mind-alia |
| A05 | Premier niveau | Maze reproductible avec seed 42 | Mind-alia |
| A06 | Niveau suivant | Nouveau maze aléatoire | Mind-alia |
| A07 | Mouvement contre un mur | Le joueur reste sur place | Mind-alia |
| A08 | Pacgum mangée | Objet retiré et score augmenté | Mind-alia |
| A09 | Super-pacgum mangée | Fantômes edible et score augmenté | Partagé |
| A10 | Collision avec un fantôme | Vie perdue et respawn au centre | Mind-alia |
| A11 | Fantôme edible mangé | Points ajoutés et fantôme respawn | Mind-alia |
| A12 | Fin du temps | Vie perdue et niveau recommencé | Mind-alia |
| A13 | Fin d'un niveau | Passage au niveau suivant | Partagé |
| A14 | Fin du dixième niveau | Écran de victoire | Partagé |
| A15 | Zéro vie | Écran Game Over | Partagé |
| A16 | Pause | Jeu et temps arrêtés puis repris | Partagé |
| A17 | Cheat mode | Chaque commande produit son effet | Partagé |
| A18 | Highscore valide | Score sauvegardé et visible au menu | Partagé |
| A19 | Nom invalide | Sauvegarde refusée proprement | Partagé |
| A20 | Package Itch.io | Téléchargement et lancement réussis | Partagé |

## 11. Analyse des risques

| Risque | Impact | Probabilité | Prévention et solution | Responsable |
| --- | --- | --- | --- | --- |
| Interface du wheel modifiée pendant l'évaluation | Élevé | Moyen | Garder l'adaptation uniquement dans `maze.py` et tester la réinstallation | Mind-alia |
| Fonction Pygame sans équivalent MLX | Élevé | Moyen | Mettre à jour `MLX_MAPPING.md` à chaque nouvelle fonction | JulesCamuzet |
| Logique du jeu mélangée à l'UI | Élevé | Moyen | Interdire les imports Pygame dans `game.py` et `entities.py` | Partagé |
| Deux fichiers de highscores différents | Moyen | Élevé | Supprimer `SCORES_PATH` et utiliser `GameConfig.highscore_filename` | JulesCamuzet |
| Conflits Git sur les fichiers partagés | Moyen | Moyen | Un propriétaire temporaire et petites pull requests | Partagé |
| Assets absents du package | Élevé | Moyen | Test du build depuis un dossier neuf | JulesCamuzet |
| Comportement dépendant du FPS | Élevé | Moyen | Utiliser `delta_time` dans le moteur et tests à plusieurs FPS | Mind-alia |
| Manque de temps pour le packaging | Élevé | Moyen | Créer le `.spec` avant la finition visuelle complète | Partagé |
| Configuration modifiée en soutenance | Élevé | Élevé | Valeurs par défaut, clés inconnues ignorées et tests dédiés | Mind-alia |

## 12. Décisions techniques

| Décision | Raison |
| --- | --- |
| Pydantic pour les données | Types clairs, validation centralisée et messages d'erreur |
| Pygame limité aux équivalents MLX | Respect de la contrainte graphique du sujet |
| MazeGenerator derrière `generate_maze()` | Isoler l'interface du package externe |
| JSON pour les highscores | Format simple, lisible et facile à tester |
| Logique sans Pygame | Tests unitaires rapides et séparation nette |
| `GameState` lu par l'UI | Éviter que l'UI duplique les règles |
| Itch.io et PyInstaller | Publication gratuite, build privé et régénérable |
| Pull requests courtes | Relecture plus simple et moins de conflits |

## 13. Blocages et problèmes rencontrés

| Date | Problème | Solution | État |
| --- | --- | --- | --- |
| 25 juillet 2026 | Arborescence initiale trop complexe | Réduction à des modules ciblés | Résolu |
| 25 juillet 2026 | Résultat numérique du maze difficile à comprendre | Documentation du bitmask `1, 2, 4, 8` | Résolu |
| 27 juillet 2026 | Push SSH GitHub temporairement impossible | Vérification des ports et nouvelle tentative | Résolu |
| 28 juillet 2026 | `mazegenerator` sans stubs Mypy | Ignorer uniquement les imports externes non typés | Résolu |
| 28 juillet 2026 | Fichier de scores vide non valide | Initialiser le JSON avec `[]` | Résolu |
| 28 juillet 2026 | Deux chemins de highscores dans le projet | Tâche J02 pour unifier les deux couches | Ouvert |
| 28 juillet 2026 | `AppMain` et `Ui` non connectés | Tâche partagée S01 | Ouvert |

## 14. Journal de progression

| Date | Réalisé | Preuve | Prochaine étape |
| --- | --- | --- | --- |
| 25 juillet 2026 | Arborescence, Makefile et configuration initiale | commits de fondation | Parser et modèles |
| 28 juillet 2026 | Config, maze, highscores et CLI validés | commit `f2a94b0`, 19 tests | Moteur de jeu |
| 28 juillet 2026 | Welcome, menu, scores et sprites intégrés sur `main` | commits UI jusqu'à `5cb6844` | Renderer du maze |
| 28 juillet 2026 | Plan complet réparti entre deux développeurs | ce document | M04, J02 et S01 |

Ce tableau doit être complété après chaque pull request fusionnée avec la
date, le résultat obtenu, le lien ou commit de preuve et la prochaine
étape concrète.

## 15. Definition of Done

Une tâche est terminée uniquement si :

- son comportement est démontrable ;
- les erreurs attendues sont gérées sans traceback ;
- des tests automatiques couvrent la logique lorsque c'est possible ;
- `make test` passe ;
- `make lint` passe ;
- l'autre développeur a relu la pull request ;
- la documentation concernée est mise à jour ;
- aucun fichier temporaire, cache ou score local n'est commité.

Le projet complet est terminé uniquement lorsque les 20 tests
d'acceptation sont réussis depuis un clone neuf et que le build Itch.io
peut être téléchargé et lancé.
