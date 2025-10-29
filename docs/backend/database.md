## Base de données

### ORM

SQLAlchemy avec déclarative models.

### Migrations

Alembic pour les migrations de schéma.

### Relations

- Toutes les relations utilisent `ondelete="CASCADE"` où approprié
- Relations lazy-loading pour performance
