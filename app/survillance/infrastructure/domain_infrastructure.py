"""
Implementación de repositorios de dominio que usan mapeadores.
Adaptadores entre las interfaces de dominio y SQLAlchemy ORM.
"""
from typing import Optional, Sequence

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

# Importar modelos ORM
from app.survillance.domain.entities import (
    Oficina as OficinaORM,
    Conexion as ConexionORM,
    Clip as ClipORM,
    Usuario as UsuarioORM,
    Evento as EventoORM,
    Notificacion as NotificacionORM,
    Reporte as ReporteORM,
    InferenceRequest as InferenceRequestORM
)

# Importar entidades de dominio
from ..domain.entities.oficina import Oficina
from ..domain.entities.conexion import Conexion
from ..domain.entities.clip import Clip
from ..domain.entities.usuario import Usuario
from ..domain.entities.evento import Evento
from ..domain.entities.notificacion import Notificacion
from ..domain.entities.reporte import Reporte
from ..domain.entities.inference_request import InferenceRequest

# Importar value objects
from ..domain.value_objects.identifiers import (
    IdOficina, IdConexion, IdClip, IdUsuario,
    IdEvento, IdNotificacion, IdReporte, IdInferenceRequest
)
from ..domain.value_objects.timestamps import UtcDatetime

# Importar mapeadores
from ..domain import mappers


