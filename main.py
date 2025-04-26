# main.py
from fastapi import FastAPI
# --- Importar asynccontextmanager ---
from contextlib import asynccontextmanager # <--- Importar esto

# Importar SQLModel y tu función init_db
from sqlmodel import SQLModel # Asegúrate que SQLModel se importe si no lo estaba ya
from database import settings, init_db

# importa tus routers...
from routers.vehiculos import router as vehiculos_router
from routers.auth import router as auth_router # <--- ASEGÚRATE DE IMPORTARLO
from routers.usuarios import router as usuarios_router # <--- Importar el nuevo router

# Importa otros routers que tengas...
# from routers.neumaticos import router as neumaticos_router
# from routers.auth import router as auth_router


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

# --- Eliminar el decorador @app.on_event ---
# @app.on_event("startup")   <--- Eliminar esta línea
# async def on_startup():    <--- Eliminar esta línea
#     await init_db()        <--- Eliminar esta línea
# incluye routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(usuarios_router, prefix="/usuarios", tags=["Usuarios"]) # <--- Incluir el 
app.include_router(vehiculos_router, prefix="/vehiculos", tags=["Vehículos"])


# Incluye tus otros routers aquí...
# app.include_router(neumaticos_router, prefix="/neumaticos", tags=["Neumáticos y Eventos"])
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


# Puedes añadir una ruta raíz simple para verificar que la app corre
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Bienvenido a {settings.APP_NAME}"}                                                    