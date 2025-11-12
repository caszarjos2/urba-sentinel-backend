"""
Entidad de dominio: InferenceRequest (control de idempotencia de webhooks).
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class InferenceRequest:
    """
    Entidad de dominio para control de idempotencia de webhooks de inferencia.
    Garantiza que un request_id solo se procese una vez.
    """
    request_id: str
    received_at: datetime
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validaciones de dominio"""
        if not self.request_id or not self.request_id.strip():
            raise ValueError("request_id no puede estar vacío")
        
        if len(self.request_id) > 64:
            raise ValueError("request_id no puede exceder 64 caracteres")
    
    def is_duplicate(self) -> bool:
        """
        Verifica si este request ya fue procesado.
        En la práctica, si la entidad existe en BD, es un duplicado.
        """
        return True  # Si existe la instancia, ya fue procesado