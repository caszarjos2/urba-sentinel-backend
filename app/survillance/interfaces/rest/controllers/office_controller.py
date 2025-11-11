"""
Controlador CRUD de oficinas.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db import get_session
from app.shared.security import get_current_user_id
from app.survillance.infrastructure.repositories import OficinaRepository
from app.survillance.application.services import OficinaService
from app.survillance.application.dto import *


router = APIRouter(prefix="/api/oficinas", tags=["Oficinas"])


@router.post("", response_model=OficinaResponse, status_code=201)
async def create_oficina(
    data: OficinaCreate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Crea una nueva oficina"""
    oficina_repo = OficinaRepository(session)
    service = OficinaService(oficina_repo)
    
    oficina = await service.create(data)
    return OficinaResponse.model_validate(oficina)


@router.get("/{id_oficina}", response_model=OficinaResponse)
async def get_oficina(
    id_oficina: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Obtiene una oficina por ID"""
    oficina_repo = OficinaRepository(session)
    service = OficinaService(oficina_repo)
    
    oficina = await service.get_by_id(id_oficina)
    return OficinaResponse.model_validate(oficina)


@router.get("", response_model=List[OficinaResponse])
async def list_oficinas(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Lista todas las oficinas"""
    oficina_repo = OficinaRepository(session)
    service = OficinaService(oficina_repo)
    
    oficinas = await service.get_all(limit, offset)
    return [OficinaResponse.model_validate(o) for o in oficinas]


@router.put("/{id_oficina}", response_model=OficinaResponse)
async def update_oficina(
    id_oficina: int,
    data: OficinaUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Actualiza una oficina"""
    oficina_repo = OficinaRepository(session)
    service = OficinaService(oficina_repo)
    
    oficina = await service.update(id_oficina, data)
    return OficinaResponse.model_validate(oficina)


@router.delete("/{id_oficina}", status_code=204)
async def delete_oficina(
    id_oficina: int,
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id)
):
    """Elimina una oficina"""
    oficina_repo = OficinaRepository(session)
    service = OficinaService(oficina_repo)
    
    await service.delete(id_oficina)