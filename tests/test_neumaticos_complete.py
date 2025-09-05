"""Tests completos para el módulo de neumáticos alineados con esquema PostgreSQL."""
import pytest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4, UUID
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from ges_neu_api.core.test_models import (
    FabricanteNeumatico, ModeloNeumatico, Neumatico, EstadoNeumaticoEnum,
    Vehiculos, PosicionesNeumatico, TiposVehiculo
)


class TestNeumaticoModel:
    """Tests del modelo Neumatico alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_neumatico_basic(self, db_session: AsyncSession):
        """Test creación básica de neumático con campos obligatorios."""
        # Crear fabricante primero
        fabricante = FabricanteNeumatico(
            nombre="BRIDGESTONE",
            codigo_abreviado="BS",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()

        # Crear modelo de neumático con campos exactos del esquema PostgreSQL
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="R250",
            medida="295/80R22.5",
            tipo_construccion="RADIAL",
            indice_carga=154,
            indice_velocidad="M",
            profundidad_original_mm=Decimal("16.00"),
            vida_util_esperada_km=120000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00013333")
        )
        db_session.add(modelo)
        await db_session.commit()
        await db_session.refresh(modelo)

        # Crear neumático con campos obligatorios según esquema PostgreSQL
        neumatico = Neumatico(
            numero_serie="NEU001",
            dot="1524",
            modelo_id=modelo.id,
            fecha_compra=date(2024, 1, 15),
            fecha_fabricacion=date(2024, 1, 1),
            costo_compra=Decimal("850.00"),
            moneda_compra="PEN",
            es_reencauchado=False,
            vida_actual=1,
            estado_actual=EstadoNeumaticoEnum.EN_STOCK,
            profundidad_inicial_mm=Decimal("16.00"),
            profundidad_remanente_actual_mm=Decimal("15.50"),
            kilometraje_acumulado=0,
            kilometraje_vida_actual=0,
            reencauches_realizados=0,
            activo=True
        )
        
        db_session.add(neumatico)
        await db_session.commit()
        await db_session.refresh(neumatico)

        # Verificar campos obligatorios
        assert neumatico.id is not None
        assert neumatico.modelo_id == modelo.id
        assert neumatico.fecha_compra == date(2024, 1, 15)
        assert neumatico.estado_actual == EstadoNeumaticoEnum.EN_STOCK
        assert neumatico.vida_actual == 1
        assert neumatico.es_reencauchado is False
        assert neumatico.kilometraje_acumulado == 0
        assert neumatico.reencauches_realizados == 0
        assert neumatico.profundidad_remanente_actual_mm == Decimal("15.50")
        assert neumatico.activo is True  # Default value

    @pytest.mark.asyncio
    async def test_neumatico_estados_enum(self, db_session: AsyncSession):
        """Test validación de estados del enum según PostgreSQL."""
        # Crear fabricante primero (requerido por foreign key)
        fabricante = FabricanteNeumatico(
            nombre="MICHELIN",
            codigo_abreviado="MIC",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        # Crear modelo con campos exactos del esquema PostgreSQL
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="XZE2",
            medida="315/80R22.5",
            indice_carga="156",
            indice_velocidad="L",
            profundidad_original_mm=Decimal("17.00"),
            permite_reencauche=True,
            vida_util_teorica_km=150000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00011333")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Test todos los estados válidos del enum PostgreSQL
        estados_validos = [
            EstadoNeumaticoEnum.EN_STOCK,
            EstadoNeumaticoEnum.INSTALADO,
            EstadoNeumaticoEnum.EN_REPARACION,
            EstadoNeumaticoEnum.EN_REENCAUCHE,
            EstadoNeumaticoEnum.DESECHADO,
            EstadoNeumaticoEnum.EN_TRANSITO
        ]

        for estado in estados_validos:
            neumatico = Neumatico(
                modelo_id=modelo.id,
                fecha_compra=date(2024, 1, 15),
                estado_actual=estado,
                vida_actual=1,
                es_reencauchado=False,
                kilometraje_acumulado=0,
                reencauches_realizados=0,
                profundidad_remanente_actual_mm=Decimal("16.00")
            )
            db_session.add(neumatico)
            await db_session.commit()
            await db_session.refresh(neumatico)
            
            assert neumatico.estado_actual == estado

    @pytest.mark.asyncio
    async def test_neumatico_campos_numericos_precision(self, db_session: AsyncSession):
        """Test precisión de campos numéricos según esquema PostgreSQL."""
        # Crear fabricante primero (requerido por foreign key)
        fabricante = FabricanteNeumatico(
            nombre="CONTINENTAL",
            codigo_abreviado="CON",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        # Crear modelo con campos exactos del esquema PostgreSQL
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="HSR2",
            medida="295/80R22.5",
            indice_carga="152",
            indice_velocidad="M",
            profundidad_original_mm=Decimal("15.50"),
            permite_reencauche=True,
            vida_util_teorica_km=130000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00011923")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Test campos con precisión específica NUMERIC(5,2) y NUMERIC(10,2)
        neumatico = Neumatico(
            modelo_id=modelo.id,
            fecha_compra=date(2024, 2, 1),
            estado_actual=EstadoNeumaticoEnum.EN_STOCK,
            vida_actual=1,
            es_reencauchado=False,
            kilometraje_acumulado=25000,
            reencauches_realizados=0,
            profundidad_remanente_actual_mm=Decimal("12.75"),  # NUMERIC(5,2)
            costo_compra=Decimal("850.50"),  # NUMERIC(10,2)
            profundidad_inicial_mm=Decimal("15.50"),  # NUMERIC(5,2)
            tasa_desgaste_actual_mm_km=Decimal("0.00011000")  # NUMERIC(10,8)
        )
        
        db_session.add(neumatico)
        await db_session.commit()
        await db_session.refresh(neumatico)

        # Verificar precisión mantenida
        assert neumatico.profundidad_remanente_actual_mm == Decimal("12.75")
        assert neumatico.costo_compra == Decimal("850.50")
        assert neumatico.profundidad_inicial_mm == Decimal("15.50")
        assert neumatico.tasa_desgaste_actual_mm_km == Decimal("0.00011000")

    @pytest.mark.asyncio
    async def test_neumatico_default_values(self, db_session: AsyncSession):
        """Test valores por defecto según esquema PostgreSQL."""
        # Crear fabricante primero (requerido por foreign key)
        fabricante = FabricanteNeumatico(
            nombre="KUMHO",
            codigo_abreviado="KUM",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="KRD02",
            medida="295/80R22.5",
            indice_carga="152",
            indice_velocidad="M",
            profundidad_original_mm=Decimal("15.50"),
            permite_reencauche=True,
            vida_util_teorica_km=128000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00012109")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Crear neumático sin especificar campos con defaults
        neumatico = Neumatico(
            modelo_id=modelo.id,
            fecha_compra=date(2024, 1, 15),
            estado_actual=EstadoNeumaticoEnum.EN_STOCK,
            vida_actual=1,
            es_reencauchado=False,
            # kilometraje_acumulado debería defaultear a 0
            reencauches_realizados=0,
            profundidad_remanente_actual_mm=Decimal("15.50")
        )
        db_session.add(neumatico)
        await db_session.commit()
        await db_session.refresh(neumatico)

        # Verificar defaults aplicados
        assert neumatico.kilometraje_acumulado == 0
        assert neumatico.activo is True


class TestNeumaticoEndpoints:
    """Tests de endpoints REST para neumáticos."""

    def mock_current_user(self):
        """Mock para usuario autenticado usando token real."""
        return {
            "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12",  # UUID del token real
            "email": "test@example.com",
            "nombre": "Test User",
            "activo": True
        }

    @pytest.mark.asyncio
    async def test_create_neumatico_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint POST /api/v1/neumaticos/ con validación de esquema."""
        # Override de la dependencia de autenticación
        from ges_neu_api.modules.auth.dependencies import get_current_user
        from ges_neu_api.main import app
        
        app.dependency_overrides[get_current_user] = lambda: self.mock_current_user()
        # Crear fabricante y modelo de prueba
        fabricante = FabricanteNeumatico(
            nombre="GOODYEAR",
            codigo_abreviado="GY",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="G159",
            medida="315/80R22.5",
            indice_carga="156",
            indice_velocidad="L",
            profundidad_original_mm=Decimal("16.00"),
            permite_reencauche=True,
            vida_util_teorica_km=140000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00011429")
        )
        db_session.add(modelo)
        await db_session.commit()

        neumatico = Neumatico(
            numero_serie="GT2024001",
            dot="DOT 0124",
            modelo_id=modelo.id,
            fecha_compra=date(2024, 1, 15),
            estado_actual=EstadoNeumaticoEnum.EN_STOCK,
            vida_actual=1,
            es_reencauchado=False,
            kilometraje_acumulado=0,
            reencauches_realizados=0,
            profundidad_remanente_actual_mm=Decimal("16.00")
        )
        db_session.add(neumatico)
        await db_session.commit()

        # Test endpoint (bypass auth para tests)
        response = await client.get("/api/v1/neumaticos/", headers={"Authorization": "Bearer test-token"})
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        # Verificar estructura de respuesta alineada con esquema
        neumatico_data = data[0]
        assert "id" in neumatico_data
        assert "numero_serie" in neumatico_data
        assert "estado_actual" in neumatico_data
        assert "vida_actual" in neumatico_data
        assert "kilometraje_acumulado" in neumatico_data
        assert "profundidad_remanente_actual_mm" in neumatico_data

    @pytest.mark.asyncio
    async def test_create_neumatico_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint POST /api/v1/neumaticos/ con validación de esquema."""
        # Crear tipo de vehículo y vehículo de prueba
        tipo_vehiculo = TiposVehiculo(
            nombre="Camión de Carga",
            descripcion="Camión para transporte de carga",
            categoria_principal="CAMION",
            ejes_standard=3,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()
        await db_session.refresh(tipo_vehiculo)
        
        vehiculo = Vehiculos(
            tipo_vehiculo_id=tipo_vehiculo.id,
            placa="ABC123",
            vin="CHASIS123",
            numero_economico="V001",
            marca="VOLVO",
            modelo_vehiculo="FH16",
            anio_fabricacion=2020,
            activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        # Crear fabricante y modelo
        fabricante = FabricanteNeumatico(
            nombre="BRIDGESTONE",
            codigo_abreviado="BRI",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="R249",
            medida="315/80R22.5",
            indice_carga="156",
            indice_velocidad="L",
            profundidad_original_mm=Decimal("16.50"),
            permite_reencauche=True,
            vida_util_teorica_km=140000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00011786")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Datos alineados con esquema PostgreSQL
        neumatico_data = {
            "numero_serie": "PR2024001",
            "dot": "DOT 0324",
            "modelo_id": str(modelo.id),
            "fecha_compra": "2024-03-15",
            "fecha_fabricacion": "2024-01-10",
            "costo_compra": 920.00,
            "moneda_compra": "PEN",
            "es_reencauchado": False,
            "vida_actual": 1,
            "estado_actual": "EN_STOCK",
            "kilometraje_acumulado": 0,
            "reencauches_realizados": 0,
            "profundidad_inicial_mm": 15.00,
            "profundidad_remanente_actual_mm": 15.00,
            "activo": True
        }

        response = await client.post("/api/v1/neumaticos/", json=neumatico_data)
        assert response.status_code == 200
        
        created_data = response.json()
        assert created_data["numero_serie"] == "PR2024001"
        assert created_data["estado_actual"] == "EN_STOCK"
        assert created_data["vida_actual"] == 1
        assert created_data["es_reencauchado"] is False
        
        # Limpiar override
        from ges_neu_api.main import app
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_neumatico_filters_by_estado(self, client: AsyncClient, db_session: AsyncSession):
        """Test filtros por estado según enum PostgreSQL."""
        # Override de la dependencia de autenticación
        from ges_neu_api.modules.auth.dependencies import get_current_user
        from ges_neu_api.main import app
        
        app.dependency_overrides[get_current_user] = lambda: self.mock_current_user()
        # Crear fabricante y modelo
        fabricante = FabricanteNeumatico(
            nombre="YOKOHAMA",
            codigo_abreviado="YOK",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="104ZR",
            medida="295/80R22.5",
            indice_carga="152",
            indice_velocidad="M",
            profundidad_original_mm=Decimal("16.50"),
            permite_reencauche=True,
            vida_util_teorica_km=135000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00012222")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Crear neumáticos con diferentes estados
        estados_test = [
            EstadoNeumaticoEnum.EN_STOCK,
            EstadoNeumaticoEnum.INSTALADO,
            EstadoNeumaticoEnum.EN_REPARACION
        ]

        for i, estado in enumerate(estados_test):
            neumatico = Neumatico(
                numero_serie=f"YK202400{i+1}",
                modelo_id=modelo.id,
                fecha_compra=date(2024, 1, 15),
                estado_actual=estado,
                vida_actual=1,
                es_reencauchado=False,
                kilometraje_acumulado=0,
                reencauches_realizados=0,
                profundidad_remanente_actual_mm=Decimal("16.50")
            )
            db_session.add(neumatico)
        
        await db_session.commit()

        # Test filtro por estado
        response = await client.get("/api/v1/neumaticos/?estado=EN_STOCK")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        for item in data:
            assert item["estado_actual"] == "EN_STOCK"
            
        # Limpiar override
        from ges_neu_api.main import app
        app.dependency_overrides.clear()


class TestNeumaticoConstraints:
    """Tests de constraints y validaciones del esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_neumatico_required_fields(self, db_session: AsyncSession):
        """Test campos obligatorios según constraints NOT NULL."""
        # Crear fabricante y modelo
        fabricante = FabricanteNeumatico(
            nombre="HANKOOK",
            codigo_abreviado="HAN",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="DH31",
            medida="315/80R22.5",
            indice_carga="156",
            indice_velocidad="L",
            profundidad_original_mm=Decimal("17.00"),
            permite_reencauche=True,
            vida_util_teorica_km=145000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00011724")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Test que campos obligatorios no pueden ser None
        with pytest.raises(Exception):  # Should raise constraint violation
            neumatico = Neumatico(
                modelo_id=modelo.id,
                # fecha_compra=None,  # Campo obligatorio omitido
                estado_actual=EstadoNeumaticoEnum.EN_STOCK,
                vida_actual=1,
                es_reencauchado=False,
                kilometraje_acumulado=0,
                reencauches_realizados=0,
                profundidad_remanente_actual_mm=Decimal("17.00")
            )
            db_session.add(neumatico)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_neumatico_default_values(self, db_session: AsyncSession):
        """Test valores por defecto según esquema PostgreSQL."""
        # Crear fabricante primero (requerido por foreign key)
        fabricante = FabricanteNeumatico(
            nombre="KUMHO",
            codigo_abreviado="KUM",
            activo=True
        )
        db_session.add(fabricante)
        await db_session.commit()
        await db_session.refresh(fabricante)
        
        modelo = ModeloNeumatico(
            fabricante_id=fabricante.id,
            nombre_modelo="KRD02",
            medida="295/80R22.5",
            indice_carga="152",
            indice_velocidad="M",
            profundidad_original_mm=Decimal("15.50"),
            permite_reencauche=True,
            vida_util_teorica_km=128000,
            tasa_desgaste_esperada_mm_km=Decimal("0.00012109")
        )
        db_session.add(modelo)
        await db_session.commit()

        # Crear neumático sin especificar campos con defaults
        neumatico = Neumatico(
            modelo_id=modelo.id,
            fecha_compra=date(2024, 1, 15),
            estado_actual=EstadoNeumaticoEnum.EN_STOCK,
            # vida_actual no especificado - default 1
            # es_reencauchado no especificado - default False
            # kilometraje_acumulado no especificado - default 0
            # reencauches_realizados no especificado - default 0
            profundidad_remanente_actual_mm=Decimal("15.50")
        )
        
        db_session.add(neumatico)
        await db_session.commit()
        await db_session.refresh(neumatico)

        # Verificar defaults aplicados
        assert neumatico.vida_actual == 1
        assert neumatico.es_reencauchado is False
        assert neumatico.kilometraje_acumulado == 0
        assert neumatico.reencauches_realizados == 0
        assert neumatico.activo is True  # Default según esquema
        assert neumatico.moneda_compra == "PEN"  # Default según esquema
