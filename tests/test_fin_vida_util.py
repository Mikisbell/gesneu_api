"""
Tests para la funcionalidad de alertas de fin de vida útil de neumáticos.
"""
import pytest
import uuid
from datetime import datetime, date, timedelta, timezone
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.usuario import Usuario
from models.fabricante import FabricanteNeumatico
from models.modelo import ModeloNeumatico
from models.neumatico import Neumatico
from models.alerta import Alerta
from schemas.common import TipoAlertaEnum

from services.alert_service import AlertService


@pytest.mark.asyncio
async def test_alerta_fin_vida_util_por_edad(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando un neumático supera la edad máxima."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_fin_vida_user1",
        email="test_fin_vida1@example.com",
        hashed_password="hash",
        nombre_completo="Test Fin Vida User 1",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear modelo
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestFinVida1",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático con fecha de fabricación antigua (más de 7 años)
    fecha_fabricacion_antigua = date.today() - timedelta(days=365 * 8)  # 8 años atrás
    
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-FIN-VIDA-001",
        modelo_id=modelo.id,
        fecha_compra=date.today() - timedelta(days=365 * 7.5),  # 7.5 años atrás
        fecha_fabricacion=fecha_fabricacion_antigua,
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK",
        kilometraje_acumulado=50000  # Kilometraje por debajo del límite
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Verificar que no hay alertas previas
    query_before = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_before = await db_session.exec(query_before)
    assert result_before.first() is None, "No debería haber alerta antes de la verificación"
    
    # Crear el servicio y ejecutar la verificación
    alert_service = AlertService(db_session)
    await alert_service._check_fin_vida_util(neumatico)
    
    # Verificar que se ha creado la alerta
    query_after = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_after = await db_session.exec(query_after)
    alerta = result_after.first()
    
    # Aserciones
    assert alerta is not None, "Debería haberse creado una alerta para el neumático con edad excesiva"
    assert "EDAD_MAXIMA" in alerta.datos_contexto.get("motivos", [])
    assert "años, superando el máximo recomendado" in alerta.descripcion


@pytest.mark.asyncio
async def test_alerta_fin_vida_util_por_kilometraje(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando un neumático supera el kilometraje máximo."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_fin_vida_user2",
        email="test_fin_vida2@example.com",
        hashed_password="hash",
        nombre_completo="Test Fin Vida User 2",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear modelo
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestFinVida2",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático con kilometraje excesivo pero edad adecuada
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-FIN-VIDA-002",
        modelo_id=modelo.id,
        fecha_compra=date.today() - timedelta(days=365 * 3),  # 3 años atrás (edad aceptable)
        fecha_fabricacion=date.today() - timedelta(days=365 * 3.5),  # 3.5 años atrás
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK",
        kilometraje_acumulado=90000  # Kilometraje por encima del límite (80000)
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Verificar que no hay alertas previas
    query_before = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_before = await db_session.exec(query_before)
    assert result_before.first() is None, "No debería haber alerta antes de la verificación"
    
    # Crear el servicio y ejecutar la verificación
    alert_service = AlertService(db_session)
    await alert_service._check_fin_vida_util(neumatico)
    
    # Verificar que se ha creado la alerta
    query_after = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_after = await db_session.exec(query_after)
    alerta = result_after.first()
    
    # Aserciones
    assert alerta is not None, "Debería haberse creado una alerta para el neumático con kilometraje excesivo"
    assert "KILOMETRAJE_MAXIMO" in alerta.datos_contexto.get("motivos", [])
    assert "km, superando el máximo recomendado" in alerta.descripcion


@pytest.mark.asyncio
async def test_no_alerta_fin_vida_util_parametros_normales(db_session: AsyncSession):
    """Prueba que no se genera una alerta cuando el neumático está dentro de los parámetros normales."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_fin_vida_user3",
        email="test_fin_vida3@example.com",
        hashed_password="hash",
        nombre_completo="Test Fin Vida User 3",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear modelo
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestFinVida3",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático con parámetros normales
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-FIN-VIDA-003",
        modelo_id=modelo.id,
        fecha_compra=date.today() - timedelta(days=365 * 2),  # 2 años atrás
        fecha_fabricacion=date.today() - timedelta(days=365 * 2.5),  # 2.5 años atrás
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK",
        kilometraje_acumulado=30000  # Kilometraje normal
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Verificar que no hay alertas previas
    query_before = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_before = await db_session.exec(query_before)
    assert result_before.first() is None, "No debería haber alerta antes de la verificación"
    
    # Crear el servicio y ejecutar la verificación
    alert_service = AlertService(db_session)
    await alert_service._check_fin_vida_util(neumatico)
    
    # Verificar que no se ha creado ninguna alerta
    query_after = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_after = await db_session.exec(query_after)
    alerta = result_after.first()
    
    # Aserciones
    assert alerta is None, "No debería haberse creado una alerta para el neumático con parámetros normales"
