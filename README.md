# Sistema de Seguridad y Vigilancia - Backend

Backend completo en Python 3.11 con FastAPI siguiendo **Domain-Driven Design (DDD)** por capas, conectado a PostgreSQL via SQLAlchemy 2.0 async y Alembic.

## 📋 Características

- ✅ **Arquitectura DDD completa** con capa de dominio pura
- ✅ Autenticación JWT (registro/login/refresh)
- ✅ CRUDs completos de todas las entidades del dominio
- ✅ Ingesta de video RTSP mediante FFmpeg con segmentación automática
- ✅ Buffer circular con retención configurable por cámara
- ✅ Webhook de inferencia con dos contratos (offsets relativos y timestamps absolutos)
- ✅ Idempotencia de webhooks mediante InferenceRequest
- ✅ Generación de subclips multi-clip sin recodificar
- ✅ 9 entidades de dominio inmutables con validaciones
- ✅ 15 value objects para type safety
- ✅ Repositorios con interfaces Protocol
- ✅ Mapeadores bidireccionales ORM ↔ Dominio

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│         Controllers (HTTP/FastAPI)      │  ← Endpoints REST
├─────────────────────────────────────────┤
│      Services (Application Layer)       │  ← Casos de uso
├─────────────────────────────────────────┤
│    Domain (Entities + Value Objects)    │  ← Lógica de negocio PURA
├─────────────────────────────────────────┤
│    Repository Interfaces (Protocol)     │  ← Contratos
├─────────────────────────────────────────┤
│  Repository Adapters (Infrastructure)   │  ← SQLAlchemy async
├─────────────────────────────────────────┤
│         Database (PostgreSQL)           │
└─────────────────────────────────────────┘
```

### Estructura de Carpetas

```
app/
├── main.py                          # Punto de entrada FastAPI
├── config/
│   └── settings.py                  # Configuración con pydantic-settings
├── shared/
│   ├── db.py                        # Engine y session async
│   ├── security.py                  # JWT y hashing
│   ├── time.py                      # Helpers UTC
│   └── ffmpeg_utils.py              # Cut & concat
└── seguridad_vigilancia/
    ├── domain/                      # ⭐ CAPA DE DOMINIO PURA
    │   ├── entities/                # 9 entidades inmutables
    │   │   ├── oficina.py
    │   │   ├── conexion.py
    │   │   ├── clip.py
    │   │   ├── usuario.py
    │   │   ├── evento.py
    │   │   ├── notificacion.py
    │   │   ├── reporte.py
    │   │   ├── inference_request.py
    │   │   └── event_snapshot.py
    │   ├── value_objects/           # 15 VOs con validación
    │   │   ├── identifiers.py       # 9 IDs tipados
    │   │   ├── timestamps.py        # UTC, Duration, Millis
    │   │   └── media_paths.py       # Storage, Subclip, Snapshot
    │   ├── enums.py                 # 4 enums del dominio
    │   ├── repositories_interfaces.py  # 9 interfaces Protocol
    │   ├── mappers.py               # 16 funciones to_domain/to_orm
    │   └── models.py                # Modelos ORM SQLAlchemy
    │
    ├── application/
    │   ├── dto.py                   # Schemas Pydantic v2
    │   ├── services.py              # Servicios CRUD
    │   ├── inference_service.py     # Procesamiento webhooks
    │   ├── clip_resolver.py         # Resolver rangos a clips
    │   └── retention_service.py     # Lógica de retención
    │
    ├── infrastructure/
    │   ├── repositories.py          # Repos SQLAlchemy (legacy)
    │   ├── domain_repositories.py   # ⭐ Adaptadores de dominio
    │   └── migrations/              # Alembic
    │
    ├── interface/controllers/       # 9 Controllers HTTP
    │   ├── auth_controller.py
    │   ├── oficinas_controller.py
    │   ├── conexiones_controller.py
    │   ├── clips_controller.py
    │   ├── eventos_controller.py
    │   ├── notificaciones_controller.py
    │   ├── reportes_controller.py
    │   ├── inference_webhook_controller.py
    │   └── admin_controller.py
    │
    └── ingestion/
        ├── camera_supervisor.py     # Orquestador de workers
        ├── camera_worker.py         # Worker por cámara
        └── retention_job.py         # Job periódico
