## Fichier

- `backend/services/notifications/interface.py` : contrat générique `NotificationService` (méthode `send` à base de templates).
- `backend/services/notifications/email_service.py` : implémentation SMTP du contrat générique.
- `backend/services/notifications/template_manager.py` : résout et rend les templates (texte / HTML).
- `backend/services/notifications/smtp_client.py` : client SMTP asynchrone.
- `backend/services/notifications/dependencies.py` : usine FastAPI pour les dépendances `NotificationService`, `SMTPClient`, `TemplateManager`.

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

## Intégration

- `backend/services/notifications/dependencies.py` fournit :
  - `get_template_manager`
  - `get_smtp_client`
  - `get_notification_service`

Les endpoints de `backend/api/authentication.py` consomment ces dépendances via `Depends`. Les notifications sont déclenchées via les méthodes `notify_*` de `AuthenticationService`, ce qui garde les contrôleurs fins et le service en charge du contexte métier.
