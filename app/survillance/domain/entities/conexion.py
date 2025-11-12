"""
Entidad de dominio: Conexión/Cámara (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from ..enums import ModoIngesta


@dataclass
class Conexion:
    """
    Entidad de dominio que representa una cámara RTSP.
    """
    id_oficina: int
    nombre_camara: str
    rtsp_url: str
    modo_ingesta: ModoIngesta
    habilitada: bool
    retention_minutes: int
    ubicacion: Optional[str] = None
    estado: Optional[str] = None
    ultimo_ping: Optional[datetime] = None
    fps_sample: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.nombre_camara or not self.nombre_camara.strip():
            raise ValueError("nombre_camara no puede estar vacío")
        
        if len(self.nombre_camara) > 120:
            raise ValueError("nombre_camara no puede exceder 120 caracteres")
        
        if not self.rtsp_url or not self.rtsp_url.strip():
            raise ValueError("rtsp_url no puede estar vacío")
        
        if not self.rtsp_url.startswith(('rtsp://', 'rtmp://')):
            raise ValueError("rtsp_url debe comenzar con rtsp:// o rtmp://")
        
        if self.retention_minutes < 0:
            raise ValueError("retention_minutes debe ser >= 0")
        
        if self.fps_sample is not None and self.fps_sample <= 0:
            raise ValueError("fps_sample debe ser > 0 si se especifica")
    
    def is_active(self) -> bool:
        """Verifica si la cámara está activa"""
        return self.habilitada and self.estado == "activa"