
import logging
import sys
from typing import Optional

from core.config import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
) -> None:

    # Déterminer le niveau de log
    if level is None:
        log_level = logging.WARNING if settings.DEBUG else logging.INFO
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)

    # Format par défaut des logs
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # Configuration du root logger
    logging.basicConfig(
        level=log_level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True,
    )

    # Réduire le verbosité des bibliothèques tierces
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("socketio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# Initialisation automatique du logging au chargement du module
setup_logging()

