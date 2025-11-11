"""
Servicios de aplicación: casos de uso y orquestación de lógica de negocio.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
import os

from fastapi import HTTPException, status

from app.shared.security import hash_password, verify_password, create_access_token
from app.shared.time import now_utc, parse_utc
from app.shared.ffmpeg_utils import cut_and_concat
from app.survillance.domain.entities import *
from app.survillance.domain.repositories_interfaces import *
from app.survillance.application.dto import *
from app.survillance.application.clip_resolver import ClipResolver
from app.config.settings import settings


class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    def __init__(self, user_repo: IUsuarioRepository):
        self.user_repo = user_repo
    
    async def register(self, data: RegisterRequest) -> Usuario:
        """Registra un nuevo usuario"""
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya registrado"
            )
        userEntity = Usuario(
            nombre=data.nombre,
            apellido=data.apellido,
            email=data.email,
            password_hash=hash_password(data.password),
            rol=data.rol,
            fecha_creacion=now_utc(),
        )
        usuario = await self.user_repo.create(
            userEntity
        )
        
        return usuario
    
    async def login(self, data: LoginRequest) -> TokenResponse:
        usuario = await self.user_repo.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        # VO UtcDatetime en la entidad:
        usuario.ultimo_login = now_utc()
        await self.user_repo.update(usuario)

        # Usa el id de dominio
        token = create_access_token({"sub": str(usuario.id)})

        return TokenResponse(access_token=token, expires_in=settings.JWT_EXPIRES_MIN * 6000)
    
    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        """Refresca un token JWT (simplificado)"""
        # En producción, implementar refresh token separado
        token = create_access_token({"sub": 1})
        return TokenResponse(
            access_token=token,
            expires_in=settings.JWT_EXPIRES_MIN * 6000
        )


class OficinaService:
    """Servicio CRUD de oficinas"""
    
    def __init__(self, oficina_repo: IOficinaRepository):
        self.oficina_repo = oficina_repo
    
    async def create(self, data: OficinaCreate) -> Oficina:
        """Crea una oficina"""
        oficina = Oficina(
            nombre_oficina=data.nombre_oficina,
            direccion=data.direccion,
            ciudad=data.ciudad,
            responsable=data.responsable,
            telefono_contacto=data.telefono_contacto,
            fecha_registro=now_utc()
        )
        return await self.oficina_repo.create(oficina)
    
    async def get_by_id(self, id_oficina: int) -> Oficina:
        """Obtiene oficina por ID"""
        oficina = await self.oficina_repo.get_by_id(id_oficina)
        if not oficina:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oficina no encontrada"
            )
        return oficina
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Oficina]:
        """Lista todas las oficinas"""
        return await self.oficina_repo.get_all(limit, offset)
    
    async def update(self, id_oficina: int, data: OficinaUpdate) -> Oficina:
        """Actualiza una oficina"""
        oficina = await self.get_by_id(id_oficina)
        
        if data.nombre_oficina is not None:
            oficina.nombre_oficina = data.nombre_oficina
        if data.direccion is not None:
            oficina.direccion = data.direccion
        if data.ciudad is not None:
            oficina.ciudad = data.ciudad
        if data.responsable is not None:
            oficina.responsable = data.responsable
        if data.telefono_contacto is not None:
            oficina.telefono_contacto = data.telefono_contacto
        
        return await self.oficina_repo.update(oficina)
    
    async def delete(self, id_oficina: int) -> bool:
        """Elimina una oficina"""
        return await self.oficina_repo.delete(id_oficina)


class ConexionService:
    """Servicio CRUD de conexiones/cámaras"""
    
    def __init__(self, conexion_repo: IConexionRepository):
        self.conexion_repo = conexion_repo
    
    async def create(self, data: ConexionCreate) -> Conexion:
        """Crea una conexión"""
        conexion = Conexion(
            id_oficina=data.id_oficina,
            nombre_camara=data.nombre_camara,
            ubicacion=data.ubicacion,
            rtsp_url=data.rtsp_url,
            estado="inactiva",
            modo_ingesta=data.modo_ingesta,
            fps_sample=data.fps_sample,
            habilitada=data.habilitada,
            retention_minutes=data.retention_minutes,
            created_at=now_utc()
        )
        return await self.conexion_repo.create(conexion)
    
    async def get_by_id(self, id_conexion: int) -> Conexion:
        """Obtiene conexión por ID"""
        conexion = await self.conexion_repo.get_by_id(id_conexion)
        if not conexion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conexión no encontrada"
            )
        return conexion
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_oficina: Optional[int] = None,
        habilitada: Optional[bool] = None
    ) -> List[Conexion]:
        """Lista todas las conexiones con filtros"""
        return await self.conexion_repo.get_all(limit, offset, id_oficina, habilitada)
    
    async def update(self, id_conexion: int, data: ConexionUpdate) -> Conexion:
        """Actualiza una conexión"""
        conexion = await self.get_by_id(id_conexion)
        
        if data.nombre_camara is not None:
            conexion.nombre_camara = data.nombre_camara
        if data.ubicacion is not None:
            conexion.ubicacion = data.ubicacion
        if data.rtsp_url is not None:
            conexion.rtsp_url = data.rtsp_url
        if data.estado is not None:
            conexion.estado = data.estado
        if data.modo_ingesta is not None:
            conexion.modo_ingesta = data.modo_ingesta
        if data.fps_sample is not None:
            conexion.fps_sample = data.fps_sample
        if data.habilitada is not None:
            conexion.habilitada = data.habilitada
        if data.retention_minutes is not None:
            conexion.retention_minutes = data.retention_minutes
        
        conexion.updated_at = now_utc()
        
        return await self.conexion_repo.update(conexion)
    
    async def delete(self, id_conexion: int) -> bool:
        """Elimina una conexión"""
        return await self.conexion_repo.delete(id_conexion)


class ClipService:
    """Servicio para gestión de clips"""
    
    def __init__(self, clip_repo: IClipRepository):
        self.clip_repo = clip_repo
    
    async def get_by_id(self, id_clip: int) -> Clip:
        """Obtiene clip por ID"""
        clip = await self.clip_repo.get_by_id(id_clip)
        if not clip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Clip no encontrado"
            )
        return clip
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_conexion: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Clip]:
        """Lista clips con filtros"""
        return await self.clip_repo.get_all(limit, offset, id_conexion, start_time, end_time)


class EventoService:
    """Servicio para gestión de eventos"""
    
    def __init__(
        self,
        evento_repo: IEventoRepository,
        clip_repo: IClipRepository
    ):
        self.evento_repo = evento_repo
        self.clip_repo = clip_repo
    
    async def get_by_id(self, id_evento: int) -> Evento:
        """Obtiene evento por ID"""
        evento = await self.evento_repo.get_by_id(id_evento)
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        return evento
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_conexion: Optional[int] = None,
        tipo_evento: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Evento]:
        """Lista eventos con filtros"""
        return await self.evento_repo.get_all(
            limit, offset, id_conexion, tipo_evento, start_time, end_time
        )
    
    async def generar_subclip(self, id_evento: int, padding: int = 2) -> Evento:
        """
        Genera un subclip del evento, concatenando múltiples clips si es necesario.
        """
        evento = await self.get_by_id(id_evento)
        
        if not evento.t_inicio_ms or not evento.t_fin_ms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evento no tiene offsets de tiempo"
            )
        
        # Calcular rango con padding
        start_abs = evento.timestamp_evento + timedelta(milliseconds=-padding * 1000)
        end_abs = evento.timestamp_evento + timedelta(
            milliseconds=evento.t_fin_ms + padding * 1000
        )
        
        # Obtener clips que cubren el rango
        clips = await self.clip_repo.get_by_time_range(
            evento.id_conexion,
            start_abs,
            end_abs
        )
        
        if not clips:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron clips para el rango de tiempo"
            )
        
        # Resolver clips a lista de cortes
        parts = ClipResolver.resolve_time_range(clips, start_abs, end_abs)
        
        # Generar ruta de salida
        events_dir = os.path.join(settings.STORAGE_BASE_PATH, "events")
        os.makedirs(events_dir, exist_ok=True)
        
        timestamp_str = evento.timestamp_evento.strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(
            events_dir,
            f"event_{evento.id_evento}_{timestamp_str}.mp4"
        )
        
        # Directorio temporal
        temp_dir = os.path.join(settings.STORAGE_BASE_PATH, "temp")
        
        # Cortar y concatenar
        success = await cut_and_concat(parts, out_path, temp_dir)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al generar subclip"
            )
        
        # Actualizar evento
        evento.subclip_path = out_path
        evento.subclip_duracion_sec = int((end_abs - start_abs).total_seconds())
        
        return await self.evento_repo.update(evento)


class NotificacionService:
    """Servicio CRUD de notificaciones"""
    
    def __init__(self, notif_repo: INotificacionRepository):
        self.notif_repo = notif_repo
    
    async def create(self, data: NotificacionCreate) -> Notificacion:
        """Crea una notificación"""
        notif = Notificacion(
            id_evento=data.id_evento,
            canal=data.canal,
            destinatario=data.destinatario,
            estado="pendiente"
        )
        return await self.notif_repo.create(notif)
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_evento: Optional[int] = None
    ) -> List[Notificacion]:
        """Lista notificaciones"""
        return await self.notif_repo.get_all(limit, offset, id_evento)
    
    async def update(
        self,
        id_notificacion: int,
        data: NotificacionUpdate
    ) -> Notificacion:
        """Actualiza notificación"""
        notif = await self.notif_repo.get_by_id(id_notificacion)
        if not notif:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
        
        if data.estado is not None:
            notif.estado = data.estado
        if data.fecha_envio is not None:
            notif.fecha_envio = data.fecha_envio
        
        return await self.notif_repo.update(notif)


class ReporteService:
    """Servicio CRUD de reportes"""
    
    def __init__(self, reporte_repo: IReporteRepository):
        self.reporte_repo = reporte_repo
    
    async def create(self, data: ReporteCreate, id_usuario: int) -> Reporte:
        """Crea un reporte"""
        reporte = Reporte(
            id_usuario=id_usuario,
            id_clip=data.id_clip,
            titulo=data.titulo,
            descripcion=data.descripcion,
            rango_fecha_inicio=data.rango_fecha_inicio,
            rango_fecha_fin=data.rango_fecha_fin,
            filtro_confianza=data.filtro_confianza,
            tipo_evento=data.tipo_evento,
            fecha_generacion=now_utc()
        )
        return await self.reporte_repo.create(reporte)
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        id_usuario: Optional[int] = None
    ) -> List[Reporte]:
        """Lista reportes"""
        return await self.reporte_repo.get_all(limit, offset, id_usuario)