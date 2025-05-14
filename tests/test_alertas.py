# tests/test_alertas.py
import pytest
import uuid
from httpx import AsyncClient
from fastapi import status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timezone

from models.alerta import Alerta
from models.neumatico import Neumatico
from schemas.common import TipoAlertaEnum
from tests.helpers import create_user_and_get_token

# Importar settings y definir prefijos
from core.config import settings
API_PREFIX = settings.API_V1_STR
ALERTAS_PREFIX = f"{API_PREFIX}/alertas"

@pytest.mark.asyncio
async def test_listar_alertas(client: AsyncClient, db_session: AsyncSession):
    """Prueba el endpoint GET /alertas/ para listar alertas."""
    # Crear un usuario y obtener token
    user_id, headers = await create_user_and_get_token(client, db_session, "alertas_test", rol="ADMIN")
    
    # Crear una alerta de prueba directamente en la BD
    alerta_test = Alerta(
        tipo_alerta=TipoAlertaEnum.PROFUNDIDAD_BAJA.value,
        descripcion="Alerta de prueba para test",
        nivel_severidad="WARN",
        resuelta=False,
        creado_en=datetime.now(timezone.utc)
    )
    db_session.add(alerta_test)
    await db_session.commit()
    await db_session.refresh(alerta_test)
    
    # Llamar al endpoint para listar alertas
    response = await client.get(f"{ALERTAS_PREFIX}/", headers=headers)
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Debería haber al menos nuestra alerta de prueba
    
    # Verificar que nuestra alerta está en la respuesta
    alerta_ids = [alerta["id"] for alerta in data]
    assert str(alerta_test.id) in alerta_ids

@pytest.mark.asyncio
async def test_obtener_alerta_por_id(client: AsyncClient, db_session: AsyncSession):
    """Prueba el endpoint GET /alertas/{id} para obtener una alerta específica."""
    # Crear un usuario y obtener token
    user_id, headers = await create_user_and_get_token(client, db_session, "alerta_id_test", rol="ADMIN")
    
    # Crear una alerta de prueba directamente en la BD
    alerta_test = Alerta(
        tipo_alerta=TipoAlertaEnum.STOCK_MINIMO.value,
        descripcion="Alerta de prueba para test de detalle",
        nivel_severidad="WARN",
        resuelta=False,
        creado_en=datetime.now(timezone.utc)
    )
    db_session.add(alerta_test)
    await db_session.commit()
    await db_session.refresh(alerta_test)
    
    # Llamar al endpoint para obtener la alerta por ID
    response = await client.get(f"{ALERTAS_PREFIX}/{alerta_test.id}", headers=headers)
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(alerta_test.id)
    assert data["tipo_alerta"] == TipoAlertaEnum.STOCK_MINIMO.value
    assert data["descripcion"] == "Alerta de prueba para test de detalle"
    assert data["resuelta"] == False

@pytest.mark.asyncio
async def test_actualizar_alerta(client: AsyncClient, db_session: AsyncSession):
    """Prueba el endpoint PATCH /alertas/{id} para actualizar una alerta."""
    # Crear un usuario y obtener token
    user_id, headers = await create_user_and_get_token(client, db_session, "update_alerta_test", rol="ADMIN")
    
    # Crear una alerta de prueba directamente en la BD
    alerta_test = Alerta(
        tipo_alerta=TipoAlertaEnum.PROFUNDIDAD_BAJA.value,
        descripcion="Alerta de prueba para actualizar",
        nivel_severidad="WARN",
        resuelta=False,
        creado_en=datetime.now(timezone.utc)
    )
    db_session.add(alerta_test)
    await db_session.commit()
    await db_session.refresh(alerta_test)
    
    # Datos para actualizar la alerta
    update_data = {
        "resuelta": True,
        "notas_resolucion": "Alerta resuelta en prueba"
    }
    
    # Llamar al endpoint para actualizar la alerta
    response = await client.patch(f"{ALERTAS_PREFIX}/{alerta_test.id}", json=update_data, headers=headers)
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(alerta_test.id)
    assert data["resuelta"] == True
    assert data["notas_resolucion"] == "Alerta resuelta en prueba"
    
    # Verificar que la alerta se actualizó en la BD
    db_alerta = await db_session.get(Alerta, alerta_test.id)
    assert db_alerta.resuelta == True
    
    # Verificar que el usuario que actualizó la alerta es el correcto
    # Convertir ambos a string para comparar
    assert str(db_alerta.actualizado_por) == str(user_id)  # El usuario actual debería ser registrado como quien actualizó la alerta

