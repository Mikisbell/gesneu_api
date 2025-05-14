import pytest
import uuid
import json
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from models.neumatico import Neumatico
from models.modelo import ModeloNeumatico
from models.alerta import Alerta
from models.evento_neumatico import EventoNeumatico, TipoEventoNeumaticoEnum
from models.usuario import Usuario
from schemas.common import TipoAlertaEnum
from services.alert_service import AlertService

@pytest.mark.asyncio
async def test_check_limite_reencauches(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando un neumático alcanza el límite de reencauches."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_user",
        email="test@example.com",
        hashed_password="hash",  # En un caso real usar un hash adecuado
        nombre_completo="Test User",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo con un límite de reencauches
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloPrueba",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        reencauches_maximos=2,  # Límite de 2 reencauches
        permite_reencauche=True
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático que ya ha alcanzado el límite de reencauches
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-REENCAUCHE-001",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),  # Añadir fecha de compra obligatoria
        profundidad_inicial_mm=18.0,
        profundidad_actual_mm=10.0,
        reencauches_realizados=2,  # Ya tiene 2 reencauches (alcanza el límite)
        es_reencauchado=True,
        estado_actual="EN_STOCK"  # Agregar un estado válido
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento para el neumático (puede ser cualquier tipo)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
        fecha_evento=datetime.now(timezone.utc),
        usuario_id=usuario.id  # Añadir el ID de usuario creado anteriormente
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar la verificación
    alert_service = AlertService(db_session)
    await alert_service._check_limite_reencauches(neumatico)
    
    # Verificar que se creó una alerta
    from sqlmodel import select
    
    query = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.LIMITE_REENCAUCHES.value,
        Alerta.neumatico_id == neumatico.id
    )
    result = await db_session.exec(query)
    alerta = result.first()
    
    # Aserciones
    assert alerta is not None, "No se generó la alerta de límite de reencauches"
    assert alerta.nivel_severidad == "WARN"
    assert "límite de 2 reencauches" in alerta.descripcion
    
    # Verificar el contexto de la alerta
    assert alerta.datos_contexto is not None
    
    # Convertir a enteros para la comparación ya que los valores podrían estar almacenados como strings
    reencauches_realizados = int(alerta.datos_contexto.get("reencauches_realizados")) if alerta.datos_contexto.get("reencauches_realizados") is not None else None
    reencauches_maximos = int(alerta.datos_contexto.get("reencauches_maximos")) if alerta.datos_contexto.get("reencauches_maximos") is not None else None
    
    assert reencauches_realizados == 2
    assert reencauches_maximos == 2

@pytest.mark.asyncio
async def test_no_alerta_cuando_no_alcanza_limite_reencauches(db_session: AsyncSession):
    """Prueba que NO se genera una alerta cuando un neumático NO ha alcanzado su límite de reencauches."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_user2",
        email="test2@example.com",
        hashed_password="hash",
        nombre_completo="Test User 2",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo con un límite de reencauches
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloPrueba2",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        reencauches_maximos=3,  # Límite de 3 reencauches
        permite_reencauche=True
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático que NO ha alcanzado el límite de reencauches
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-REENCAUCHE-002",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=1,  # Solo tiene 1 reencauche (no alcanza el límite de 3)
        es_reencauchado=True,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento para el neumático
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
        fecha_evento=datetime.now(timezone.utc),
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar la verificación
    alert_service = AlertService(db_session)
    await alert_service._check_limite_reencauches(neumatico)
    
    # Verificar que NO se creó una alerta
    query = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.LIMITE_REENCAUCHES.value,
        Alerta.neumatico_id == neumatico.id
    )
    result = await db_session.exec(query)
    alerta = result.first()
    
    # Aserciones - no debe haber alerta
    assert alerta is None, "Se generó una alerta cuando no debería"

@pytest.mark.asyncio
async def test_no_alerta_cuando_modelo_no_permite_reencauche(db_session: AsyncSession):
    """Prueba que NO se genera una alerta cuando el modelo del neumático no permite reencauche."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_user3",
        email="test3@example.com",
        hashed_password="hash",
        nombre_completo="Test User 3",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo que NO permite reencauche
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloSinReencauche",
        medida="315/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=20.0,
        reencauches_maximos=0,  # No aplica ya que no permite reencauche
        permite_reencauche=False  # No permite reencauche
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático con reencauches (aunque el modelo no lo permita)
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-NO-REENCAUCHE",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=20.0,
        reencauches_realizados=1,  # Tiene 1 reencauche (pero el modelo no permite reencauche)
        es_reencauchado=True,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear el servicio y ejecutar la verificación
    alert_service = AlertService(db_session)
    await alert_service._check_limite_reencauches(neumatico)
    
    # Verificar que NO se creó una alerta
    query = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.LIMITE_REENCAUCHES.value,
        Alerta.neumatico_id == neumatico.id
    )
    result = await db_session.exec(query)
    alerta = result.first()
    
    # Aserciones - no debe haber alerta
    assert alerta is None, "Se generó una alerta para un modelo que no permite reencauche"

