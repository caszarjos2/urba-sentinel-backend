"""
Servicio de autenticación y gestión de usuarios.
"""
from fastapi import HTTPException, status

from app.shared.security import hash_password, verify_password, create_access_token
from app.shared.time import now_utc
from app.survillance.domain.entities.usuario import Usuario
from app.survillance.domain.repositories_interfaces import IUsuarioRepository
from app.survillance.application.dto import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
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
        # Crear entidad sin id (autoincrement)
        userEntity = Usuario(
            nombre=data.nombre,
            email=data.email,
            password_hash=hash_password(data.password),
            apellido=data.apellido,
            rol=data.rol,
            fecha_creacion=now_utc(),
            # id=None (implícito, no se pasa)
            # ultimo_login=None (implícito, no se pasa)
        )
        usuario = await self.user_repo.create(userEntity)
        
        return usuario
    
    async def login(self, data: LoginRequest) -> TokenResponse:
        usuario = await self.user_repo.get_by_email(data.email)
        if not usuario or not verify_password(data.password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        # Actualizar último login
        usuario.ultimo_login = now_utc()
        usuario = await self.user_repo.update(usuario)

        # Usa el id de dominio (int)
        if usuario.id is None:
            raise HTTPException(status_code=500, detail="Usuario sin ID")
        token = create_access_token(usuario.id)

        # expires_in en segundos
        return TokenResponse(access_token=token, expires_in=settings.JWT_EXPIRES_MIN * 60)
    
    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        """Refresca un token JWT (simplificado)"""
        # En producción, implementar refresh token separado
        token = create_access_token({"sub": 1})
        return TokenResponse(
            access_token=token,
            expires_in=settings.JWT_EXPIRES_MIN * 3600
        )

