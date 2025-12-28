"""
Tests pour les endpoints /api/lobbies.

Structure:
- Un fichier par endpoint
- Tests organisés par code de statut avec séparateurs # <status_code>
- Payloads de base dans helpers.py

Pour exécuter tous les tests des lobbies:
    uv run pytest tests/app/api/lobbies/ -v
    
Pour exécuter un test spécifique:
    uv run pytest tests/app/api/lobbies/test_create_lobby.py -v
    uv run pytest tests/app/api/lobbies/test_get_lobby.py -v
"""

