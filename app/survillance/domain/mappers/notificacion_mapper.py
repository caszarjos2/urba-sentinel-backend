"""
Mapper para Notificacion: conversión entre entidad de dominio y modelo ORM.
"""
from typing import Optional

from app.survillance.models.notificacion_model import Notificacion as NotificacionORM
from app.survillance.domain.entities.notificacion import Notificacion
from app.survillance.domain.enums import EstadoNotificacion
from ._helpers import _as_dt


def notificacion_to_domain(orm: NotificacionORM) -> Notificacion:
    """Convierte modelo ORM a entidad de dominio"""
    return Notificacion(
        id_evento=orm.id_evento,
        canal=orm.canal or "",
        destinatario=orm.destinatario or "",
        estado=EstadoNotificacion(orm.estado),
        fecha_envio=orm.fecha_envio,  # ORM ya devuelve datetime con tz o None
        id=orm.id_notificacion
    )


def notificacion_to_orm(entity: Notificacion, existing: Optional[NotificacionORM] = None) -> NotificacionORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or NotificacionORM()
    
    # NO setear id_notificacion si entity.id es None (autoincrement)
    if entity.id is not None:
        orm.id_notificacion = entity.id
    
    orm.id_evento = entity.id_evento
    orm.canal = entity.canal
    orm.destinatario = entity.destinatario
    orm.estado = entity.estado.value
    # fecha_envio puede ser None
    if entity.fecha_envio is not None:
        orm.fecha_envio = _as_dt(entity.fecha_envio)
    
    return orm

