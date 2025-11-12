"""
Mapper para Conexion: conversión entre entidad de dominio y modelo ORM.
"""
from typing import Optional

from app.survillance.models.conexion_model import Conexion as ConexionORM
from app.survillance.domain.entities.conexion import Conexion
from app.survillance.domain.enums import ModoIngesta
from ._helpers import _as_dt


def conexion_to_domain(orm: ConexionORM) -> Conexion:
    """Convierte modelo ORM a entidad de dominio"""
    return Conexion(
        id_oficina=orm.id_oficina,
        nombre_camara=orm.nombre_camara,
        rtsp_url=orm.rtsp_url,
        modo_ingesta=ModoIngesta(orm.modo_ingesta),
        habilitada=orm.habilitada,
        retention_minutes=orm.retention_minutes,
        ubicacion=orm.ubicacion,
        estado=orm.estado,
        ultimo_ping=orm.ultimo_ping,  # ORM ya devuelve datetime con tz o None
        fps_sample=orm.fps_sample,
        created_at=orm.created_at,  # ORM ya devuelve datetime con tz
        updated_at=orm.updated_at,  # Puede ser None
        id=orm.id_conexion
    )


def conexion_to_orm(entity: Conexion, existing: Optional[ConexionORM] = None) -> ConexionORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or ConexionORM()
    
    # NO setear id_conexion si entity.id es None (autoincrement)
    if entity.id is not None:
        orm.id_conexion = entity.id
    
    orm.id_oficina = entity.id_oficina
    orm.nombre_camara = entity.nombre_camara
    orm.rtsp_url = entity.rtsp_url
    orm.modo_ingesta = entity.modo_ingesta.value
    orm.habilitada = entity.habilitada
    orm.retention_minutes = entity.retention_minutes
    orm.ubicacion = entity.ubicacion
    orm.estado = entity.estado
    # created_at: si viene None, el ORM usará el default (now_utc)
    if entity.created_at is not None:
        orm.created_at = _as_dt(entity.created_at)
    if entity.ultimo_ping is not None:
        orm.ultimo_ping = _as_dt(entity.ultimo_ping)
    orm.fps_sample = entity.fps_sample
    if entity.updated_at is not None:
        orm.updated_at = _as_dt(entity.updated_at)
    
    return orm

