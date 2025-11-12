"""
Controlador de autenticación: registro, login, refresh.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.db import get_session
from app.survillance.infrastructure.repositories import UsuarioRepository
from app.survillance.application.services.auth_service import AuthService
from app.survillance.application.dto import *


router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterRequest,
    session: AsyncSession = Depends(get_session)
):
    """Registra un nuevo usuario"""
    user_repo = UsuarioRepository(session)
    auth_service = AuthService(user_repo)
    
    usuario = await auth_service.register(data)
    
    # Generar token automáticamente
    token_response = await auth_service.login(
        LoginRequest(email=data.email, password=data.password)
    )
    
    return token_response


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """Autentica un usuario y retorna JWT"""
    user_repo = UsuarioRepository(session)
    auth_service = AuthService(user_repo)
    
    return await auth_service.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    session: AsyncSession = Depends(get_session)
):
    """Refresca un token JWT"""
    user_repo = UsuarioRepository(session)
    auth_service = AuthService(user_repo)
    
    return await auth_service.refresh(data)