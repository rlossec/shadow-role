# Services d’authentification et de notification

Ce document résume les responsabilités des services `auth` et `notifications`, leur articulation dans les endpoints, ainsi que les points d’extension pour adapter leur comportement.

## Vue d’ensemble

- `backend/services/auth/service.py` : logique métier d’authentification (inscription, login, rotation/logout des tokens JWT, activation de compte, notifications métier, etc.).
- `backend/services/auth/token_manager.py` : gestion des tokens de réinitialisation et d’activation hors JWT.
- `backend/services/auth/link_builder.py` : génération des liens (activation, reset) propres au domaine d’authentification.
- `backend/services/notifications/interface.py` : contrat générique `NotificationService` (méthode `send` à base de templates).
- `backend/services/notifications/email_service.py` : implémentation SMTP du contrat générique.
- `backend/services/notifications/template_manager.py` : résout et rend les templates (texte / HTML).
- `backend/services/notifications/smtp_client.py` : client SMTP asynchrone.
- `backend/services/notifications/dependencies.py` : usine FastAPI pour les dépendances `NotificationService`, `SMTPClient`, `TemplateManager`.
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

## Notifications : couches techniques

### Interface générique

- `NotificationService` (`backend/services/notifications/interface.py`) expose `async def send(to, template_name, context)`.
- L’interface est agnostique du médium d’envoi et du métier : seul le nom du template et le contexte lui importent.

### Implémentation Email

- `EmailNotificationService` (`backend/services/notifications/email_service.py`) :
  - Résout `subject.txt`, `body.txt`, `body.html` via `NotificationTemplateManager`.
  - Rassemble un email multipart texte/HTML.
  - Confie l’envoi à `SMTPClient`.
- `NotificationTemplateManager` charge les fichiers de `backend/services/notifications/templates` (extensibles / override possibles).
- `SMTPClient` encapsule `aiosmtplib` et la configuration SMTP des settings.

## Intégration FastAPI

- `backend/services/notifications/dependencies.py` fournit :
  - `get_template_manager`
  - `get_smtp_client`
  - `get_notification_service` (retourne l’implémentation email).
- `backend/services/auth/dependencies.py` fournit :
  - `get_link_builder`
  - `get_authentication_service`
  - `get_password_reset_manager`, `get_account_activation_manager`
  - `get_current_user` / `get_current_active_user`

Les endpoints de `backend/api/authentication.py` consomment ces dépendances via `Depends`. Les notifications sont déclenchées via les méthodes `notify_*` de `AuthenticationService`, ce qui garde les contrôleurs fins et le service en charge du contexte métier.

## Points d’extension

- **Canal de notification** : fournir une implémentation custom de `NotificationService` (SMS, push, webhook, etc.) et la brancher dans `get_notification_service`.
- **Templates** : changer le dossier de templates, brancher un moteur différent, internationaliser en ajoutant d’autres variantes.
- **Liens** : personnaliser `NotificationLinkBuilder` (multi-front, sous-domaines par environnement, paramètres additionnels).
- **JWT** : modifier `JWTRepository` (algorithme, claims supplémentaires) ou `TokenRepository` (stockage Redis, etc.).

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
