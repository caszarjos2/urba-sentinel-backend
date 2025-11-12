"""
Mapper para Reporte: conversión entre entidad de dominio y modelo ORM.
"""
from typing import Optional
from decimal import Decimal

from app.survillance.models.reporte_model import Reporte as ReporteORM
from app.survillance.domain.entities.reporte import Reporte
from ._helpers import _as_dt


def reporte_to_domain(orm: ReporteORM) -> Reporte:
    """Convierte modelo ORM a entidad de dominio"""
    return Reporte(
        id_usuario=orm.id_usuario,
        titulo=orm.titulo or "",
        descripcion=orm.descripcion,
        id_clip=orm.id_clip,
        rango_fecha_inicio=orm.rango_fecha_inicio,  # ORM ya devuelve datetime con tz o None
        rango_fecha_fin=orm.rango_fecha_fin,  # ORM ya devuelve datetime con tz o None
        filtro_confianza=float(orm.filtro_confianza) if orm.filtro_confianza else None,
        tipo_evento=orm.tipo_evento,
        fecha_generacion=orm.fecha_generacion,  # ORM ya devuelve datetime con tz
        id=orm.id_reporte
    )


def reporte_to_orm(entity: Reporte, existing: Optional[ReporteORM] = None) -> ReporteORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or ReporteORM()
    
    # NO setear id_reporte si entity.id es None (autoincrement)
    if entity.id is not None:
        orm.id_reporte = entity.id
    
    orm.id_usuario = entity.id_usuario
    orm.titulo = entity.titulo
    orm.descripcion = entity.descripcion
    orm.id_clip = entity.id_clip
    # fecha_generacion: si viene None, el ORM usará el default (now_utc)
    if entity.fecha_generacion is not None:
        orm.fecha_generacion = _as_dt(entity.fecha_generacion)
    if entity.rango_fecha_inicio is not None:
        orm.rango_fecha_inicio = _as_dt(entity.rango_fecha_inicio)
    if entity.rango_fecha_fin is not None:
        orm.rango_fecha_fin = _as_dt(entity.rango_fecha_fin)
    orm.filtro_confianza = Decimal(str(entity.filtro_confianza)) if entity.filtro_confianza is not None else None
    orm.tipo_evento = entity.tipo_evento
    
    return orm

