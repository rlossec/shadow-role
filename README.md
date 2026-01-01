# Shadow Role

> **Jeu social en ligne basé sur les mécaniques "Qui suis-je ? / Mission secrète"**  
> Distribution de rôles/missions en temps réel via WebSocket

[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)

## 🚀 Quick Start

### Prérequis

- **Python 3.12+** avec [uv](https://github.com/astral-sh/uv)
- **Node.js 18+** et npm
- **PostgreSQL 14+** (ou Docker)
- **Docker** (optionnel)

### Lancement rapide avec Docker TODO

```bash
docker-compose up
```

Accès aux services :

- 🎮 **Frontend** : http://localhost:5173
- ⚡ **Backend API** : http://localhost:8000
- 📚 **Documentation API** : http://localhost:8000/docs
- 📧 **Fake SMTP** : http://localhost:8025

### Lancement manuel

#### 1. Backend

```bash
cd backend
uv sync                              # Installer les dépendances
uv run uvicorn main:app --reload     # Lancer le serveur (port 8000)
```

#### 2. Frontend

```bash
cd frontend
npm install                          # Installer les dépendances
npm run dev                          # Lancer le serveur (port 5173)
```

#### 3. SMTP (développement)

```bash
cd fake_smtp
docker-compose up -d                 # Interface web sur port 8025
```

## 📖 Documentation

| Document                                             | Description                                              |
| ---------------------------------------------------- | -------------------------------------------------------- |
| **[Guide de démarrage](./docs/getting_started.md)**  | Installation détaillée, configuration, premiers pas      |
| **[Architecture](./docs/architecture.md)**           | Vue d'ensemble de l'architecture du projet               |
| **[Backend](./docs/backend/README.md)**              | Documentation technique du backend (FastAPI, SQLAlchemy) |
| **[Frontend](./docs/frontend/README.md)**            | Documentation technique du frontend (React, TypeScript)  |
| **[API Reference](./docs/backend/API_REFERENCE.md)** | Documentation interactive Swagger (serveur lancé)        |

## 🏗️ Stack Technique

### Backend

- **Framework** : FastAPI
- **ORM** : SQLAlchemy (async)
- **Validation** : Pydantic
- **Base de données** : PostgreSQL
- **Authentification** : JWT (Access + Refresh tokens)
- **Temps réel** : Socket.IO

### Frontend

- **Framework** : React 18 + TypeScript
- **Build Tool** : Vite
- **Styling** : Tailwind CSS
- **State Management** : TanStack Query + Context API
- **Routing** : React Router
- **HTTP Client** : Axios
- **WebSocket** : Socket.IO Client

### Architecture

- **Pattern Repository** : Abstraction de l'accès aux données
- **CQRS** : Séparation Command/Query
- **Services spécialisés** : Responsabilité unique (SRP)
- **Dependency Injection** : Via FastAPI

## 📁 Structure du Projet

```
shadow-role/
├── backend/              # Application FastAPI
│   ├── app/
│   │   ├── api/          # Routes REST
│   │   ├── handlers/     # Handlers WebSocket
│   │   ├── services/     # Logique métier
│   │   ├── repositories/ # Accès aux données
│   │   ├── models/       # Modèles SQLAlchemy
│   │   └── schemas/      # Schémas Pydantic
│   ├── tests/            # Tests unitaires et d'intégration
│   └── main.py           # Point d'entrée
│
├── frontend/             # Application React
│   ├── src/
│   │   ├── pages/        # Pages de l'application
│   │   ├── components/   # Composants réutilisables
│   │   ├── hooks/        # Hooks personnalisés
│   │   ├── services/     # Services API
│   │   └── contexts/     # Contextes React
│   └── package.json
│
├── docs/                 # Documentation complète
│   ├── GETTING_STARTED.md
│   ├── ARCHITECTURE.md
│   ├── backend/
│   └── frontend/
│
└── fake_smtp/            # Serveur SMTP de développement
```

## 🧪 Tests

```bash
# Backend
cd backend
uv run pytest                    # Tous les tests
uv run pytest -v --cov=app      # Avec couverture
```

## 📝 License

Ce projet est sous licence [MIT](./LICENSE).

## 🆘 Support

- 📚 **Documentation** : Consultez le dossier `docs/`
- 🐛 **Issues** : [GitHub Issues](https://github.com/rlossec/shadow-role/issues)
- 💬 **Discussions** : [GitHub Discussions](https://github.com/rlossec/shadow-role/discussions)
