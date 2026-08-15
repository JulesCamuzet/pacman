# Project management — Pacman

Dernière mise à jour : 15 août 2026
Équipe : **Alexis Lasserre (`allasser`)** et **Jules Camuzet (`jcamuzet`)**

Ce document rassemble les preuves de gestion du projet : organisation de
l'équipe, planning prévu et réel, décisions techniques, risques, problèmes,
tests d'acceptation et travail restant. Il décrit l'état réel du dépôt et doit
être mis à jour jusqu'à la livraison.

## 1. Objectif et contraintes du sujet

L'objectif est de livrer un Pacman jouable en Python 3.13 avec Pygame. Le jeu
doit charger sa configuration depuis un fichier JSON, générer ses labyrinthes,
gérer plusieurs niveaux et des highscores, puis être fourni sous une forme
installable et jouable sur Itch.io.

Contraintes suivies par l'équipe :

- un seul argument en ligne de commande : le chemin du fichier JSON ;
- données d'entrée contrôlées avant leur utilisation ;
- erreurs signalées proprement sans traceback pour le joueur ;
- labyrinthe généré par la bibliothèque fournie, avec un chemin de sortie ;
- déplacements, pacgums, score, vies, fantômes et progression de niveau ;
- temps limité par niveau, écran de victoire et écran de défaite distincts ;
- highscores persistants et limités aux dix meilleurs résultats ;
- documentation de l'installation, de l'architecture et de la gestion du
  projet ;
- cheat mode et packaging local terminés ; déploiement Itch.io à effectuer
  avant la remise finale.

## 2. Organisation de l'équipe

| Domaine | Responsable principal | Travail réalisé |
| --- | --- | --- |
| Structure initiale du dépôt | Alexis | Arborescence minimale, fichiers de base, `.gitignore`, Makefile |
| Configuration et données | Alexis | Lecture JSON, normalisation, modèles Pydantic, valeurs de secours |
| Génération du labyrinthe | Alexis | Adaptateur de `mazegenerator`, conversion des murs, validation des données |
| Highscores côté données | Alexis | Modèle validé, lecture tolérante, tri et conservation du top 10 |
| Interface Pygame | Jules | Fenêtre, pages, menus, affichage, sprites, police et mise en page |
| Pacman et rendu du jeu | Jules | Affichage du maze, rails, Pacman, mouvements, animation, HUD et pause |
| Fantômes et intelligence artificielle | Alexis | Quatre fantômes, BFS, cibles propres, modes et collisions |
| Progression de partie | Partagé | Niveaux, score, vies, timer, victoire, défaite et intégration UI/moteur |
| Stabilisation finale | Alexis + Jules | Tests manuels, correction des derniers bugs et préparation de la remise |

Cette répartition garde une frontière simple : Alexis produit et valide les
données et les règles de jeu ; Jules transforme cet état en interface Pygame.
Les changements qui touchent les deux couches sont vérifiés ensemble.

## 3. Méthode de collaboration

- Le dépôt GitHub commun est `JulesCamuzet/pacman`.
- Chaque fonctionnalité importante est développée sur une branche dédiée,
  puis intégrée après vérification.
- Les commits servent de journal technique et restent limités à un objectif.
- Avant une intégration, l'auteur exécute les tests et le lint disponibles.
- Les contrats partagés (`GameConfig`, `MazeData`, `GameState`) sont discutés
  avant de modifier l'interface ou le moteur.
- Une décision simple est prise par le responsable du domaine. Une décision
  qui affecte les deux parties est validée par Alexis et Jules.
- Un bug bloquant est reproduit, isolé, corrigé puis couvert par un test quand
  cela est raisonnable.
- Les derniers bugs d'intégration sont traités en binôme afin de contrôler à
  la fois le comportement du moteur et son rendu.

## 4. Planning prévu et avancement réel

Le planning de départ séparait le projet en fondations, moteur et interface.
Dans la pratique, le moteur et l'interface ont avancé en parallèle, puis les
fantômes et les règles finales ont été intégrés après le premier jeu jouable.

