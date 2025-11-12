"""
Servicio para gestión de clips.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from app.survillance.domain.entities.clip import Clip
from app.survillance.domain.repositories_interfaces import IClipRepository


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

