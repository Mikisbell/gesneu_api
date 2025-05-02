# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlmodel import SQLModel
from database import settings, init_db

# Importa tus routers existentes...
from routers.vehiculos import router as vehiculos_router
from routers.auth import router as auth_router
from routers.usuarios import router as usuarios_router
from routers.neumaticos import router as neumaticos_router
# --- AÑADIR IMPORTACIÓN DEL NUEVO ROUTER ---
from routers.proveedores import router as proveedores_router
from routers.tipos_vehiculo import router as tipos_vehiculo_router
from routers.fabricantes_neumatico import router as fabricantes_router # <-- Nueva importación

# --- Definir el lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta ANTES de que la aplicación empiece a recibir requests
    print("Iniciando aplicación y base de datos...")
    await init_db() # Llama a tu función para crear tablas
    print("Base de datos lista.")
    yield
    # Código que se ejecuta DESPUÉS de que la aplicación termine (limpieza)
    print("Cerrando aplicación...")
    # Aquí podrías añadir código para cerrar conexiones si fuera necesario,
    # aunque SQLAlchemy suele manejarlo bien.

# --- Crear la app CON el lifespan ---
app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan # <--- Pasar la función lifespan aquí
)
# incluye routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(usuarios_router, prefix="/usuarios", tags=["Usuarios"]) # <--- Incluir el 
app.include_router(vehiculos_router, prefix="/vehiculos", tags=["Vehículos"])
app.include_router(neumaticos_router, prefix="/neumaticos", tags=["Neumáticos y Eventos"])
app.include_router(tipos_vehiculo_router)
app.include_router(proveedores_router)
app.include_router(fabricantes_router) # <-- Nueva línea

# Puedes añadir una ruta raíz simple para verificar que la app corre
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Bienvenido a {settings.APP_NAME}"}                                                    