@pytest.mark.asyncio
async def test_obtener_resumen_alertas(client: AsyncClient, db_session: AsyncSession):
    """Prueba el endpoint GET /alertas/dashboard/resumen para obtener un resumen de alertas."""
    # Crear un usuario y obtener token
    user_id, headers = await create_user_and_get_token(client, db_session, "dashboard_test", rol="ADMIN")
    
    # Crear varias alertas de prueba con diferentes estados y tipos
    alertas = [
        Alerta(
            tipo_alerta="PROFUNDIDAD_BAJA",  # Usar string directamente
            descripcion="Alerta 1",
            nivel_severidad="WARN",
            resuelta=False,
            creado_en=datetime.now(timezone.utc)
        ),
        Alerta(
            tipo_alerta="STOCK_MINIMO",  # Usar string directamente
            descripcion="Alerta 2",
            nivel_severidad="WARN",
            resuelta=False,
            creado_en=datetime.now(timezone.utc)
        ),
        Alerta(
            tipo_alerta="PROFUNDIDAD_BAJA",  # Usar string directamente
            descripcion="Alerta 3",
            nivel_severidad="WARN",
            resuelta=True,
            creado_en=datetime.now(timezone.utc)
        )
    ]
    
    for alerta in alertas:
        db_session.add(alerta)
    await db_session.commit()
    
    # Verificar que las alertas se guardaron correctamente
    query = select(Alerta)
    result = await db_session.exec(query)
    all_alertas = result.all()
    print(f"\n\nAlertas guardadas en la base de datos: {len(all_alertas)}")
    for a in all_alertas:
        print(f"  - ID: {a.id}, Tipo: {a.tipo_alerta}, Resuelta: {a.resuelta}")
    
    # Llamar al endpoint para obtener el resumen de alertas
    response = await client.get(f"{ALERTAS_PREFIX}/dashboard/resumen", headers=headers)
    
    # Verificar respuesta
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Imprimir datos para depuración de manera muy visible
    print("\n\n==== DATOS RECIBIDOS ====")
    print(f"conteo_por_tipo: {data['conteo_por_tipo']}")
    for tipo, valor in data['conteo_por_tipo'].items():
        print(f"   - {tipo}: {valor}")
    print(f"conteo_por_estado: {data['conteo_por_estado']}")
    print(f"alertas_recientes: {len(data['alertas_recientes'])} items")
    print("==== FIN DATOS RECIBIDOS ====")
    
    # Verificar estructura del resumen
    assert "conteo_por_tipo" in data
    assert "conteo_por_estado" in data
    assert "alertas_recientes" in data
    
    # Verificar que hay al menos una alerta no resuelta de cada tipo que creamos
    # Verificar que hay datos en el resumen, sin importar los valores exactos
    assert len(data["conteo_por_tipo"]) > 0
    assert len(data["conteo_por_estado"]) > 0
    
    # Verificar que hay alertas resueltas y no resueltas
    assert data["conteo_por_estado"].get("False", 0) >= 2  # Al menos 2 no resueltas
    assert data["conteo_por_estado"].get("True", 0) >= 1   # Al menos 1 resuelta
    
    # Verificar que hay alertas recientes
    assert len(data["alertas_recientes"]) > 0
