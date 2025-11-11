"""
Mapeadores entre entidades de dominio y modelos ORM.
Traduce entre la capa de dominio pura y la capa de infraestructura.
"""
from typing import Optional
from decimal import Decimal

# Importar modelos ORM (ajustar path según estructura real)
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
from .entities.oficina import Oficina
from .entities.conexion import Conexion
from .entities.clip import Clip
from .entities.usuario import Usuario
from .entities.evento import Evento
from .entities.notificacion import Notificacion
from .entities.reporte import Reporte
from .entities.inference_request import InferenceRequest
from ...shared.time import _as_dt_utc

# Importar value objects
from .value_objects.identifiers import (
    IdOficina, IdConexion, IdClip, IdUsuario,
    IdEvento, IdNotificacion, IdReporte, IdInferenceRequest
)
from .value_objects.timestamps import UtcDatetime, DurationSeconds, MilliSeconds
from .value_objects.media_paths import StoragePath, SubclipPath

# Importar enums
from .enums import TipoEvento, ModoIngesta, EstadoNotificacion


# ============ OFICINA ============

def oficina_to_domain(orm: OficinaORM) -> Oficina:
    """Convierte modelo ORM a entidad de dominio"""
    return Oficina(
        id=IdOficina(orm.id_oficina),
        nombre_oficina=orm.nombre_oficina,
        direccion=orm.direccion,
        ciudad=orm.ciudad,
        responsable=orm.responsable,
        telefono_contacto=orm.telefono_contacto,
        fecha_registro=UtcDatetime(orm.fecha_registro) if orm.fecha_registro else None
    )


def oficina_to_orm(entity: Oficina, existing: Optional[OficinaORM] = None) -> OficinaORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or OficinaORM()
    
    orm.id_oficina = int(entity.id)
    orm.nombre_oficina = entity.nombre_oficina
    orm.direccion = entity.direccion
    orm.ciudad = entity.ciudad
    orm.responsable = entity.responsable
    orm.telefono_contacto = entity.telefono_contacto
    if entity.fecha_registro:
        orm.fecha_registro = entity.fecha_registro.to_datetime()
    
    return orm


# ============ CONEXION ============

def conexion_to_domain(orm: ConexionORM) -> Conexion:
    """Convierte modelo ORM a entidad de dominio"""
    return Conexion(
        id=IdConexion(orm.id_conexion),
        id_oficina=IdOficina(orm.id_oficina),
        nombre_camara=orm.nombre_camara,
        ubicacion=orm.ubicacion,
        rtsp_url=orm.rtsp_url,
        estado=orm.estado,
        ultimo_ping=UtcDatetime(orm.ultimo_ping) if orm.ultimo_ping else None,
        modo_ingesta=ModoIngesta(orm.modo_ingesta),
        fps_sample=orm.fps_sample,
        habilitada=orm.habilitada,
        retention_minutes=orm.retention_minutes,
        created_at=UtcDatetime(orm.created_at) if orm.created_at else None,
        updated_at=UtcDatetime(orm.updated_at) if orm.updated_at else None
    )


def conexion_to_orm(entity: Conexion, existing: Optional[ConexionORM] = None) -> ConexionORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or ConexionORM()
    
    orm.id_conexion = int(entity.id)
    orm.id_oficina = int(entity.id_oficina)
    orm.nombre_camara = entity.nombre_camara
    orm.ubicacion = entity.ubicacion
    orm.rtsp_url = entity.rtsp_url
    orm.estado = entity.estado
    if entity.ultimo_ping:
        orm.ultimo_ping = entity.ultimo_ping.to_datetime()
    orm.modo_ingesta = entity.modo_ingesta.value
    orm.fps_sample = entity.fps_sample
    orm.habilitada = entity.habilitada
    orm.retention_minutes = entity.retention_minutes
    if entity.created_at:
        orm.created_at = entity.created_at.to_datetime()
    if entity.updated_at:
        orm.updated_at = entity.updated_at.to_datetime()
    
    return orm


# ============ CLIP ============

