# Game Steps

## Préalable - API REST

Avant que l'on souhaite lancer une partie, des données sont nécessaires : Le jeu, les missions associées ou la création de compte utilisateurs.

1. Création de comptes utilisateurs
2. Création d'un jeu - Game
3. Ajout de mission sur un jeu
4. Création d'un lobby sur un jeu

## Session de jeu

5. Les utilisateurs se connectent à la websocket (considéré par défaut comme spectateur dans le lobby)
6. Les utilisateurs et l'host peuvent s'enregistrer comme joueur (ou rester spectateur)
7. L'host peut lancer la partie (sous vérification des contraintes)
8. La partie a la status "waiting" et l'host décide des étapes suivantes :

   8.1. Phase de suggestion,
   8.2. Phase de jeu/Round
   8.3. Phase de Validation

## Phase de suggestion

Si l'hôte enclenche la phase de suggestion, chaque joueur peut utiliser la websocket pour donner des idées de missions/roles. Elles n'ont le statut que de suggestion dans un premier temps.
L'hôte a la possibilité de voir les suggestions s'il n'est pas joueur. Auquel cas il peut sélectionner ou ignorer chaque suggestion, ainsi que d'inclure les missions du jeu.
Il peut valider sa sélection et ainsi clore cette phase.

## Phase de jeu/Round

L'hôte peut lancer cette phase (contraine qu'il y ait suffisamment de missions/roles pour un round).
Côté applicatif, il ne se passe rien, le jeu se passe à l'oral.
L'hôte décide quand il souhaite clore le round.

## Phase de Validation

L'hôte peut passer à la validation (si un round n'a pas été validé).
Auquel cas il peut décider de quelles missions/roles ont été bien réalisé. Il peut ajuster les points également.
