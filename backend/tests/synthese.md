# Synthèse des Tests

Ce document récapitule tous les tests effectués dans le projet, organisés par catégorie.

## 📊 Vue d'ensemble

| Catégorie              | Fichiers de test |
| ---------------------- | ---------------- |
| **API Authentication** | 7 fichiers       |
| **API CRUD**           | 20 fichiers      |
| **Services**           | 6 fichiers       |
| **WebSocket**          | 2 fichiers       |

## 1. Tests API Authentication

**Localisation** : `backend/tests/app/api/authentication/`

### Endpoints testés

#### POST `/auth/register`

- ✅ Cas de succès (status 201)
- ✅ Validation des champs obligatoires (status 422)
- ✅ Validation des emails invalides (status 422)
- ✅ Validation des champs vides (status 422)
- ✅ Validation des mots de passe correspondants (status 422)
- ✅ Doublons username/email (status 400)

**Fichier** : `test_register.py`

#### POST `/auth/jwt/login`

- ✅ Cas de succès avec username (status 200)
- ✅ Cas de succès avec email (status 200)
- ✅ Mauvais identifiants (status 400)
- ✅ Utilisateur inexistant (status 400)
- ✅ Utilisateur inactif (status 400/401)
- ✅ Validation des champs obligatoires (status 422)
- ✅ Validation des champs vides (status 400)

**Fichier** : `test_login.py`

#### POST `/auth/refresh`

- ✅ Cas de succès (status 200)
- ✅ Rotation des tokens
- ✅ Réutilisation du refresh token (status 401)
- ✅ Token invalide (status 401)
- ✅ Utilisation d'un access token comme refresh (status 401)
- ✅ Révoquement après logout (status 401)

**Fichier** : `test_refresh.py`

#### POST `/auth/activate-account`

- ✅ Cas de succès (status 200)
- ✅ Token invalide (status 400)

**Fichier** : `test_activate_account.py`

#### POST `/auth/resend_activation`

- ✅ Cas de succès (status 202)
- ✅ Email inconnu (status 202, pas de token)
- ✅ Utilisateur déjà actif (status 202, pas de token)

**Fichier** : `test_resend_activation.py`

#### POST `/auth/request-reset-password`

- ✅ Génération de token (status 202)

**Fichier** : `test_request_reset_password.py`

#### POST `/auth/reset-password`

- ✅ Cas de succès (status 200/204)
- ✅ Token invalide (status 400)

**Fichier** : `test_reset_password.py`

### Exécution

```bash
# Tous les tests d'authentification
uv run pytest tests/app/api/authentication/ -v

# Un fichier spécifique
uv run pytest tests/app/api/authentication/test_register.py -v

# Un test spécifique
uv run pytest tests/app/api/authentication/test_register.py::test_register_success -v
```

### Documentation

Voir [README.md](app/api/authentication/README.md) pour plus de détails.

---

## 2. Tests API CRUD

### 2.1. Tests Games

**Localisation** : `backend/tests/app/api/games/`

#### Endpoints testés

- **POST `/api/games`** - Création d'un jeu

  - ✅ Cas de succès (status 201)
  - ✅ Validation des champs obligatoires (status 422)
  - ✅ Authentification requise (status 401)
  - ✅ Permissions insuffisantes (status 403)

  **Fichier** : `test_create_game.py`

- **GET `/api/games`** - Liste des jeux

  - ✅ Cas de succès (status 200)
  - ✅ Filtrage et pagination
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_list_games.py`

- **GET `/api/games/{game_id}`** - Récupération d'un jeu

  - ✅ Cas de succès (status 200)
  - ✅ Jeu non trouvé (status 404)
  - ✅ UUID invalide (status 422)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_game.py`

- **GET `/api/games/{game_id}/missions`** - Missions d'un jeu

  - ✅ Cas de succès (status 200)
  - ✅ Jeu non trouvé (status 404)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_game_missions.py`

- **PUT `/api/games/{game_id}`** - Mise à jour d'un jeu

  - ✅ Cas de succès (status 200)
  - ✅ Jeu non trouvé (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Mise à jour partielle
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_update_game.py`

