# Tests du backend Shadow Role

## 📁 Structure

```
tests/
├── conftest.py                 # Configuration pytest et fixtures
├── test_auth_register.py      # Tests endpoint /auth/register
├── test_auth_login.py         # Tests endpoint /auth/login
└── test_auth_me.py            # Tests endpoint /auth/me
```

## 🚀 Lancer les tests

```bash
uv sync # Installer les dépendances de test
uv run pytest # Lancer tous les tests
uv run pytest -v # Avec output détaillé
uv run pytest --cov=. --cov-report=html # Avec couverture

uv run pytest tests/test_auth_register.py # Un fichier spécifique
uv run pytest tests/test_auth_register.py::test_register_success # Un test spécifique
```
