# Référence des composants frontend

## Organisation des dossiers

```
frontend/src/components/
└── common/
    ├── base/           # Boutons, cartes, modales génériques
    ├── data/           # Composants liés aux données (tableaux, stats)
    ├── forms/          # Entrées de formulaire, validations
    ├── layout/         # Composants structurels (grids, sections)
    ├── loader/         # Indicateurs de chargement
    └── overlay/        # Dialogs, toasts, overlays
```

Les composants partagés sont écrits en **TypeScript (`.tsx`)** et suivent une convention `PascalCase`. Chaque sous-dossier expose un index pour faciliter les imports sélectifs.

## Composants clés

- **`common/base/Button.tsx`** : Bouton primaire avec variantes (`primary`, `secondary`, `ghost`).
- **`common/base/Card.tsx`** : Conteneur stylé pour encadrer des informations.
- **`common/forms/Input.tsx`** : Champ de saisie contrôlé avec gestion des erreurs.
- **`common/layout/Section.tsx`** : Wrapper pour structurer les vues en sections.
- **`common/loader/Spinner.tsx`** : Indicateur de chargement standard.
- **`common/overlay/Modal.tsx`** : Boîte de dialogue modale avec gestion d’ouverture/fermeture.

> Voir les fichiers correspondants sous `frontend/src/components/common/**` pour la signature exacte et les props.

## Conventions

- Les composants sont _stateless_ lorsque possible ; la logique est externalisée dans les hooks (`frontend/src/hooks/`).
- Les styles s’appuient sur des classes utilitaires définies dans `App.css` et `index.css`, complétées par des tokens de thème (`THEME-README.md`).
- Les icônes sont centralisées dans `frontend/src/icons/` et importées au besoin pour garder un namespace unique (`Icon.tsx`).
