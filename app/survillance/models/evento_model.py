"""
Modelo ORM de SQLAlchemy 2.0 para Evento.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.shared.db import Base


class Evento(Base):
    """Evento de seguridad detectado por IA"""
    __tablename__ = "eventos"
    
    id_evento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_conexion: Mapped[int] = mapped_column(ForeignKey("conexiones.id_conexion"), nullable=False)
    id_clip: Mapped[Optional[int]] = mapped_column(ForeignKey("clips.id_clip"))
    id_usuario: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id_usuario"))
    tipo_evento: Mapped[str] = mapped_column(String(30), nullable=False)
    confianza: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    t_inicio_ms: Mapped[Optional[int]] = mapped_column(Integer)
    t_fin_ms: Mapped[Optional[int]] = mapped_column(Integer)
    timestamp_evento: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        index=True
    )
    procesado: Mapped[bool] = mapped_column(Boolean, default=False)
    subclip_path: Mapped[Optional[str]] = mapped_column(Text)
    subclip_duracion_sec: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Relaciones
    conexion: Mapped["Conexion"] = relationship("Conexion", back_populates="eventos")
    clip: Mapped[Optional["Clip"]] = relationship("Clip", back_populates="eventos")
    usuario: Mapped[Optional["Usuario"]] = relationship("Usuario", back_populates="eventos")
    notificaciones: Mapped[list["Notificacion"]] = relationship(
        "Notificacion",
        back_populates="evento",
        cascade="all, delete-orphan"
    )

