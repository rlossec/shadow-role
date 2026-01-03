# Index de la Documentation - Shadow Role

## Par où commencer

| Je veux...                    | Lire...                                                |
| ----------------------------- | ------------------------------------------------------ |
| **Lancer l'application**      | [README Principal](../README.md) → Section Quick Start |
| **Installer de zéro**         | [Guide de Démarrage](./getting_started.md)             |
| **Comprendre l'architecture** | [Architecture](./architecture.md)                      |
| **Développer le backend**     | [Documentation Backend](./backend/README.md)           |
| **Développer le frontend**    | [Documentation Frontend](./frontend/README.md)         |

## 📖 Documentation par Catégorie

### 🏗️ Architecture et Concepts

- **[Architecture Générale](./architecture.md)**

  - Vue d'ensemble du système
  - Stack technique
  - Patterns et principes
  - Communication et flux de données

- **[Communication](./overview/communication.md)**

  - REST API
  - WebSocket

- **[Sécurité](./overview/security.md)**

  - Authentification JWT
  - Protection des routes
  - Bonnes pratiques de sécurité

### 🔧 Backend - FastAPI

Documentation complète : **[Backend README](./backend/README.md)**

#### Guides Techniques

- **[Authentification](./backend/authentication.md)**
- **[Architecture Backend](./backend/backend_architecture.md)**
- **[Référence API](./backend/API_REFERENCE.md)**
- **[Orchestration](./backend/orchestration.md)**
- **[WebSocket](./backend/websocket.md)**
- **[Tests Backend](./backend/tests.md)**

### ⚛️ Frontend (React TypeScript)

Documentation complète : **[Frontend README](./frontend/README.md)**

#### Guides Techniques

- **[Authentification Frontend](./frontend/authentication.md)**
- **[TanStack Query](./frontend/tanstack_query.md)**
- **[Context](./frontend/context.md)**
- **[WebSocket Client](./frontend/websocket.md)**
- **[API Client](./frontend/api_client.md)**
- **[Composants UI](./frontend/ui_components.md)**
- **[Custom Hooks](./frontend/custom_hooks.md)**
- **[Forms](./frontend/forms.md)**
- **[Pages Reference](./frontend/pages_reference.md)**
- **[Tailwind CSS](./frontend/tailwind.md)**

### 🧪 Tests et Qualité

- **[Tests Backend](./backend/tests.md)**
- **[Conventions de Code](./contributing/code_conventions.md)**
- **[Repository Pattern](./contributing/repository_pattern.md)**
- **[CQRS](./contributing/cqrs.md)**

### 🚀 Déploiement et Ops

- **[Guide de Déploiement](./devops/deployment.md)**
- **[Monitoring](./devops/monitoring.md)**

### 🤝 Contribution

- **[Guide de Contribution](./contributing/README.md)**

## 📁 Structure de la Documentation

### Fichiers Principaux (racine `docs/`)

| Fichier              | Description                        |
| -------------------- | ---------------------------------- |
| `INDEX.md`           | Ce fichier - point d'entrée        |
| `README.md`          | Vue d'ensemble de la documentation |
| `getting_started.md` | Guide d'installation et démarrage  |
| `architecture.md`    | Architecture générale du système   |

### Overview (`docs/overview/`)

| Fichier                | Description                   |
| ---------------------- | ----------------------------- |
| `communication.md`     | Communication REST/WebSocket  |
| `security.md`          | Sécurité et authentification  |
| `game_flow.md`         | Flux de jeu                   |
| `game_process_flow.md` | Processus de jeu              |
| `requirements.md`      | Exigences fonctionnelles      |
| `user_guide.md`        | Guide utilisateur             |
| `dev_guide.md`         | Guide développeur             |
| `changelog.md`         | Journal des modifications     |
| `architecture/`        | Diagrammes d'architecture     |
| `database/`            | Documentation base de données |

### Backend (`docs/backend/`)

| Fichier                   | Description                       |
| ------------------------- | --------------------------------- |
| `README.md`               | Documentation principale backend  |
| `backend_architecture.md` | Architecture détaillée du backend |
| `authentication.md`       | Authentification backend          |
| `API_REFERENCE.md`        | Référence complète de l'API       |
| `orchestration.md`        | Orchestration des services        |
| `websocket.md`            | WebSocket et Socket.IO            |
| `tests.md`                | Tests backend                     |

### Frontend (`docs/frontend/`)

| Fichier              | Description                       |
| -------------------- | --------------------------------- |
| `README.md`          | Documentation principale frontend |
| `authentication.md`  | Authentification frontend         |
| `tanstack_query.md`  | TanStack Query (React Query)      |
| `context.md`         | Context API                       |
| `websocket.md`       | WebSocket Client                  |
| `api_client.md`      | Client API (Axios)                |
| `ui_components.md`   | Composants UI                     |
| `tailwind.md`        | Tailwind CSS                      |
| `custom_hooks.md`    | Hooks personnalisés               |
| `forms.md`           | Gestion des formulaires           |
| `pages_reference.md` | Référence des pages               |

### Database (`docs/overview/database/`)

| Fichier       | Description                              |
| ------------- | ---------------------------------------- |
| `README.md`   | Documentation principale base de données |
| `mcd.md`      | Modèle Conceptuel de Données (MCD)       |
| `mcd.mermaid` | Diagramme MCD au format Mermaid          |

### Architecture (`docs/overview/architecture/`)

| Fichier                    | Description                      |
| -------------------------- | -------------------------------- |
| `architecture_overview.md` | Vue d'ensemble de l'architecture |
| `architecture_flow.md`     | Flux d'architecture              |
| `lobby_and_game_flow.md`   | Flux du lobby et du jeu          |

### Patterns (`docs/contributing/`)

| Fichier                 | Description           |
| ----------------------- | --------------------- |
| `README.md`             | Guide de contribution |
| `repository_pattern.md` | Pattern Repository    |
| `cqrs.md`               | Pattern CQRS          |
| `code_conventions.md`   | Conventions de code   |

### DevOps (`docs/devops/`)

| Fichier         | Description                 |
| --------------- | --------------------------- |
| `deployment.md` | Guide de déploiement        |
| `monitoring.md` | Monitoring et observabilité |
