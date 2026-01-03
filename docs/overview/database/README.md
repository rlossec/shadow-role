# Schéma de Base de Données

Ce document décrit le schéma complet de la base de données Shadow Role.

## Modèles SQLAlchemy

Les modèles sont définis dans `backend/app/models/` :

- `user.py` : Modèle User
- `game.py` : Modèle Game
- `lobby.py` : Modèle Lobby
- `player.py` : Modèle Player
- `mission.py` : Modèle Mission
- `mission_assigned.py` : Modèle AssignedMission
- `round.py` : Modèle Round

## Contraintes et Index

### Index Principaux

- `users.username` : Index unique
- `users.email` : Index unique
- `lobbies.code` : Index unique
- `players.lobby_id` : Index pour requêtes fréquentes
- `missions.game_id` : Index pour filtrage par jeu

### Contraintes

- Clés étrangères avec `ondelete` approprié
- Unicité des champs marqués `unique=True`
- Valeurs par défaut pour les champs optionnels

Voir le [Modèle Conceptuel de Données](./mcd.md) pour une description détaillée.