| Période prévue | Lot prévu | Réalisation effective | Écart constaté |
| --- | --- | --- | --- |
| 23–25 juillet | Dépôt et structure | Arborescence, configuration initiale, Makefile et nettoyage Git | Conforme |
| 25–28 juillet | Données et maze | JSON, Pydantic, génération et highscores préparés par Alexis | Conforme |
| 28 juillet–1 août | Première version jouable | UI, maze, Pacman, menus, HUD, pause et niveaux réalisés par Jules | Conforme, intégration progressive |
| 2–7 août | Fantômes et stabilisation | Phase décalée : analyse et préparation avant implémentation | Retard sur les fantômes |
| 8–10 août | IA et intégration | BFS, quatre fantômes, collisions, rendu et menu de génération par Alexis | Retard rattrapé |
| 11–13 août | Finition fonctionnelle | maze non parfait, IA équilibrée, timer, victoire et tests d'application | Conforme au planning révisé |
| 15 août | Conformité | Cheat mode, highscores UI, IA, configuration, tests et package macOS ARM64 | Réalisé |
| Avant remise | Livraison | Upload Itch.io et test du téléchargement sur une machine propre | À terminer |

## 5. Journal de progression

| Date | Auteur | Résultat vérifiable |
| --- | --- | --- |
| 23 juillet | Jules | Création initiale du dépôt |
| 23–25 juillet | Alexis | Structure minimale, `.gitignore`, configuration et Makefile |
| 27 juillet | Équipe | Première intégration par pull request |
| 28 juillet | Alexis | Couche de données validée pour l'interface (`f2a94b0`) |
| 28–31 juillet | Jules | Menus, maze, Pacman, mouvements, HUD, niveaux, scores et responsive |
| 8 août | Alexis | BFS commun, initialisation des fantômes et collisions |
| 9–10 août | Alexis | Affichage des fantômes et génération de maze depuis le menu |
| 10 août | Jules | Ajustement de la fenêtre et des tailles de police |
| 12 août | Alexis | maze toujours non parfait, IA classique, timer et victoire distincte |
| 13 août | Alexis | Documentation finale et audit des exigences restantes |

## 6. Kanban actuel

### Terminé

- [x] Initialiser et nettoyer le dépôt.
- [x] Définir la configuration JSON et ses valeurs de secours.
- [x] Valider les données avec Pydantic.
- [x] Convertir la sortie du générateur en `MazeData` exploitable.
- [x] Afficher le labyrinthe, Pacman, les pacgums et le HUD.
- [x] Gérer les déplacements, la pause, les vies et les niveaux.
- [x] Afficher quatre fantômes avec leurs sprites.
- [x] Utiliser un BFS commun pour leurs déplacements.
- [x] Donner une cible de poursuite différente à chaque fantôme.
- [x] Alterner les modes scatter et chase.
- [x] Gérer le mode frightened, les fantômes mangés et leur réapparition.
- [x] Centraliser le ratio de vitesse des fantômes.
- [x] Réinitialiser les fantômes après la perte d'une vie.
- [x] Limiter le temps de chaque niveau.
- [x] Séparer victoire finale et défaite.
- [x] Forcer la génération de labyrinthes non parfaits.
- [x] Ajouter une page de génération qui lance directement la partie.
- [x] Ajouter des tests automatisés pour les règles principales.
- [x] Ajouter et documenter le cheat mode d'évaluation.
- [x] Relier toute l'interface au service Pydantic des highscores.
- [x] Permettre à une liste vide ou partielle d'atteindre dix scores.
- [x] Garantir une vitesse effective des fantômes inférieure à Pacman.
- [x] Préparer et lancer le package PyInstaller macOS ARM64.

### En cours

- [ ] Tester manuellement une partie complète sur les machines cibles.
- [ ] Ajuster la zone de collision Pacman/fantôme après test de jouabilité.
- [ ] Télécharger le futur package publié et jouer une partie complète sur
  une machine propre.

### À faire avant la remise

- [ ] Déployer la version jouable sur Itch.io.

## 7. Choix techniques et décisions

