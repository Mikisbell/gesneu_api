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
    
    # Crear el servicio y ejecutar la verificación sin evento (solo verifica edad y kilometraje)
    alert_service = AlertService(db_session)
    alerta = await alert_service._check_fin_vida_util(neumatico)
    
    # Verificar que no se ha creado ninguna alerta
    query_after = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_after = await db_session.exec(query_after)
    assert result_after.first() is None, "No debería haberse creado ninguna alerta para un neumático con parámetros normales"


@pytest.mark.asyncio
async def test_alerta_fin_vida_util_por_desgaste_avanzado(db_session: AsyncSession):
    """Prueba que se genera una alerta de advertencia cuando un neumático supera el umbral de desgaste avanzado."""
    # Configuración similar al test anterior pero con desgaste del 75% (advertencia)
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_desgaste_user2",
        email="test_desgaste2@example.com",
        hashed_password="hash",
        nombre_completo="Test Desgaste User 2",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestDesgaste2",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-DESGASTE-002",
        modelo_id=modelo.id,
        fecha_compra=date.today() - timedelta(days=365 * 1),
        fecha_fabricacion=date.today() - timedelta(days=365 * 1.5),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_USO",
        kilometraje_acumulado=30000
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear evento de inspección con desgaste avanzado (75%)
    from models.evento_neumatico import EventoNeumatico, TipoEventoNeumaticoEnum
    
    # Profundidad avanzada: 18mm - (18mm * 0.75) = 4.5mm (75% de desgaste)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION.value,
        usuario_id=usuario.id,
        timestamp_evento=datetime.now(timezone.utc),
        profundidad_remanente_mm=4.5,  # 75% de desgaste (advertencia)
        presion_psi=90,
        notas="Inspección de prueba con desgaste avanzado"
    )
    db_session.add(evento)
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
    alerta = await alert_service._check_fin_vida_util(neumatico, evento)
    
    # Aserciones
    assert alerta is not None, "Debería haberse creado una alerta para el neumático con desgaste avanzado"
    assert alerta.tipo_alerta == TipoAlertaEnum.PROFUNDIDAD_BAJA.value
    assert alerta.nivel_severidad == "WARN"
    assert "por debajo del mínimo recomendado" in alerta.descripcion
    assert alerta.datos_contexto["profundidad_actual"] == 4.5
    assert alerta.datos_contexto["profundidad_minima"] == 5.0  # Valor por defecto
    assert alerta.datos_contexto["unidad"] == "mm"


@pytest.mark.asyncio
async def test_no_alerta_fin_vida_util_sin_desgaste_significativo(db_session: AsyncSession):
    """Prueba que no se genera alerta cuando el desgaste es menor al umbral de advertencia."""
    # Configuración similar a los tests anteriores pero con desgaste del 50%
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_desgaste_user3",
        email="test_desgaste3@example.com",
        hashed_password="hash",
        nombre_completo="Test Desgaste User 3",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestDesgaste3",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-DESGASTE-003",
        modelo_id=modelo.id,
        fecha_compra=date.today() - timedelta(days=180),  # 6 meses atrás
        fecha_fabricacion=date.today() - timedelta(days=365),  # 1 año atrás
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_USO",
        kilometraje_acumulado=15000
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear evento de inspección con desgaste normal (50%)
    from models.evento_neumatico import EventoNeumatico, TipoEventoNeumaticoEnum
    
    # Profundidad normal: 18mm - (18mm * 0.5) = 9mm (50% de desgaste)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION.value,
        usuario_id=usuario.id,
        timestamp_evento=datetime.now(timezone.utc),
        profundidad_remanente_mm=9.0,  # 50% de desgaste (normal)
        presion_psi=90,
        notas="Inspección de prueba con desgaste normal"
    )
    db_session.add(evento)
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
    alerta = await alert_service._check_fin_vida_util(neumatico, evento)
    
    # Aserciones - No debería generarse alerta
    assert alerta is None, "No debería generarse alerta para desgaste normal"
    
    # Verificar que no se creó ninguna alerta en la base de datos
    query_after = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.FIN_VIDA_UTIL_ESTIMADO.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_after = await db_session.exec(query_after)
    assert result_after.first() is None, "No debería haberse creado ninguna alerta"
