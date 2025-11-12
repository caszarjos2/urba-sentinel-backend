"""
Implementación de repositorios de dominio que usan mapeadores.
Adaptadores entre las interfaces de dominio y SQLAlchemy ORM.
"""
from typing import Optional, Sequence, List
from datetime import datetime

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

# Importar modelos ORM
from app.survillance.models import (
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

# Importar mapeadores
from ..domain.mappers import (
    oficina_to_domain, oficina_to_orm,
    conexion_to_domain, conexion_to_orm,
    clip_to_domain, clip_to_orm,
    usuario_to_domain, usuario_to_orm,
    evento_to_domain, evento_to_orm,
    notificacion_to_domain, notificacion_to_orm,
    reporte_to_domain, reporte_to_orm,
    inference_request_to_domain, inference_request_to_orm
)


class OficinaRepository:
    """Adaptador de repositorio de oficinas usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Oficina]:
        """Obtiene una oficina por ID"""
        result = await self.session.execute(
            select(OficinaORM).where(OficinaORM.id_oficina == id)
        )
        orm = result.scalar_one_or_none()
        return oficina_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Oficina]:
        """Obtiene una oficina por ID (alias para servicios)"""
        return await self.get(id)
    
    async def list(self, limit: int = 50, offset: int = 0) -> Sequence[Oficina]:
        """Lista oficinas con paginación"""
        result = await self.session.execute(
            select(OficinaORM).limit(limit).offset(offset)
        )
        return [oficina_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Oficina]:
        """Lista todas las oficinas (alias para servicios)"""
        return list(await self.list(limit, offset))
    
    async def create(self, oficina: Oficina) -> Oficina:
        """Crea una nueva oficina"""
        orm = oficina_to_orm(oficina)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return oficina_to_domain(orm)
    
    async def update(self, oficina: Oficina) -> Oficina:
        """Actualiza una oficina existente"""
        if oficina.id is None:
            raise ValueError("No se puede actualizar una oficina sin ID")
        result = await self.session.execute(
            select(OficinaORM).where(OficinaORM.id_oficina == oficina.id)
        )
        existing_orm = result.scalar_one()
        orm = oficina_to_orm(oficina, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return oficina_to_domain(orm)
    
    async def delete(self, id: int) -> bool:
        """Elimina una oficina"""
        await self.session.execute(
            sql_delete(OficinaORM).where(OficinaORM.id_oficina == id)
        )
        return True


class ConexionRepository:
    """Adaptador de repositorio de conexiones usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Conexion]:
        """Obtiene una conexión por ID"""
        result = await self.session.execute(
            select(ConexionORM).where(ConexionORM.id_conexion == id)
        )
        orm = result.scalar_one_or_none()
        return conexion_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Conexion]:
        """Obtiene una conexión por ID (alias para servicios)"""
        return await self.get(id)
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_oficina: Optional[int] = None,
        habilitada: Optional[bool] = None
    ) -> Sequence[Conexion]:
        """Lista conexiones con filtros opcionales"""
        query = select(ConexionORM)
        
        if id_oficina is not None:
            query = query.where(ConexionORM.id_oficina == id_oficina)
        
        if habilitada is not None:
            query = query.where(ConexionORM.habilitada == habilitada)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [conexion_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_oficina: Optional[int] = None,
        habilitada: Optional[bool] = None
    ) -> List[Conexion]:
        """Lista todas las conexiones con filtros (alias para servicios)"""
        return list(await self.list(limit, offset, id_oficina, habilitada))
    
    async def list_enabled(self) -> Sequence[Conexion]:
        """Lista solo conexiones habilitadas"""
        result = await self.session.execute(
            select(ConexionORM).where(ConexionORM.habilitada == True)
        )
        return [conexion_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, conexion: Conexion) -> Conexion:
        """Crea una nueva conexión"""
        orm = conexion_to_orm(conexion)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return conexion_to_domain(orm)
    
    async def update(self, conexion: Conexion) -> Conexion:
        """Actualiza una conexión existente"""
        if conexion.id is None:
            raise ValueError("No se puede actualizar una conexión sin ID")
        result = await self.session.execute(
            select(ConexionORM).where(ConexionORM.id_conexion == conexion.id)
        )
        existing_orm = result.scalar_one()
        orm = conexion_to_orm(conexion, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return conexion_to_domain(orm)
    
    async def delete(self, id: int) -> bool:
        """Elimina una conexión"""
        await self.session.execute(
            sql_delete(ConexionORM).where(ConexionORM.id_conexion == id)
        )
        return True


class ClipRepository:
    """Adaptador de repositorio de clips usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Clip]:
        """Obtiene un clip por ID"""
        result = await self.session.execute(
            select(ClipORM).where(ClipORM.id_clip == id)
        )
        orm = result.scalar_one_or_none()
        return clip_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Clip]:
        """Obtiene un clip por ID (alias para servicios)"""
        return await self.get(id)
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_conexion: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Sequence[Clip]:
        """Lista clips con filtros opcionales"""
        query = select(ClipORM)
        
        if id_conexion is not None:
            query = query.where(ClipORM.id_conexion == id_conexion)
        
        if start_time is not None:
            query = query.where(ClipORM.start_time_utc >= start_time)
        
        if end_time is not None:
            query = query.where(ClipORM.start_time_utc <= end_time)
        
        query = query.order_by(ClipORM.start_time_utc.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [clip_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_conexion: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Clip]:
        """Lista todos los clips con filtros (alias para servicios)"""
        return list(await self.list(limit, offset, id_conexion, start_time, end_time))
    
    async def find_by_time_range(
        self,
        id_conexion: int,
        start_time: datetime,
        end_time: datetime
    ) -> Sequence[Clip]:
        """Encuentra clips que intersectan con un rango de tiempo"""
        result = await self.session.execute(
            select(ClipORM)
            .where(ClipORM.id_conexion == id_conexion)
            .where(ClipORM.start_time_utc < end_time)
            .order_by(ClipORM.start_time_utc)
        )
        return [clip_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_by_time_range(
        self,
        id_conexion: int,
        start_time: datetime,
        end_time: datetime
    ) -> List[Clip]:
        """Alias para servicios"""
        return list(await self.find_by_time_range(id_conexion, start_time, end_time))
    
    async def find_old_clips(
        self,
        id_conexion: int,
        older_than: datetime
    ) -> Sequence[Clip]:
        """Encuentra clips más antiguos que una fecha"""
        result = await self.session.execute(
            select(ClipORM)
            .where(ClipORM.id_conexion == id_conexion)
            .where(ClipORM.fecha_guardado < older_than)
        )
        return [clip_to_domain(orm) for orm in result.scalars().all()]
    
    async def create(self, clip: Clip) -> Clip:
        """Crea un nuevo clip"""
        orm = clip_to_orm(clip)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return clip_to_domain(orm)
    
    async def delete(self, id: int) -> None:
        """Elimina un clip"""
        await self.session.execute(
            sql_delete(ClipORM).where(ClipORM.id_clip == id)
        )


class UsuarioRepository:
    """Adaptador de repositorio de usuarios usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID"""
        result = await self.session.execute(
            select(UsuarioORM).where(UsuarioORM.id_usuario == id)
        )
        orm = result.scalar_one_or_none()
        return usuario_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID (alias para servicios)"""
        return await self.get(id)
    
    async def get_by_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por email"""
        result = await self.session.execute(
            select(UsuarioORM).where(UsuarioORM.email == email)
        )
        orm = result.scalar_one_or_none()
        return usuario_to_domain(orm) if orm else None
    
    async def create(self, usuario: Usuario) -> Usuario:
        """Crea un nuevo usuario"""
        orm = usuario_to_orm(usuario)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return usuario_to_domain(orm)
    
    async def update(self, usuario: Usuario) -> Usuario:
        """Actualiza un usuario existente"""
        if usuario.id is None:
            raise ValueError("No se puede actualizar un usuario sin ID")
        result = await self.session.execute(
            select(UsuarioORM).where(UsuarioORM.id_usuario == usuario.id)
        )
        existing_orm = result.scalar_one()
        orm = usuario_to_orm(usuario, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return usuario_to_domain(orm)


class EventoRepository:
    """Adaptador de repositorio de eventos usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Evento]:
        """Obtiene un evento por ID"""
        result = await self.session.execute(
            select(EventoORM).where(EventoORM.id_evento == id)
        )
        orm = result.scalar_one_or_none()
        return evento_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Evento]:
        """Obtiene un evento por ID (alias para servicios)"""
        return await self.get(id)
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_conexion: Optional[int] = None,
        tipo_evento: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Sequence[Evento]:
        """Lista eventos con filtros opcionales"""
        query = select(EventoORM)
        
        if id_conexion is not None:
            query = query.where(EventoORM.id_conexion == id_conexion)
        
        if tipo_evento is not None:
            query = query.where(EventoORM.tipo_evento == tipo_evento)
        
        if start_time is not None:
            query = query.where(EventoORM.timestamp_evento >= start_time)
        
        if end_time is not None:
            query = query.where(EventoORM.timestamp_evento <= end_time)
        
        query = query.order_by(EventoORM.timestamp_evento.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [evento_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_conexion: Optional[int] = None,
        tipo_evento: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Evento]:
        """Lista todos los eventos con filtros (alias para servicios)"""
        return list(await self.list(limit, offset, id_conexion, tipo_evento, start_time, end_time))
    
    async def create(self, evento: Evento) -> Evento:
        """Crea un nuevo evento"""
        orm = evento_to_orm(evento)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return evento_to_domain(orm)
    
    async def update(self, evento: Evento) -> Evento:
        """Actualiza un evento existente"""
        if evento.id is None:
            raise ValueError("No se puede actualizar un evento sin ID")
        result = await self.session.execute(
            select(EventoORM).where(EventoORM.id_evento == evento.id)
        )
        existing_orm = result.scalar_one()
        orm = evento_to_orm(evento, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return evento_to_domain(orm)


class NotificacionRepository:
    """Adaptador de repositorio de notificaciones usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Notificacion]:
        """Obtiene una notificación por ID"""
        result = await self.session.execute(
            select(NotificacionORM).where(NotificacionORM.id_notificacion == id)
        )
        orm = result.scalar_one_or_none()
        return notificacion_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Notificacion]:
        """Obtiene una notificación por ID (alias para servicios)"""
        return await self.get(id)
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_evento: Optional[int] = None
    ) -> Sequence[Notificacion]:
        """Lista notificaciones con filtros opcionales"""
        query = select(NotificacionORM)
        
        if id_evento is not None:
            query = query.where(NotificacionORM.id_evento == id_evento)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [notificacion_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_evento: Optional[int] = None
    ) -> List[Notificacion]:
        """Lista todas las notificaciones con filtros (alias para servicios)"""
        return list(await self.list(limit, offset, id_evento))
    
    async def create(self, notificacion: Notificacion) -> Notificacion:
        """Crea una nueva notificación"""
        orm = notificacion_to_orm(notificacion)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return notificacion_to_domain(orm)
    
    async def update(self, notificacion: Notificacion) -> Notificacion:
        """Actualiza una notificación existente"""
        if notificacion.id is None:
            raise ValueError("No se puede actualizar una notificación sin ID")
        result = await self.session.execute(
            select(NotificacionORM).where(NotificacionORM.id_notificacion == notificacion.id)
        )
        existing_orm = result.scalar_one()
        orm = notificacion_to_orm(notificacion, existing_orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return notificacion_to_domain(orm)


class ReporteRepository:
    """Adaptador de repositorio de reportes usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[Reporte]:
        """Obtiene un reporte por ID"""
        result = await self.session.execute(
            select(ReporteORM).where(ReporteORM.id_reporte == id)
        )
        orm = result.scalar_one_or_none()
        return reporte_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[Reporte]:
        """Obtiene un reporte por ID (alias para servicios)"""
        return await self.get(id)
    
    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
        id_usuario: Optional[int] = None
    ) -> Sequence[Reporte]:
        """Lista reportes con filtros opcionales"""
        query = select(ReporteORM)
        
        if id_usuario is not None:
            query = query.where(ReporteORM.id_usuario == id_usuario)
        
        query = query.order_by(ReporteORM.fecha_generacion.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return [reporte_to_domain(orm) for orm in result.scalars().all()]
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_usuario: Optional[int] = None
    ) -> List[Reporte]:
        """Lista todos los reportes con filtros (alias para servicios)"""
        return list(await self.list(limit, offset, id_usuario))
    
    async def create(self, reporte: Reporte) -> Reporte:
        """Crea un nuevo reporte"""
        orm = reporte_to_orm(reporte)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return reporte_to_domain(orm)


class InferenceRequestRepository:
    """Adaptador de repositorio de inference requests usando entidades de dominio"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: int) -> Optional[InferenceRequest]:
        """Obtiene un inference request por ID"""
        result = await self.session.execute(
            select(InferenceRequestORM).where(InferenceRequestORM.id == id)
        )
        orm = result.scalar_one_or_none()
        return inference_request_to_domain(orm) if orm else None
    
    async def get_by_id(self, id: int) -> Optional[InferenceRequest]:
        """Obtiene un inference request por ID (alias para servicios)"""
        return await self.get(id)
    
    async def get_by_request_id(self, request_id: str) -> Optional[InferenceRequest]:
        """Obtiene un inference request por request_id único"""
        result = await self.session.execute(
            select(InferenceRequestORM).where(InferenceRequestORM.request_id == request_id)
        )
        orm = result.scalar_one_or_none()
        return inference_request_to_domain(orm) if orm else None
    
    async def exists_by_request_id(self, request_id: str) -> bool:
        """Verifica si un request_id ya existe (idempotencia)"""
        result = await self.session.execute(
            select(InferenceRequestORM).where(InferenceRequestORM.request_id == request_id)
        )
        return result.scalar_one_or_none() is not None
    
    async def create(self, inference_request: InferenceRequest) -> InferenceRequest:
        """Crea un nuevo inference request"""
        orm = inference_request_to_orm(inference_request)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return inference_request_to_domain(orm)