def clip_to_domain(orm: ClipORM) -> Clip:
    """Convierte modelo ORM a entidad de dominio"""
    return Clip(
        id=IdClip(orm.id_clip),
        id_conexion=IdConexion(orm.id_conexion),
        storage_path=StoragePath(orm.storage_path),
        start_time_utc=UtcDatetime(orm.start_time_utc),
        duration_sec=DurationSeconds(orm.duration_sec),
        fecha_guardado=UtcDatetime(orm.fecha_guardado) if orm.fecha_guardado else None
    )


def clip_to_orm(entity: Clip, existing: Optional[ClipORM] = None) -> ClipORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or ClipORM()
    
    orm.id_clip = int(entity.id)
    orm.id_conexion = int(entity.id_conexion)
    orm.storage_path = str(entity.storage_path)
    orm.start_time_utc = entity.start_time_utc.to_datetime()
    orm.duration_sec = int(entity.duration_sec)
    if entity.fecha_guardado:
        orm.fecha_guardado = entity.fecha_guardado.to_datetime()
    
    return orm


# ============ USUARIO ============

def usuario_to_domain(orm: UsuarioORM) -> Usuario:
    """Convierte modelo ORM a entidad de dominio"""
    return Usuario(
        id=IdUsuario(orm.id_usuario),
        nombre=orm.nombre,
        apellido=orm.apellido,
        email=orm.email,
        password_hash=orm.password_hash,
        rol=orm.rol,
        fecha_creacion=UtcDatetime(orm.fecha_creacion) if orm.fecha_creacion else None,
        ultimo_login=UtcDatetime(orm.ultimo_login) if orm.ultimo_login else None
    )


def usuario_to_orm(entity: Usuario, existing: Optional[UsuarioORM] = None) -> UsuarioORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or UsuarioORM()
    
    orm.nombre = entity.nombre
    orm.apellido = entity.apellido
    orm.email = entity.email
    orm.password_hash = entity.password_hash
    orm.rol = entity.rol
    if entity.fecha_creacion:
        orm.fecha_creacion = _as_dt_utc(entity.fecha_creacion)
    if entity.ultimo_login:
        orm.ultimo_login = _as_dt_utc(entity.ultimo_login)
    
    return orm


# ============ EVENTO ============

def evento_to_domain(orm: EventoORM) -> Evento:
    """Convierte modelo ORM a entidad de dominio"""
    return Evento(
        id=IdEvento(orm.id_evento),
        id_conexion=IdConexion(orm.id_conexion),
        id_clip=IdClip(orm.id_clip) if orm.id_clip else None,
        id_usuario=IdUsuario(orm.id_usuario) if orm.id_usuario else None,
        tipo_evento=TipoEvento(orm.tipo_evento),
        confianza=float(orm.confianza) if orm.confianza else None,
        t_inicio_ms=MilliSeconds(orm.t_inicio_ms) if orm.t_inicio_ms is not None else MilliSeconds(0),
        t_fin_ms=MilliSeconds(orm.t_fin_ms) if orm.t_fin_ms is not None else MilliSeconds(0),
        timestamp_evento=UtcDatetime(orm.timestamp_evento),
        procesado=orm.procesado,
        subclip_path=SubclipPath(orm.subclip_path) if orm.subclip_path else None,
        subclip_duracion_sec=DurationSeconds(orm.subclip_duracion_sec) if orm.subclip_duracion_sec is not None else None
    )


def evento_to_orm(entity: Evento, existing: Optional[EventoORM] = None) -> EventoORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or EventoORM()
    
    orm.id_evento = int(entity.id)
    orm.id_conexion = int(entity.id_conexion)
    orm.id_clip = int(entity.id_clip) if entity.id_clip else None
    orm.id_usuario = int(entity.id_usuario) if entity.id_usuario else None
    orm.tipo_evento = entity.tipo_evento.value
    orm.confianza = Decimal(str(entity.confianza)) if entity.confianza is not None else None
    orm.t_inicio_ms = int(entity.t_inicio_ms)
    orm.t_fin_ms = int(entity.t_fin_ms)
    orm.timestamp_evento = entity.timestamp_evento.to_datetime()
    orm.procesado = entity.procesado
    orm.subclip_path = str(entity.subclip_path) if entity.subclip_path else None
    orm.subclip_duracion_sec = int(entity.subclip_duracion_sec) if entity.subclip_duracion_sec else None
    
    return orm


