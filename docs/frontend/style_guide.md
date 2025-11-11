# Guide de style frontend

## Stack UI

- **Tailwind CSS** pour la grille utilitaire.
- Styles globaux dans `frontend/src/index.css` et `frontend/src/App.css`.
- Thème (couleurs, typographies, espacements) documenté dans `frontend/src/THEME-README.md`.

## Conventions

- Utiliser des classes Tailwind pour la mise en page rapide ; compléter avec des classes personnalisées uniquement lorsque nécessaire (`App.css`).
- Préfixer les classes utilitaires spécifiques projet par `sr-` pour éviter les collisions.
- Centraliser les couleurs et tokens dans `:root` (`index.css`) afin de pouvoir basculer de thème facilement.

## Composants

- Les composants UI doivent accepter une prop `className` pour permettre l’extension.
- Préférer des composants composables (e.g. `Card`, `Button`) concentrés dans `components/common/base/`.

## Accessibilité

- Toujours renseigner `aria-label` ou `aria-labelledby` pour les boutons icône (`icons`).
- S’assurer que les contrastes suivent les recommandations WCAG (voir palette dans `THEME-README.md`).

> Ajouter ici vos règles de design system supplémentaires (typographies, grilles, iconographie) au fur et à mesure.
