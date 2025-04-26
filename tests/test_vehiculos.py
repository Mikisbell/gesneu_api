# tests/test_vehiculos.py
import pytest
import uuid # Asegurar import de uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession # <-- Import correcto

# Importa tus modelos y schemas necesarios
from models.usuario import Usuario
from models.tipo_vehiculo import TipoVehiculo
from models.vehiculo import Vehiculo # Importar Vehiculo para el assert final
from core.security import create_access_token

# No necesitas el fixture session_transaction aquí,
# la limpieza la maneja el scope="function" de db_session
# y el override asegura que se use la sesión correcta.

@pytest.mark.asyncio
async def test_crear_leer_eliminar_vehiculo(client: AsyncClient, db_session: AsyncSession):
    # --- Preparación ---
    # 1. Crear Tipo de Vehículo
    #    (Asegúrate que no haya conflictos si corre en paralelo, nombres únicos etc)
    tipo_vehiculo = TipoVehiculo(nombre="Camión Prueba Test")
    db_session.add(tipo_vehiculo)
    # ¡Necesitas esperar a que las operaciones de BD se completen!
    await db_session.commit()
    await db_session.refresh(tipo_vehiculo)
    tipo_vehiculo_id = tipo_vehiculo.id

    # 2. Crear Usuario de Prueba
    #    (Considera usar una función helper o fixture para crear usuarios)
    test_user = Usuario(username="testuser_veh", email="test_veh@example.com", rol="ADMIN")
    # test_user.password_hash = hash_password('password123') # Si usas hash
    db_session.add(test_user)
    await db_session.commit() # <-- await commit
    await db_session.refresh(test_user) # <-- await refresh

    # 3. Obtener Token
    access_token = create_access_token(data={"sub": test_user.username})
    headers = {"Authorization": f"Bearer {access_token}"}

    # --- Ejecución y Verificación ---
    # 1. Crear vehículo
    payload = {
        "numero_economico": "ECO-TEST-123",
        "placa": "TEST-VEH-1",
        "tipo_vehiculo_id": str(tipo_vehiculo_id) # ID como string
    }
    r = await client.post("/vehiculos/", json=payload, headers=headers)
    assert r.status_code == status.HTTP_201_CREATED, f"Status esperado 201, obtenido {r.status_code}: {r.text}"
    veh = r.json()
    vid = veh.get("id")
    assert vid, "La respuesta JSON debe contener el ID del vehículo creado"
    vid_uuid = uuid.UUID(vid) # Convertir a UUID para usar con la sesión

    # Opcional: Verificar en DB que se creó correctamente ANTES de seguir
    vehiculo_creado_db = await db_session.get(Vehiculo, vid_uuid)
    assert vehiculo_creado_db is not None
    assert vehiculo_creado_db.numero_economico == payload["numero_economico"]

    # 2. Leer vehículo
    r = await client.get(f"/vehiculos/{vid}", headers=headers)
    assert r.status_code == status.HTTP_200_OK, f"Status esperado 200, obtenido {r.status_code}: {r.text}"
    data = r.json()
    assert data["numero_economico"] == payload["numero_economico"]
    assert data["placa"] == payload["placa"]

    # 3. Eliminación lógica
    r = await client.delete(f"/vehiculos/{vid}", headers=headers)
    assert r.status_code == status.HTTP_204_NO_CONTENT, f"Status esperado 204, obtenido {r.status_code}: {r.text}"

    # 4. Verificar inactivo directamente en DB (más fiable que llamar a la lista)
    #    Refrescar el estado desde la DB después del DELETE
    db_session.expire(vehiculo_creado_db)
    vehiculo_tras_delete = await db_session.get(Vehiculo, vid_uuid)
    assert vehiculo_tras_delete is not None, f"Vehículo {vid} no encontrado en DB tras delete"
    assert not vehiculo_tras_delete.activo, f"Vehículo {vid} debería estar inactivo tras delete"
    assert vehiculo_tras_delete.fecha_baja is not None, f"Vehículo {vid} debería tener fecha_baja tras delete"

    # Opcional: Verificar llamando a la lista de inactivos si quieres probar ese endpoint también
    r_inactive = await client.get("/vehiculos/", params={"activo": "false"}, headers=headers)
    assert r_inactive.status_code == status.HTTP_200_OK
    items_inactivos = r_inactive.json()
    assert isinstance(items_inactivos, list), "La respuesta de vehículos inactivos debería ser una lista"
    inactivo_encontrado = any(item.get("id") == vid for item in items_inactivos)
    assert inactivo_encontrado, f"Vehículo {vid} no encontrado en listado de inactivos: {items_inactivos}"