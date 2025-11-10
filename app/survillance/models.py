"""
Modelos ORM de SQLAlchemy 2.0 para todas las entidades del dominio.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Integer, String, Text,
    ForeignKey, Numeric, TIMESTAMP
)
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


class Conexion(Base):
    """Cámara con su configuración RTSP e ingesta"""
    __tablename__ = "conexiones"
    
    id_conexion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_oficina: Mapped[int] = mapped_column(ForeignKey("oficinas.id_oficina"), nullable=False)
    nombre_camara: Mapped[str] = mapped_column(String(120), nullable=False)
    ubicacion: Mapped[Optional[str]] = mapped_column(String(255))
    rtsp_url: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[Optional[str]] = mapped_column(String(50), default="inactiva")
    ultimo_ping: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    modo_ingesta: Mapped[str] = mapped_column(String(20), default="SEGMENT")
    fps_sample: Mapped[Optional[int]] = mapped_column(Integer)
    habilitada: Mapped[bool] = mapped_column(Boolean, default=True)
    retention_minutes: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_utc
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=now_utc
    )
    
    # Relaciones
    oficina: Mapped["Oficina"] = relationship("Oficina", back_populates="conexiones")
    clips: Mapped[list["Clip"]] = relationship(
        "Clip",
        back_populates="conexion",
        cascade="all, delete-orphan"
    )
    eventos: Mapped[list["Evento"]] = relationship(
        "Evento",
        back_populates="conexion",
        cascade="all, delete-orphan"
    )


class Clip(Base):
    """Buffer de clips segmentados en disco"""
    __tablename__ = "clips"
    
    id_clip: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_conexion: Mapped[int] = mapped_column(ForeignKey("conexiones.id_conexion"), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    start_time_utc: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_guardado: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_utc
    )
    
    # Relaciones
    conexion: Mapped["Conexion"] = relationship("Conexion", back_populates="clips")
    eventos: Mapped[list["Evento"]] = relationship(
        "Evento",
        back_populates="clip"
    )
    reportes: Mapped[list["Reporte"]] = relationship(
        "Reporte",
        back_populates="clip"
    )


class Usuario(Base):
    """Usuario del sistema con autenticación JWT"""
    __tablename__ = "usuarios"
    
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[Optional[str]] = mapped_column(String(60))
    fecha_creacion: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_utc
    )
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    
    # Relaciones
    eventos: Mapped[list["Evento"]] = relationship(
        "Evento",
        back_populates="usuario"
    )
    reportes: Mapped[list["Reporte"]] = relationship(
        "Reporte",
        back_populates="usuario"
    )


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


class Reporte(Base):
    """Reporte generado por un usuario"""
    __tablename__ = "reportes"
    
    id_reporte: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    id_clip: Mapped[Optional[int]] = mapped_column(ForeignKey("clips.id_clip"))
    titulo: Mapped[Optional[str]] = mapped_column(String(200))
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    rango_fecha_inicio: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    rango_fecha_fin: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    filtro_confianza: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    tipo_evento: Mapped[Optional[str]] = mapped_column(String(50))
    fecha_generacion: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_utc
    )
    
    # Relaciones
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="reportes")
    clip: Mapped[Optional["Clip"]] = relationship("Clip", back_populates="reportes")


class InferenceRequest(Base):
    """Control de idempotencia para webhooks de inferencia"""
    __tablename__ = "inference_requests"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=now_utc,
        nullable=False
    )