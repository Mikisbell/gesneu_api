# main.py (Corregido para incluir vehiculos_router)
from fastapi import FastAPI
# --- MODIFICADO: Limpiar imports e incluir vehiculos_router ---
# Se elimina la línea duplicada "from routers import auth_router"
# Se añade vehiculos_router a la importación principal
from routers import auth_router, neumaticos_router, vehiculos_router
# --- FIN MODIFICACIÓN ---

# Opcional: Configuración adicional de CORS, etc. si es necesario
# from fastapi.middleware.cors import CORSMiddleware

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title="API GesNeuBD - Gestión de Neumáticos",
    description="API para gestionar el ciclo de vida de neumáticos.",
    version="0.1.0",
)

# Opcional: Configurar CORS si tu frontend está en un dominio diferente
# origins = [
#     "http://localhost",
#     "http://localhost:8080", # Ejemplo si tu frontend corre en el puerto 8080
#     # Añade aquí los orígenes permitidos
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Incluir los routers en la aplicación
app.include_router(auth_router.router) # Para /token (sin prefijo general)
app.include_router(
    neumaticos_router.router,
    prefix="/api/v1" # Prefijo común para las rutas de neumáticos/eventos
    # Los tags como "Neumáticos y Eventos" se definen mejor dentro del propio router
)
# --- MODIFICADO: Descomentar e incluir vehiculos_router ---
# Incluir el nuevo router de vehículos con su propio prefijo y tag
app.include_router(
    vehiculos_router.router,
    prefix="/api/v1/vehiculos", # Ruta base para los endpoints de vehículos
    tags=["Vehículos"] # Etiqueta para agrupar en /docs
)
# --- FIN MODIFICACIÓN ---


# Endpoint raíz simple
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bienvenido a la API de GesNeuBD"}

# Eventos de startup/shutdown (se mantienen comentados)
# @app.on_event("startup")
# async def on_startup():
#     # await init_db() # Crear tablas si no existen (cuidado si ya las creaste con SQL)
#     print("Iniciando API...")

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Cerrar conexión a BD, etc.
#     pass