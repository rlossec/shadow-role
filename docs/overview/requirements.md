# Cahier des Charges - ShadowRole

## Principe du jeu

On débute le jeu, un rôle ou une mission est attribué à chaque joueur de manière aléatoire.

> Une **mission** sera donnée au joueur mais sera secrète auprès des autres joueurs
> Un **rôle** sera secret auprès du joueur qui devra le deviner et sera communiqué aux autres joueurs.

**Phase :**

- Suggestion : Les joueurs peuvent proposer des missions ou des rôles.
- Round : A l’oral, les joueurs jouent et essayer de deviner les missions rôles
- Validation : L’host/admin valide les points (possible concertations)

## 2. Objectifs du projet

- Permettre la création de lobbies de jeu par les utilisateurs
- Distribuer dynamiquement des rôles / missions aux joueurs
- Gérer les sessions de jeu en temps réel via WebSocket
- Suivre les scores et les performances des joueurs

## 3. Fonctionnalités principales

### 3.1. Authentification utilisateur

- Inscription / Connexion avec email et mot de passe
- Authentification basée sur JWT (JSON Web Tokens)
- Gestion des sessions utilisateur
- Profil utilisateur avec historique de parties

### 3.2. Jeux

- Un lobby peut être associé à un jeu
- Un jeu définira les règles et les missions ou rôles associés

### 3.3. Rôles et missions

- Création de bibliothèque de rôles par jeu
- Missions peut avoir des types différents signalant à qui elles sont communiqués
- Niveaux de difficulté des missions : indicatif puis taux de succès

### 3.4. Lobby

- Création de lobby avec code unique partageable
- Rejoindre un lobby via code
- Paramétrage du nombre de joueurs par lobby
- Expiration automatique des lobbies inactifs
- Statuts des lobbies : "waiting | running | paused | ended"
- Phase des lobbies : "none | suggestion | round | validation"

### 3.5. Communication temps réel

- WebSocket pour les mises à jour instantanées
- Notifications d'événements (joueur rejoint/part, mission complétée, etc.)
