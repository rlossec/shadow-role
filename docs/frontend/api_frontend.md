# API côté frontend

Les appels HTTP sont centralisés dans `frontend/src/services/api/`.  
Chaque module ne fait que manipuler des DTO typés et laisse la logique métier aux hooks (`useAuth`, `useLobbies`, …).

## Instances et utilitaires

| Fichier                     | Rôle                                                                 |
| --------------------------- | -------------------------------------------------------------------- |
| `lib/axios.ts`              | Crée deux instances Axios (JSON + form), pose les intercepteurs JWT. |
| `services/notifications.ts` | Service léger d’affichage (toast/alert)                              |
| `config/api.ts`             | Base URL + mapping des endpoints REST                                |

### Authentification

| Fichier                     | Rôle                                                           |
| --------------------------- | -------------------------------------------------------------- |
| `services/api/auth.ts`      | Login/logout, register, refresh, reset password, activation    |
| `contexts/AuthProvider.tsx` | Conserve l’utilisateur courant, gère la persistance des tokens |
| `hooks/useAuth.ts`          | Expose l’API auth aux composants (`login`, `register`, …)      |

### Autres domaines

| Fichier                   | Responsabilité principale                      |
| ------------------------- | ---------------------------------------------- |
| `services/api/games.ts`   | Catalogue des jeux                             |
| `services/api/lobbies.ts` | CRUD lobbies, actions host                     |
| `services/api/players.ts` | Gestion des joueurs & missions                 |
| `services/api/index.ts`   | Ré-export des services (utilisé par les hooks) |

> Tous ces services renvoient des promesses typées (`Promise<T>`), avec les interfaces déclarées dans `src/types/`.

## Hooks orchestrateurs

- `useAuth.ts` : session utilisateur, formulaires d’auth, erreurs centralisées.
- `useGames.ts`, `useLobbies.ts`, `usePlayers.ts` : chargement via React Query (`lib/react-query.ts`).
- `useLobbyContext.ts` : accès au temps réel (WebSocket) exposé par `LobbyProvider`.

## Temps réel (lobbies)

Le temps réel est géré par `contexts/LobbyProvider.tsx`, qui ouvre la connexion Socket.IO via `hooks/useWebSocket.ts`.
Le hook `useLobbyContext()` expose :

| Propriété               | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| `connected`             | Indique si le socket est connecté                     |
| `users`                 | Utilisateurs actuellement connectés au lobby          |
| `gameState`             | État courant de la partie (joueurs, missions, rôles…) |
| `emit(event, payload?)` | Permet d’émettre un événement côté client             |

### Événements WebSocket utilisés côté frontend

| Événement émis (`emit`)        | Rôle / déclenchement                                |
| ------------------------------ | --------------------------------------------------- |
| `join_lobby`                   | Rejoindre la salle dès que la connexion est établie |
| `lobby:start_game`             | Démarrer ou reprendre la partie                     |
| `lobby:pause_game`             | Mettre la partie en pause                           |
| `lobby:start_proposal_phase`   | Lancer la phase de propositions                     |
| `lobby:start_round`            | Démarrer une nouvelle manche                        |
| `lobby:start_validation_phase` | Démarrer la phase de validation                     |
| `lobby:end_round`              | Terminer la manche en cours                         |
| `lobby:end_game`               | Clore la partie et afficher les résultats           |

> Ces événements complètent les endpoints REST (cf. doc backend) et correspondent aux actions disponibles dans `components/lobby/GameControls.tsx`.

## Ajouter un nouveau service

1. Déclarer l’endpoint dans `config/api.ts`.
2. Implémenter le module dans `services/api/<nouveau-module>.ts`.
3. Mettre à jour `services/api/index.ts` et les hooks concernés.
4. Documenter la responsabilité dans ce fichier.
