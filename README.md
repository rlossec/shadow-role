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

#### SMTP

```bash
cd fake_smtp
docker-compose up -d
```

Le frontend sera accessible sur `http://localhost:5173`
Le backend sera accessible sur `http://localhost:8000`
Documentation API disponible sur `http://localhost:8000/docs`
Le fake SMPT disponible sur `http://localhost:8025/`

### Lancement avec Docker

```bash
docker-compose up
```

Cette commande lance simultanément le backend, le frontend et la base de données.

## 🗂️ Structure du projet

| Domaine        | Dossier              | Description                 |
| -------------- | -------------------- | --------------------------- |
| Documentation  | `/docs`              | Schémas, architecture, flux |
| Backend (REST) | `/backend/api    `   | Endpoints API               |
| WebSocket      | `/backend/websocket` | Temps réel par lobby        |
| Frontend       | `/frontend/src`      | React + Hooks + Context     |

### Arborescence

```
├── backend/

│   ├── api/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── schemas/           # Pydantic
│   ├── models/                # Modèles SQLAlchemy
│   ├── repositories/
│   ├── services /             # Logique métier
│   ├── utils /                #
│   ├── websocket/             #
│   ├── tests/                 # Tests unitaires backend
│   ├── main.py                # Point d’entrée FastAPI
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
├── README.md
```
