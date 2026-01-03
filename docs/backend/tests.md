# Tests du backend

Ce document est une synthèse de la documentation des tests. Ils sont inclus dans le dossiers de [tests](../../backend/tests/)

## 📚 Documentation disponible

### Dans `backend/tests/`

- **[synthese.md](../../backend/tests/synthese.md)** : 📊 **Récapitulatif complet de tous les tests par catégorie**
- **[README.md](../../backend/tests/README.md)** : Guide pratique pour exécuter les tests
- **[strategy.md](../../backend/tests/strategy.md)** : Stratégie de test et approche progressive
- **[scenarios.md](../../backend/tests/scenarios.md)** : Scénarios de test E2E complets
- **[flows.md](../../backend/tests/flows.md)** : Description des flux de jeu
- **[routes.md](../../backend/tests/routes.md)** : Utilisation des noms de route dans les tests

## 🚀 Démarrage rapide

### Exécuter tous les tests

```bash
uv run pytest tests/ -v
```

### Exécuter une catégorie spécifique

```bash
# Tests de services
uv run pytest tests/app/services/ -v

# Tests WebSocket unitaires
uv run pytest tests/app/websocket/unit/ -v

# Tests WebSocket E2E
uv run pytest tests/app/websocket/e2e/ -v -s

# Tests API
uv run pytest tests/app/api/ -v
```
