## Prérequis

- **Python 3.12**
- **Node.js 20 - Typescript**
- **PostgreSQL**
- **Docker** (optionnel) pour lancer la fake SMTP

Le backend est sur `http://localhost:8000`.

Le frontend est servi par Vite sur `http://localhost:5173`.

Le MailHog disponible sur `http://localhost:8025`.

## 1. Installation du backend

```bash
cd backend
uv sync
uv run main.py
```

## 2. Installation du frontend

```bash
cd frontend
npm install
npm run dev
```

## 3. Installation SMTP

```bash
cd fake_smtp
docker-compose up -d
```