```

## 🎯 Capa de Dominio (DDD)

### Entidades Inmutables

**9 entidades** con `@dataclass(frozen=True)` y validaciones automáticas:

1. **Oficina** - Oficinas físicas
2. **Conexion** - Cámaras RTSP con configuración
3. **Clip** - Segmentos de video en buffer
4. **Usuario** - Usuarios del sistema
5. **Evento** - Eventos de seguridad detectados por IA
6. **Notificacion** - Notificaciones de eventos
7. **Reporte** - Reportes generados
8. **InferenceRequest** - Control de idempotencia de webhooks
9. **EventSnapshot** - Snapshots/frames de eventos

### Value Objects

**15 value objects** con validación incorporada:

**Identifiers (9):**
```python
IdOficina(1)        # Valida > 0
IdConexion(2)
IdClip(3)
IdEvento(4)
IdUsuario(5)
IdReporte(6)
IdNotificacion(7)
IdInferenceRequest(8)
IdEventSnapshot(9)
```

**Timestamps (3):**
```python
UtcDatetime(dt)              # Garantiza UTC timezone
DurationSeconds(30)          # Valida >= 0
MilliSeconds(1500)           # Valida >= 0
```

**Media Paths (3):**
```python
StoragePath("clip.mp4")      # Valida .mp4
SubclipPath("event.mp4")     # Valida .mp4
SnapshotPath("frame.jpg")    # Valida .jpg/.png/.webp
```

### Enums del Dominio

```python
TipoEvento = {"forcejeo", "patada", "golpe"}
ModoIngesta = {"WEBHOOK_ONLY", "PUSH", "SEGMENT"}
EstadoConexion = {"activa", "inactiva", "error"}
EstadoNotificacion = {"pendiente", "enviada", "fallida"}
```

### Ejemplo de Uso

```python
from app.seguridad_vigilancia.domain import (
    Oficina, IdOficina, UtcDatetime
)
from datetime import datetime, timezone

# Crear entidad con validaciones automáticas
oficina = Oficina(
    id=IdOficina(1),
    nombre_oficina="Oficina Central",
    direccion="Av. Principal 123",
    ciudad="Lima",
    responsable="Juan Pérez",
    telefono_contacto="+51999999999",
    fecha_registro=UtcDatetime(datetime.now(timezone.utc))
)

# Validaciones automáticas
try:
    oficina_invalida = Oficina(
        id=IdOficina(0),  # ❌ ValueError: debe ser > 0
        nombre_oficina="",  # ❌ ValueError: no puede estar vacío
        ...
    )
except ValueError as e:
    print(f"Error de validación: {e}")
```

## 📦 Instalación

### 1. Requisitos previos

- Python 3.11+
- PostgreSQL 14+
- FFmpeg instalado y accesible

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/seguridad

# JWT
JWT_SECRET=tu_secreto_super_seguro_cambiar_en_produccion
JWT_ALGORITHM=HS256
JWT_EXPIRES_MIN=60

# FFmpeg (ajustar según SO)
FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe  # Windows
# FFMPEG_PATH=/usr/bin/ffmpeg         # Linux

SEGMENT_SECONDS=20
STORAGE_BASE_PATH=D:\videos           # Windows
# STORAGE_BASE_PATH=/var/videos       # Linux

# Opcional
IA_BASE_URL=http://localhost:8001
WEBHOOK_SECRET=secret_webhook
```

### 4. Crear base de datos

```bash
# PostgreSQL
psql -U postgres
CREATE DATABASE seguridad;
\q
```

### 5. Ejecutar migraciones

```bash
# Generar migración inicial
alembic revision --autogenerate -m "init schema"

# Aplicar migraciones
alembic upgrade head
```

### 6. Ejecutar aplicación

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en:
- Documentación Swagger: http://localhost:8000/docs
- API: http://localhost:8000/api/

## 🚀 Inicio Rápido

### Linux/Mac

```bash
chmod +x quick_start.sh
./quick_start.sh
```

### Windows

```bash
quick_start.bat
```

## 🎯 Uso

### 1. Registrar un usuario

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Admin",
    "apellido": "Sistema",
    "email": "admin@example.com",
    "password": "password123",
    "rol": "admin"
  }'
```

### 2. Crear una oficina

```bash
export TOKEN="eyJ..."  # Token del registro/login

curl -X POST http://localhost:8000/api/oficinas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre_oficina": "Oficina Central",
    "direccion": "Av. Principal 123",
    "ciudad": "Lima",
    "responsable": "Juan Pérez",
    "telefono_contacto": "+51999999999"
  }'
```

### 3. Registrar una cámara

```bash
curl -X POST http://localhost:8000/api/conexiones \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id_oficina": 1,
    "nombre_camara": "Cámara Entrada Principal",
    "ubicacion": "Puerta principal",
    "rtsp_url": "rtsp://username:password@192.168.1.100:554/stream1",
    "modo_ingesta": "SEGMENT",
    "habilitada": true,
    "retention_minutes": 60
  }'
