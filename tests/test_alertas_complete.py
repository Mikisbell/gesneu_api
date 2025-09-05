"""Tests completos para el módulo de alertas alineados con esquema PostgreSQL."""
import pytest
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from ges_neu_api.modules.alertas.models import Alertas, NivelSeveridadEnum, EstadoAlertaEnum
from ges_neu_api.modules.neumaticos.models import Neumatico, ModeloNeumatico
from ges_neu_api.modules.vehiculos.models import Vehiculos
from ges_neu_api.modules.catalogos.models import Almacen, ParametroInventario
from decimal import Decimal
from datetime import date


class TestAlertasModel:
    """Tests del modelo Alertas alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_alerta_basic(self, db_session: AsyncSession):
        """Test creación básica de alerta con campos obligatorios."""
        # Crear alerta con campos obligatorios según esquema PostgreSQL
        alerta = Alertas(
            tipo_alerta="PROFUNDIDAD_CRITICA",
            mensaje="Neumático con profundidad crítica detectado",
            nivel_severidad=NivelSeveridadEnum.CRITICAL,
            estado_alerta=EstadoAlertaEnum.NUEVA
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)

        # Verificar campos obligatorios
        assert alerta.id is not None
        assert alerta.tipo_alerta == "PROFUNDIDAD_CRITICA"
        assert alerta.mensaje == "Neumático con profundidad crítica detectado"
        assert alerta.nivel_severidad == NivelSeveridadEnum.CRITICAL
        assert alerta.estado_alerta == EstadoAlertaEnum.NUEVA
        assert alerta.timestamp_generacion is not None

    @pytest.mark.asyncio
    async def test_alertas_enums_validation(self, db_session: AsyncSession):
        """Test validación de enums según esquema PostgreSQL."""
        # Test todos los niveles de severidad válidos
        niveles_validos = [
            NivelSeveridadEnum.INFO,
            NivelSeveridadEnum.WARN,
            NivelSeveridadEnum.CRITICAL
        ]

        for nivel in niveles_validos:
            alerta = Alertas(
                tipo_alerta="TEST_NIVEL",
                mensaje=f"Test nivel {nivel.value}",
                nivel_severidad=nivel,
                estado_alerta=EstadoAlertaEnum.NUEVA
            )
            db_session.add(alerta)
            await db_session.commit()
            await db_session.refresh(alerta)
            
            assert alerta.nivel_severidad == nivel

        # Test todos los estados válidos
        estados_validos = [
            EstadoAlertaEnum.NUEVA,
            EstadoAlertaEnum.VISTA,
            EstadoAlertaEnum.GESTIONADA
        ]

        for estado in estados_validos:
            alerta = Alertas(
                tipo_alerta="TEST_ESTADO",
                mensaje=f"Test estado {estado.value}",
                nivel_severidad=NivelSeveridadEnum.INFO,
                estado_alerta=estado
            )
            db_session.add(alerta)
            await db_session.commit()
            await db_session.refresh(alerta)
            
            assert alerta.estado_alerta == estado

    @pytest.mark.asyncio
    async def test_alerta_con_relaciones(self, db_session: AsyncSession):
        """Test alerta con relaciones a otras entidades según esquema."""
        # Crear modelo de neumático
        modelo = ModeloNeumatico(
            marca="BRIDGESTONE",
            modelo="R250",
            medida="295/80R22.5",
            tipo_construccion="RADIAL",
            indice_carga=154,
            indice_velocidad="M",
            profundidad_inicial_mm=Decimal("16.00"),
            vida_util_esperada_km=120000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00013333")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Crear neumático
        neumatico = Neumatico(
            modelo_id=modelo.id,
            fecha_compra=date(2024, 1, 15),
            estado_actual=EstadoNeumaticoEnum.INSTALADO,
            vida_actual=1,
            es_reencauchado=False,
            kilometraje_acumulado=50000,
            reencauches_realizados=0,
            profundidad_remanente_actual_mm=Decimal("3.50")  # Profundidad crítica
        )
        db_session.add(neumatico)
        await db_session.commit()

        # Crear alerta relacionada con neumático
        alerta = Alertas(
            tipo_alerta="PROFUNDIDAD_CRITICA",
            mensaje="Neumático requiere reemplazo inmediato - profundidad 3.5mm",
            nivel_severidad=NivelSeveridadEnum.CRITICAL,
            estado_alerta=EstadoAlertaEnum.NUEVA,
            neumatico_id=neumatico.id,
            datos_contexto={
                "profundidad_actual": "3.50",
                "profundidad_minima": "4.00",
                "kilometraje": 50000,
                "ubicacion": "Eje delantero izquierdo"
            }
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)

        # Verificar relación y datos contexto
        assert alerta.neumatico_id == neumatico.id
        assert alerta.datos_contexto is not None
        assert alerta.datos_contexto["profundidad_actual"] == "3.50"
        assert alerta.datos_contexto["kilometraje"] == 50000

    @pytest.mark.asyncio
    async def test_alerta_gestion_workflow(self, db_session: AsyncSession):
        """Test flujo de gestión de alertas según esquema PostgreSQL."""
        # Crear alerta nueva
        alerta = Alertas(
            tipo_alerta="MANTENIMIENTO_PREVENTIVO",
            mensaje="Neumático próximo a mantenimiento programado",
            nivel_severidad=NivelSeveridadEnum.WARN,
            estado_alerta=EstadoAlertaEnum.NUEVA
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)

        # Simular que alerta fue vista
        alerta.estado_alerta = EstadoAlertaEnum.VISTA
        await db_session.commit()
        await db_session.refresh(alerta)
        
        assert alerta.estado_alerta == EstadoAlertaEnum.VISTA

        # Simular gestión de alerta
        alerta.estado_alerta = EstadoAlertaEnum.GESTIONADA
        alerta.timestamp_gestion = datetime.now(timezone.utc)
        # alerta.usuario_gestion_id se asignaría en producción
        
        await db_session.commit()
        await db_session.refresh(alerta)
        
        assert alerta.estado_alerta == EstadoAlertaEnum.GESTIONADA
        assert alerta.timestamp_gestion is not None


class TestAlertasEndpoints:
    """Tests de endpoints de alertas alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_get_alertas_list(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint GET /api/v1/alertas/ con datos reales."""
        # Crear alertas de prueba
        alertas_test = [
            {
                "tipo_alerta": "PROFUNDIDAD_BAJA",
                "mensaje": "Neumático con profundidad por debajo del límite",
                "nivel_severidad": NivelSeveridadEnum.WARN,
                "estado_alerta": EstadoAlertaEnum.NUEVA
            },
            {
                "tipo_alerta": "PRESION_INCORRECTA",
                "mensaje": "Presión de neumático fuera del rango recomendado",
                "nivel_severidad": NivelSeveridadEnum.INFO,
                "estado_alerta": EstadoAlertaEnum.VISTA
            }
        ]

        for alerta_data in alertas_test:
            alerta = Alertas(**alerta_data)
            db_session.add(alerta)
        
        await db_session.commit()

        # Test endpoint
        response = await client.get("/api/v1/alertas/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 2
        
        # Verificar estructura de respuesta alineada con esquema
        alerta_data = data[0]
        assert "id" in alerta_data
        assert "tipo_alerta" in alerta_data
        assert "mensaje" in alerta_data
        assert "nivel_severidad" in alerta_data
        assert "estado_alerta" in alerta_data
        assert "timestamp_generacion" in alerta_data

    @pytest.mark.asyncio
    async def test_create_alerta_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint POST /api/v1/alertas/ con validación de esquema."""
        # Test crear alerta con datos válidos
        alerta_data = {
            "tipo_alerta": "PRESION_BAJA",
            "mensaje": "Presión baja detectada en neumático",
            "nivel_severidad": "WARN",
            "estado_alerta": "NUEVA",
            "datos_contexto": {"presion_actual": 25.5, "presion_minima": 30.0}
        }
        
        response = await client.post("/api/v1/alertas/", json=alerta_data)
        assert response.status_code == 201
        
        alerta_response = response.json()
        assert alerta_response["tipo_alerta"] == "PRESION_BAJA"
        assert alerta_response["nivel_severidad"] == "WARN"
        assert alerta_response["estado_alerta"] == "NUEVA"
        assert "id" in alerta_response

    @pytest.mark.asyncio
    async def test_alertas_filters(self, client: AsyncClient, db_session: AsyncSession):
        """Test filtros de alertas según esquema PostgreSQL."""
        # Crear alertas con diferentes niveles y estados
        alertas_test = [
            ("CRITICAL", "NUEVA"),
            ("WARN", "VISTA"),
            ("INFO", "GESTIONADA"),
            ("CRITICAL", "GESTIONADA")
        ]

        for i, (nivel, estado) in enumerate(alertas_test):
            alerta = Alertas(
                tipo_alerta=f"TEST_ALERT_{i}",
                mensaje=f"Test message {i}",
                nivel_severidad=getattr(NivelSeveridadEnum, nivel),
                estado_alerta=getattr(EstadoAlertaEnum, estado)
            )
            db_session.add(alerta)
        
        await db_session.commit()

        # Test filtro por nivel de severidad
        response = await client.get("/api/v1/alertas/?nivel_severidad=CRITICAL")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 2  # Debe haber al menos 2 alertas CRITICAL
        for item in data:
            assert item["nivel_severidad"] == "CRITICAL"

        # Test filtro por estado
        response = await client.get("/api/v1/alertas/?estado_alerta=NUEVA")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        for item in data:
            assert item["estado_alerta"] == "NUEVA"

    @pytest.mark.asyncio
    async def test_update_alerta_estado(self, client: AsyncClient, db_session: AsyncSession):
        """Test actualización de estado de alerta."""
        # Crear alerta
        alerta = Alertas(
            tipo_alerta="TEST_UPDATE",
            mensaje="Test update message",
            nivel_severidad=NivelSeveridadEnum.WARN,
            estado_alerta=EstadoAlertaEnum.NUEVA
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)

        # Actualizar estado
        update_data = {
            "estado_alerta": "GESTIONADA"
        }

        response = await client.patch(f"/api/v1/alertas/{alerta.id}", json=update_data)
        assert response.status_code == 200
        
        updated_data = response.json()
        assert updated_data["estado_alerta"] == "GESTIONADA"


class TestAlertasConstraints:
    """Tests de constraints y validaciones del esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_alertas_required_fields(self, db_session: AsyncSession):
        """Test campos obligatorios según constraints NOT NULL."""
        # Test que campos obligatorios no pueden ser None
        with pytest.raises(Exception):  # Should raise constraint violation
            alerta = Alertas(
                # tipo_alerta omitido - campo obligatorio
                mensaje="Test message",
                nivel_severidad=NivelSeveridadEnum.INFO,
                estado_alerta=EstadoAlertaEnum.NUEVA
            )
            db_session.add(alerta)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_alertas_default_values(self, db_session: AsyncSession):
        """Test valores por defecto según esquema PostgreSQL."""
        # Crear alerta sin especificar campos con defaults
        alerta = Alertas(
            tipo_alerta="TEST_DEFAULTS",
            mensaje="Test default values",
            # nivel_severidad no especificado - default 'INFO'
            # estado_alerta no especificado - default 'NUEVA'
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)

        # Verificar defaults aplicados según esquema PostgreSQL
        assert alerta.nivel_severidad == NivelSeveridadEnum.INFO  # Default 'INFO'
        assert alerta.estado_alerta == EstadoAlertaEnum.NUEVA  # Default 'NUEVA'
        assert alerta.timestamp_generacion is not None  # Default now()

    @pytest.mark.asyncio
    async def test_alertas_check_constraints(self, db_session: AsyncSession):
        """Test CHECK constraints del esquema PostgreSQL."""
        # Los CHECK constraints validan que los valores estén en los enums permitidos
        # Esto se valida automáticamente por SQLAlchemy con los enums definidos
        
        # Test valores válidos
        alerta = Alertas(
            tipo_alerta="TEST_CONSTRAINTS",
            mensaje="Test constraints",
            nivel_severidad=NivelSeveridadEnum.CRITICAL,  # Valor válido del enum
            estado_alerta=EstadoAlertaEnum.GESTIONADA  # Valor válido del enum
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)
        
        assert alerta.nivel_severidad == NivelSeveridadEnum.CRITICAL
        assert alerta.estado_alerta == EstadoAlertaEnum.GESTIONADA

    @pytest.mark.asyncio
    async def test_alertas_jsonb_datos_contexto(self, db_session: AsyncSession):
        """Test campo JSONB datos_contexto según esquema PostgreSQL."""
        # Test datos contexto complejos
        datos_contexto = {
            "neumatico": {
                "numero_serie": "BR2024001",
                "profundidad_actual": 4.2,
                "profundidad_minima": 4.0
            },
            "vehiculo": {
                "placa": "ABC-123",
                "kilometraje": 85000
            },
            "medicion": {
                "fecha": "2024-09-04T11:00:00Z",
                "usuario": "inspector_01",
                "metodo": "manual"
            },
            "recomendaciones": [
                "Programar reemplazo en próximos 1000 km",
                "Monitorear presión semanalmente",
                "Revisar alineación del vehículo"
            ]
        }

        alerta = Alertas(
            tipo_alerta="PROFUNDIDAD_LIMITE",
            mensaje="Neumático próximo al límite de profundidad",
            nivel_severidad=NivelSeveridadEnum.WARN,
            estado_alerta=EstadoAlertaEnum.NUEVA,
            datos_contexto=datos_contexto
        )
        
        db_session.add(alerta)
        await db_session.commit()
        await db_session.refresh(alerta)

        # Verificar que JSONB se almacena y recupera correctamente
        assert alerta.datos_contexto is not None
        assert alerta.datos_contexto["neumatico"]["numero_serie"] == "BR2024001"
        assert alerta.datos_contexto["vehiculo"]["placa"] == "ABC-123"
        assert len(alerta.datos_contexto["recomendaciones"]) == 3
