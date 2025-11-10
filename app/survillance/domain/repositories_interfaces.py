"""
Interfaces de repositorios de dominio usando typing.Protocol.
Define contratos sin acoplar a implementación específica.
"""
from typing import Protocol, Sequence, Optional

from .entities.oficina import Oficina
from .entities.conexion import Conexion
from .entities.clip import Clip
from .entities.usuario import Usuario
from .entities.evento import Evento
from .entities.notificacion import Notificacion
from .entities.reporte import Reporte
from .entities.inference_request import InferenceRequest
from .entities.event_snapshot import EventSnapshot

from .value_objects.identifiers import (
    IdOficina, IdConexion, IdClip, IdUsuario,
    IdEvento, IdNotificacion, IdReporte,
    IdInferenceRequest, IdEventSnapshot
)
from .value_objects.timestamps import UtcDatetime


class IOficinaRepository(Protocol):
    """Repositorio de oficinas"""
    
    async def get(self, id: IdOficina) -> Optional[Oficina]:
        """Obtiene una oficina por ID"""
        ...
    
    async def list(self, limit: int = 50, offset: int = 0) -> Sequence[Oficina]:
        """Lista oficinas con paginación"""
        ...
    
    async def create(self, oficina: Oficina) -> Oficina:
        """Crea una nueva oficina"""
        ...
    
    async def update(self, oficina: Oficina) -> Oficina:
        """Actualiza una oficina existente"""
        ...
    
    async def delete(self, id: IdOficina) -> None:
        """Elimina una oficina"""
        ...


class IConexionRepository(Protocol):
    """Repositorio de conexiones/cámaras"""
    
    async def get(self, id: IdConexion) -> Optional[Conexion]:
        """Obtiene una conexión por ID"""
        ...
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_oficina: Optional[IdOficina] = None,
        habilitada: Optional[bool] = None
    ) -> Sequence[Conexion]:
        """Lista conexiones con filtros opcionales"""
        ...
    
    async def list_enabled(self) -> Sequence[Conexion]:
        """Lista solo conexiones habilitadas"""
        ...
    
    async def create(self, conexion: Conexion) -> Conexion:
        """Crea una nueva conexión"""
        ...
    
    async def update(self, conexion: Conexion) -> Conexion:
        """Actualiza una conexión existente"""
        ...
    
    async def delete(self, id: IdConexion) -> None:
        """Elimina una conexión"""
        ...


class IClipRepository(Protocol):
    """Repositorio de clips"""
    
    async def get(self, id: IdClip) -> Optional[Clip]:
        """Obtiene un clip por ID"""
        ...
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_conexion: Optional[IdConexion] = None,
        start_time: Optional[UtcDatetime] = None,
        end_time: Optional[UtcDatetime] = None
    ) -> Sequence[Clip]:
        """Lista clips con filtros opcionales"""
        ...
    
    async def find_by_time_range(
        self,
        id_conexion: IdConexion,
        start_time: UtcDatetime,
        end_time: UtcDatetime
    ) -> Sequence[Clip]:
        """Encuentra clips que intersectan con un rango de tiempo"""
        ...
    
    async def find_old_clips(
        self,
        id_conexion: IdConexion,
        older_than: UtcDatetime
    ) -> Sequence[Clip]:
        """Encuentra clips más antiguos que una fecha"""
        ...
    
    async def create(self, clip: Clip) -> Clip:
        """Crea un nuevo clip"""
        ...
    
    async def delete(self, id: IdClip) -> None:
        """Elimina un clip"""
        ...


class IUsuarioRepository(Protocol):
    """Repositorio de usuarios"""
    
    async def get(self, id: IdUsuario) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        ...
    
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email"""
        ...
    
    async def create(self, usuario: Usuario) -> Usuario:
        """Crea un nuevo usuario"""
        ...
    
    async def update(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario existente"""
        ...


class IEventoRepository(Protocol):
    """Repositorio de eventos"""
    
    async def get(self, id: IdEvento) -> Optional[Evento]:
        """Obtiene un evento por ID"""
        ...
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_conexion: Optional[IdConexion] = None,
        tipo_evento: Optional[str] = None,
        start_time: Optional[UtcDatetime] = None,
        end_time: Optional[UtcDatetime] = None
    ) -> Sequence[Evento]:
        """Lista eventos con filtros opcionales"""
        ...
    
    async def create(self, evento: Evento) -> Evento:
        """Crea un nuevo evento"""
        ...
    
    async def update(self, evento: Evento) -> Evento:
        """Actualiza un evento existente"""
        ...


class INotificacionRepository(Protocol):
    """Repositorio de notificaciones"""
    
    async def get(self, id: IdNotificacion) -> Optional[Notificacion]:
        """Obtiene una notificación por ID"""
        ...
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_evento: Optional[IdEvento] = None
    ) -> Sequence[Notificacion]:
        """Lista notificaciones con filtros opcionales"""
        ...
    
    async def create(self, notificacion: Notificacion) -> Notificacion:
        """Crea una nueva notificación"""
        ...
    
    async def update(self, notificacion: Notificacion) -> Notificacion:
        """Actualiza una notificación existente"""
        ...


class IReporteRepository(Protocol):
    """Repositorio de reportes"""
    
    async def get(self, id: IdReporte) -> Optional[Reporte]:
        """Obtiene un reporte por ID"""
        ...
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_usuario: Optional[IdUsuario] = None
    ) -> Sequence[Reporte]:
        """Lista reportes con filtros opcionales"""
        ...
    
    async def create(self, reporte: Reporte) -> Reporte:
        """Crea un nuevo reporte"""
        ...


class IInferenceRequestRepository(Protocol):
    """Repositorio de inference requests (idempotencia)"""
    
    async def get(self, id: IdInferenceRequest) -> Optional["InferenceRequest"]:
        """Obtiene un inference request por ID"""
        ...
    
    async def get_by_request_id(self, request_id: str) -> Optional["InferenceRequest"]:
        """Obtiene un inference request por request_id único"""
        ...
    
    async def exists_by_request_id(self, request_id: str) -> bool:
        """Verifica si un request_id ya existe (idempotencia)"""
        ...
    
    async def create(self, inference_request: "InferenceRequest") -> "InferenceRequest":
        """Crea un nuevo inference request"""
        ...


class IEventSnapshotRepository(Protocol):
    """Repositorio de event snapshots"""
    
    async def get(self, id: "IdEventSnapshot") -> Optional["EventSnapshot"]:
        """Obtiene un snapshot por ID"""
        ...
    
    async def list_by_event(
        self,
        id_evento: IdEvento,
        limit: int = 50,
        offset: int = 0
    ) -> Sequence["EventSnapshot"]:
        """Lista snapshots de un evento específico"""
        ...
    
    async def create(self, snapshot: "EventSnapshot") -> "EventSnapshot":
        """Crea un nuevo snapshot"""
        ...
    
    async def delete(self, id: "IdEventSnapshot") -> None:
        """Elimina un snapshot"""
        ...