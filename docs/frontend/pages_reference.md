# Référence des pages

Les pages principales sont regroupées dans `frontend/src/pages/`. Elles sont chargées via le routeur défini dans `App.tsx`.

| Page                  | Description                                                    | Routes / Accès |
| --------------------- | -------------------------------------------------------------- | -------------- |
| `Login.tsx`           | Formulaire d’authentification initiale                         | `/login`       |
| `LobbyPage.tsx`       | Liste et gestion des lobbies disponibles                       | `/lobbies`     |
| `LobbyDetailPage.tsx` | Vue détaillée d’un lobby (joueurs, statut, actions host)       | `/lobbies/:id` |
| `Dashboard.tsx`       | Vue synthétique post-connexion (raccourcis, dernières parties) | `/`            |
| `WebSocketTest.tsx`   | Page utilitaire pour valider les échanges temps réel           | `/dev/ws-test` |

> Les routes exactes sont définies dans `frontend/src/App.tsx`. Adapter la table lorsque de nouvelles pages sont introduites.
