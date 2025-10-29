# Visibilité des Missions et Évolution

Ce document explique en détail le système de visibilité des missions et comment elles peuvent évoluer durant une partie.

## Concept de Mission

Dans ShadowRole, une **MISSION** représente la **personnalité intellectuelle** d'un joueur. Cela peut être :

- Un objectif à accomplir
- Un trait de personnalité à incarner
- Un secret à découvrir
- Une personnalité à devenir

## Visibilité

Chaque mission a deux propriétés de visibilité indépendantes qui contrôlent qui peut la voir :

### `is_known_by_player` (Boolean)

Indique si le joueur propriétaire de la mission peut la voir.

- `true` : Le joueur voit sa propre mission
- `false` : Le joueur ne voit pas sa mission (découverte progressive)

### `is_known_by_others` (Boolean)

Indique si les autres joueurs peuvent voir cette mission.

- `true` : Tous les joueurs voient cette mission
- `false` : Seul le joueur propriétaire la voit (ou personne si `is_known_by_player = false`)

## Combinaisons possibles pour les MISSIONS

La visibilité contrôle qui peut voir la mission et, si elle est liée à un rôle, la visibilité du rôle associé :

| `is_known_by_player` | `is_known_by_others` | Résultat                                                  |
| -------------------- | -------------------- | --------------------------------------------------------- |
| `true`               | `false`              | Seul le joueur voit sa mission/rôle (secrète)             |
| `true`               | `true`               | Tout le monde voit la mission/rôle (publique)             |
| `false`              | `false`              | Personne ne voit la mission/rôle (à découvrir)            |
| `false`              | `true`               | Les autres voient ce que le joueur ne voit pas (ironique) |

## Exemples avec visibilité de mission/rôle

### Mission/Rôle secrets (mafia / trahison)

```json
{
  "mission": {
    "title": "Tu es le Mafioso",
    "role_id": "role_mafioso",
    "is_known_by_player": true,
    "is_known_by_others": false
  },
  "role": {
    "name": "Mafioso"
  }
}
```

Le joueur sait qu'il est Mafioso avec la mission associée, mais les autres pensent qu'il est un citoyen normal.

### Mission/Rôle publics (équipe commune)

```json
{
  "mission": {
    "title": "Défend le village",
    "role_id": "role_knight",
    "is_known_by_player": true,
    "is_known_by_others": true
  },
  "role": {
    "name": "Chevalier"
  }
}
```

Tout le monde sait que ce joueur est un Chevalier et sa mission.

### Mission/Rôle à découvrir (transformation)

```json
{
  "mission": {
    "title": "Tu es Innocent",
    "role_id": "role_innocent",
    "is_known_by_player": false,
    "is_known_by_others": false
  },
  "role": {
    "name": "Innocent"
  }
}
```

Personne ne sait encore que ce joueur est "Innocent", cela sera révélé plus tard.

## Exemples de missions

### Mission secrète (coopération cachée)

```json
{
  "title": "Protéger le roi",
  "is_known_by_player": true,
  "is_known_by_others": false
}
```

Le joueur sait qu'il doit protéger le roi, mais les autres ne le savent pas.

### Mission publique (objectif partagé)

```json
{
  "title": "Collecter 10 or",
  "is_known_by_player": true,
  "is_known_by_others": true
}
```

Tout le monde sait que ce joueur doit collecter 10 or.

### Mission à découvrir (mystère)

```json
{
  "title": "Tu es le traître",
  "is_known_by_player": false,
  "is_known_by_others": false
}
```

Personne ne sait encore que ce joueur est le traître. Cela sera révélé plus tard.

## Évolution de mission

Les missions peuvent **évoluer** pendant la partie grâce au champ `mission_state` dans la table PLAYER.

### Structure du `mission_state`

Le champ `mission_state` est un JSON libre qui peut stocker :

```json
{
  "phase": "initial|progression|finale",
  "progress": 0.75,
  "revealed_to": ["player_123", "player_456"],
  "custom_data": {}
}
```

### Exemple d'évolution

**Phase initiale** (statut : waiting/playing début) :

```json
{
  "mission_id": "mission_001",
  "mission_state": null
}
```

Le joueur a une mission assignée mais l'état n'a pas encore évolué.

**Après quelques actions** :

```json
{
  "mission_id": "mission_001",
  "mission_state": {
    "phase": "progression",
    "objectives_completed": 2,
    "total_objectives": 5
  }
}
```

**Phase finale** :