```

### 4. Iniciar ingesta de cámara

```bash
# Iniciar una cámara específica
curl -X POST http://localhost:8000/api/admin/cameras/1/start \
  -H "Authorization: Bearer $TOKEN"

# Iniciar todas las cámaras habilitadas
curl -X POST http://localhost:8000/api/admin/cameras/start \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Webhook de inferencia

#### Contrato A (offsets relativos al clip)

```bash
curl -X POST http://localhost:8000/api/inferencia/resultados \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "abc-123",
    "conexion_id": 1,
    "clip_id": 42,
    "modelo_version": "v1.0.0",
    "eventos": [
      {
        "tipo": "golpe",
        "t_inicio_ms": 1200,
        "t_fin_ms": 3400,
        "confianza": 0.92
      }
    ]
  }'
```

#### Contrato B (timestamp absoluto)

```bash
curl -X POST http://localhost:8000/api/inferencia/resultados \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "def-456",
    "conexion_id": 1,
    "modelo_version": "v1.0.0",
    "eventos": [
      {
        "tipo": "forcejeo",
        "timestamp_utc": "2025-11-06T15:02:11.200Z",
        "dur_ms": 2300,
        "confianza": 0.87
      }
    ]
  }'
```

**Idempotencia:** El mismo `request_id` no se procesará dos veces.

### 6. Generar subclip de un evento

```bash
curl -X POST "http://localhost:8000/api/eventos/1/generar-subclip?padding=2" \
  -H "Authorization: Bearer $TOKEN"
```

## 📚 Documentación

### Documentación Principal

- **README.md** (este archivo) - Visión general
- **API_EXAMPLES.md** - Ejemplos de todos los endpoints
- **ESTRUCTURA_PROYECTO.md** - Árbol completo de directorios

### Documentación de Arquitectura DDD

- **ARQUITECTURA_DOMINIO.md** - Teoría y patrones DDD aplicados
- **EJEMPLO_USO_DOMINIO.md** - Ejemplos prácticos de entidades y VOs
- **VALIDACION_CAPA_DOMINIO.md** - Checklist de completitud (100%)
- **GUIA_MIGRACION_DOMINIO.md** - Cómo migrar a usar la capa de dominio

## 🔧 Configuración de retención

La retención se aplica automáticamente cada 60 segundos. Cada cámara tiene su propia política configurada en `retention_minutes`.

**Importante:** 
- Los clips en `STORAGE_BASE_PATH/events/` (subclips de eventos) **NO** se eliminan
- Solo se eliminan clips del buffer circular de cada cámara

### Aplicar retención manualmente

```bash
curl -X POST http://localhost:8000/api/admin/retention/apply \
  -H "Authorization: Bearer $TOKEN"
```

### Ver estado de retención

```bash
curl -X GET http://localhost:8000/api/admin/retention/status \
  -H "Authorization: Bearer $TOKEN"
```

## 🎬 Generación de subclips multi-clip

El sistema puede generar subclips que cruzan múltiples clips originales:

1. **Resolución de rangos:** El `ClipResolver` identifica todos los clips que intersectan el rango temporal
2. **Corte sin recodificar:** Usa `ffmpeg -c copy` para extraer segmentos
3. **Concatenación:** Usa demuxer `concat` para unir sin recodificar
4. **Fallback:** Si falla (problemas de GOP), recodifica solo el resultado final

## ⏰ Sincronización NTP/UTC

**Recomendaciones:**

1. **Sincronizar servidores con NTP:**
```bash
# Linux
sudo timedatectl set-ntp true

# Windows
w32tm /config /syncfromflags:manual /manualpeerlist:"time.windows.com"
w32tm /config /update
```

2. **Verificar timezone en PostgreSQL:**
```sql
SHOW timezone;
-- Debe ser UTC o configurar:
ALTER DATABASE seguridad SET timezone TO 'UTC';
```

3. **Todos los timestamps se almacenan en UTC** usando `TIMESTAMP WITH TIME ZONE`

## 📊 Entidades del Dominio

### Tablas principales

- **oficinas:** Oficinas físicas
- **conexiones:** Cámaras RTSP
- **clips:** Buffer de clips segmentados
- **usuarios:** Usuarios del sistema
- **eventos:** Eventos detectados por IA
- **notificaciones:** Notificaciones de eventos
- **reportes:** Reportes generados
- **inference_requests:** Control de idempotencia de webhooks
- **event_snapshots:** Snapshots/frames de eventos (opcional)

