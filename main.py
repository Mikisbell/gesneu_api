# main.py (Versión Corregida)

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware # Asegúrate de importar CORS

# --- CORRECCIÓN DE IMPORTS ---
from sqlmodel import SQLModel # Puede que no necesites SQLModel aquí directamente
from core.config import settings # Importar settings de core.config
from database import init_db     # Importar init_db de database
# -----------------------------

import models # Importar el paquete models para que SQLAlchemy descubra los modelos
# Importa tus routers existentes...
from routers.vehiculos import router as vehiculos_router
from routers.auth import router as auth_router
from routers.usuarios import router as usuarios_router
from routers.neumaticos import router as neumaticos_router
from routers.proveedores import router as proveedores_router
from routers.tipos_vehiculo import router as tipos_vehiculo_router
from routers.fabricantes_neumatico import router as fabricantes_router

# --- Definir el lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    # Considera si realmente quieres inicializar la BD en cada inicio
    # await init_db()
    # print("Base de datos inicializada.")
    yield
    print("Apagando aplicación...")

# --- Crear la app CON el lifespan ---
app = FastAPI(
    title=settings.PROJECT_NAME, # <-- CORREGIDO
    description="API para el Sistema de Gestión de Neumáticos V2 (GesNeu)",
    version="2.0.0", # Podrías poner esto en settings también
    lifespan=lifespan
)

# --- Configurar CORS ---
# (Asegúrate de tener esta sección o similar si necesitas CORS)
origins = []
if settings.BACKEND_CORS_ORIGINS:
     # Divide la cadena por comas y elimina espacios extra
    origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]

if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"], # Permite todos los métodos
        allow_headers=["*"], # Permite todos los headers
    )


# --- Incluir Routers con Prefijos ---
# Es buena práctica usar el API_V1_STR de la configuración
# En main.py (versión corregida que te di)
api_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(usuarios_router, prefix=f"{api_prefix}/usuarios", tags=["Usuarios"])
app.include_router(vehiculos_router, prefix=f"{api_prefix}/vehiculos", tags=["Vehículos"])
app.include_router(neumaticos_router, prefix=f"{api_prefix}/neumaticos", tags=["Neumáticos y Eventos"]) # Añadido prefijo
app.include_router(tipos_vehiculo_router, prefix=f"{api_prefix}/tipos-vehiculo", tags=["Tipos de Vehículo"]) # Añadido prefijo
app.include_router(proveedores_router, prefix=f"{api_prefix}/proveedores", tags=["Proveedores"]) # Añadido prefijo
app.include_router(fabricantes_router, prefix=f"{api_prefix}/fabricantes-neumatico", tags=["Fabricantes Neumático"]) # Añadido prefijo

# --- Ruta Raíz ---
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Bienvenido a {settings.PROJECT_NAME}"} # <-- CORREGIDO

