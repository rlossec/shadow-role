# Documentation ShadowRole

Bienvenue dans la documentation du projet ShadowRole. Cette documentation couvre tous les aspects du projet, de la conception à l'implémentation.

## Structure de la documentation

### 📋 Vue d'ensemble

- **[Cahier des charges](./cahier-des-charges.md)** : Objectifs, fonctionnalités et spécifications du projet
- **[Modèles de données](./modeles-donnees.md)** : Description détaillée de tous les modèles (USER, LOBBY, GAME, MISSION, ROLE, PLAYER)
- **[Visibilité des missions](./visibilite-missions.md)** : Explication du système de visibilité et d'évolution des missions

### 📊 Diagrammes

- **[Diagramme MCD (Modèle Conceptuel de Données)](./mcd.mermaid)** : Entités et relations entre les modèles
- **[Architecture globale](./global.mermaid)** : Vue d'ensemble de l'architecture système

### 🔧 Architecture technique

- **[Backend - Architecture](./backend/architecture.md)** : Structure, endpoints, WebSocket, authentification JWT
- **[Frontend - Architecture](./frontend/architecture.md)** : Structure React, composants, hooks, routing

## Modèles de données

Le système ShadowRole est basé sur 6 modèles principaux :

1. **USER** - Utilisateurs de la plateforme avec authentification JWT
2. **LOBBY** - Sessions de jeu créées par les utilisateurs
3. **GAME** - Types de jeux disponibles (rôles, missions, hybrides)
4. **MISSION** - Objectifs assignés aux joueurs
5. **ROLE** - Rôles jouables dans les différents types de jeux
6. **PLAYER** - Participation d'un utilisateur à un lobby

### Diagramme des relations

```12:20:docs/mcd.mermaid
    PLAYER {
        uuid id PK
        uuid lobby_id FK
        uuid user_id FK
        uuid role_id FK "nullable"
        uuid mission_id FK "nullable"
        int score
```

Voir le [fichier complet](./mcd.mermaid) pour le diagramme complet.

## Flux de données

### Authentification

1. L'utilisateur s'inscrit/connexion via `/api/auth/register` ou `/api/auth/login`
2. Le backend génère un JWT token
3. Le token est stocké côté client (localStorage)
4. Toutes les requêtes suivantes incluent le token dans le header `Authorization`

### Création de partie

1. L'utilisateur crée un lobby avec un type de jeu
2. Un code unique est généré pour inviter d'autres joueurs
3. D'autres joueurs rejoignent via le code
4. Le hôte démarre la partie
5. Les rôles et missions sont distribués automatiquement

### Communication temps réel

- **WebSocket** : `/ws/lobby/{lobby_id}`
- Broadcast de tous les événements (joueur rejoint, mission complétée, etc.)
- Chat en temps réel dans les lobbies

## Technologies utilisées

### Backend

- **FastAPI** - Framework web Python
- **SQLAlchemy** - ORM pour la base de données
- **Pydantic** - Validation des données
- **Python-JOSE** - Authentification JWT
- **Alembic** - Migrations de base de données
- **WebSocket** - Communication temps réel

### Frontend

- **React** - Framework JavaScript
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Context API** - Gestion d'état
- **WebSocket API** - Client WebSocket

### Base de données

- **PostgreSQL** (production) ou **SQLite** (développement)
- Schéma relationnel avec 6 tables principales

## Navigation rapide

| Document                                            | Description                            |
| --------------------------------------------------- | -------------------------------------- |
| [Cahier des charges](./cahier-des-charges.md)       | Objectifs et fonctionnalités           |
| [Modèles de données](./modeles-donnees.md)          | Détails de chaque modèle               |
| [Visibilité des missions](./visibilite-missions.md) | Système de visibilité et évolution     |
| [MCD](./mcd.mermaid)                                | Diagramme entité-relation              |
| [Architecture Backend](./backend/architecture.md)   | Endpoints, WebSocket, authentification |
| [Architecture Frontend](./frontend/architecture.md) | Composants, hooks, routing             |

## Prochaines étapes

Après avoir documenté le projet, les étapes suivantes seront :

1. ✅ Documentation complète des modèles
2. ⏳ Implémentation des modèles SQLAlchemy
3. ⏳ Création des endpoints REST
4. ⏳ Implémentation WebSocket
5. ⏳ Interface utilisateur React
6. ⏳ Tests et déploiement

## Contribution

Cette documentation sert de référence pour tous les développeurs travaillant sur le projet. Chaque modification de l'architecture ou des modèles doit être documentée ici.

---

**Note** : Cette documentation est écrite en Markdown et utilise Mermaid pour les diagrammes. Les fichiers `.mermaid` peuvent être visualisés dans n'importe quel éditeur compatible ou sur [Mermaid Live Editor](https://mermaid.live).
