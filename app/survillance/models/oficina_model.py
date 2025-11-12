"""
Modelo ORM de SQLAlchemy 2.0 para Oficina.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.shared.db import Base
from app.shared.time import now_utc


class Oficina(Base):
    """Oficina física donde se instalan cámaras"""
    __tablename__ = "oficinas"
    
    id_oficina: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_oficina: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[Optional[str]] = mapped_column(String(255))
    ciudad: Mapped[Optional[str]] = mapped_column(String(100))
    responsable: Mapped[Optional[str]] = mapped_column(String(100))
    telefono_contacto: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_registro: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_utc
    )
    
    # Relaciones
    conexiones: Mapped[list["Conexion"]] = relationship(
        "Conexion",
        back_populates="oficina",
        cascade="all, delete-orphan"
    )

