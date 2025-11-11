"""
Entidad de dominio: Reporte (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.identifiers import IdReporte, IdUsuario, IdClip
from ..value_objects.timestamps import UtcDatetime


@dataclass
class Reporte:
    """
    Entidad de dominio que representa un reporte generado por usuario.
    Inmutable para garantizar consistencia.
    """
    id: Optional[IdReporte] = None
    id_usuario: IdUsuario
    id_clip: IdClip
    titulo: str
    descripcion: Optional[str]
    rango_fecha_inicio: Optional[UtcDatetime]
    rango_fecha_fin: Optional[UtcDatetime]
    filtro_confianza: Optional[float]
    tipo_evento: Optional[str]
    fecha_generacion: Optional[UtcDatetime]
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.titulo or not self.titulo.strip():
            raise ValueError("titulo no puede estar vacío")
        
        if len(self.titulo) > 200:
            raise ValueError("titulo no puede exceder 200 caracteres")
        
        if self.filtro_confianza is not None:
            if not (0.0 <= self.filtro_confianza <= 1.0):
                raise ValueError(f"filtro_confianza debe estar entre 0.0 y 1.0, recibido: {self.filtro_confianza}")
        
        # Validar que fecha_inicio < fecha_fin si ambas existen
        if (self.rango_fecha_inicio and self.rango_fecha_fin and 
            self.rango_fecha_inicio.value >= self.rango_fecha_fin.value):
            raise ValueError("rango_fecha_inicio debe ser anterior a rango_fecha_fin")
    
    def has_date_range(self) -> bool:
        """Verifica si el reporte tiene un rango de fechas"""
        return self.rango_fecha_inicio is not None and self.rango_fecha_fin is not None