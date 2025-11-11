# Schémas de base de données

## ORM

Le projet utilise **SQLAlchemy** avec le style déclaratif pour définir les modèles persistants.

## Migrations

Les migrations de schéma sont gérées via **Alembic**. Un script de maintenance est disponible dans `backend/scripts/`.

## Relations et contraintes

- Utilisation d’`ondelete="CASCADE"` lorsque pertinent afin de garantir l’intégrité référentielle.
- Chargement différé (_lazy loading_) par défaut pour les relations afin d’optimiser les performances.

Pour une description détaillée de chaque entité et de ses attributs, se référer au document `docs/overview/modeles-donnees.md`.
