from __future__ import annotations

from datetime import datetime, timezone


def normalize_datetime(value: datetime) -> datetime:
    """Ensure datetime is timezone-aware in UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