| Décision | Pourquoi | Conséquence |
| --- | --- | --- |
| Python 3.13 + Pygame | Stack demandée et adaptée à une boucle de jeu 2D | Installation reproductible avec `.venv` |
| Pydantic pour les contrats | Valider les types, limites et formes des données | L'UI reçoit des objets structurés |
| Normalisation avant validation | Le sujet demande un comportement propre en cas de mauvaise configuration | Valeurs invalides remplacées avec un warning |
| Adaptateur autour de `mazegenerator` | Isoler la dépendance externe du reste du jeu | Le moteur consomme uniquement `MazeData` |
| `perfect=False` imposé | Le sujet et la jouabilité exigent des chemins alternatifs | L'option n'est plus exposée au joueur |
| BFS commun aux quatre fantômes | Algorithme lisible, fiable et partagé | Chaque fantôme change seulement sa cible |
| Cibles inspirées du Pacman classique | Éviter quatre poursuivants identiques | Rouge direct, rose en avant, bleu vectoriel, orange selon la distance |
| Modes scatter/chase/frightened/eaten | Créer des respirations et une difficulté plus juste | Le comportement varie pendant la partie |
| Ratio fantôme configuré à 75 % | La première version était trop difficile | Arrondi borné pour garder au moins un pixel/frame d'écart avec Pacman |
| Page Generate en une action | Garder une interface simple | Un seed aléatoire est créé puis le jeu démarre |
| Timer basé sur une échéance | Éviter les dérives et gérer la pause | L'échéance est décalée pendant la pause |

## 8. Risques et mesures de réduction

| Risque | Probabilité | Impact | Mesure prise ou prévue |
| --- | --- | --- | --- |
| Générateur externe sans stubs mypy | Élevée | Moyen | `--ignore-missing-imports` dans le lint courant ; isoler l'import dans `maze.py` |
| JSON absent ou corrompu | Moyenne | Élevé | Valeurs de configuration sûres et lecture de scores tolérante |
| Régression du highscore | Faible | Élevé | Service Pydantic unique utilisé par le moteur et toute l'UI |
| IA trop difficile | Faible | Élevé | Modes classiques, fuite BFS et fantômes réellement plus lents |
| Collision ressentie comme injuste | Faible | Élevé | Distance ramenée à 55 % d'une case et couverte par des tests |
| Fenêtre trop grande selon l'écran | Faible | Moyen | Format fixe 1000×900 et contenu borné par des tests de mise en page |
| Maze injouable | Faible | Élevé | Vérification des dimensions, murs, coordonnées et shortest path |
| Régression lors de l'intégration | Moyenne | Élevé | pytest, flake8, mypy et tests manuels avant fusion |
| Packaging tardif | Moyenne | Élevé | Réserver un lot dédié avant la remise et tester sur machine propre |
| Blocage du push SSH GitHub | Moyenne | Moyen | Vérifier la clé, les droits et le remote avant la livraison |

## 9. Problèmes rencontrés et résolutions

| Problème | Cause identifiée | Résolution |
| --- | --- | --- |
| Branche sans upstream | Première publication de la branche | Utiliser `git push --set-upstream origin <branche>` |
| Connexion GitHub SSH impossible | Port 22 ou configuration de clé indisponible | Vérifier la clé/remote ; ne pas confondre avec une erreur du code |
| mypy refuse `mazegenerator` | Bibliothèque fournie sans stubs ni `py.typed` | Ignorer uniquement les imports externes non typés dans le lint courant |
| Highscore absent ou vide | Fichier inexistant ou JSON vide | Retourner une liste vide côté API robuste ; initialiser le fichier avec `[]` |
| Fantômes absents à l'écran | État moteur non relié au renderer | Ajouter `DisplayGhosts` et charger les sprites correspondants |
| Fantômes trop rapides/difficiles | Poursuite trop efficace et vitesse entière parfois identique à Pacman | Scatter/chase, fuite frightened et vitesse entière strictement inférieure |
| Partie perdue avant de jouer | Collision ou état mal réinitialisé | Réinitialiser Pacman, fantômes et cycle après une vie perdue |
| Fenêtre mal adaptée | Ancien canevas haut de 1500 pixels | Utiliser un format fixe 1000×900 et recentrer le maze et le HUD |
| Option perfect incohérente | Possibilité d'activer un mode non souhaité | Retirer l'option et toujours passer `perfect=False` |

