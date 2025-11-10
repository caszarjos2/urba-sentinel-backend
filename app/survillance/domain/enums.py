"""
Enums del dominio: tipos de evento, modos de ingesta, estados.
"""
from enum import Enum


class TipoEvento(str, Enum):
    """Tipos de eventos de seguridad detectables"""
    FORCEJEO = "forcejeo"
    PATADA = "patada"
    GOLPE = "golpe"


class ModoIngesta(str, Enum):
    """Modos de ingesta de video"""
    WEBHOOK_ONLY = "WEBHOOK_ONLY"
    PUSH = "PUSH"
    SEGMENT = "SEGMENT"


class EstadoConexion(str, Enum):
    """Estados posibles de una conexión"""
    ACTIVA = "activa"
    INACTIVA = "inactiva"
    ERROR = "error"


class EstadoNotificacion(str, Enum):
    """Estados de notificación"""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    FALLIDA = "fallida"