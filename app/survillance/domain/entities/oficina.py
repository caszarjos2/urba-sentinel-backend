"""
Entidad de dominio: Oficina (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional

from ..value_objects.identifiers import IdOficina
from ..value_objects.timestamps import UtcDatetime


@dataclass
class Oficina:
    """
    Entidad de dominio que representa una oficina física.
    Inmutable para garantizar consistencia.
    """
    id: Optional[IdOficina] = None
    nombre_oficina: str
    direccion: Optional[str]
    ciudad: Optional[str]
    responsable: Optional[str]
    telefono_contacto: Optional[str]
    fecha_registro: Optional[UtcDatetime]
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.nombre_oficina or not self.nombre_oficina.strip():
            raise ValueError("nombre_oficina no puede estar vacío")
        
        if len(self.nombre_oficina) > 150:
            raise ValueError("nombre_oficina no puede exceder 150 caracteres")