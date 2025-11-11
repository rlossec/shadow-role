from __future__ import annotations

from pathlib import Path
from string import Template
from typing import Any


class TemplateNotFoundError(LookupError):
    """Template introuvable."""


class NotificationTemplateManager:
    """Gestionnaire simple de templates texte/HTML pour les notifications."""

    def __init__(self, base_path: Path | str | None = None) -> None:
        default_path = Path(__file__).parent / "templates"
        self.base_path = Path(base_path) if base_path else default_path

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """Rendre un template en injectant un contexte via ``string.Template``."""
        path = self.base_path / template_name
        if not path.is_file():
            raise TemplateNotFoundError(f"Template '{template_name}' introuvable (base={self.base_path}).")

        template = Template(path.read_text(encoding="utf-8"))
        return template.safe_substitute(context)