```json
{
  "mission_id": "mission_001",
  "mission_state": {
    "phase": "finale",
    "revealed_to_all": true,
    "completed_at": "2024-01-01T12:30:00Z"
  }
}
```

## Implémentation backend

### Vérification de visibilité

```python
def can_player_see_mission(player: Player, mission: Mission) -> bool:
    """Vérifie si un joueur peut voir une mission"""

    # Si c'est la mission du joueur
    if player.mission_id == mission.id:
        return mission.is_known_by_player

    # Si c'est la mission d'un autre joueur
    return mission.is_known_by_others
```

### Mise à jour du `mission_state`

```python
def update_mission_state(player: Player, state: dict):
    """Met à jour l'état évolutif de la mission"""

    current_state = player.mission_state or {}
    current_state.update(state)
    player.mission_state = current_state

    # Exemple : Révéler la mission à d'autres joueurs
    if "revealed_to_all" in state and state["revealed_to_all"]:
        mission = Mission.query.get(player.mission_id)
        mission.is_known_by_others = True
```

## Rôles vs Missions

### ROLE (Personnages)

- Représente un **personnage** que le joueur incarne
- Exemples : "Chevalier", "Magicien", "Pirate", "Éclaireur", "Traître"
- **Pas de gestion directe de visibilité** au niveau du rôle
- **Peut être lié à une mission** : plusieurs missions peuvent pointer vers ce rôle (1-N via `mission.role_id`)

### MISSION (Personnalités intellectuelles)

- Représente la **personnalité intellectuelle** du joueur
- Exemples : "Protéger le secret", "Infiltre-toi", "Collecte des indices"
- **Peut être secrète** et **évolutive**
- Propriétés de visibilité : `is_known_by_player` et `is_known_by_others`

### Distinction

- Un joueur a **un personnage** (ROLE) qu'il **joue**
- Un joueur a **une personnalité intellectuelle** (MISSION) qu'il **devient**

### Lien optionnel ROLE ↔ MISSION

Pour certains jeux, une **mission peut être associée** à un rôle spécifique via `mission.role_id` :

```json
{
  "role": {
    "name": "Espion",
    "id": "role_spy"
  },
  "mission": {
    "title": "Infiltre-toi dans la forteresse",
    "role_id": "role_spy",
    "is_known_by_player": true,
    "is_known_by_others": false
  }
}
```

Dans ce cas :

- Le joueur reçoit un rôle "Espion"
- Le joueur reçoit une mission "Infiltrer la forteresse" qui est liée au rôle Espion
- La **visibilité est gérée par la mission** : `is_known_by_player` et `is_known_by_others`
- Si la mission est secrète (`is_known_by_others: false`), le rôle associé est également secret
- Les autres joueurs ne savent ni son rôle ni sa mission

## Cas d'usage réel

### Jeu 1 : "Infiltration"

- **ROLE** : Agent secret (visibilité : secrète - `is_known_by_player: true, is_known_by_others: false`)
- **MISSION** : Tuer le roi (visibilité : secrète - `is_known_by_player: true, is_known_by_others: false`)
- **MISSION_STATE** : Trace qui a vu la mission, progression des actions
- Le joueur sait qu'il est agent secret avec pour mission de tuer le roi, les autres ne le savent pas

### Jeu 2 : "Transformation"

- **ROLE** : Humain normal (visibilité : publique - `is_known_by_player: true, is_known_by_others: true`)
- **MISSION** : Tu deviens un loup-garou cette nuit (visibilité : à découvrir - `is_known_by_player: false, is_known_by_others: false`)
- **MISSION_STATE** : Évolution de la transformation, effets visibles par phase
- Tous savent qu'il est humain normal, mais personne ne sait qu'il devient loup-garou

### Jeu 3 : "Collaboration"

- **ROLE** : Membre de l'équipe (visibilité : publique - `is_known_by_player: true, is_known_by_others: true`)
- **MISSION** : Objectif commun à 5 joueurs (visibilité : publique - `is_known_by_player: true, is_known_by_others: true`)
- **MISSION_STATE** : Progression collective du groupe
- Tout est public pour ce jeu coopératif

### Jeu 4 : "Rôle lié à Mission"

- **ROLE** : Espion
- **MISSION** : Infiltre la forteresse (`role_id` : lié au rôle Espion, visibilité secrète)
- Les deux sont liés via `mission.role_id` et gardés secrets
- Le joueur est Espion ET doit infiltrer la forteresse (rôle et mission liés)
- La visibilité est gérée par les propriétés de la mission