## 🔐 Seguridad

- **JWT:** Tokens con expiración configurable
- **Bcrypt:** Hashing de contraseñas
- **Idempotencia:** Webhooks idempotentes por `request_id` usando `InferenceRequest`
- **CORS:** Configurado (ajustar en producción)
- **Validaciones:** Centralizadas en entidades de dominio

## 🚀 Escalabilidad

El sistema está diseñado para escalar a **8+ cámaras:**

- Workers independientes por cámara (asyncio)
- Procesamiento async de clips
- Buffer circular con retención configurable
- Sin dependencias cloud
- Arquitectura DDD facilita evolución del sistema

## 📝 Endpoints principales

### Autenticación
- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token

### CRUD
- `/api/oficinas` - CRUD oficinas
- `/api/conexiones` - CRUD conexiones/cámaras
- `/api/clips` - Listado de clips
- `/api/eventos` - Eventos detectados
- `/api/notificaciones` - Notificaciones
- `/api/reportes` - Reportes

### Inferencia
- `POST /api/inferencia/resultados` - Webhook IA (contratos A y B)

### Administración
- `POST /api/admin/cameras/start` - Iniciar todas
- `POST /api/admin/cameras/{id}/start` - Iniciar cámara
- `POST /api/admin/cameras/{id}/stop` - Detener cámara
- `GET /api/admin/cameras/status` - Estado
- `POST /api/admin/retention/apply` - Aplicar retención
- `GET /api/admin/retention/status` - Estado retención

### Otros
- `GET /api/health` - Health check
- `GET /docs` - Documentación Swagger

## 🎯 Ventajas de la Arquitectura DDD

### ✅ Validación Centralizada

```python
# Antes (en múltiples lugares)
if len(nombre) > 150:
    raise HTTPException(...)

# Ahora (una sola vez en la entidad)
@dataclass(frozen=True)
class Oficina:
    nombre_oficina: str
    
    def __post_init__(self):
        if len(self.nombre_oficina) > 150:
            raise ValueError("excede 150 caracteres")
```

### ✅ Type Safety con Value Objects

```python
# Antes (fácil confundir IDs)
def crear_evento(conexion_id: int, clip_id: int):  # ¿Cuál es cuál?
    pass

# Ahora (el compilador detecta errores)
def crear_evento(conexion_id: IdConexion, clip_id: IdClip):
    pass

crear_evento(IdClip(42), IdConexion(7))  # ❌ Error de tipos!
```

### ✅ Testabilidad Sin Mocks

```python
def test_evento_duracion():
    evento = Evento(...)  # Sin BD, sin mocks
    assert evento.duracion_ms() == MilliSeconds(2500)
```

### ✅ Expresividad del Código

```python
# Antes
if evento.confianza >= 0.8:
    notify()

# Ahora
if evento.is_high_confidence(threshold=0.8):
    notify()
```

## 🐛 Troubleshooting

### FFmpeg no encontrado
```bash
# Verificar FFmpeg
ffmpeg -version

# Linux: instalar
sudo apt install ffmpeg

# Windows: descargar de ffmpeg.org y actualizar FFMPEG_PATH en .env
```

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql  # Linux
# O verificar servicios en Windows

# Verificar credenciales en DATABASE_URL
```

### Clips no se registran
- Verificar que el directorio `STORAGE_BASE_PATH` exista y tenga permisos
- Revisar logs de FFmpeg en stderr
- Verificar que RTSP URL sea accesible

## 🧪 Testing

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Ejecutar tests
pytest tests/

# Tests de dominio (sin BD)
pytest tests/domain/

# Tests de integración
pytest tests/integration/
```

## 📄 Licencia

Este proyecto es para uso interno.

## 👥 Contribuir

### Guía de Migración a Dominio

Si quieres contribuir usando la capa de dominio:

1. Lee `GUIA_MIGRACION_DOMINIO.md`
2. Crea servicios en `services_domain.py`
3. Usa adaptadores de `infrastructure/domain_repositories.py`
4. Escribe tests de dominio en `tests/domain/`

### Estructura de Commits

```
feat: añadir nueva funcionalidad
fix: corregir bug
refactor: refactorizar código
docs: actualizar documentación
test: añadir tests
```

## 📞 Soporte

Para soporte técnico, contactar al equipo de desarrollo.

---

**Versión:** 1.0.0  
**Python:** 3.11+  
**FastAPI:** 0.104.1  
**SQLAlchemy:** 2.0.23  
**Arquitectura:** Domain-Driven Design (DDD)