- **DELETE `/api/games/{game_id}`** - Suppression d'un jeu

  - ✅ Cas de succès (status 204)
  - ✅ Jeu non trouvé (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_delete_game.py`

### 2.2. Tests Lobbies

**Localisation** : `backend/tests/app/api/lobbies/`

#### Endpoints testés

- **POST `/api/lobbies`** - Création d'un lobby

  - ✅ Cas de succès (status 201)
  - ✅ Validation des champs obligatoires (status 422)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_create_lobby.py`

- **GET `/api/lobbies`** - Liste des lobbies

  - ✅ Cas de succès (status 200)
  - ✅ Filtrage et pagination
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_list_lobbies.py`

- **GET `/api/lobbies/{lobby_id}`** - Récupération d'un lobby

  - ✅ Cas de succès (status 200)
  - ✅ Lobby non trouvé (status 404)
  - ✅ UUID invalide (status 422)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_lobby.py`

- **GET `/api/lobbies/code/{code}`** - Récupération par code

  - ✅ Cas de succès (status 200)
  - ✅ Code invalide (status 404)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_lobby_by_code.py`

- **PUT `/api/lobbies/{lobby_id}`** - Mise à jour d'un lobby

  - ✅ Cas de succès (status 200)
  - ✅ Lobby non trouvé (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Mise à jour partielle
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_update_lobby.py`

- **DELETE `/api/lobbies/{lobby_id}`** - Suppression d'un lobby

  - ✅ Cas de succès (status 204)
  - ✅ Lobby non trouvé (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_delete_lobby.py`

### 2.3. Tests Missions

**Localisation** : `backend/tests/app/api/missions/`

#### Endpoints testés

- **POST `/api/missions`** - Création d'une mission

  - ✅ Cas de succès (status 201)
  - ✅ Validation des champs obligatoires (status 422)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_create_mission.py`

- **GET `/api/missions/{mission_id}`** - Récupération d'une mission

  - ✅ Cas de succès (status 200)
  - ✅ Mission non trouvée (status 404)
  - ✅ UUID invalide (status 422)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_mission.py`

- **GET `/api/missions/game/{game_id}`** - Missions d'un jeu

  - ✅ Cas de succès (status 200)
  - ✅ Jeu non trouvé (status 404)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_missions_by_game.py`

- **PUT `/api/missions/{mission_id}`** - Mise à jour d'une mission

  - ✅ Cas de succès (status 200)
  - ✅ Mission non trouvée (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Mise à jour partielle
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_update_mission.py`

- **DELETE `/api/missions/{mission_id}`** - Suppression d'une mission

  - ✅ Cas de succès (status 204)
  - ✅ Mission non trouvée (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_delete_mission.py`

### 2.4. Tests Players

**Localisation** : `backend/tests/app/api/players/`

#### Endpoints testés

- **GET `/api/players/{player_id}`** - Récupération d'un joueur

  - ✅ Cas de succès (status 200)
  - ✅ Joueur non trouvé (status 404)
  - ✅ UUID invalide (status 422)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_player.py`

- **GET `/api/players/{player_id}/missions`** - Missions d'un joueur

  - ✅ Cas de succès (status 200)
  - ✅ Joueur non trouvé (status 404)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_player_missions.py`

- **GET `/api/lobbies/{lobby_id}/players`** - Joueurs d'un lobby

  - ✅ Cas de succès (status 200)
  - ✅ Lobby non trouvé (status 404)
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_get_lobby_players.py`

- **PUT `/api/players/{player_id}`** - Mise à jour d'un joueur

  - ✅ Cas de succès (status 200)
  - ✅ Joueur non trouvé (status 404)
  - ✅ Permissions insuffisantes (status 403)
  - ✅ Mise à jour partielle
  - ✅ Authentification requise (status 401)

  **Fichier** : `test_update_player.py`

### Exécution

```bash
# Tous les tests CRUD
uv run pytest tests/app/api/games/ -v
uv run pytest tests/app/api/lobbies/ -v
uv run pytest tests/app/api/missions/ -v
uv run pytest tests/app/api/players/ -v

# Un fichier spécifique
uv run pytest tests/app/api/lobbies/test_create_lobby.py -v

# Un test spécifique
uv run pytest tests/app/api/lobbies/test_create_lobby.py::test_create_lobby_success -v
```

### Documentation

Voir [README.md](app/api/lobbies/README.md) pour plus de détails sur les lobbies.

---

## 3. Tests Services

**Localisation** : `backend/tests/app/services/`

### Services testés

#### PhaseService

**Fichier** : `test_phase_service.py`

Tests pour la gestion des phases de jeu :

- ✅ Démarrer une partie (`start_game`)
- ✅ Mettre en pause (`pause_game`)
- ✅ Reprendre (`resume_game`)
- ✅ Terminer (`end_game`)
- ✅ Gérer les phases (SUGGESTION, ROUND, VALIDATION)
- ✅ Transitions entre phases
- ✅ Validation des préconditions

#### LobbyService

**Fichier** : `test_lobby_service.py`

Tests pour la gestion des lobbies :

- ✅ Création de lobby
- ✅ Inscription des joueurs (`register_player`)
- ✅ Validation des limites (min/max players)
- ✅ Gestion du statut du lobby
- ✅ Validation des permissions

#### RoundService

**Fichier** : `test_round_service.py`

Tests pour la gestion des rounds :

- ✅ Création de round
- ✅ Attribution des missions
- ✅ Fermeture de round
- ✅ Calcul des résultats
- ✅ Gestion du statut du round

#### ScoreService

**Fichier** : `test_score_service.py`

Tests pour le calcul des scores :

- ✅ Calcul des scores par mission
- ✅ Calcul des scores par round
- ✅ Calcul des scores finaux
- ✅ Gestion de la difficulté
- ✅ Validation des résultats

#### MissionService

**Fichier** : `test_mission_service.py`

Tests pour la gestion des missions :

- ✅ Création de mission
- ✅ Récupération de missions
- ✅ Mise à jour de mission
- ✅ Suppression de mission
- ✅ Validation des données

#### MissionPoolService

**Fichier** : `test_mission_pool_service.py`

Tests pour la gestion du pool de missions :

- ✅ Sélection de missions
- ✅ Filtrage par jeu
- ✅ Filtrage par suggestions
- ✅ Gestion du pool disponible

### Exécution

```bash
# Tous les tests de services
uv run pytest tests/app/services/ -v

# Un service spécifique
uv run pytest tests/app/services/test_phase_service.py -v

# Un test spécifique
uv run pytest tests/app/services/test_phase_service.py::test_start_game_success -v
```

---

## 4. Tests WebSocket

**Localisation** : `backend/tests/app/websocket/`

### 4.1. Tests Unitaires

**Localisation** : `backend/tests/app/websocket/unit/`

#### GameCommandHandler

**Fichier** : `test_game_command_handler.py`

Tests unitaires avec mocks pour isoler la logique métier :

- ✅ **Démarrage de partie**

  - Démarrage réussi
  - Validation des préconditions
  - Gestion des erreurs

- ✅ **Gestion des suggestions**

  - Création de suggestion
  - Validation de suggestion
  - Rejet de suggestion
  - Gestion des erreurs

- ✅ **Gestion des rounds**

  - Démarrage de round
  - Attribution des missions
  - Gestion des erreurs

- ✅ **Validation des missions**

  - Validation réussie
  - Validation échouée
  - Gestion des erreurs

- ✅ **Finalisation**
  - Finalisation de round
  - Finalisation de partie
  - Calcul des scores

### 4.2. Tests E2E

**Localisation** : `backend/tests/app/websocket/e2e/`

#### Scénario "Qui suis je"

**Fichier** : `test_e2e_qui_suis_je.py`

Test end-to-end complet avec un vrai serveur WebSocket :

- ✅ **Connexion WebSocket**

  - Authentification via JWT
  - Connexions multiples
  - Reconnexion

- ✅ **Gestion du lobby**

  - Création de lobby
  - Rejoindre un lobby
  - Inscription des joueurs
  - Synchronisation de l'état

- ✅ **Flux de jeu complet**

  - Démarrage de partie
  - Phase de suggestion
  - Validation des suggestions
  - Démarrage de round
  - Attribution des missions
  - Validation des missions
  - Finalisation de round
  - Fin de partie

- ✅ **Événements WebSocket**
  - Vérification de tous les événements émis
  - Vérification des broadcasts
  - Vérification des messages privés

### Exécution

```bash
# Tests unitaires WebSocket
uv run pytest tests/app/websocket/unit/ -v

# Tests E2E WebSocket
uv run pytest tests/app/websocket/e2e/ -v -s

# Un test spécifique
uv run pytest tests/app/websocket/unit/test_game_command_handler.py::test_start_game_success -v
uv run pytest tests/app/websocket/e2e/test_e2e_qui_suis_je.py -v -s
```

### Documentation

Voir [SCENARIOS.md](SCENARIOS.md) pour plus de détails sur le scénario E2E.

---

## 📈 Statistiques

### Répartition des tests

- **API Authentication** : 7 fichiers de test
- **API CRUD** : 20 fichiers de test
  - Games : 6 fichiers
  - Lobbies : 6 fichiers
  - Missions : 5 fichiers
  - Players : 4 fichiers
- **Services** : 6 fichiers de test
- **WebSocket** : 2 fichiers de test
  - Unitaires : 1 fichier
  - E2E : 1 fichier

### Couverture des cas de test

Chaque endpoint/service est testé pour :

- ✅ Cas de succès
- ✅ Validation des données
- ✅ Gestion des erreurs (404, 400, 401, 403, 422)
- ✅ Authentification et autorisation
- ✅ Cas limites

---

## 🔗 Liens utiles

- [Stratégie de test](STRATEGY.md)
- [Scénarios de test](SCENARIOS.md)
- [Flux de jeu](FLOWS.md)
- [Utilisation des routes](ROUTES.md)
- [README principal](README.md)
