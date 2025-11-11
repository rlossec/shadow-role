# Tests frontend

## Stratégie actuelle

- Utiliser **Vitest** pour les tests unitaires de composants/hook (non configuré : à mettre en place).
- Prévoir **React Testing Library** pour simuler les interactions utilisateur.
- Scénarios d’intégration à exécuter via **Playwright** ou **Cypress** (à définir).

## Priorités

1. Couvrir les hooks critiques (`useAuth`, `useLobbies`, `useWebSocket`).
2. Tester les composants de formulaire (`common/forms/*`) pour la validation.
3. E2E minimal : flux `login → rejoindre un lobby → recevoir un événement`.

> Ce document sert de feuille de route ; mettre à jour quand l’outillage est en place.
