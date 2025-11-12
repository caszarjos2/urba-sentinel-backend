"""
Entidad de dominio: Notificación (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ..enums import EstadoNotificacion


@dataclass
class Notificacion:
    """
    Entidad de dominio que representa una notificación de evento.
    """
    id_evento: int
    canal: str
    destinatario: str
    estado: EstadoNotificacion
    fecha_envio: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.canal or not self.canal.strip():
            raise ValueError("canal no puede estar vacío")
        
        if not self.destinatario or not self.destinatario.strip():
            raise ValueError("destinatario no puede estar vacío")
        
        # Si está enviada, debe tener fecha de envío
        if self.estado == EstadoNotificacion.ENVIADA and self.fecha_envio is None:
            raise ValueError("Una notificación enviada debe tener fecha_envio")
    
    def is_sent(self) -> bool:
        """Verifica si la notificación fue enviada"""
        return self.estado == EstadoNotificacion.ENVIADA
    
    def has_failed(self) -> bool:
        """Verifica si la notificación falló"""
        return self.estado == EstadoNotificacion.FALLIDA