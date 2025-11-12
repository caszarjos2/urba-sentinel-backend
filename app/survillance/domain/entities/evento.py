"""
Entidad de dominio: Evento (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ..value_objects.timestamps import DurationSeconds, MilliSeconds
from ..value_objects.media_paths import SubclipPath
from ..enums import TipoEvento


@dataclass
class Evento:
    """
    Entidad de dominio que representa un evento de seguridad detectado.
    """
    id_conexion: int
    tipo_evento: TipoEvento
    t_inicio_ms: MilliSeconds
    t_fin_ms: MilliSeconds
    timestamp_evento: datetime
    procesado: bool
    id_clip: Optional[int] = None
    id_usuario: Optional[int] = None
    confianza: Optional[float] = None
    subclip_path: Optional[SubclipPath] = None
    subclip_duracion_sec: Optional[DurationSeconds] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if self.confianza is not None:
            if not (0.0 <= self.confianza <= 1.0):
                raise ValueError(f"confianza debe estar entre 0.0 y 1.0, recibido: {self.confianza}")
        
        if int(self.t_inicio_ms) > int(self.t_fin_ms):
            raise ValueError(f"t_inicio_ms ({self.t_inicio_ms}) no puede ser mayor que t_fin_ms ({self.t_fin_ms})")
    
    def duracion_ms(self) -> MilliSeconds:
        """Calcula la duración del evento en milisegundos"""
        return MilliSeconds(int(self.t_fin_ms) - int(self.t_inicio_ms))
    
    def tiene_subclip(self) -> bool:
        """Verifica si el evento tiene un subclip generado"""
        return self.subclip_path is not None
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Verifica si el evento tiene alta confianza"""
        if self.confianza is None:
            return False
        return self.confianza >= threshold