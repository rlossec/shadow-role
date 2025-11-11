# 🧱 PHASE 1 — Documentation (priorité haute)

### Légende

- 🟩 = terminé
- 🟨 = en cours
- ⬜ = à faire
- 🟥 = bloquant / erreur
- `Haute`, `Moyenne`, `Basse` = priorité

📌 **Objectif** : Maintenir une base documentaire complète et à jour.

| Statut | Tâche                                                                          | Priorité | Détails                                       |
| ------ | ------------------------------------------------------------------------------ | -------- | --------------------------------------------- |
| 🟩     | Restructurer `docs/README.md`                                                  | Haute    | Table des matières alignée sur l’arborescence |
| 🟩     | Compléter `overview/dev_guide.md`, `user_guide.md`, `changelog.md`             | Haute    | Guides overview remplis                       |
| 🟨     | Décrire le client WebSocket côté frontend (`frontend/websocket-client.md`)     | Moyenne  | Présenter `useWebSocket`, événements écoutés  |
| ⬜     | Documenter les données de base (`docs/data/missions.md`, `docs/data/roles.md`) | Moyenne  | Référentiel missions/rôles                    |
| ⬜     | Ajouter un diagramme FSM (`docs/overview/game-state.mermaid`)                  | Basse    | États `waiting → running → ended`             |

---

# ⚙️ PHASE 2 — Backend REST (priorité haute)

📌 **Objectif** : Mettre en place la structure de base du backend, avec routes REST et JWT.

| Statut | Tâche                                                          | Priorité | Détails                                     |
| ------ | -------------------------------------------------------------- | -------- | ------------------------------------------- |
| ⬜     | Configurer FastAPI (CORS, routers, DB)                         | Haute    | Fichier `main.py` et `app.include_router()` |
| ⬜     | Authentification JWT (login/register)                          | Haute    | `/api/auth/*`                               |
| ⬜     | Modèles SQLAlchemy (User, Lobby, Game, Mission, Role, Player)  | Haute    | `backend/models/*.py`                       |
| ⬜     | Schémas Pydantic (validation)                                  | Haute    | `backend/db/schemas/*.py`                   |
| ⬜     | Repositories CRUD (DAO)                                        | Moyenne  | `backend/repositories/*.py`                 |
| ⬜     | Endpoints REST : `/api/lobbies`, `/api/missions`, `/api/games` | Moyenne  | CRUD + relations                            |
| ⬜     | Endpoint pour suggestions                                      | Moyenne  | `/api/missions/suggest`                     |
| ⬜     | Tests unitaires REST                                           | Basse    | pytest + httpx                              |

---

# 🔌 PHASE 3 — WebSocket / Temps réel (priorité haute)

📌 **Objectif** : Synchroniser l’état du jeu (lobby, joueurs, missions, scores).

| Statut | Tâche                                                                   | Priorité | Détails                                         |
| ------ | ----------------------------------------------------------------------- | -------- | ----------------------------------------------- |
| ⬜     | Implémenter `ConnectionManager`                                         | Haute    | Gère connexions, rooms, broadcast               |
| ⬜     | Implémenter `GameService`                                               | Haute    | Logique métier (états, rôles, missions, scores) |
| ⬜     | Créer les events : `join_lobby`, `start_game`, `mission_assigned`, etc. | Haute    | Centraliser les noms d’événements               |
| ⬜     | Authentification WS par JWT dans le handshake                           | Haute    | Middleware Socket.IO                            |
| ⬜     | Mapping entre events client ↔ backend                                   | Moyenne  | Documenter et typer les payloads                |
| ⬜     | Tests de charge WS (multi clients)                                      | Basse    | Simulation des événements                       |

---

# 💻 PHASE 4 — Frontend (priorité moyenne)

📌 **Objectif** : Construire une interface fluide et réactive avec React + Tailwind.

| Statut | Tâche                                                           | Priorité | Détails                   |
| ------ | --------------------------------------------------------------- | -------- | ------------------------- |
| 🟩     | Initialiser React (Vite, Tailwind, Router)                      | Haute    | Structure `/frontend/src` |
| ⬜     | Créer `useAuth`, `useLobbies`, `useWebSocket` hooks             | Haute    | Connexions REST + WS      |
| ⬜     | Créer pages principales : `Login`, `LobbyList`, `Lobby`, `Game` | Haute    | Routing complet           |
| ⬜     | Composant Lobby : affichage joueurs + bouton start              | Haute    | Intégré au flux WS        |
| ⬜     | Composant GameView : affichage mission/rôle + score             | Haute    | Adapté selon type         |
| ⬜     | Gestion des états de jeu (waiting, running, ended)              | Moyenne  | via Context               |
| ⬜     | Interface Host : contrôles (start, end round, end game)         | Moyenne  | boutons WS                |
| ⬜     | UI Chat en temps réel                                           | Basse    | message event             |

---

# 🧪 PHASE 5 — Tests & Intégration (priorité basse)

| Statut | Tâche                                           | Priorité | Détails              |
| ------ | ----------------------------------------------- | -------- | -------------------- |
| ⬜     | Tests unitaires Backend REST                    | Moyenne  | pytest + SQLite      |
| ⬜     | Tests d’intégration WS (simulate multi-clients) | Moyenne  | socketio.AsyncClient |
| ⬜     | Tests E2E Front (Playwright ou Cypress)         | Basse    | scénario complet     |
| ⬜     | CI/CD GitHub Actions                            | Basse    | lint + tests + build |
| ⬜     | Déploiement Docker Compose                      | Basse    | API + DB + Front     |

---

# 📊 Suivi & Progression

| Phase            | Objectif                               | Avancement |
| ---------------- | -------------------------------------- | ---------- |
| 📘 Documentation | Structurer & visualiser l’architecture | 🟩 80%     |
| ⚙️ Backend REST  | Auth + CRUD + relations                | 🟨 0%      |
| 🔌 WebSocket     | Gestion temps réel + logique de jeu    | 🟨 0%      |
| 💻 Frontend      | UI + WebSocket + Routing               | ⬜ 0%      |
| 🧪 Tests / CI    | Automatisation                         | ⬜ 0%      |

---

# 🧩 Notes / Idées à explorer

- [ ] Ajouter un **endpoint de "suggestions locales"** liées à un lobby
- [ ] Permettre à l’host de **relancer une manche** sans recréer de lobby
- [ ] Ajouter un **mode hybride** (mission + rôle)
- [ ] Persister l’historique des parties par utilisateur
- [ ] Intégrer un **chat vocal** ou bouton lien Discord
- [ ] Exporter les résultats (PDF ou JSON)

---

# 📅 Étapes prioritaires suivantes

1. 🧭 Documenter les comportements WebSocket côté frontend (`frontend/websocket-client.md`).
2. ⚙️ Implémenter `ConnectionManager` + `GameService` minimal.
3. 💻 Connecter `useWebSocket` dans React (LobbyPage + GamePage).
4. 🧪 Tester le flux complet "join → start → assign → score → end".

---

> Ce fichier est évolutif : chaque tâche peut être déplacée selon l’avancement.  
> Tu peux cocher les éléments avec ✅ ou 🟩 au fur et à mesure.

---
