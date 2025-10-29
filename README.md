## Quick Start

### Prérequis

- Python 3.12+ avec [uv](https://github.com/astral-sh/uv)
- Node.js et npm (pour le frontend)

### Lancement en développement

#### Backend

```bash
cd backend
uv sync                              # Installer les dépendances
uv run uvicorn main:app --reload    # Lancer le serveur (port 8000)
```

Le backend sera accessible sur http://localhost:8000
Documentation API disponible sur http://localhost:8000/docs

#### Frontend

```bash
cd frontend
npm install                          # Installer les dépendances
npm run dev                          # Lancer le serveur de développement
```

Le frontend sera accessible sur http://localhost:5173 (Vite par défaut)

### Lancement avec Docker

```bash
docker-compose up
```

Cette commande lance simultanément le backend, le frontend et la base de données.

## Structure du projet

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
