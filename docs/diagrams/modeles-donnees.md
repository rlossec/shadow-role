# Modèles de Données - ShadowRole

Ce document décrit en détail tous les modèles de données du système ShadowRole.

## Diagramme MCD

Voir le fichier `mcd.mermaid` pour le diagramme Mermaid complet des entités et relations.

---

## 1. USER

Représente un utilisateur de la plateforme avec ses informations de connexion et de profil.

### Attributs

| Attribut        | Type     | Description                | Contraintes                       |
| --------------- | -------- | -------------------------- | --------------------------------- |
| `id`            | UUID     | Identifiant unique         | PK, généré automatiquement        |
| `username`      | String   | Nom d'utilisateur          | Obligatoire, unique               |
| `email`         | String   | Adresse email              | Obligatoire, unique, format email |
| `password_hash` | String   | Hash du mot de passe       | Obligatoire, hashé avec bcrypt    |
| `created_at`    | DateTime | Date de création du compte | Automatique                       |
| `updated_at`    | DateTime | Dernière mise à jour       | Automatique                       |
| `is_active`     | Boolean  | Compte actif/suspendu      | Par défaut : true                 |

### Relations

- **Héberge des lobbies** : Un utilisateur peut créer plusieurs lobbies au fil du temps (1-N)
  **Contrainte** : il ne peut créer qu'un seul lobby actif à la fois.
- **Participe** : Un utilisateur peut être joueur dans plusieurs lobbies au fil du temps (1-N via PLAYER)
  **Contrainte** : il ne peut rejoindre qu'un seul lobby actif à la fois.

### Métadonnées

- Index sur `email` et `username` pour performances

---

## 2. LOBBY (Session de Jeu)

Une session de jeu active ou en attente, créée par un utilisateur.

### Attributs

| Attribut          | Type     | Description                    | Contraintes                              |
| ----------------- | -------- | ------------------------------ | ---------------------------------------- |
| `id`              | UUID     | Identifiant unique             | PK, généré automatiquement               |
| `name`            | String   | Nom du lobby                   | Obligatoire, max 100 caractères          |
| `code`            | String   | Code d'invitation              | UK, généré aléatoirement, unique         |
| `game_id`         | UUID     | Type de jeu utilisé            | FK vers GAME, obligatoire                |
| `host_id`         | UUID     | Créateur/gestionnaire du lobby | FK vers USER, obligatoire                |
| `status`          | Enum     | État du lobby                  | waiting, starting, in_progress, finished |
| `max_players`     | Integer  | Nombre maximum de joueurs      | Obligatoire, min: 2, max: 100            |
| `current_players` | Integer  | Nombre actuel de joueurs       | Calculé dynamiquement                    |
| `created_at`      | DateTime | Date de création               | Automatique                              |
| `expires_at`      | DateTime | Date d'expiration              | Optionnel, par défaut +2h                |

### Relations

- **Hébergé par** : Un lobby est créé par un utilisateur (N-1 vers USER)
- **Utilise** : Un lobby utilise un type de jeu (N-1 vers GAME)
- **Contient** : Un lobby contient plusieurs joueurs (1-N vers PLAYER)

### Métadonnées

- Index sur `code` pour recherche rapide
- Index sur `status` pour filtrage
- Auto-nettoyage des lobbies expirés (cron job)

### Règles métier

- **Host** : Le `host_id` peut être :
  - Un joueur participant (il a un PLAYER dans ce lobby)
  - Un admin qui gère le lobby sans jouer
- Seul le host peut démarrer le lobby (`status: waiting → starting`)
- Un lobby doit avoir au moins 2 joueurs pour démarrer
- Le `current_players` ne compte que les joueurs actifs, pas le host si celui-ci n'est pas joueur

---

## 3. GAME (Type de Jeu)

Définit les règles, configurations et types de jeux disponibles dans le système.

### Attribut

