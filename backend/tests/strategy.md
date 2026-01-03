# Stratégie de Test

Ce document décrit la stratégie de test pour comprendre le fonctionnement du backend étape par étape.

## Philosophie de test

### Approche progressive

1. **Tests unitaires des services**
2. **Tests d'intégration des services**
3. **Tests des handlers**
4. **Tests end-to-end**

## Structure des tests

```
backend/tests/
├── services/
│   ├── test_phase_service.py
│   ├── test_lobby_service.py
│   ├── test_round_service.py
│   ├── test_score_service.py
│   └── ...
└── app/
    └── api/
        └── ...                          # Tests d'intégration API REST
```

## Exécution des tests

### Tests unitaires des services

```bash
uv run pytest tests/app/services/test_phase_service.py -v      # Tester PhaseService (gestion des phases)
uv run pytest tests/app/services/test_lobby_service.py -v      # Tester LobbyService (gestion des lobbies)
uv run pytest tests/app/services/test_round_service.py -v      # Tester RoundService (gestion des rounds)
uv run pytest tests/app/services/test_score_service.py -v      # Tester ScoreService (calcul des scores)
```

### Tests des handlers WebSocket

```bash
uv run pytest tests/app/websocket/unit/test_game_command_handler.py -v
```

### Tests E2E

```bash
uv run pytest tests/app/websocket/e2e/test_e2e_qui_suis_je.py -v -s
```

## Avancement

- ✅ Tests unitaires des services de base (Phase, Lobby, Round, Score)
- ⏳ Tests unitaires des handlers WebSocket
- ⏳ Tests d'intégration
- ⏳ Tests de performance
- ⏳ Tests de charge
