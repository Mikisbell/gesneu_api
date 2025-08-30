from fastapi import APIRouter

router = APIRouter(
    tags=["Neumáticos"],
    responses={404: {"description": "No encontrado"}},
)

# Aquí se añadirán las rutas (endpoints) para los neumáticos en el futuro.
# Por ejemplo:
# @router.get("/")
# async def listar_neumaticos():
#     return [{"id": 1, "modelo": "Ejemplo 1"}, {"id": 2, "modelo": "Ejemplo 2"}]

# @router.get("/{neumatico_id}")
# async def obtener_neumatico(neumatico_id: int):
#     return {"id": neumatico_id, "modelo": "Ejemplo"}

# @router.post("/")
# async def crear_neumatico():
#     return {"mensaje": "Neumático creado exitosamente"}