class OficinaRepository:
    """Adaptador de repositorio de oficinas usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdOficina) -> Optional[Oficina]:
        result = await self.session.execute(
            select(OficinaORM).where(OficinaORM.id_oficina == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.oficina_to_domain(orm) if orm else None
    
    async def list(self, limit: int = 50, offset: int = 0) -> Sequence[Oficina]:
        result = await self.session.execute(
            select(OficinaORM).limit(limit).offset(offset)
        )
        return [mappers.oficina_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, oficina: Oficina) -> Oficina:
        orm = mappers.oficina_to_orm(oficina)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.oficina_to_domain(orm)
    
    async def update(self, oficina: Oficina) -> Oficina:
        result = await self.session.execute(
            select(OficinaORM).where(OficinaORM.id_oficina == int(oficina.id))
        )
        existing_orm = result.scalar_one()
        orm = mappers.oficina_to_orm(oficina, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.oficina_to_domain(orm)
    
    async def delete(self, id: IdOficina) -> None:
        await self.session.execute(
            sql_delete(OficinaORM).where(OficinaORM.id_oficina == int(id))
        )


class ConexionRepository:
    """Adaptador de repositorio de conexiones usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdConexion) -> Optional[Conexion]:
        result = await self.session.execute(
            select(ConexionORM).where(ConexionORM.id_conexion == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.conexion_to_domain(orm) if orm else None
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_oficina: Optional[IdOficina] = None,
        habilitada: Optional[bool] = None
    ) -> Sequence[Conexion]:
        query = select(ConexionORM)
        
        if id_oficina is not None:
            query = query.where(ConexionORM.id_oficina == int(id_oficina))
        
        if habilitada is not None:
            query = query.where(ConexionORM.habilitada == habilitada)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [mappers.conexion_to_domain(orm) for orm in result.scalars().all()]
    
    async def list_enabled(self) -> Sequence[Conexion]:
        result = await self.session.execute(
            select(ConexionORM).where(ConexionORM.habilitada == True)
        )
        return [mappers.conexion_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, conexion: Conexion) -> Conexion:
        orm = mappers.conexion_to_orm(conexion)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.conexion_to_domain(orm)
    
    async def update(self, conexion: Conexion) -> Conexion:
        result = await self.session.execute(
            select(ConexionORM).where(ConexionORM.id_conexion == int(conexion.id))
        )
        existing_orm = result.scalar_one()
        orm = mappers.conexion_to_orm(conexion, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.conexion_to_domain(orm)
    
    async def delete(self, id: IdConexion) -> None:
        await self.session.execute(
            sql_delete(ConexionORM).where(ConexionORM.id_conexion == int(id))
        )


class ClipRepository:
    """Adaptador de repositorio de clips usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdClip) -> Optional[Clip]:
        result = await self.session.execute(
            select(ClipORM).where(ClipORM.id_clip == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.clip_to_domain(orm) if orm else None
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_conexion: Optional[IdConexion] = None,
        start_time: Optional[UtcDatetime] = None,
        end_time: Optional[UtcDatetime] = None
    ) -> Sequence[Clip]:
        query = select(ClipORM)
        
        if id_conexion is not None:
            query = query.where(ClipORM.id_conexion == int(id_conexion))
        
        if start_time is not None:
            query = query.where(ClipORM.start_time_utc >= start_time.to_datetime())
        
        if end_time is not None:
            query = query.where(ClipORM.start_time_utc <= end_time.to_datetime())
        
        query = query.order_by(ClipORM.start_time_utc.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [mappers.clip_to_domain(orm) for orm in result.scalars().all()]
    
    async def find_by_time_range(
        self,
        id_conexion: IdConexion,
        start_time: UtcDatetime,
        end_time: UtcDatetime
    ) -> Sequence[Clip]:
        result = await self.session.execute(
            select(ClipORM)
            .where(ClipORM.id_conexion == int(id_conexion))
            .where(ClipORM.start_time_utc < end_time.to_datetime())
            .order_by(ClipORM.start_time_utc)
        )
        return [mappers.clip_to_domain(orm) for orm in result.scalars().all()]
    
    async def find_old_clips(
        self,
        id_conexion: IdConexion,
        older_than: UtcDatetime
    ) -> Sequence[Clip]:
        result = await self.session.execute(
            select(ClipORM)
            .where(ClipORM.id_conexion == int(id_conexion))
            .where(ClipORM.fecha_guardado < older_than.to_datetime())
        )
        return [mappers.clip_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, clip: Clip) -> Clip:
        orm = mappers.clip_to_orm(clip)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.clip_to_domain(orm)
    
    async def delete(self, id: IdClip) -> None:
        await self.session.execute(
            sql_delete(ClipORM).where(ClipORM.id_clip == int(id))
        )


class UsuarioRepository:
    """Adaptador de repositorio de usuarios usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdUsuario) -> Optional[Usuario]:
        result = await self.session.execute(
            select(UsuarioORM).where(UsuarioORM.id_usuario == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.usuario_to_domain(orm) if orm else None
    
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        result = await self.session.execute(
            select(UsuarioORM).where(UsuarioORM.email == email)
        )
        orm = result.scalar_one_or_none()
        return mappers.usuario_to_domain(orm) if orm else None
    
    async def create(self, usuario: Usuario) -> Usuario:
        orm = mappers.usuario_to_orm(usuario)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.usuario_to_domain(orm)
    
    async def update(self, usuario: Usuario) -> Usuario:
        result = await self.session.execute(
            select(UsuarioORM).where(UsuarioORM.id_usuario == int(usuario.id))
        )
        existing_orm = result.scalar_one()
        orm = mappers.usuario_to_orm(usuario, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.usuario_to_domain(orm)


class EventoRepository:
    """Adaptador de repositorio de eventos usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdEvento) -> Optional[Evento]:
        result = await self.session.execute(
            select(EventoORM).where(EventoORM.id_evento == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.evento_to_domain(orm) if orm else None
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_conexion: Optional[IdConexion] = None,
        tipo_evento: Optional[str] = None,
        start_time: Optional[UtcDatetime] = None,
        end_time: Optional[UtcDatetime] = None
    ) -> Sequence[Evento]:
        query = select(EventoORM)
        
        if id_conexion is not None:
            query = query.where(EventoORM.id_conexion == int(id_conexion))
        
        if tipo_evento is not None:
            query = query.where(EventoORM.tipo_evento == tipo_evento)
        
        if start_time is not None:
            query = query.where(EventoORM.timestamp_evento >= start_time.to_datetime())
        
        if end_time is not None:
            query = query.where(EventoORM.timestamp_evento <= end_time.to_datetime())
        
        query = query.order_by(EventoORM.timestamp_evento.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [mappers.evento_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, evento: Evento) -> Evento:
        orm = mappers.evento_to_orm(evento)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.evento_to_domain(orm)
    
    async def update(self, evento: Evento) -> Evento:
        result = await self.session.execute(
            select(EventoORM).where(EventoORM.id_evento == int(evento.id))
        )
        existing_orm = result.scalar_one()
        orm = mappers.evento_to_orm(evento, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.evento_to_domain(orm)


class NotificacionRepository:
    """Adaptador de repositorio de notificaciones usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdNotificacion) -> Optional[Notificacion]:
        result = await self.session.execute(
            select(NotificacionORM).where(NotificacionORM.id_notificacion == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.notificacion_to_domain(orm) if orm else None
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_evento: Optional[IdEvento] = None
    ) -> Sequence[Notificacion]:
        query = select(NotificacionORM)
        
        if id_evento is not None:
            query = query.where(NotificacionORM.id_evento == int(id_evento))
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [mappers.notificacion_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, notificacion: Notificacion) -> Notificacion:
        orm = mappers.notificacion_to_orm(notificacion)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.notificacion_to_domain(orm)
    
    async def update(self, notificacion: Notificacion) -> Notificacion:
        result = await self.session.execute(
            select(NotificacionORM).where(NotificacionORM.id_notificacion == int(notificacion.id))
        )
        existing_orm = result.scalar_one()
        orm = mappers.notificacion_to_orm(notificacion, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.notificacion_to_domain(orm)


class ReporteRepository:
    """Adaptador de repositorio de reportes usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdReporte) -> Optional[Reporte]:
        result = await self.session.execute(
            select(ReporteORM).where(ReporteORM.id_reporte == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.reporte_to_domain(orm) if orm else None
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_usuario: Optional[IdUsuario] = None
    ) -> Sequence[Reporte]:
        query = select(ReporteORM)
        
        if id_usuario is not None:
            query = query.where(ReporteORM.id_usuario == int(id_usuario))
        
        query = query.order_by(ReporteORM.fecha_generacion.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [mappers.reporte_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, reporte: Reporte) -> Reporte:
        orm = mappers.reporte_to_orm(reporte)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.reporte_to_domain(orm)


class InferenceRequestRepository:
    """Adaptador de repositorio de inference requests usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: IdInferenceRequest) -> Optional[InferenceRequest]:
        result = await self.session.execute(
            select(InferenceRequestORM).where(InferenceRequestORM.id == int(id))
        )
        orm = result.scalar_one_or_none()
        return mappers.inference_request_to_domain(orm) if orm else None
    
    async def get_by_request_id(self, request_id: str) -> Optional[InferenceRequest]:
        result = await self.session.execute(
            select(InferenceRequestORM).where(InferenceRequestORM.request_id == request_id)
        )
        orm = result.scalar_one_or_none()
        return mappers.inference_request_to_domain(orm) if orm else None
    
    async def exists_by_request_id(self, request_id: str) -> bool:
        result = await self.session.execute(
            select(InferenceRequestORM).where(InferenceRequestORM.request_id == request_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def create(self, inference_request: InferenceRequest) -> InferenceRequest:
        orm = mappers.inference_request_to_orm(inference_request)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return mappers.inference_request_to_domain(orm)