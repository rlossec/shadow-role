# 📘 Modèle de données — ShadowRole

_Version : 1.0 — Structure relationnelle et contraintes principales_

---

## 🧍‍♂️ USER

### Description

Représente un compte utilisateur global sur la plateforme.

Il peut être joueur, hôte ou simple spectateur, selon le contexte du lobby.

C’est la base pour l’authentification et la gestion des permissions.

### Champs

| Champ               | Type       | Contraintes / Description        |
| ------------------- | ---------- | -------------------------------- |
| **id**              | `uuid`     | PK                               |
| **username**        | `string`   | Unique par utilisateur (non nul) |
| **email**           | `string`   | Unique, indexé pour connexion    |
| **hashed_password** | `string`   | Stocké avec Argon2 ou équivalent |
| **created_at**      | `datetime` | Auto-généré                      |
| **updated_at**      | `datetime` | Mis à jour à chaque modification |
| **is_active**       | `boolean`  | Définit l’état du compte         |
| **is_superuser**    | `boolean`  | Permissions administratives      |

### Relations

- `USER` ⟶ `LOBBY` (1–N) : un utilisateur peut héberger plusieurs lobbies
- `USER` ⟶ `PLAYER` (1–N) : un utilisateur peut être joueur dans plusieurs lobbies
- `USER` ⟶ `MISSION` (1–N) : un utilisateur peut créer plusieurs missions personnalisées

---

## 🎮 GAME_TYPE

### Description

Catégorie ou famille de jeu.

Exemples : _“Jeu de rôle”, “Jeu d’enquête”, “Jeu de bluff”_.

### Champs

| Champ           | Type     | Description                 |
| --------------- | -------- | --------------------------- |
| **id**          | `uuid`   | PK                          |
| **name**        | `string` | Nom du type de jeu          |
| **description** | `string` | Description du genre de jeu |

### Relations

- `GAME_TYPE` ⟶ `GAME` (1–N) : un type peut regrouper plusieurs jeux

---

## 🕹️ GAME

### Description

Décrit un jeu spécifique jouable dans la plateforme.

Exemple : _Qui suis-je_, _Espion Secret_, _Mission Impossible_.

### Champs

| Champ            | Type       | Contraintes / Description |
| ---------------- | ---------- | ------------------------- |
| **id**           | `uuid`     | PK                        |
| **name**         | `string`   | Nom du jeu                |
| **description**  | `string`   | Brève description         |
| **game_type_id** | `uuid`     | FK → `GAME_TYPE.id`       |
| **image_url**    | `string`   | Image d’illustration      |
| **min_players**  | `int`      | Nombre minimal requis     |
| **max_players**  | `int`      | Nombre maximal autorisé   |
| **created_at**   | `datetime` | Date de création          |
| **updated_at**   | `datetime` | Date de modification      |

### Relations

- `GAME` ⟶ `GAME_TYPE` (N–1)
- `GAME` ⟶ `MISSION` (1–N)
- `GAME` ⟶ `LOBBY` (1–N)
- `GAME` ⟶ `GAMETAG` (N-0)

---

## 🏠 LOBBY

### Description

Instance de jeu créée par un hôte.

Contient les joueurs, les missions attribuées, et la progression de la partie.

### Champs

| Champ           | Type       | Contraintes / Description                           |
| --------------- | ---------- | --------------------------------------------------- |
| **id**          | `uuid`     | PK                                                  |
| **name**        | `string`   | Nom du lobby                                        |
| **code**        | `string`   | Code unique de partage                              |
| **game_id**     | `uuid`     | FK → `GAME.id`                                      |
| **host_id**     | `uuid`     | FK → `USER.id`                                      |
| **status**      | `enum`     | `"waiting"`, `"running"`, `"paused"`, `"ended"`     |
| **phase**       | `enum`     | `"none"`, `"suggestion"`, `"round"`, `"validation"` |
| **min_players** | `int`      | Contrainte minimale                                 |
| **max_players** | `int`      | Contrainte maximale                                 |
| **created_at**  | `datetime` | Date de création                                    |
| **expires_at**  | `datetime` | Expiration automatique du lobby                     |

### Relations

- `LOBBY` ⟶ `PLAYER` (1–N)
- `LOBBY` ⟶ `ROUND` (1–N)
- `LOBBY` ⟶ `GAME` (N–1)
- `LOBBY` ⟶ `USER` (N–1) — hôte

---

## 👥 PLAYER

### Description

Lien entre un utilisateur et un lobby.

Représente un joueur actif (avec alias, couleur et score).

### Champs

