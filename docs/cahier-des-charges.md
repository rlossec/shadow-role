# Cahier des Charges - ShadowRole

## 1. Vue d'ensemble du projet

**ShadowRole** est une plateforme web de jeu en ligne permettant à des joueurs de se connecter et de participer à des sessions de jeu collaboratives basées sur des rôles et des missions.

## 2. Objectifs du projet

- Permettre la création de lobbies de jeu par les utilisateurs
- Faciliter la connexion et l'authentification des joueurs via JWT
- Distribuer dynamiquement des rôles et missions aux joueurs
- Gérer les sessions de jeu en temps réel via WebSocket
- Suivre les scores et les performances des joueurs

## 3. Fonctionnalités principales

### 3.1. Authentification utilisateur

- Inscription / Connexion avec email et mot de passe
- Authentification basée sur JWT (JSON Web Tokens)
- Gestion des sessions utilisateur
- Profil utilisateur avec historique de parties

### 3.2. Gestion des lobbies

- Création de lobby avec code unique partageable
- Rejoindre un lobby via code
- Limitation du nombre de joueurs par lobby
- Expiration automatique des lobbies inactifs
- Statut des lobbies : en attente → démarré → en cours → terminé

### 3.3. Système de jeu

- Types de jeux configurables (basés sur rôles, missions, ou hybride)
- Distribution automatique des rôles aux joueurs
- Attribution de missions individuelles ou collectives
- Timer pour les missions avec durée estimée
- Système de scoring et de récompenses

### 3.4. Rôles et missions

- Création de bibliothèque de rôles par jeu
- Missions secrètes ou partagées
- Niveaux de difficulté des missions
- Système d'abilités par rôle
- Liaison optionnelle entre rôles et missions

### 3.5. Communication temps réel

- WebSocket pour les mises à jour instantanées
- Chat dans les lobbies
- Notifications d'événements (joueur rejoint/part, mission complétée, etc.)

## 4. Contraintes techniques

### 4.1. Backend

- **Framework** : FastAPI (Python)
- **Base de données** : PostgreSQL ou SQLite
- **ORM** : SQLAlchemy
- **Authentification** : JWT (Python-JOSE)
- **WebSocket** : FastAPI WebSocket
- **Validation** : Pydantic

### 4.2. Frontend

- **Framework** : React
- **Routing** : React Router
- **Styling** : Tailwind CSS
- **WebSocket Client** : native WebSocket ou Socket.io-client
- **State Management** : Context API ou Redux Toolkit

### 4.3. Déploiement

- Docker pour containerisation
- Support multi-environnement (dev/staging/prod)
- Variables d'environnement pour configuration

## 5. Modèles de données

### 5.1. USER

Représente les utilisateurs de la plateforme avec leurs informations de connexion.

### 5.2. LOBBY

Session de jeu créée par un hôte, utilisant un type de jeu spécifique.

### 5.3. GAME

Modèle de jeu définissant les règles, rôles et missions possibles.

### 5.4. MISSION

Tâches/objectifs assignés aux joueurs pendant le jeu.

### 5.5. ROLE

Rôles jouables dans un type de jeu, avec leurs capacités spécifiques.

### 5.6. PLAYER

Représente la participation d'un utilisateur à un lobby avec son rôle et sa mission assignés.

## 6. Flux utilisateur typique

1. **Connexion** : L'utilisateur se connecte avec son compte
2. **Création de lobby** : Un utilisateur crée un lobby et choisit un type de jeu
3. **Rejoindre** : D'autres utilisateurs rejoignent le lobby via le code
4. **Distribution** : Quand le lobby démarre, rôles et missions sont distribués
5. **Jeu** : Les joueurs interagissent selon leurs rôles et missions
6. **Fin de partie** : Scoring et résultats affichés

## 7. Critères de succès

- Latence WebSocket < 100ms
- Support de 50+ joueurs simultanés par lobby
- Interface intuitive avec < 3 clics pour rejoindre un lobby
- Compatibilité navigateurs modernes (Chrome, Firefox, Safari, Edge)
- Disponibilité > 99.5%

## 8. Roadmap

### Phase 1 : MVP (Minimum Viable Product)

- Authentification JWT
- Création et gestion de lobbies
- Un type de jeu de base
- Distribution simple de rôles

### Phase 2 : Amélioration

- Système de missions
- WebSocket pour temps réel
- Chat et notifications
- Système de scoring avancé

### Phase 3 : Expansion

- Plusieurs types de jeux
- Statistiques et historique
- Avatar et personnalisation
- Mode compétitif avec classements
