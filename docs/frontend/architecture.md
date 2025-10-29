# Architecture Frontend - ShadowRole

## Vue d'ensemble

Le frontend de ShadowRole est construit avec **React** et utilise une architecture component-based avec gestion d'état pour les interactions temps réel.

## Structure des modules

```
frontend/
├── src/
│   ├── main.jsx              # Point d'entrée React
│   ├── App.jsx                # Composant racine avec routing
│   ├── pages/                 # Pages principales
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── LobbyList.jsx      # Liste des lobbies disponibles
│   │   ├── CreateLobby.jsx    # Création d'un lobby
│   │   ├── JoinLobby.jsx      # Rejoindre via code
│   │   ├── WaitingRoom.jsx    # Salle d'attente
│   │   ├── GameRoom.jsx       # Interface de jeu
│   │   └── ResultPage.jsx     # Résultats finaux
│   ├── components/            # Composants réutilisables
│   │   ├── PlayerList.jsx
│   │   ├── RoleCard.jsx
│   │   ├── MissionCard.jsx
│   │   ├── Timer.jsx
│   │   ├── NavBar.jsx
│   │   ├── ChatBox.jsx
│   │   └── LobbyCard.jsx
│   ├── hooks/                 # Custom hooks React
│   │   ├── useAuth.js         # Gestion authentification
│   │   ├── useWebSocket.js    # Connexion WebSocket
│   │   ├── useLobby.js        # État lobby
│   │   └── useGame.js         # État jeu
│   ├── context/               # Context API
│   │   ├── AuthContext.jsx    # Contexte utilisateur
│   │   ├── LobbyContext.jsx   # Contexte lobby
│   │   └── WebSocketContext.jsx # Contexte WebSocket
│   ├── api/                   # Appels API
│   │   ├── auth.js
│   │   ├── lobby.js
│   │   ├── player.js
│   │   └── game.js
│   ├── utils/                 # Utilitaires
│   │   ├── constants.js       # Constantes
│   │   ├── helpers.js         # Fonctions helper
│   │   └── websocket.js       # Client WebSocket
│   └── styles/                # Styles Tailwind
│       └── globals.css
├── public/
│   ├── index.html
│   └── assets/
└── package.json
```

## Gestion d'état

### AuthContext

Gère l'authentification et les informations utilisateur.

```javascript
const { user, login, logout, isAuthenticated } = useAuth();
```

### LobbyContext

Gère l'état du lobby actif et les joueurs.

```javascript
const { lobby, players, joinLobby, leaveLobby, startGame } = useLobby();
```

### WebSocketContext

Gère la connexion WebSocket et les messages en temps réel.

### Types de messages WebSocket gérés

- `player_joined` → Mise à jour liste joueurs
- `player_left` → Retrait du joueur
- `lobby_started` → Redirection vers GameRoom
- `role_assigned` → Affichage du rôle
- `mission_assigned` → Affichage de la mission
- `game_update` → État du jeu
- `timer_update` → Update du timer
- `game_ended` → Redirection vers ResultPage

## Composants principaux

### LobbyCard

Affiche les informations d'un lobby (nom, nombre de joueurs, statut).

### PlayerList

Liste des joueurs avec leurs statuts.

### RoleCard

Carte affichant le rôle assigné (cachée jusqu'au démarrage).

### MissionCard

Carte affichant la mission (peut être secrète).

### Timer

Composant de compte à rebours pour les missions.

### ChatBox

Chat temps réel pour la communication entre joueurs.

## Pages principales

### 1. Login / Register

- Formulaire d'authentification
- Validation des champs
- Gestion des erreurs
- Redirection après succès

### 2. LobbyList

- Affichage des lobbies disponibles
- Filtres par statut/nombre de joueurs
- Bouton "Créer un lobby"
- Rejoindre un lobby

### 3. CreateLobby

- Formulaire de création
- Sélection du type de jeu
- Choix du nombre max de joueurs
- Génération du code unique

### 4. WaitingRoom

- Liste des joueurs connectés
- Afficher le code du lobby (partageable)
- Bouton "Démarrer" (hôte uniquement)
- Quitter le lobby
- Chat pour discussion

### 5. GameRoom

- Affichage du rôle assigné
- Affichage de la mission
- Timer de la mission
- Actions disponibles selon le rôle
- Chat entre joueurs

### 6. ResultPage

- Scores finaux
- Classement
- Statistiques
- Retour à l'accueil

## Appels API

### Module api/auth.js

```javascript
export const login = async (email, password) => {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return response.json();
};
```

### Module api/lobby.js

```javascript
export const createLobby = async (name, gameId, maxPlayers) => {
  const response = await fetch("/api/lobby", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ name, game_id: gameId, max_players: maxPlayers }),
  });
  return response.json();
};
```

## Styling avec Tailwind CSS

### Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: "#3B82F6",
        secondary: "#8B5CF6",
        danger: "#EF4444",
        success: "#10B981",
      },
    },
  },
};
```

### Exemples de classes

- Cartes : `bg-white rounded-lg shadow-md p-6`
- Boutons : `bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark`
- Layouts : `flex justify-between items-center gap-4`

## Gestion des erreurs

### Error Boundary

```javascript
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

### Toast notifications

Utilisation de `react-hot-toast` pour les notifications.

## Optimisations

### Code Splitting

```javascript
const GameRoom = lazy(() => import("./pages/GameRoom"));
const WaitingRoom = lazy(() => import("./pages/WaitingRoom"));
```

### Memoization

```javascript
const MemoizedPlayerList = memo(PlayerList);
```

### Debounce

```javascript
const debouncedSearch = useMemo(
  () => debounce(searchLobbies, 300),
  [searchLobbies]
);
```

## Déploiement

### Build

```bash
npm run build
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Production

- Serveur statique (Nginx)
- CDN pour assets
- SSL/HTTPS
- Compression des assets (gzip)