| Champ         | Type       | Description                         |
| ------------- | ---------- | ----------------------------------- |
| **id**        | `uuid`     | PK                                  |
| **lobby_id**  | `uuid`     | FK → `LOBBY.id`                     |
| **user_id**   | `uuid`     | FK → `USER.id`                      |
| **score**     | `int`      | Score total du joueur dans ce lobby |
| **joined_at** | `datetime` | Date d’entrée dans le lobby         |
| **left_at**   | `datetime` | Date de sortie (nullable)           |

### Relations

- `PLAYER` ⟶ `USER` (N–1)
- `PLAYER` ⟶ `LOBBY` (N–1)
- `PLAYER` ⟶ `ASSIGNED_MISSION` (1–N)

> ⚠️ alias et color ne sont pas stockés ici : tu pourrais les réintroduire si tu veux personnaliser chaque joueur visuellement.

---

## 🎯 MISSION

### Description

Représente une mission ou un rôle possible pour un jeu.

Peut être définie globalement ou créée par un joueur lors d’une phase de suggestion.

### Champs

| Champ           | Type     | Description                                       |
| --------------- | -------- | ------------------------------------------------- |
| **id**          | `uuid`   | PK                                                |
| **game_id**     | `uuid`   | FK → `GAME.id`                                    |
| **title**       | `string` | Nom de la mission / rôle                          |
| **created_by**  | `uuid`   | FK → `USER.id` (nullable, si créée par un joueur) |
| **type**        | `enum`   | `"mission"` ou `"role"`                           |
| **description** | `text`   | Détails ou instructions                           |
| **image_url**   | `string` | Illustration optionnelle                          |
| **difficulty**  | `int`    | Niveau indicatif                                  |

### Relations

- `MISSION` ⟶ `GAME` (N–1)
- `MISSION` ⟶ `USER` (N–1)
- `MISSION` ⟶ `ASSIGNED_MISSION` (1–N)

---

## 🧩 ASSIGNED_MISSION

### Description

Table d’association entre `PLAYER` et `MISSION`.

Stocke les missions réellement attribuées durant une session.

### Champs

| Champ            | Type       | Description                                          |
| ---------------- | ---------- | ---------------------------------------------------- |
| **id**           | `uuid`     | PK                                                   |
| **player_id**    | `uuid`     | FK → `PLAYER.id`                                     |
| **mission_id**   | `uuid`     | FK → `MISSION.id`                                    |
| **status**       | `enum`     | `"active"`, `"completed"`, `"failed"`, `"cancelled"` |
| **assigned_at**  | `datetime` | Date d’attribution                                   |
| **completed_at** | `datetime` | Date de clôture (nullable)                           |

### Relations

- `ASSIGNED_MISSION` ⟶ `PLAYER` (N–1)
- `ASSIGNED_MISSION` ⟶ `MISSION` (N–1)

---

## 🔁 ROUND

### Description

Représente une manche de jeu dans un lobby.

Permet de séquencer la progression et d’attribuer des missions à chaque tour.

### Champs

| Champ            | Type       | Description                 |
| ---------------- | ---------- | --------------------------- |
| **id**           | `uuid`     | PK                          |
| **lobby_id**     | `uuid`     | FK → `LOBBY.id`             |
| **round_number** | `int`      | Numéro du tour (1, 2, 3, …) |
| **status**       | `enum`     | `"running"` ou `"finished"` |
| **started_at**   | `datetime` | Début du round              |
| **ended_at**     | `datetime` | Fin du round (nullable)     |

### Relations

- `ROUND` ⟶ `LOBBY` (N–1)

---

## 🔗 Résumé des relations principales

| Relation                       | Type | Description                                         |
| ------------------------------ | ---- | --------------------------------------------------- |
| `USER` → `LOBBY`               | 1–N  | Un utilisateur peut héberger plusieurs lobbies      |
| `USER` → `PLAYER`              | 1–N  | Un utilisateur peut participer à plusieurs lobbies  |
| `GAME_TYPE` → `GAME`           | 1–N  | Un type regroupe plusieurs jeux                     |
| `GAME` → `MISSION`             | 1–N  | Un jeu définit ses missions                         |
| `LOBBY` → `PLAYER`             | 1–N  | Un lobby contient des joueurs                       |
| `PLAYER` → `ASSIGNED_MISSION`  | 1–N  | Un joueur reçoit plusieurs missions                 |
| `MISSION` → `ASSIGNED_MISSION` | 1–N  | Une mission peut être attribuée à plusieurs joueurs |
| `LOBBY` → `ROUND`              | 1–N  | Plusieurs manches par lobby                         |
