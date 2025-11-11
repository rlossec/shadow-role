# Tests backend

## Objectifs

- Garantir la fiabilité des endpoints REST (statuts, payloads, erreurs).
- Valider la logique métier des services (assignations, transitions d’état).
- Vérifier la cohérence des schémas de données (relations, contraintes).
- Assurer la robustesse du serveur WebSocket (auth, diffusion, gestion de rooms).

## Outils

- **pytest** : framework de tests principal.
- **httpx.AsyncClient** : client asynchrone pour tester FastAPI.
- **pytest-asyncio** : gestion de la boucle événementielle.
- **faker** / factories locales : génération de données.
- **sqlite en mémoire** pour les tests rapides (config dans `tests/conftest.py`).

## Structure des tests

```
backend/tests/
├── api/                 # Tests d’intégration REST
│   └── authentication/  # Exemple : login, register, refresh
├── services/            # Tests unitaires des services (à créer)
├── websocket/           # Scénarios temps réel (à compléter)
├── fixtures/            # Fixtures partagées (db, client, données)
└── README.md            # Consignes spécifiques
```

## Priorités de couverture

1. **Auth** : création compte, login, refresh, protection routes.
2. **Lobbies** : création, rejoindre, démarrer, sécurité (accès autorisés).
3. **GameService** : assignation rôles/missions, transitions `waiting → running → ended`.
4. **WebSocket** : connexion JWT, broadcast `lobby_joined`, cycle `start_game`.

## Commandes

- `uv run pytest` : exécuter toute la suite.
- `uv run pytest backend/tests/api` : cibler les tests REST.
- `uv run pytest backend/tests/websocket` : lancer les scénarios temps réel (prévoir un serveur test).

> Documenter ici les nouveaux dossiers de tests ou pratiques recommandées au fur et à mesure.