| Attribut      | Type     | Description             | Contraintes                       |
| ------------- | -------- | ----------------------- | --------------------------------- |
| `id`          | UUID     | Identifiant unique      | PK, généré automatiquement        |
| `name`        | String   | Nom du jeu              | Obligatoire, unique               |
| `description` | String   | Description du jeu      | Obligatoire                       |
| `rules`       | Text     | Règles détaillées       | Obligatoire                       |
| `type`        | Enum     | Type de mécanique       | role_based, mission_based, hybrid |
| `config`      | JSON     | Configuration dynamique | Ex: durée, nombre de rôles, etc.  |
| `created_at`  | DateTime | Date de création        | Automatique                       |
| `updated_at`  | DateTime | Dernière modification   | Automatique                       |

### Relations

- **Utilisé par** : Plusieurs lobbies peuvent utiliser ce jeu (1-N vers LOBBY)
- **Définit des missions** : Un jeu contient plusieurs missions (1-N vers MISSION)
- **Définit des rôles** : Un jeu contient plusieurs rôles (1-N vers ROLE)

### Exemples de types de jeux

- **role_based** : Jeux où chaque joueur a un rôle
- **mission_based** : Jeux avec objectifs à accomplir
- **hybrid** : Combinaison des deux mécaniques

### Métadonnées

- Le champ `config` peut contenir des paramètres comme :
  ```json
  {
    "min_players": 4,
    "max_players": 10,
    "hidden_roles": true,
    "allow_role_switch": false
  }
  ```

---

## 4. MISSION

Représente la **personnalité intellectuelle** d'un joueur dans un jeu. La mission peut évoluer durant la partie.

### Attributs

| Attribut                     | Type    | Description                     | Contraintes                |
| ---------------------------- | ------- | ------------------------------- | -------------------------- |
| `id`                         | UUID    | Identifiant unique              | PK, généré automatiquement |
| `game_id`                    | UUID    | Jeu associé                     | FK vers GAME, obligatoire  |
| `role_id`                    | UUID    | Rôle associé                    | FK vers ROLE, nullable     |
| `title`                      | String  | Titre de la mission             | Obligatoire                |
| `description`                | Text    | Description détaillée           | Obligatoire                |
| `difficulty`                 | Integer | Niveau de difficulté de 0 à 100 | Obligatoire, 0-100         |
| `estimated_duration_minutes` | Integer | Durée estimée                   | Obligatoire, en minutes    |
| `is_known_by_player`         | Boolean | Visible par le joueur lui-même  | Par défaut : true          |
| `is_known_by_others`         | Boolean | Visible par les autres joueurs  | Par défaut : false         |

### Relations

- **Appartient à** : Une mission est liée à un type de jeu (N-1 vers GAME)
- **Optionnellement liée** : Une mission peut être liée à un rôle spécifique (N-1 vers ROLE, nullable)
- **Assignée à** : Plusieurs joueurs peuvent recevoir la même mission (1-N vers PLAYER)

### Métadonnées

- Index sur `game_id` pour performances
- Index sur `role_id` pour recherches

### Règles métier

- **Visibilité** : Contrôle qui peut voir la mission
  - `is_known_by_player = true` : Le joueur voit sa propre mission
  - `is_known_by_others = true` : Tous les joueurs voient cette mission
  - Si les deux sont `false`, personne ne voit la mission (état initial)
- **Lien optionnel avec rôle** : Une mission peut être associée à un rôle via `role_id`
  - `role_id` nullable : la mission est indépendante
  - `role_id` non-null : la mission est liée à un rôle spécifique
- Les missions peuvent être partagées entre plusieurs joueurs (coop)

---

## 5. ROLE

Représente les **personnages possibles** dans un type de jeu. Chaque rôle est un personnage que les joueurs peuvent incarner.

### Attributs

| Attribut      | Type    | Description                     | Contraintes                 |
| ------------- | ------- | ------------------------------- | --------------------------- |
| `id`          | UUID    | Identifiant unique              | PK, généré automatiquement  |
| `game_id`     | UUID    | Jeu associé                     | FK vers GAME, obligatoire   |
| `name`        | String  | Nom du personnage               | Obligatoire, unique par jeu |
| `description` | Text    | Description du personnage       | Obligatoire                 |
| `image_url`   | String  | URL de l'image du personnage    | Optionnel                   |
| `min_players` | Integer | Minimum de joueurs avec ce rôle | Par défaut : 0              |

