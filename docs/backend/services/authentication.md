## Vue d’ensemble

- `backend/services/auth/service.py` : logique métier d’authentification (inscription, login, rotation/logout des tokens JWT, activation de compte, notifications métier, etc.).
- `backend/services/auth/token_manager.py` : gestion des tokens de réinitialisation et d’activation hors JWT.
- `backend/services/auth/link_builder.py` : génération des liens (activation, reset) propres au domaine d’authentification.
- `backend/services/auth/dependencies.py` : assemble `AuthenticationService` en injectant répertoires, denylist JWT, notification service et link builder.

## AuthenticationService

Fichier : `backend/services/auth/service.py`

Responsabilités principales :

- **Inscription** (`register_user`) : vérifie l’unicité username/email puis persiste un utilisateur inactif.
- **Authentification** (`authenticate_user`) : charge un utilisateur via username/email et valide son mot de passe.
- **Gestion des JWT** :
  - `create_token_pair` : produit un couple `access` + `refresh`.
  - `rotate_refresh_token` : vérifie le refresh présenté, invalide son `jti` via la deny-list (`TokenRepository`) et retourne un nouveau couple.
  - `revoke_refresh_token` : révoque un refresh token (logout, sécurité).
- **Activation / mot de passe** :
  - `notify_account_activation`, `notify_activation_confirmation`, `notify_password_reset` construisent le contexte métier et délèguent l’envoi de notification.
  - `set_user_active`, `set_user_password`, `get_user_by_id/email` orchestrent l’état utilisateur.

L’instance est construite via `build_authentication_service`, qui assemble :

- `UserRepository` (accès base SQLAlchemy) ;
- `TokenRepository` (deny-list des refresh tokens) ;
- `JWTRepository` (création/validation des JWT) ;
- `NotificationService` générique (via les dépendances notifications) ;
- `NotificationLinkBuilder` (construction des URLs de confirmation).

## Token managers (hors JWT)

Fichier : `backend/services/auth/token_manager.py`

- `PasswordResetManager` : crée des tokens de réinitialisation (stock SQL), vérifie leur validité, marque un usage.
- `AccountActivationTokenManager` : même logique pour les activations de compte.

Ces classes se basent aussi sur `UserRepository` pour lire/écrire en base.

## Flux d’activation

1. `POST /auth/register`
   - `AuthenticationService.register_user`
   - `AccountActivationTokenManager.create_token`
   - `AuthenticationService.notify_account_activation` (template `auth_activation`)
2. `POST /auth/activate-account`
   - Vérification du token (`AccountActivationTokenManager.verify_token`)
   - `AuthenticationService.set_user_active`
   - `AuthenticationService.notify_activation_confirmation` (template `auth_activation_confirmation`)

Ce découpage permet :

- de remplacer l’orchestrateur d’emails sans changer la logique métier ;
- d’auditer/révoquer les jetons facilement ;
- d’étoffer la logique (ex. multi-facteurs) en étendant `AuthenticationService`.

## Intégration

- `backend/services/auth/dependencies.py` fournit :
  - `get_link_builder`
  - `get_authentication_service`
  - `get_password_reset_manager`, `get_account_activation_manager`
  - `get_current_user` / `get_current_active_user`

### Workflow

1. **Inscription** : `POST /auth/register` crée un utilisateur inactif **et** déclenche immédiatement l’envoi d’un email d’activation contenant un lien signé.
2. **Confirmation par email** : l’utilisateur suit le lien reçu (token signé) pour appeler `POST /auth/activate-account` et activer son compte.
3. **Connexion** : `POST /auth/jwt/login` retourne un couple `access_token` / `refresh_token` (compte actif requis).
4. **Refresh token** : `POST /auth/refresh` régénère un **nouveau** couple de jetons et invalide immédiatement le refresh token présenté.
5. **Requêtes protégées** : ajouter l’en-tête `Authorization: Bearer <access_token>`.

### Autres endpoints utiles :

- `POST /auth/resend_activation` renvoie l'email d'activation (si le compte est encore inactif).
  **Gestion mot de passe** :
  - `POST /auth/request-reset-password` envoie un lien de réinitialisation par mail.
  - `POST /auth/reset-password` applique le changement avec le jeton fourni.
