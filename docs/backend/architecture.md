# Architecture Backend - ShadowRole

## Vue d'ensemble

Le backend de ShadowRole est construit avec **FastAPI** et **Socket.IO**, et suit une architecture modulaire inspirée du pattern **Clean Architecture**.
Les couches métier sont clairement séparées pour garantir la maintenabilité, la testabilité et l’évolutivité du projet.

## Structure des modules

```
backend/
├── main.py               # Point d'entrée FastAPI
├── routers/
├── core/
├── models/               # Modèles SQLAlchemy
│   ├── user.py
│   ├── lobby.py
│   ├── game.py
│   ├── mission.py
│   ├── role.py
│   └── player.py
├── schemas/             # Pydantic schemas
│   ├── user.py
│   ├── lobby.py
│   ├── game.py
│   ├── mission.py
│   └── role.py
├── repositories/        # DAO Pattern
│   ├── user_repository.py
│   ├── lobby_repository.py
│   ├── game_repository.py
│   ├── mission_repository.py
│   └── role_repository.py
├── services/           # Logique métier
└── utils/
```

## Patterns utilisés

### 1. Repository Pattern

Chaque modèle a son repository pour abstraire l'accès à la base de données.

**Exemple** :

```python
class UserRepository:
    def create(self, user_data)
    def get_by_email(self, email)
    def get_by_id(self, user_id)
    def update(self, user_id, user_data)
```

### 2. Service Layer

Couche de logique métier indépendante de la base de données.

**Exemple** :

```python
class AuthService:
    def register(self, email, password) -> User
    def login(self, email, password) -> Token
    def verify_token(self, token) -> User
```

## Configuration

### Variables d'environnement

```bash
# Base de données
DATABASE_URL=

# Application
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX

DEBUG=false
```
