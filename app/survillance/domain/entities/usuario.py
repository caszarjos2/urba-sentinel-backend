"""
Entidad de dominio: Usuario (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional, Any
import re
from datetime import datetime

from ..value_objects.identifiers import IdUsuario
from ..value_objects.timestamps import UtcDatetime

@dataclass
class Usuario:
    """
    Entidad de dominio que representa un usuario del sistema.
    Inmutable para garantizar consistencia.
    """
    nombre: str
    apellido: Optional[str]
    email: str
    password_hash: str
    rol: Optional[str]
    fecha_creacion: Optional[datetime]
    id: Optional[IdUsuario] = None
    ultimo_login: Optional[datetime] = None

    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.nombre or not self.nombre.strip():
            raise ValueError("nombre no puede estar vacío")
        
        if len(self.nombre) > 100:
            raise ValueError("nombre no puede exceder 100 caracteres")
        
        if not self.email or not self.email.strip():
            raise ValueError("email no puede estar vacío")
        
        # Validación básica de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError(f"email inválido: {self.email}")
        
        if not self.password_hash or not self.password_hash.strip():
            raise ValueError("password_hash no puede estar vacío")
    
    def full_name(self) -> str:
        """Retorna el nombre completo"""
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre