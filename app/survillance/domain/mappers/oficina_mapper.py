"""
Mapper para Oficina: conversión entre entidad de dominio y modelo ORM.
"""
from typing import Optional

from app.survillance.models.oficina_model import Oficina as OficinaORM
from app.survillance.domain.entities.oficina import Oficina
from ._helpers import _as_dt


def oficina_to_domain(orm: OficinaORM) -> Oficina:
    """Convierte modelo ORM a entidad de dominio"""
    return Oficina(
        nombre_oficina=orm.nombre_oficina,
        direccion=orm.direccion,
        ciudad=orm.ciudad,
        responsable=orm.responsable,
        telefono_contacto=orm.telefono_contacto,
        fecha_registro=orm.fecha_registro,  # ORM ya devuelve datetime con tz
        id=orm.id_oficina
    )


def oficina_to_orm(entity: Oficina, existing: Optional[OficinaORM] = None) -> OficinaORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or OficinaORM()
    
    # NO setear id_oficina si entity.id es None (autoincrement)
    if entity.id is not None:
        orm.id_oficina = entity.id
    
    orm.nombre_oficina = entity.nombre_oficina
    orm.direccion = entity.direccion
    orm.ciudad = entity.ciudad
    orm.responsable = entity.responsable
    orm.telefono_contacto = entity.telefono_contacto
    # fecha_registro: si viene None, el ORM usará el default (now_utc)
    if entity.fecha_registro is not None:
        orm.fecha_registro = _as_dt(entity.fecha_registro)
    
    return orm

