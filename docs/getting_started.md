# Guide de Démarrage - Shadow Role

Ce guide vous accompagne pas à pas pour installer et configurer l'application Shadow Role sur votre environnement de développement.

## Table des Matières

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement de l'Application](#lancement-de-lapplication)
- [Vérification de l'Installation](#vérification-de-linstallation)
- [Problèmes Courants](#problèmes-courants)
- [Prochaines Étapes](#prochaines-étapes)

## Prérequis

### Python

Shadow Role utilise Python 3.12+ backend.

```bash
python --version  # Doit afficher 3.12 ou supérieur
```

### uv

[uv](https://github.com/astral-sh/uv) pour la gestion des dépendances

```bash
# Installation de uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Installation de uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Vérification
uv --version

```

### Node.js et npm

Le frontend nécessite Node.js 18 ou supérieur.

```bash
# Vérification
node --version  # Doit afficher v18.x ou supérieur
npm --version
```

### PostgreSQL

**Installation locale**

- [PostgreSQL 14+](https://www.postgresql.org/download/)
- Créez une base de données `shadow_role_dev`

### Docker (optionnel mais recommandé)

Pour le SMTP de développement et une installation simplifiée :

- [Docker Desktop](https://www.docker.com/products/docker-desktop)

## Installation

### 1. Cloner le Projet

```bash
git clone https://github.com/rlossec/shadow-role.git
cd shadow-role
```

### 2. Configuration du Backend

```bash
cd backend

# Installer les dépendances Python
uv sync

# Copier le fichier de configuration
cp .env.example .env
```

Éditez le fichier `.env` avec vos paramètres :

```env
# Base de données
DATABASE_URL=postgresql+asyncpg://shadowrole:dev_password@localhost:5432/shadow_role_dev

# JWT
SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (développement)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@shadowrole.local

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Environnement
ENVIRONMENT=development
DEBUG=true
```

### 3. Configuration du Frontend

```bash
cd ../frontend

# Installer les dépendances npm
npm install

# Copier le fichier de configuration
cp .env.example .env
```

Éditez le fichier `.env` si nécessaire :

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

### 4. Configuration du SMTP (développement)

Pour recevoir et visualiser les emails en développement :

```bash
cd ../fake_smtp
docker-compose up -d
```

Cela lance [MailHog](https://github.com/mailhog/MailHog), accessible sur http://localhost:8025

## Configuration

### Variables d'Environnement Backend

| Variable                      | Description                     | Valeur par défaut         |
| ----------------------------- | ------------------------------- | ------------------------- |
| `DATABASE_URL`                | URL de connexion PostgreSQL     | -                         |
| `SECRET_KEY`                  | Clé secrète pour JWT            | -                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie des tokens d'accès | 30                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Durée de vie des refresh tokens | 7                         |
| `SMTP_HOST`                   | Hôte SMTP                       | localhost                 |
| `SMTP_PORT`                   | Port SMTP                       | 1025                      |
| `CORS_ORIGINS`                | Origins autorisées pour CORS    | ["http://localhost:5173"] |

### Variables d'Environnement Frontend

| Variable       | Description          | Valeur par défaut     |
| -------------- | -------------------- | --------------------- |
| `VITE_API_URL` | URL de l'API backend | http://localhost:8000 |
| `VITE_WS_URL`  | URL WebSocket        | http://localhost:8000 |

## Lancement de l'Application

Ouvrez **trois terminaux** distincts :

**Terminal 1 - Backend** :

```bash
cd backend
uv run main.py
```

**Terminal 2 - Frontend** :

```bash
cd frontend
npm run dev
```

**Terminal 3 - SMTP (optionnel)** :

```bash
cd fake_smtp
docker-compose up
```

### Ports Utilisés

- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc
- **MailHog UI** : http://localhost:8025
- **PostgreSQL** : localhost:5432

## Vérification de l'Installation

### 1. Vérifier le Backend

Accédez à http://localhost:8000/docs - vous devriez voir la documentation Swagger.

Testez l'endpoint de health check :

```bash
curl http://localhost:8000/health
# Devrait retourner: {"status":"ok"}
```

### 2. Vérifier le Frontend

Accédez à http://localhost:5173 - vous devriez voir la page d'accueil de Shadow Role.

### 3. Tester l'Authentification

1. Créez un compte depuis l'interface web
2. Vérifiez que l'email de confirmation apparaît dans MailHog (http://localhost:8025)
3. Connectez-vous avec vos identifiants

### 4. Tester le WebSocket

1. Créez ou rejoignez un lobby
2. Ouvrez l'inspecteur de votre navigateur (F12)
3. Dans l'onglet "Network" ou "Réseau", vérifiez la connexion WebSocket
4. Vous devriez voir des messages échangés en temps réel

## Problèmes Courants

### Erreur : "Database connection failed"

**Solution** :

1. Vérifiez que PostgreSQL est bien lancé
2. Vérifiez vos identifiants dans `.env`
3. Testez la connexion manuellement :

```bash
psql -h localhost -U shadowrole -d shadow_role_dev
```

### Erreur : "Port already in use"

**Solution** :

```bash
# Trouver le processus qui utilise le port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Tuer le processus
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Erreur : "Module not found"

**Backend** :

```bash
cd backend
uv sync --force  # Réinstaller les dépendances
```

**Frontend** :

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Erreur CORS

Si vous voyez des erreurs CORS dans la console :

1. Vérifiez que `CORS_ORIGINS` dans `.env` contient bien l'URL de votre frontend
2. Relancez le backend

## Prochaines Étapes

Maintenant que votre environnement est configuré :

1. 📖 **Consultez l'architecture** : [docs/architecture.md](./architecture.md)
2. 🔧 **Explorez le backend** : [docs/backend/README.md](./backend/README.md)
3. ⚛️ **Découvrez le frontend** : [docs/frontend/README.md](./frontend/README.md)

## Besoin d'Aide ?

- 📚 **Documentation complète** : Dossier `docs/`
- 🐛 **Signaler un bug** : [GitHub Issues](https://github.com/rlossec/shadow-role/issues)
- 💬 **Poser une question** : [GitHub Discussions](https://github.com/rlossec/shadow-role/discussions)
