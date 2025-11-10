"""
Punto de entrada principal de la aplicación FastAPI.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.shared.db import engine, Base
from app.survillance import models

from app.config.settings import settings
from app.survillance.ingestion.camera_supervisor import camera_supervisor
from app.survillance.ingestion.retention_job import retention_job

# Importar controladores
from app.survillance.interfaces.rest.controllers import (
    auth_controller,
    office_controller,
    conection_controller,
    clip_controller,
    events_controller,
    notification_controller,
    notification_controller,
    report_controller,
    inference_controller,
    admin_controller
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print("Iniciando aplicación...")
    
    # Crear directorios base
    os.makedirs(settings.STORAGE_BASE_PATH, exist_ok=True)
    os.makedirs(os.path.join(settings.STORAGE_BASE_PATH, "events"), exist_ok=True)
    os.makedirs(os.path.join(settings.STORAGE_BASE_PATH, "temp"), exist_ok=True)
    
    # Iniciar job de retención
    
    print("Aplicación iniciada correctamente")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    
    # Shutdown
    print("Deteniendo aplicación...")
    
    # Detener ingesta
    await camera_supervisor.stop_all()
    
    # Detener job de retención
    await retention_job.stop()
    
    print("Aplicación detenida")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Seguridad y Vigilancia",
    description="Backend para gestión de cámaras RTSP, eventos de IA y buffer de clips",
    version="1.0.0",
    lifespan=lifespan
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Montar archivos estáticos (opcional)
media_path = os.path.join(settings.STORAGE_BASE_PATH)
if os.path.exists(media_path):
    app.mount("/media", StaticFiles(directory=media_path), name="media")


# Registrar routers
app.include_router(auth_controller.router)
app.include_router(office_controller.router)
app.include_router(conection_controller.router)
app.include_router(clip_controller.router)
app.include_router(events_controller.router)
app.include_router(notification_controller.router)
app.include_router(report_controller.router)
app.include_router(inference_controller.router)
app.include_router(admin_controller.router)


@app.get("/api/health")
async def health_check():
    """Endpoint de salud"""
    return {
        "status": "ok",
        "message": "Sistema de Seguridad y Vigilancia operativo"
    }


@app.get("/")
async def root():
    """Redirige a la documentación"""
    return {
        "message": "Sistema de Seguridad y Vigilancia API",
        "docs": "/docs",
        "health": "/api/health"
    }