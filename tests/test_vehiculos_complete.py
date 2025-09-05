"""Tests completos para el módulo de vehículos alineados con esquema PostgreSQL."""
import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

# Import test models for SQLite compatibility
from ges_neu_api.core.test_models import (
    Vehiculos, TiposVehiculo, ConfiguracionesEje, PosicionesNeumatico,
    TipoEjeEnum, LadoVehiculoEnum
)


class TestVehiculoModel:
    """Tests del modelo Vehiculo alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_vehiculo_basic(self, db_session: AsyncSession):
        """Test creación básica de vehículo con campos obligatorios."""
        # Crear tipo de vehículo primero - campos exactos según esquema PostgreSQL
        tipo_vehiculo = TiposVehiculo(
            nombre="CAMION_CARGA",
            descripcion="Camión de carga pesada",
            categoria_principal="TRANSPORTE",
            subtipo="CARGA_PESADA",
            ejes_standard=3,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        # Crear vehículo con campos obligatorios según esquema PostgreSQL
        vehiculo = Vehiculos(
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V001",
            placa="ABC-123",
            vin="1HGBH41JXMN109186",
            marca="VOLVO",
            modelo_vehiculo="FH16",
            anio_fabricacion=2020,
            activo=True
        )
        
        db_session.add(vehiculo)
        await db_session.commit()
        await db_session.refresh(vehiculo)

        # Verificar campos obligatorios según esquema PostgreSQL
        assert vehiculo.id is not None
        assert vehiculo.tipo_vehiculo_id == tipo_vehiculo.id
        assert vehiculo.numero_economico == "V001"
        assert vehiculo.placa == "ABC-123"
        assert vehiculo.vin == "1HGBH41JXMN109186"
        assert vehiculo.marca == "VOLVO"
        assert vehiculo.modelo_vehiculo == "FH16"
        assert vehiculo.anio_fabricacion == 2020
        assert vehiculo.activo is True
        assert vehiculo.fecha_alta is not None  # Default CURRENT_DATE
        assert vehiculo.creado_en is not None

    @pytest.mark.asyncio
    async def test_vehiculo_campos_opcionales(self, db_session: AsyncSession):
        """Test campos opcionales del vehículo según esquema."""
        # Crear tipo de vehículo
        tipo_vehiculo = TiposVehiculo(
            nombre="Camión Cisterna",
            descripcion="Vehículo para transporte de líquidos",
            categoria="PESADO",
            numero_ejes=4,
            capacidad_carga_kg=30000,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        # Crear vehículo con campos opcionales
        vehiculo = Vehiculos(
            placa="XYZ-789",
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V002",
            marca="SCANIA",
            modelo_vehiculo="R450",
            anio_fabricacion=2021,
            vin="YS2R4X20009123456",
            activo=True
        )
        
        db_session.add(vehiculo)
        await db_session.commit()
        await db_session.refresh(vehiculo)

        # Verificar campos opcionales
        assert vehiculo.vin == "YS2R4X20009123456"
        assert vehiculo.marca == "SCANIA"
        assert vehiculo.modelo_vehiculo == "R450"
        assert vehiculo.anio_fabricacion == 2021
        assert vehiculo.activo is True


class TestConfiguracionesEjeModel:
    """Tests del modelo ConfiguracionesEje alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_configuracion_eje(self, db_session: AsyncSession):
        """Test creación de configuración de eje."""
        # Crear tipo de vehículo y vehículo
        tipo_vehiculo = TiposVehiculo(
            nombre="Tractocamión",
            descripcion="Vehículo para arrastre de semirremolques",
            categoria="PESADO",
            numero_ejes=3,
            capacidad_carga_kg=40000,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        vehiculo = Vehiculos(
            placa="TRC-001",
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V003",
            marca="KENWORTH",
            modelo_vehiculo="T800",
            anio_fabricacion=2019,
            vin="1XKDDB0X0KJ123456",
            activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        # Crear configuración de eje según esquema PostgreSQL
        config_eje = ConfiguracionesEje(
            vehiculo_id=vehiculo.id,
            numero_eje=1,
            tipo_eje=TipoEjeEnum.DIRECCION,
            posicion_vehiculo="DELANTERO",
            neumaticos_por_lado=1,
            presion_recomendada_psi=Decimal("110.00"),
            carga_maxima_kg=7000,
            activo=True
        )
        
        db_session.add(config_eje)
        await db_session.commit()
        await db_session.refresh(config_eje)

        # Verificar campos
        assert config_eje.vehiculo_id == vehiculo.id
        assert config_eje.numero_eje == 1
        assert config_eje.tipo_eje == TipoEjeEnum.DIRECCION
        assert config_eje.posicion_vehiculo == "DELANTERO"
        assert config_eje.neumaticos_por_lado == 1
        assert config_eje.presion_recomendada_psi == Decimal("110.00")
        assert config_eje.carga_maxima_kg == 7000
        assert config_eje.activo is True

    @pytest.mark.asyncio
    async def test_tipo_eje_enum_validation(self, db_session: AsyncSession):
        """Test validación de enum TipoEje según PostgreSQL."""
        # Crear vehículo base
        tipo_vehiculo = TiposVehiculo(
            nombre="Camión 6x4",
            categoria="PESADO",
            numero_ejes=3,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        vehiculo = Vehiculos(
            placa="CAM-6X4",
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V004",
            marca="MERCEDES-BENZ",
            modelo_vehiculo="ACTROS",
            anio_fabricacion=2020,
            vin="WDB9444321L123456",
            activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        # Test todos los tipos de eje válidos según PostgreSQL
        tipos_validos = [
            TipoEjeEnum.DIRECCION,
            TipoEjeEnum.TRACCION,
            TipoEjeEnum.ARRASTRE,
            TipoEjeEnum.ELEVADOR,
            TipoEjeEnum.RETRACTIL,
            TipoEjeEnum.OTRO
        ]

        for i, tipo in enumerate(tipos_validos, 1):
            config_eje = ConfiguracionesEje(
                vehiculo_id=vehiculo.id,
                numero_eje=i,
                tipo_eje=tipo,
                posicion_vehiculo=f"EJE_{i}",
                neumaticos_por_lado=2,
                presion_recomendada_psi=Decimal("100.00"),
                carga_maxima_kg=10000,
                activo=True
            )
            db_session.add(config_eje)
            await db_session.commit()
            await db_session.refresh(config_eje)
            
            assert config_eje.tipo_eje == tipo


class TestPosicionesNeumaticoModel:
    """Tests del modelo PosicionesNeumatico alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_posicion_neumatico(self, db_session: AsyncSession):
        """Test creación de posición de neumático."""
        # Crear estructura completa: tipo -> vehículo -> configuración -> posición
        tipo_vehiculo = TiposVehiculo(
            nombre="Bus Interprovincial",
            categoria="PESADO",
            numero_ejes=2,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        vehiculo = Vehiculos(
            placa="BUS-001",
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V005",
            marca="MERCEDES-BENZ",
            modelo_vehiculo="OF1721",
            anio_fabricacion=2018,
            vin="9BM906024JB123456",
            activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        config_eje = ConfiguracionesEje(
            vehiculo_id=vehiculo.id,
            numero_eje=1,
            tipo_eje=TipoEjeEnum.DIRECCION,
            posicion_vehiculo="DELANTERO",
            neumaticos_por_lado=1,
            presion_recomendada_psi=Decimal("105.00"),
            carga_maxima_kg=6500,
            activo=True
        )
        db_session.add(config_eje)
        await db_session.commit()

        # Crear posición de neumático según esquema PostgreSQL
        posicion = PosicionesNeumatico(
            configuracion_eje_id=config_eje.id,
            codigo_posicion="1L",
            lado_vehiculo=LadoVehiculoEnum.IZQUIERDO,
            orden_posicion=1,
            es_repuesto=False,
            activo=True
        )
        
        db_session.add(posicion)
        await db_session.commit()
        await db_session.refresh(posicion)

        # Verificar campos
        assert posicion.configuracion_eje_id == config_eje.id
        assert posicion.codigo_posicion == "1L"
        assert posicion.lado_vehiculo == LadoVehiculoEnum.IZQUIERDO
        assert posicion.orden_posicion == 1
        assert posicion.es_repuesto is False
        assert posicion.activo is True

    @pytest.mark.asyncio
    async def test_lado_vehiculo_enum_validation(self, db_session: AsyncSession):
        """Test validación de enum LadoVehiculo según PostgreSQL."""
        # Crear estructura base
        tipo_vehiculo = TiposVehiculo(nombre="Test", categoria="LIVIANO", numero_ejes=2, activo=True)
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        vehiculo = Vehiculos(
            placa="TEST-001", tipo_vehiculo_id=tipo_vehiculo.id, numero_economico="V006",
            marca="TEST", modelo_vehiculo="TEST", anio_fabricacion=2020, activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        config_eje = ConfiguracionesEje(
            vehiculo_id=vehiculo.id, numero_eje=1, tipo_eje=TipoEjeEnum.DIRECCION,
            posicion_vehiculo="TEST", neumaticos_por_lado=1, 
            presion_recomendada_psi=Decimal("100.00"), carga_maxima_kg=5000, activo=True
        )
        db_session.add(config_eje)
        await db_session.commit()

        # Test todos los lados válidos según PostgreSQL
        lados_validos = [
            LadoVehiculoEnum.IZQUIERDO,
            LadoVehiculoEnum.DERECHO,
            LadoVehiculoEnum.CENTRAL,
            LadoVehiculoEnum.INDETERMINADO
        ]

        for i, lado in enumerate(lados_validos, 1):
            posicion = PosicionesNeumatico(
                configuracion_eje_id=config_eje.id,
                codigo_posicion=f"T{i}",
                lado_vehiculo=lado,
                orden_posicion=i,
                es_repuesto=False,
                activo=True
            )
            db_session.add(posicion)
            await db_session.commit()
            await db_session.refresh(posicion)
            
            assert posicion.lado_vehiculo == lado


class TestVehiculosEndpoints:
    """Tests de endpoints de vehículos alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_get_vehiculos_list(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint GET /api/v1/vehiculos/ con datos reales."""
        # Crear tipo y vehículo de prueba
        tipo_vehiculo = TiposVehiculo(
            nombre="Camión Liviano",
            categoria="LIVIANO",
            numero_ejes=2,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        vehiculo = Vehiculos(
            placa="TEST-123",
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V008",
            marca="ISUZU",
            modelo_vehiculo="NPR",
            anio_fabricacion=2019,
            vin="JALC4B16907123456",
            activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        # Test endpoint
        response = await client.get("/api/v1/vehiculos/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        # Verificar estructura de respuesta alineada con esquema
        vehiculo_data = data[0]
        assert "id" in vehiculo_data
        assert "placa" in vehiculo_data
        assert "marca" in vehiculo_data
        assert "modelo" in vehiculo_data
        assert "anio_fabricacion" in vehiculo_data
        assert "activo" in vehiculo_data

    @pytest.mark.asyncio
    async def test_get_tipos_vehiculo(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint GET /api/v1/vehiculos/tipos."""
        # Crear tipos de vehículo
        tipos_test = [
            {"nombre": "Sedán", "categoria": "LIVIANO", "numero_ejes": 2},
            {"nombre": "Camión Pesado", "categoria": "PESADO", "numero_ejes": 3}
        ]

        for tipo_data in tipos_test:
            tipo = TiposVehiculo(**tipo_data, activo=True)
            db_session.add(tipo)
        
        await db_session.commit()

        # Test endpoint
        response = await client.get("/api/v1/vehiculos/tipos")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 2
        
        # Verificar estructura
        tipo_data = data[0]
        assert "id" in tipo_data
        assert "nombre" in tipo_data
        assert "categoria" in tipo_data
        assert "numero_ejes" in tipo_data

    @pytest.mark.asyncio
    async def test_get_configuraciones_eje(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint GET /api/v1/vehiculos/configuraciones-eje."""
        # Crear estructura completa
        tipo_vehiculo = TiposVehiculo(nombre="Test Truck", categoria="PESADO", numero_ejes=2, activo=True)
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        vehiculo = Vehiculos(
            placa="CFG-001", tipo_vehiculo_id=tipo_vehiculo.id, numero_economico="V007",
            marca="TEST", modelo_vehiculo="CFG", anio_fabricacion=2020, activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        config_eje = ConfiguracionesEje(
            vehiculo_id=vehiculo.id, numero_eje=1, tipo_eje=TipoEjeEnum.DIRECCION,
            posicion_vehiculo="DELANTERO", neumaticos_por_lado=1, 
            presion_recomendada_psi=Decimal("100.00"), carga_maxima_kg=5000, activo=True
        )
        db_session.add(config_eje)
        await db_session.commit()

        # Test endpoint
        response = await client.get("/api/v1/vehiculos/configuraciones-eje")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        
        # Verificar estructura
        config_data = data[0]
        assert "id" in config_data
        assert "vehiculo_id" in config_data
        assert "numero_eje" in config_data
        assert "tipo_eje" in config_data

    @pytest.mark.asyncio
    async def test_create_vehiculo_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint POST /api/v1/vehiculos/ con validación de esquema."""
        # Crear tipo de vehículo primero
        tipo_vehiculo = TiposVehiculo(
            nombre="Pickup",
            categoria="LIVIANO",
            numero_ejes=2,
            activo=True
        )
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        # Datos alineados con esquema PostgreSQL
        vehiculo_data = {
            "placa": "PKP-001",
            "tipo_vehiculo_id": str(tipo_vehiculo.id),
            "marca": "TOYOTA",
            "modelo": "HILUX",
            "anio_fabricacion": 2021,
            "numero_chasis": "MR0FB22G0M0123456",
            "numero_motor": "2GD-FTV",
            "color": "BLANCO",
            "kilometraje_actual": 25000,
            "activo": True
        }

        response = await client.post("/api/v1/vehiculos/", json=vehiculo_data)
        assert response.status_code == 201
        
        created_data = response.json()
        assert created_data["placa"] == "PKP-001"
        assert created_data["marca"] == "TOYOTA"
        assert created_data["modelo"] == "HILUX"
        assert created_data["anio_fabricacion"] == 2021


class TestVehiculosConstraints:
    """Tests de constraints y validaciones del esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_vehiculo_unique_constraints(self, db_session: AsyncSession):
        """Test constraints únicos según esquema PostgreSQL."""
        # Crear tipo de vehículo
        tipo_vehiculo = TiposVehiculo(nombre="Test Type", categoria="LIVIANO", numero_ejes=2, activo=True)
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        # Crear primer vehículo
        vehiculo1 = Vehiculo(
            placa="UNQ-001",
            tipo_vehiculo_id=tipo_vehiculo.id,
            marca="NISSAN",
            modelo="NAVARA",
            anio_fabricacion=2020,
            numero_chasis="UNIQUE123456789",
            numero_motor="YD25DDTI",
            activo=True
        )
        db_session.add(vehiculo1)
        await db_session.commit()

        # Intentar crear vehículo con placa duplicada (debería fallar)
        with pytest.raises(Exception):  # Should raise unique constraint violation
            vehiculo2 = Vehiculo(
                placa="UNQ-001",  # Placa duplicada
                tipo_vehiculo_id=tipo_vehiculo.id,
                marca="FORD",
                modelo="RANGER",
                anio_fabricacion=2021,
                numero_chasis="DIFFERENT123456",
                numero_motor="PUMA22TDCI",
                activo=True
            )
            db_session.add(vehiculo2)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_vehiculo_required_fields(self, db_session: AsyncSession):
        """Test campos obligatorios según constraints NOT NULL."""
        tipo_vehiculo = TiposVehiculo(nombre="Required Test", categoria="LIVIANO", numero_ejes=2, activo=True)
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        # Test que campos obligatorios no pueden ser None
        with pytest.raises(Exception):  # Should raise constraint violation
            vehiculo = Vehiculos(
                # numero_economico omitido - campo obligatorio
                placa="TEST-REQ",
                tipo_vehiculo_id=tipo_vehiculo.id,
                marca="TEST",
                modelo_vehiculo="TEST",
                anio_fabricacion=2020,
                activo=True
            )
            db_session.add(vehiculo)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_vehiculo_default_values(self, db_session: AsyncSession):
        """Test valores por defecto según esquema PostgreSQL."""
        tipo_vehiculo = TiposVehiculo(nombre="Default Test", categoria="LIVIANO", numero_ejes=2, activo=True)
        db_session.add(tipo_vehiculo)
        await db_session.commit()

        # Crear vehículo sin especificar campos con defaults
        vehiculo = Vehiculos(
            placa="DEF-001",
            tipo_vehiculo_id=tipo_vehiculo.id,
            numero_economico="V009",
            marca="DEFAULT",
            modelo_vehiculo="TEST",
            anio_fabricacion=2020
            # activo no especificado - default True
            # creado_en no especificado - default now()
        )
        
        db_session.add(vehiculo)
        await db_session.commit()
        await db_session.refresh(vehiculo)

        # Verificar defaults aplicados
        assert vehiculo.activo is True  # Default según esquema
        assert vehiculo.creado_en is not None  # Default now()
        assert vehiculo.moneda_compra == "PEN"  # Default según esquema si está definido
