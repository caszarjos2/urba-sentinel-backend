"""
Modelo ORM de SQLAlchemy 2.0 para Notificacion.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.shared.db import Base


class Notificacion(Base):
    """Notificación enviada por un evento"""
    __tablename__ = "notificaciones"
    
    id_notificacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_evento: Mapped[int] = mapped_column(ForeignKey("eventos.id_evento"), nullable=False)
    canal: Mapped[Optional[str]] = mapped_column(String(50))
    destinatario: Mapped[Optional[str]] = mapped_column(String(150))
    estado: Mapped[str] = mapped_column(String(50), default="pendiente")
    fecha_envio: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # Relaciones
    evento: Mapped["Evento"] = relationship("Evento", back_populates="notificaciones")

