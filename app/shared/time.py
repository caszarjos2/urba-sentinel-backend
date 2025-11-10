"""
Utilidades para manejo de tiempo UTC.
"""
from datetime import datetime, timezone
from typing import Optional


def now_utc() -> datetime:
    """Retorna el datetime actual en UTC timezone-aware"""
    return datetime.now(timezone.utc)


def parse_utc(dt_str: str) -> datetime:
    """Parsea un string ISO8601 a datetime UTC"""
    dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    return dt.astimezone(timezone.utc)


def to_utc(dt: datetime) -> datetime:
    """Convierte un datetime a UTC si tiene timezone, sino asume UTC"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def filename_to_utc(filename: str) -> Optional[datetime]:
    """
    Convierte nombre de archivo tipo 'clip_20251106_153045.mp4' a datetime UTC.
    Formato esperado: clip_YYYYmmdd_HHMMSS.mp4
    """
    try:
        # Extraer la parte de fecha: clip_20251106_153045.mp4 -> 20251106_153045
        parts = filename.replace('.mp4', '').split('_')
        if len(parts) >= 3:
            date_part = parts[-2]  # YYYYmmdd
            time_part = parts[-1]  # HHMMSS
            dt_str = f"{date_part}{time_part}"
            dt = datetime.strptime(dt_str, "%Y%m%d%H%M%S")
            return dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    return None