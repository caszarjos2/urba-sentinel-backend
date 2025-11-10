"""
Entidad de dominio: EventSnapshot (snapshot/frame de un evento).
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.identifiers import IdEventSnapshot, IdEvento
from ..value_objects.timestamps import MilliSeconds
from ..value_objects.media_paths import SnapshotPath


@dataclass(frozen=True)
class EventSnapshot:
    """
    Entidad de dominio que representa un snapshot (imagen) de un evento.
    Captura un frame específico del video en el momento del evento.
    Inmutable para garantizar consistencia.
    """
    id: IdEventSnapshot
    id_evento: IdEvento
    ruta_imagen: SnapshotPath
    timestamp_rel_ms: MilliSeconds
    
    def __post_init__(self):
        """Validaciones de dominio"""
        # SnapshotPath y MilliSeconds ya validan en sus constructores
        pass
    
    def is_at_event_start(self, tolerance_ms: int = 100) -> bool:
        """
        Verifica si el snapshot está cerca del inicio del evento.
        
        Args:
            tolerance_ms: Tolerancia en milisegundos
        
        Returns:
            True si está dentro de la tolerancia del inicio
        """
        return int(self.timestamp_rel_ms) <= tolerance_ms