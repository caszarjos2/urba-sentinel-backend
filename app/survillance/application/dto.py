"""
DTOs (Data Transfer Objects) usando Pydantic v2 para request/response.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============ AUTH DTOs ============

class RegisterRequest(BaseModel):
    """Request para registro de usuario"""
    nombre: str = Field(..., max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=2)
    rol: Optional[str] = Field(None, max_length=60)


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response con tokens JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Request para refresh token"""
    token: str


# ============ OFICINA DTOs ============

class OficinaCreate(BaseModel):
    """Request para crear oficina"""
    nombre_oficina: str = Field(..., max_length=150)
    direccion: Optional[str] = Field(None, max_length=255)
    ciudad: Optional[str] = Field(None, max_length=100)
    responsable: Optional[str] = Field(None, max_length=100)
    telefono_contacto: Optional[str] = Field(None, max_length=50)


class OficinaUpdate(BaseModel):
    """Request para actualizar oficina"""
    nombre_oficina: Optional[str] = Field(None, max_length=150)
    direccion: Optional[str] = Field(None, max_length=255)
    ciudad: Optional[str] = Field(None, max_length=100)
    responsable: Optional[str] = Field(None, max_length=100)
    telefono_contacto: Optional[str] = Field(None, max_length=50)


class OficinaResponse(BaseModel):
    """Response de oficina"""
    model_config = ConfigDict(from_attributes=True)
    
    id_oficina: int
    nombre_oficina: str
    direccion: Optional[str]
    ciudad: Optional[str]
    responsable: Optional[str]
    telefono_contacto: Optional[str]
    fecha_registro: datetime


# ============ CONEXION DTOs ============

class ConexionCreate(BaseModel):
    """Request para crear conexión"""
    id_oficina: int
    nombre_camara: str = Field(..., max_length=120)
    ubicacion: Optional[str] = Field(None, max_length=255)
    rtsp_url: str
    modo_ingesta: str = Field(default="SEGMENT", max_length=20)
    fps_sample: Optional[int] = None
    habilitada: bool = True
    retention_minutes: int = 60


class ConexionUpdate(BaseModel):
    """Request para actualizar conexión"""
    nombre_camara: Optional[str] = Field(None, max_length=120)
    ubicacion: Optional[str] = Field(None, max_length=255)
    rtsp_url: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=50)
    modo_ingesta: Optional[str] = Field(None, max_length=20)
    fps_sample: Optional[int] = None
    habilitada: Optional[bool] = None
    retention_minutes: Optional[int] = None


class ConexionResponse(BaseModel):
    """Response de conexión"""
    model_config = ConfigDict(from_attributes=True)
    
    id_conexion: int
    id_oficina: int
    nombre_camara: str
    ubicacion: Optional[str]
    rtsp_url: str
    estado: Optional[str]
    ultimo_ping: Optional[datetime]
    modo_ingesta: str
    fps_sample: Optional[int]
    habilitada: bool
    retention_minutes: int
    created_at: datetime
    updated_at: Optional[datetime]


# ============ CLIP DTOs ============

class ClipResponse(BaseModel):
    """Response de clip"""
    model_config = ConfigDict(from_attributes=True)
    
    id_clip: int
    id_conexion: int
    storage_path: str
    start_time_utc: datetime
    duration_sec: int
    fecha_guardado: datetime


# ============ EVENTO DTOs ============

class EventoResponse(BaseModel):
    """Response de evento"""
    model_config = ConfigDict(from_attributes=True)
    
    id_evento: int
    id_conexion: int
    id_clip: Optional[int]
    id_usuario: Optional[int]
    tipo_evento: str
    confianza: Optional[Decimal]
    t_inicio_ms: Optional[int]
    t_fin_ms: Optional[int]
    timestamp_evento: datetime
    procesado: bool
    subclip_path: Optional[str]
    subclip_duracion_sec: Optional[int]


# ============ NOTIFICACION DTOs ============

class NotificacionCreate(BaseModel):
    """Request para crear notificación"""
    id_evento: int
    canal: Optional[str] = Field(None, max_length=50)
    destinatario: Optional[str] = Field(None, max_length=150)


class NotificacionUpdate(BaseModel):
    """Request para actualizar notificación"""
    estado: Optional[str] = Field(None, max_length=50)
    fecha_envio: Optional[datetime] = None


class NotificacionResponse(BaseModel):
    """Response de notificación"""
    model_config = ConfigDict(from_attributes=True)
    
    id_notificacion: int
    id_evento: int
    canal: Optional[str]
    destinatario: Optional[str]
    estado: str
    fecha_envio: Optional[datetime]


# ============ REPORTE DTOs ============

class ReporteCreate(BaseModel):
    """Request para crear reporte"""
    id_clip: Optional[int] = None
    titulo: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    rango_fecha_inicio: Optional[datetime] = None
    rango_fecha_fin: Optional[datetime] = None
    filtro_confianza: Optional[Decimal] = None
    tipo_evento: Optional[str] = Field(None, max_length=50)


class ReporteResponse(BaseModel):
    """Response de reporte"""
    model_config = ConfigDict(from_attributes=True)
    
    id_reporte: int
    id_usuario: int
    id_clip: Optional[int]
    titulo: Optional[str]
    descripcion: Optional[str]
    rango_fecha_inicio: Optional[datetime]
    rango_fecha_fin: Optional[datetime]
    filtro_confianza: Optional[Decimal]
    tipo_evento: Optional[str]
    fecha_generacion: datetime


# ============ INFERENCE WEBHOOK DTOs ============

class EventoInferenciaBase(BaseModel):
    """Base para eventos de inferencia"""
    tipo: str
    confianza: float


class EventoInferenciaA(EventoInferenciaBase):
    """Contrato A: offsets relativos al clip"""
    t_inicio_ms: int
    t_fin_ms: int


class EventoInferenciaB(EventoInferenciaBase):
    """Contrato B: timestamp absoluto"""
    timestamp_utc: str
    dur_ms: int


class InferenceWebhookRequestA(BaseModel):
    """Request webhook con offsets relativos (Contrato A)"""
    request_id: str
    conexion_id: int
    clip_id: Optional[int] = None
    clip_path: Optional[str] = None
    modelo_version: str
    eventos: List[EventoInferenciaA]


class InferenceWebhookRequestB(BaseModel):
    """Request webhook con timestamps absolutos (Contrato B)"""
    request_id: str
    conexion_id: int
    modelo_version: str
    eventos: List[EventoInferenciaB]


class InferenceWebhookResponse(BaseModel):
    """Response de webhook de inferencia"""
    ok: bool
    created_event_ids: List[int] = []
    message: Optional[str] = None