### Relations

- **Appartient à** : Un rôle est défini pour un type de jeu (N-1 vers GAME)
- **Optionnellement lié** : Une mission peut être liée à ce rôle (1-N vers MISSION via `role_id`)
- **Assigné à** : Plusieurs joueurs peuvent avoir le même rôle (1-N vers PLAYER)

### Métadonnées

- Index sur `game_id` pour performances

### Règles métier

- Les rôles (personnages) sont distribués aléatoirement au démarrage du lobby
- `min_players` garantit qu'un certain nombre de ce personnage existe dans chaque partie
- Un même personnage peut être incarné par plusieurs joueurs si `min_players > 0`
- **Visibilité gérée par la mission** : Si un rôle est lié à une mission (via `mission.role_id`), la visibilité du rôle est déterminée par les propriétés `is_known_by_player` et `is_known_by_others` de la mission associée

---

## 6. PLAYER

Représente la participation d'un utilisateur à un lobby avec son état dans la partie.

### Attributs

| Attribut    | Type     | Description               | Contraintes                            |
| ----------- | -------- | ------------------------- | -------------------------------------- |
| `id`        | UUID     | Identifiant unique        | PK, généré automatiquement             |
| `lobby_id`  | UUID     | Lobby de participation    | FK vers LOBBY, obligatoire             |
| `user_id`   | UUID     | Utilisateur joueur        | FK vers USER, obligatoire              |
| `role_id`   | UUID     | Rôle (personnage) assigné | FK vers ROLE, nullable avant démarrage |
| `score`     | Integer  | Score du joueur           | Par défaut : 0                         |
| `status`    | Enum     | État du joueur            | waiting, playing, completed, left      |
| `joined_at` | DateTime | Date d'arrivée            | Automatique                            |
| `left_at`   | DateTime | Date de départ            | Nullable                               |

### Relations

- **Participe à** : Un joueur appartient à un lobby (N-1 vers LOBBY)
- **Est un utilisateur** : Un joueur est lié à un utilisateur (N-1 vers USER)
- **A un rôle** : Un joueur possède un personnage (N-1 vers ROLE, nullable)
- **A plusieurs missions** : Un joueur peut avoir plusieurs missions via MISSION_PLAYER (1-N)

### Métadonnées

- Contrainte unique sur `(lobby_id, user_id)` pour éviter les doublons
- Index sur `lobby_id` et `status` pour performances
- Index sur `user_id` pour historique utilisateur
- Index sur `status` pour filtrer les joueurs actifs

### Règles métier

- **Un seul lobby à la fois** : Un utilisateur ne peut être dans qu'un seul lobby actif simultanément
  - Contrainte vérifiée au niveau applicatif : on vérifie qu'il n'y a pas de PLAYER avec `status IN ('waiting', 'playing')` avant de rejoindre
- Avant le démarrage : `role_id` est NULL, `status = waiting`
- Pendant le jeu : `role_id` est assigné, `status = playing`
- Après la partie : `status = completed` ou `left`, `score` finalisé
- Les missions sont gérées séparément via la table MISSION_PLAYER

### Transitions de statut

```
waiting → playing → completed
waiting → playing → left
waiting → left (abandon avant démarrage)
```

---

## 7. MISSION_PLAYER

Table de liaison N-N entre MISSION et PLAYER, permettant à un joueur d'avoir plusieurs missions dont une active.

### Attributs

| Attribut       | Type     | Description                 | Contraintes                          |
| -------------- | -------- | --------------------------- | ------------------------------------ |
| `id`           | UUID     | Identifiant unique          | PK, généré automatiquement           |
| `player_id`    | UUID     | Joueur assigné              | FK vers PLAYER, obligatoire          |
| `mission_id`   | UUID     | Mission assignée            | FK vers MISSION, obligatoire         |
| `state`        | JSON     | État évolutif de la mission | Nullable, structure libre            |
| `status`       | Enum     | État de la mission          | active, completed, failed, cancelled |
| `assigned_at`  | DateTime | Date d'assignation          | Automatique                          |
| `completed_at` | DateTime | Date de complétion          | Nullable                             |

### Relations

