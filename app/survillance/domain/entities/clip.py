"""
Entidad de dominio: Clip (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.identifiers import IdClip, IdConexion
from ..value_objects.timestamps import UtcDatetime, DurationSeconds
from ..value_objects.media_paths import StoragePath


@dataclass
class Clip:
    """
    Entidad de dominio que representa un clip de video segmentado.
    Inmutable para garantizar consistencia.
    """
    id: Optional[IdClip] = None
    id_conexion: IdConexion
    storage_path: StoragePath
    start_time_utc: UtcDatetime
    duration_sec: DurationSeconds
    fecha_guardado: Optional[UtcDatetime]
    
    def __post_init__(self):
        """Validaciones de dominio"""
        # StoragePath y DurationSeconds ya validan en sus constructores
        pass
    
    def end_time_utc(self) -> UtcDatetime:
        """Calcula el tiempo final del clip"""
        from datetime import timedelta
        end = self.start_time_utc.value + timedelta(seconds=int(self.duration_sec))
        return UtcDatetime(end)
    
    def contains_timestamp(self, timestamp: UtcDatetime) -> bool:
        """Verifica si un timestamp está dentro del clip"""
        return (self.start_time_utc.value <= timestamp.value < 
                self.end_time_utc().value)