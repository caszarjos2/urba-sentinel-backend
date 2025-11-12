"""
Entidad de dominio: Clip (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

from ..value_objects.timestamps import DurationSeconds
from ..value_objects.media_paths import StoragePath


@dataclass
class Clip:
    """
    Entidad de dominio que representa un clip de video segmentado.
    """
    id_conexion: int
    storage_path: StoragePath
    start_time_utc: datetime
    duration_sec: DurationSeconds
    fecha_guardado: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones de dominio"""
        # StoragePath y DurationSeconds ya validan en sus constructores
        pass
    
    def end_time_utc(self) -> datetime:
        """Calcula el tiempo final del clip"""
        end = self.start_time_utc + timedelta(seconds=int(self.duration_sec))
        return end
    
    def contains_timestamp(self, timestamp: datetime) -> bool:
        """Verifica si un timestamp está dentro del clip"""
        return (self.start_time_utc <= timestamp < self.end_time_utc())