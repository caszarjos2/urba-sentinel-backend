"""
Entidad de dominio: Usuario (sin dependencias de infraestructura).
"""
from dataclasses import dataclass
from typing import Optional
import re
from datetime import datetime


@dataclass
class Usuario:
    """
    Entidad de dominio que representa un usuario del sistema.
    """
    nombre: str
    email: str
    password_hash: str
    apellido: Optional[str] = None
    rol: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    ultimo_login: Optional[datetime] = None
    id: Optional[int] = None

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