@pytest.mark.asyncio
async def test_check_and_create_alerts_limite_reencauches(db_session: AsyncSession):
    """Prueba la integración del método check_and_create_alerts para el límite de reencauches."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_user4",
        email="test4@example.com",
        hashed_password="hash",
        nombre_completo="Test User 4",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo con un límite de reencauches
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestIntegracion",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        reencauches_maximos=1,  # Límite de 1 reencauche
        permite_reencauche=True
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático que ha alcanzado el límite de reencauches
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-INTEGRACION-001",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=1,  # Igual al límite de reencauches
        es_reencauchado=True,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento de reencauche salida (esto es lo que debería desencadenar la verificación)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.REENCAUCHE_SALIDA,
        fecha_evento=datetime.now(timezone.utc),
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar el método público check_and_create_alerts
    alert_service = AlertService(db_session)
    await alert_service.check_and_create_alerts(neumatico, evento)
    
    # Verificar que se creó una alerta
    query = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.LIMITE_REENCAUCHES.value,
        Alerta.neumatico_id == neumatico.id
    )
    result = await db_session.exec(query)
    alerta = result.first()
    
    # Aserciones
    assert alerta is not None, "No se generó la alerta de límite de reencauches mediante check_and_create_alerts"
    assert alerta.nivel_severidad == "WARN"
    assert "límite de 1 reencauche" in alerta.descripcion
    
    # Verificar el contexto de la alerta
    assert alerta.datos_contexto is not None
    
    # Convertir a enteros para la comparación ya que los valores podrían estar almacenados como strings
    reencauches_realizados = int(alerta.datos_contexto.get("reencauches_realizados")) if alerta.datos_contexto.get("reencauches_realizados") is not None else None
    reencauches_maximos = int(alerta.datos_contexto.get("reencauches_maximos")) if alerta.datos_contexto.get("reencauches_maximos") is not None else None
    
    assert reencauches_realizados == 1
    assert reencauches_maximos == 1

@pytest.mark.asyncio
async def test_check_presion_baja(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando la presión está por debajo del mínimo recomendado."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_presion_user",
        email="test_presion@example.com",
        hashed_password="hash",
        nombre_completo="Test Presion User",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo con presión recomendada
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestPresion",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        presion_recomendada_psi=100.0,  # Presión recomendada 100 PSI
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-PRESION-001",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento de inspección con presión baja (80 PSI, 80% de la recomendada)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION,
        fecha_evento=datetime.now(timezone.utc),
        presion_psi=80.0,  # Presión por debajo del mínimo (85% de 100 = 85 PSI)
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar el método de verificación de presión
    alert_service = AlertService(db_session)
    await alert_service._check_presion_anormal(neumatico, evento)
    
    # Verificar que se creó una alerta
    query = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.PRESION_BAJA.value,
        Alerta.neumatico_id == neumatico.id
    )
    result = await db_session.exec(query)
    alerta = result.first()
    
    # Aserciones
    assert alerta is not None, "No se generó la alerta de presión baja"
    assert alerta.nivel_severidad == "WARN"
    assert "por debajo del mínimo recomendado" in alerta.descripcion
    
    # Verificar el contexto de la alerta
    assert alerta.datos_contexto is not None
    
    # Convertir a flotantes para la comparación ya que los valores podrían estar almacenados como strings
    presion_actual = float(alerta.datos_contexto.get("presion_actual")) if alerta.datos_contexto.get("presion_actual") is not None else None
    presion_recomendada = float(alerta.datos_contexto.get("presion_recomendada")) if alerta.datos_contexto.get("presion_recomendada") is not None else None
    
    assert presion_actual == 80.0
    assert presion_recomendada == 100.0

@pytest.mark.asyncio
async def test_check_presion_alta(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando la presión está por encima del máximo recomendado."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_presion_user2",
        email="test_presion2@example.com",
        hashed_password="hash",
        nombre_completo="Test Presion User 2",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo con presión recomendada
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestPresion2",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        presion_recomendada_psi=100.0,  # Presión recomendada 100 PSI
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-PRESION-002",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento de inspección con presión alta (120 PSI, 120% de la recomendada)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION,
        fecha_evento=datetime.now(timezone.utc),
        presion_psi=120.0,  # Presión por encima del máximo (115% de 100 = 115 PSI)
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar el método de verificación de presión
    alert_service = AlertService(db_session)
    await alert_service._check_presion_anormal(neumatico, evento)
    
    # Verificar que se creó una alerta
    query = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.PRESION_ALTA.value,
        Alerta.neumatico_id == neumatico.id
    )
    result = await db_session.exec(query)
    alerta = result.first()
    
    # Aserciones
    assert alerta is not None, "No se generó la alerta de presión alta"
    assert alerta.nivel_severidad == "WARN"
    assert "por encima del máximo recomendado" in alerta.descripcion
    
    # Verificar el contexto de la alerta
    assert alerta.datos_contexto is not None
    
    # Convertir a flotantes para la comparación ya que los valores podrían estar almacenados como strings
    presion_actual = float(alerta.datos_contexto.get("presion_actual")) if alerta.datos_contexto.get("presion_actual") is not None else None
    presion_recomendada = float(alerta.datos_contexto.get("presion_recomendada")) if alerta.datos_contexto.get("presion_recomendada") is not None else None
    
    assert presion_actual == 120.0
    assert presion_recomendada == 100.0

@pytest.mark.asyncio
async def test_no_alerta_presion_normal(db_session: AsyncSession):
    """Prueba que no se genera una alerta cuando la presión está dentro del rango normal."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_presion_user3",
        email="test_presion3@example.com",
        hashed_password="hash",
        nombre_completo="Test Presion User 3",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo con presión recomendada
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestPresion3",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        presion_recomendada_psi=100.0,  # Presión recomendada 100 PSI
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-PRESION-003",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento de inspección con presión normal (100 PSI, 100% de la recomendada)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION,
        fecha_evento=datetime.now(timezone.utc),
        presion_psi=100.0,  # Presión exactamente igual a la recomendada
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar el método de verificación de presión
    alert_service = AlertService(db_session)
    await alert_service._check_presion_anormal(neumatico, evento)
    
    # Verificar que no se crearon alertas
    query_baja = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.PRESION_BAJA.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_baja = await db_session.exec(query_baja)
    alerta_baja = result_baja.first()
    
    query_alta = select(Alerta).where(
        Alerta.tipo_alerta == TipoAlertaEnum.PRESION_ALTA.value,
        Alerta.neumatico_id == neumatico.id
    )
    result_alta = await db_session.exec(query_alta)
    alerta_alta = result_alta.first()
    
    # Aserciones
    assert alerta_baja is None, "Se generó una alerta de presión baja innecesariamente"
    assert alerta_alta is None, "Se generó una alerta de presión alta innecesariamente"