## 10. Plan de tests d'acceptation

### Tests automatisés

| Critère | Test ou commande | État |
| --- | --- | --- |
| Configuration valide et valeurs de secours | `tests/test_config.py` | Couvert |
| Initialisation et règles générales | `tests/test_game.py` | Couvert |
| Placement et dimensions | `tests/test_game_layout.py` | Couvert |
| Victoire et défaite | `tests/test_game_outcome.py` | Couvert |
| Quatre fantômes et rendu | `tests/test_ghost_display.py` | Couvert |
| BFS, cibles, modes et collisions | `tests/test_ghosts.py` | Couvert |
| Lecture, validation, UI et top 10 | `tests/test_highscores.py` | Couvert |
| Cheat mode et contrôles | `tests/test_cheats.py` | Couvert |
| Timer et pause | `tests/test_level_timer.py` | Couvert |
| Page de génération | `tests/test_maze_generator_page.py` | Couvert |
| Suite complète | `make test` | 86 tests validés le 15 août 2026 |
| Style et types | `make lint-strict` | flake8 et mypy strict validés le 15 août 2026 |

### Recette manuelle finale

| Scénario | Résultat attendu | État |
| --- | --- | --- |
| Lancer avec `make run` | Fenêtre centrée, écran d'accueil, aucun traceback | À revalider |
| Jouer avec les flèches | Pacman suit les couloirs et ne traverse pas les murs | À revalider |
| Manger une super-pacgum | Tous les fantômes actifs deviennent mangeables temporairement | À revalider |
| Toucher un fantôme actif | Une seule vie perdue et positions réinitialisées | À revalider |
| Perdre toutes les vies | Écran de défaite puis saisie du score | À revalider |
| Vider tous les niveaux | Écran de victoire distinct | À revalider |
| Attendre la fin du timer | Défaite propre à zéro seconde | À revalider |
| Mettre le jeu en pause | Timer et modes fantômes ne progressent pas | À revalider |
| Générer depuis le menu | Nouveau maze non parfait et partie immédiate | À revalider |
| Liste contenant 0 à 9 scores | Un nouveau score valide complète la liste jusqu'à dix entrées | Couvert automatiquement |
| JSON de configuration invalide | Warnings lisibles et valeurs sûres | À revalider |
| Package local | Build macOS ARM64 et lancement sans argument | Couvert localement |
| Package téléchargé | Le jeu démarre depuis la plateforme sans environnement de développement | À faire après upload |

## 11. Blocages et conflits

Aucun conflit humain bloquant n'est enregistré. Les responsabilités ont été
séparées pour limiter les modifications simultanées sur les mêmes fichiers.
Les difficultés principales ont été techniques : accès SSH à GitHub,
compatibilité mypy de la bibliothèque de maze, mise à l'échelle Pygame et
équilibrage de l'IA.

Quand une modification moteur affecte le rendu, le responsable explique le
nouveau contrat puis les deux membres testent l'intégration. En cas de
désaccord, l'équipe choisit d'abord la solution qui respecte le sujet, puis la
plus simple à lire et à maintenir.

## 12. Definition of Done

Une tâche est terminée lorsque :

- son comportement correspond au ticket et au sujet ;
- les erreurs usuelles sont gérées sans crash visible ;
- les tests concernés passent ;
- `make lint` ne signale pas de nouvelle erreur ;
- le jeu a été testé manuellement si la tâche touche l'affichage ;
- la documentation et le mapping MLX sont mis à jour si nécessaire ;
- le code est relu par l'autre membre lorsqu'il traverse la frontière
  moteur/interface ;
- le commit ne contient pas de fichiers locaux, temporaires ou secrets.

Le projet complet sera considéré comme livré lorsque l'archive préparée aura
été publiée sur Itch.io, téléchargée sur une machine propre et validée par la
recette manuelle finale.