# ============ NOTIFICACION ============

def notificacion_to_domain(orm: NotificacionORM) -> Notificacion:
    """Convierte modelo ORM a entidad de dominio"""
    return Notificacion(
        id=IdNotificacion(orm.id_notificacion),
        id_evento=IdEvento(orm.id_evento),
        canal=orm.canal or "",
        destinatario=orm.destinatario or "",
        estado=EstadoNotificacion(orm.estado),
        fecha_envio=UtcDatetime(orm.fecha_envio) if orm.fecha_envio else None
    )


def notificacion_to_orm(entity: Notificacion, existing: Optional[NotificacionORM] = None) -> NotificacionORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or NotificacionORM()
    
    orm.id_notificacion = int(entity.id)
    orm.id_evento = int(entity.id_evento)
    orm.canal = entity.canal
    orm.destinatario = entity.destinatario
    orm.estado = entity.estado.value
    if entity.fecha_envio:
        orm.fecha_envio = entity.fecha_envio.to_datetime()
    
    return orm


# ============ REPORTE ============

def reporte_to_domain(orm: ReporteORM) -> Reporte:
    """Convierte modelo ORM a entidad de dominio"""
    return Reporte(
        id=IdReporte(orm.id_reporte),
        id_usuario=IdUsuario(orm.id_usuario),
        id_clip=IdClip(orm.id_clip) if orm.id_clip else IdClip(0),  # Temporal
        titulo=orm.titulo or "",
        descripcion=orm.descripcion,
        rango_fecha_inicio=UtcDatetime(orm.rango_fecha_inicio) if orm.rango_fecha_inicio else None,
        rango_fecha_fin=UtcDatetime(orm.rango_fecha_fin) if orm.rango_fecha_fin else None,
        filtro_confianza=float(orm.filtro_confianza) if orm.filtro_confianza else None,
        tipo_evento=orm.tipo_evento,
        fecha_generacion=UtcDatetime(orm.fecha_generacion) if orm.fecha_generacion else None
    )


def reporte_to_orm(entity: Reporte, existing: Optional[ReporteORM] = None) -> ReporteORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or ReporteORM()
    
    orm.id_reporte = int(entity.id)
    orm.id_usuario = int(entity.id_usuario)
    orm.id_clip = int(entity.id_clip)
    orm.titulo = entity.titulo
    orm.descripcion = entity.descripcion
    if entity.rango_fecha_inicio:
        orm.rango_fecha_inicio = entity.rango_fecha_inicio.to_datetime()
    if entity.rango_fecha_fin:
        orm.rango_fecha_fin = entity.rango_fecha_fin.to_datetime()
    orm.filtro_confianza = Decimal(str(entity.filtro_confianza)) if entity.filtro_confianza is not None else None
    orm.tipo_evento = entity.tipo_evento
    if entity.fecha_generacion:
        orm.fecha_generacion = entity.fecha_generacion.to_datetime()
    
    return orm


# ============ INFERENCE REQUEST ============

def inference_request_to_domain(orm: InferenceRequestORM) -> InferenceRequest:
    """Convierte modelo ORM a entidad de dominio"""
    return InferenceRequest(
        id=IdInferenceRequest(orm.id),
        request_id=orm.request_id,
        received_at=UtcDatetime(orm.received_at)
    )


def inference_request_to_orm(
    entity: InferenceRequest,
    existing: Optional[InferenceRequestORM] = None
) -> InferenceRequestORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or InferenceRequestORM()
    
    orm.id = int(entity.id)
    orm.request_id = entity.request_id
    orm.received_at = entity.received_at.to_datetime()
    
    return orm