@pytest.mark.asyncio
async def test_check_desgaste_irregular(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando se detecta un desgaste irregular en la inspección de un neumático."""
    # Crear un usuario para el test
    usuario = Usuario(
        id=uuid.uuid4(),
        username="test_desgaste_user",
        email="test_desgaste@example.com",
        hashed_password="hash",
        nombre_completo="Test Desgaste User",
        activo=True
    )
    db_session.add(usuario)
    await db_session.commit()
    
    # Crear un modelo para el neumático
    modelo = ModeloNeumatico(
        id=uuid.uuid4(),
        nombre_modelo="ModeloTestDesgaste",
        medida="295/80R22.5",
        fabricante_id=uuid.uuid4(),
        profundidad_original_mm=18.0,
        permite_reencauche=True,
        reencauches_maximos=2
    )
    db_session.add(modelo)
    await db_session.commit()
    
    # Crear un neumático
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-DESGASTE-001",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento de inspección con diferentes profundidades que indican desgaste irregular
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION.value,  # Usar .value para el enum
        timestamp_evento=datetime.now(timezone.utc),
        profundidad_remanente_mm=10.0,  # Profundidad promedio
        profundidad_banda_izq=12.0,     # Profundidad en la banda izquierda
        profundidad_banda_der=8.0,      # Profundidad en la banda derecha
        profundidad_centro=10.0,         # Profundidad en el centro
        notas="Se observa desgaste irregular en los bordes laterales del neumático",
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar el método de verificación de desgaste irregular
    alert_service = AlertService(db_session)
    alerta = await alert_service._check_desgaste_irregular(neumatico, evento)
    
    # Verificar que se creó una alerta
    assert alerta is not None, "No se generó la alerta de desgaste irregular"
    assert alerta.nivel_severidad == "WARN"
    assert "Desgaste irregular detectado" in alerta.descripcion
    
    # Verificar el contexto de la alerta
    assert alerta.datos_contexto is not None
    
    # Verificar que se detectaron motivos de desgaste irregular
    motivos = alerta.datos_contexto.get("motivos", [])
    assert len(motivos) > 0, "No se detectaron motivos de desgaste irregular"
    
    # Verificar que se incluyó el comentario en el contexto
    assert "comentarios" in alerta.datos_contexto
    assert "desgaste irregular" in alerta.datos_contexto["comentarios"].lower()

@pytest.mark.asyncio
async def test_check_desgaste_irregular_comentarios(db_session: AsyncSession):
    """Prueba que se genera una alerta cuando se detecta un desgaste irregular por los comentarios de la inspección."""
    # Crear un usuario para el test
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
    
    # Crear un modelo para el neumático
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
    
    # Crear un neumático
    neumatico = Neumatico(
        id=uuid.uuid4(),
        numero_serie="TEST-DESGASTE-002",
        modelo_id=modelo.id,
        fecha_compra=datetime.now(timezone.utc).date(),
        profundidad_inicial_mm=18.0,
        reencauches_realizados=0,
        es_reencauchado=False,
        estado_actual="EN_STOCK"
    )
    db_session.add(neumatico)
    await db_session.commit()
    
    # Crear un evento de inspección donde solo los comentarios indican desgaste (sin diferencia en profundidades)
    evento = EventoNeumatico(
        id=uuid.uuid4(),
        neumatico_id=neumatico.id,
        tipo_evento=TipoEventoNeumaticoEnum.INSPECCION.value,  # Usar .value para el enum
        timestamp_evento=datetime.now(timezone.utc),
        profundidad_remanente_mm=10.0,  # Profundidad promedio uniforme
        profundidad_banda_izq=10.0,     # Misma profundidad en todas las bandas
        profundidad_banda_der=10.0,
        profundidad_centro=10.0,
        notas="Se observa desgaste central pronunciado, posible sobrepresión",
        usuario_id=usuario.id
    )
    db_session.add(evento)
    await db_session.commit()
    
    # Crear el servicio y ejecutar el método de verificación de desgaste irregular
    alert_service = AlertService(db_session)
    alerta = await alert_service._check_desgaste_irregular(neumatico, evento)
    
    # Verificar que se creó una alerta
    assert alerta is not None, "No se generó la alerta de desgaste irregular a partir de los comentarios"
    assert alerta.nivel_severidad == "WARN"
    assert "Desgaste irregular detectado" in alerta.descripcion
    
    # Verificar el contexto de la alerta
    assert alerta.datos_contexto is not None
    
    # Verificar que se detectaron motivos de desgaste irregular
    motivos = alerta.datos_contexto.get("motivos", [])
    assert len(motivos) > 0, "No se detectaron motivos de desgaste irregular"
    
    # Verificar que se incluyó el comentario en el contexto
    assert "comentarios" in alerta.datos_contexto
    assert "desgaste central" in alerta.datos_contexto["comentarios"].lower()
    
    # Verificar que se detectó el motivo en los comentarios
    assert any("desgaste central" in str(motivo).lower() for motivo in motivos)
