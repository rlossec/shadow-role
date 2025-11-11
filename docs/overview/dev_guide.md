## Prérequis

- **Python 3.12**
- **Node.js 20**
- **PostgreSQL** (local ou via conteneur) ou SQLite pour le développement rapide
- **Docker** (optionnel) pour lancer l’environnement complet

## 1. Installation du backend

```bash
cd backend
uv sync
uv run main.py
```

Le backend est sur `http://localhost:8000`.

## 2. Installation du frontend

```bash
cd frontend
npm install
npm run dev

```

Le frontend est servi par Vite sur `http://localhost:5173`.

## 3. Installation SMTP

```bash
cd fake_smtp
docker-compose up -d

```

Le frontend est servi par MailHog sur `http://localhost:8025`.

## 4. Organisation du code

- `backend/` suit une logique modulaire (API, services, repositories, websocket).
- `frontend/src/` est organisé par domaines (components, hooks, pages, services).
- Les diagrammes et documents de référence sont regroupés dans `docs/`.

## 4. Conventions

- **Lint & format** : respecter les linters configurés
- **Typage** : utiliser les annotations Python et le typage TypeScript strict.
- **Commits** : adopter un style clair (ex. `docs:`, `feat:`, `fix:`).
- **Tests** : vérifier les tests avant merge

## 5. Dépannage

- Ports occupés : vérifier que `5173` (frontend) et `8000` (backend) sont libres.
- Variables d’environnement : `.env` doit contenir la configuration DB et les clés JWT.
- WebSocket : s’assurer que le serveur backend est démarré avant de tester le temps réel.
