"""
Servicio para gestión de eventos.
"""
from datetime import datetime, timedelta
from typing import List, Optional
import os

from fastapi import HTTPException, status

from app.shared.ffmpeg_utils import cut_and_concat
from app.survillance.domain.entities.evento import Evento
from app.survillance.domain.repositories_interfaces import IEventoRepository, IClipRepository
from app.survillance.application.clip_resolver import ClipResolver
from app.survillance.domain.value_objects.media_paths import SubclipPath
from app.survillance.domain.value_objects.timestamps import DurationSeconds
from app.config.settings import settings


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
        
        # Calcular rango con padding (t_inicio_ms y t_fin_ms son MilliSeconds VOs)
        t_inicio = int(evento.t_inicio_ms)
        t_fin = int(evento.t_fin_ms)
        start_abs = evento.timestamp_evento + timedelta(milliseconds=-(padding * 1000))
        end_abs = evento.timestamp_evento + timedelta(milliseconds=t_fin + (padding * 1000))
        
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
        
        if evento.id is None:
            raise HTTPException(status_code=500, detail="Evento sin ID")
        timestamp_str = evento.timestamp_evento.strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(
            events_dir,
            f"event_{evento.id}_{timestamp_str}.mp4"
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
        evento.subclip_path = SubclipPath(out_path)
        evento.subclip_duracion_sec = DurationSeconds(int((end_abs - start_abs).total_seconds()))
        
        return await self.evento_repo.update(evento)