- **Appartient à** : Une mission joueur est liée à un joueur (N-1 vers PLAYER)
- **Référence** : Une mission joueur référence une mission (N-1 vers MISSION)

### Métadonnées

- Contrainte unique sur `(player_id, mission_id)` pour éviter les doublons
- Index sur `player_id` et `status` pour recherches
- Index sur `mission_id` pour performances
- Un seul `status = 'active'` par `player_id` à la fois (contrainte applicative)

### Règles métier

- **Une seule mission active** : Un joueur ne peut avoir qu'une seule mission avec `status = 'active'` à la fois
- Les missions peuvent être ajoutées dynamiquement par le host pendant la partie
- Le champ `state` stocke l'état évolutif de la mission :
  ```json
  {
    "phase": "initial|progression|finale",
    "progress": 0.75,
    "revealed_to": ["player_123", "player_456"]
  }
  ```
- **Transitions de statut** :
  ```
  active → completed (succès)
  active → failed (échec)
  active → cancelled (annulé par le host)
  ```

---

## Relations résumées

- **USER ↔ LOBBY** : 1-N (un utilisateur crée plusieurs lobbies)
- **USER ↔ PLAYER** : 1-N (un utilisateur peut participer à plusieurs parties, **mais un seul à la fois**)
- **LOBBY ↔ PLAYER** : 1-N (un lobby contient plusieurs joueurs)
- **LOBBY ↔ GAME** : N-1 (plusieurs lobbies utilisent le même type de jeu)
- **GAME ↔ MISSION** : 1-N (un jeu contient plusieurs missions/personnalités)
- **GAME ↔ ROLE** : 1-N (un jeu définit plusieurs personnages)
- **ROLE ↔ MISSION** : 1-N optionnel (plusieurs missions peuvent être liées à un rôle)
- **PLAYER ↔ ROLE** : N-1 (plusieurs joueurs peuvent incarner le même personnage)
- **PLAYER ↔ MISSION** : N-N via MISSION_PLAYER (un joueur peut avoir plusieurs missions, plusieurs joueurs peuvent avoir la même mission)
- **MISSION_PLAYER ↔ PLAYER** : N-1 (plusieurs missions sont assignées à un joueur)
- **MISSION_PLAYER ↔ MISSION** : N-1 (plusieurs assignations pour une même mission)

### Contrainte importante

Un utilisateur ne peut participer qu'à un **seul lobby actif** à la fois. Cette contrainte est vérifiée au niveau applicatif lors de la tentative de rejoindre un nouveau lobby.

---

## Index et optimisations

### Index recommandés

- `USER.email` (unique)
- `USER.username` (unique)
- `LOBBY.code` (unique)
- `LOBBY.status`
- `LOBBY.host_id` + `LOBBY.status` (pour vérifier lobbies actifs par host)
- `MISSION.role_id` (nullable)
- `MISSION_PLAYER(player_id, mission_id)` (unique)
- `MISSION_PLAYER.player_id` + `MISSION_PLAYER.status` (pour trouver mission active)
- `PLAYER(lobby_id, user_id)` (unique)
- `PLAYER.lobby_id`
- `PLAYER.user_id` + `PLAYER.status` (pour vérifier lobby actif d'un utilisateur)
- `PLAYER.status`

### Contraintes d'intégrité

- Suppression en cascade : si un lobby est supprimé, les PLAYER associés sont supprimés
- Suppression en cascade : si un USER est supprimé, ses lobbies et participations sont supprimées
- Suppression en cascade : si un PLAYER est supprimé, ses MISSION_PLAYER associées sont supprimées
- Suppression en cascade : si une MISSION est supprimée, les MISSION_PLAYER associées sont supprimées

### Implémentation de la contrainte "un seul lobby actif"

**Vérification lors de la création d'un lobby** :

```sql
SELECT COUNT(*) FROM lobby
WHERE host_id = ? AND status IN ('waiting', 'starting', 'in_progress')
```

**Vérification lors du join d'un lobby** :

```sql
SELECT COUNT(*) FROM player
WHERE user_id = ? AND status IN ('waiting', 'playing')
```

Si le résultat est > 0, l'action est refusée.
