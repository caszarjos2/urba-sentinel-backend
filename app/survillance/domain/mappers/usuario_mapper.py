"""
Mapper para Usuario: conversión entre entidad de dominio y modelo ORM.
"""
from typing import Optional

from app.survillance.models.usuario_model import Usuario as UsuarioORM
from app.survillance.domain.entities.usuario import Usuario
from ._helpers import _as_dt


def usuario_to_domain(orm: UsuarioORM) -> Usuario:
    """Convierte modelo ORM a entidad de dominio"""
    return Usuario(
        nombre=orm.nombre,
        email=orm.email,
        password_hash=orm.password_hash,
        apellido=orm.apellido,
        rol=orm.rol,
        fecha_creacion=orm.fecha_creacion,  # ORM ya devuelve datetime con tz
        ultimo_login=orm.ultimo_login,  # Puede ser None
        id=orm.id_usuario
    )


def usuario_to_orm(entity: Usuario, existing: Optional[UsuarioORM] = None) -> UsuarioORM:
    """Convierte entidad de dominio a modelo ORM"""
    orm = existing or UsuarioORM()
    
    # NO setear id_usuario si entity.id es None (autoincrement)
    if entity.id is not None:
        orm.id_usuario = entity.id
    
    orm.nombre = entity.nombre
    orm.apellido = entity.apellido
    orm.email = entity.email
    orm.password_hash = entity.password_hash
    orm.rol = entity.rol
    # fecha_creacion: si viene None, el ORM usará el default (now_utc)
    if entity.fecha_creacion is not None:
        orm.fecha_creacion = _as_dt(entity.fecha_creacion)
    # ultimo_login puede ser None
    if entity.ultimo_login is not None:
        orm.ultimo_login = _as_dt(entity.ultimo_login)
    
    return orm

