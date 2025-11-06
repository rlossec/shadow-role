# Shadow Role

## 🎯 Objectif

Créer un jeu social en ligne basé sur les mécaniques _"Qui suis-je ? / Mission secrète"_, avec des rôles/missions distribués en temps réel via WebSocket.

## 🧩 Périmètre technique

- **Backend** : FastAPI, SQLAlchemy, Pydantic, Socket.IO
- **Frontend** : React + Vite + TypeScript + Tailwind
- **Base de données** : PostgreSQL
- **Auth** : JWT
- **Communication** : REST (actions) + WebSocket (temps réel)

## Quick Start

### Prérequis

- Python 3.12+ avec [uv](https://github.com/astral-sh/uv)
- Node.js et npm (pour le frontend)

### Lancement en développement

#### Backend

```bash
cd backend
uv sync                              # Installer les dépendances
uv run uvicorn main:app --reload     # Lancer le serveur
```

#### Frontend

```bash
cd frontend
npm install                          # Installer les dépendances
npm run dev                          # Lancer le serveur
```

Le frontend sera accessible sur `http://localhost:5173`
Le backend sera accessible sur `http://localhost:8000`
Documentation API disponible sur `http://localhost:8000/docs`

### Lancement avec Docker

```bash
docker-compose up
```

Cette commande lance simultanément le backend, le frontend et la base de données.

## 🗂️ Structure du projet

| Domaine        | Dossier                               | Description                 |
| -------------- | ------------------------------------- | --------------------------- |
| Documentation  | `/docs`                               | Schémas, architecture, flux |
| Backend (REST) | `/backend/routers`                    | Endpoints API               |
| WebSocket      | `/backend/ws`                         | Temps réel par lobby        |
| Frontend       | `/frontend/src`                       | React + Hooks + Context     |
| Données        | `/backend/models`, `/backend/schemas` | Modèles et validation       |

### Arborescence

```
├── backend/
│   ├── app/
│   │   ├── main.py                # Point d’entrée FastAPI
│   │   ├── routers/
│   │   ├── core/
│   │   ├── models/                # Modèles SQLAlchemy
│   │   ├── schemas/               # Pydantic
│   │   └── services/              # Logique métier
│   ├── tests/                     # Tests unitaires backend
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/
│   │   └── utils/
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
│
├── docker-compose.yml
├── README.md
```
