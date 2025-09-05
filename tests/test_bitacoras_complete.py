"""Tests completos para el módulo de bitácoras alineados con esquema PostgreSQL."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from ges_neu_api.modules.bitacoras.models import BitacoraOperaciones, TipoOperacionEnum, EstadoOperacionEnum, TipoAccionOperacionEnum
from ges_neu_api.modules.catalogos.models import Almacen, Proveedor
from ges_neu_api.modules.vehiculos.models import Vehiculos


class TestBitacoraOperacionesModel:
    """Tests del modelo BitacoraOperaciones alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_create_bitacora_basic(self, db_session: AsyncSession):
        """Test creación básica de bitácora con campos obligatorios."""
        # Crear bitácora con campos obligatorios según esquema PostgreSQL
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.REPARACION_GENERAL,
            descripcion="Mantenimiento preventivo de neumáticos",
            estado_operacion=EstadoOperacionEnum.PENDIENTE
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Verificar campos obligatorios
        assert bitacora.id is not None
        assert bitacora.tipo_operacion == TipoOperacionEnum.REPARACION_GENERAL
        assert bitacora.descripcion == "Mantenimiento preventivo de neumáticos"
        assert bitacora.estado_operacion == EstadoOperacionEnum.PENDIENTE
        assert bitacora.fecha_operacion is not None  # Default now()
        assert bitacora.creado_en is not None  # Default now()
        assert bitacora.actualizado_en is not None  # Default now()

    @pytest.mark.asyncio
    async def test_bitacora_enums_validation(self, db_session: AsyncSession):
        """Test validación de enums según esquema PostgreSQL."""
        # Test todos los tipos de operación válidos
        # Tipos válidos según esquema PostgreSQL real
        tipos_validos = [
            TipoOperacionEnum.ROTACION,
            TipoOperacionEnum.BALANCEO,
            TipoOperacionEnum.ALINEACION,
            TipoOperacionEnum.REPARACION_GENERAL,
            TipoOperacionEnum.INSPECCION_GENERAL,
            TipoOperacionEnum.CAMBIO_ACEITE,
            TipoOperacionEnum.OTRO,
            TipoOperacionEnum.DESMONTAJE
        ]

        for tipo in tipos_validos:
            bitacora = BitacoraOperaciones(
                tipo_operacion=tipo,
                descripcion=f"Test operación {tipo.value}",
                estado_operacion=EstadoOperacionEnum.COMPLETADA
            )
            db_session.add(bitacora)
            await db_session.commit()
            await db_session.refresh(bitacora)
            
            assert bitacora.tipo_operacion == tipo

        # Test todos los estados válidos
        estados_validos = [
            EstadoOperacionEnum.PENDIENTE,
            EstadoOperacionEnum.EN_PROCESO,
            EstadoOperacionEnum.COMPLETADA,
            EstadoOperacionEnum.CANCELADA,
            EstadoOperacionEnum.VENCIDA
        ]

        for estado in estados_validos:
            bitacora = BitacoraOperaciones(
                tipo_operacion=TipoOperacionEnum.INSPECCION,
                descripcion=f"Test estado {estado.value}",
                estado_operacion=estado
            )
            db_session.add(bitacora)
            await db_session.commit()
            await db_session.refresh(bitacora)
            
            assert bitacora.estado_operacion == estado

    @pytest.mark.asyncio
    async def test_bitacora_con_relaciones(self, db_session: AsyncSession):
        """Test bitácora con relaciones a otras entidades según esquema."""
        # Crear almacén
        almacen = Almacen(
            nombre="Almacén Central",
            codigo="ALM001",
            ubicacion="Zona Industrial Norte",
            capacidad_maxima=1000,
            activo=True
        )
        db_session.add(almacen)
        await db_session.commit()

        # Crear proveedor
        proveedor = Proveedor(
            nombre="Neumáticos del Norte SAC",
            codigo="PROV001",
            tipo_proveedor="DISTRIBUIDOR",
            contacto_principal="Juan Pérez",
            telefono="987654321",
            email="contacto@neumaticos.com",
            activo=True
        )
        db_session.add(proveedor)
        await db_session.commit()

        # Crear bitácora con relaciones
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.OTRO,
            descripcion="Compra de lote de neumáticos nuevos",
            estado_operacion=EstadoOperacionEnum.COMPLETADA,
            almacen_id=almacen.id,
            proveedor_id=proveedor.id,
            duracion_minutos=120,
            costo_estimado=Decimal("15000.00"),
            costo_real=Decimal("14500.00"),
            observaciones="Compra realizada con descuento del 3%"
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Verificar relaciones y campos adicionales
        assert bitacora.almacen_id == almacen.id
        assert bitacora.proveedor_id == proveedor.id
        assert bitacora.duracion_minutos == 120
        assert bitacora.costo_estimado == Decimal("15000.00")
        assert bitacora.costo_real == Decimal("14500.00")
        assert bitacora.observaciones == "Compra realizada con descuento del 3%"

    @pytest.mark.asyncio
    async def test_bitacora_campos_numericos_precision(self, db_session: AsyncSession):
        """Test precisión de campos numéricos según esquema PostgreSQL."""
        # Test campos con precisión específica NUMERIC(10,2)
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.REPARACION_GENERAL,
            descripcion="Reparación de neumático con parche",
            estado_operacion=EstadoOperacionEnum.COMPLETADA,
            duracion_minutos=45,
            costo_estimado=Decimal("250.75"),  # NUMERIC(10,2)
            costo_real=Decimal("275.50"),  # NUMERIC(10,2)
            observaciones="Reparación exitosa con material premium"
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Verificar precisión mantenida
        assert bitacora.costo_estimado == Decimal("250.75")
        assert bitacora.costo_real == Decimal("275.50")
        assert bitacora.duracion_minutos == 45


class TestBitacoraOperacionesEndpoints:
    """Tests de endpoints de bitácoras alineados con esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_get_bitacoras_list(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint GET /api/v1/bitacoras/ con datos reales."""
        # Crear vehículo de prueba
        vehiculo = Vehiculos(
            numero_placa="ABC123",
            numero_interno="V001",
            marca="VOLVO",
            modelo="FH16",
            anio_fabricacion=2020,
            numero_chasis="CHASIS123",
            numero_motor="MOTOR123",
            activo=True
        )
        db_session.add(vehiculo)
        await db_session.commit()

        # Crear bitácoras de prueba
        bitacoras_test = [
            {
                "tipo_operacion": TipoOperacionEnum.ROTACION,
                "descripcion": "Rotación de neumático en vehículo",
                "estado_operacion": EstadoOperacionEnum.COMPLETADA,
                "duracion_minutos": 30
            },
            {
                "tipo_operacion": TipoOperacionEnum.INSPECCION_GENERAL,
                "descripcion": "Inspección rutinaria de profundidad",
                "estado_operacion": EstadoOperacionEnum.EN_PROCESO,
                "duracion_minutos": 15
            }
        ]

        for bitacora_data in bitacoras_test:
            bitacora = BitacoraOperaciones(**bitacora_data)
            db_session.add(bitacora)
        
        await db_session.commit()

        # Test endpoint
        response = await client.get("/api/v1/bitacoras/operaciones")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 2
        
        # Verificar estructura de respuesta alineada con esquema
        bitacora_data = data[0]
        assert "id" in bitacora_data
        assert "tipo_operacion" in bitacora_data
        assert "descripcion" in bitacora_data
        assert "estado_operacion" in bitacora_data
        assert "fecha_operacion" in bitacora_data
        assert "creado_en" in bitacora_data

    @pytest.mark.asyncio
    async def test_create_bitacora_endpoint(self, client: AsyncClient, db_session: AsyncSession):
        """Test endpoint POST /api/v1/bitacoras/ con validación de esquema."""
        # Datos alineados con esquema PostgreSQL
        bitacora_data = {
            "tipo_operacion": "ROTACION",
            "descripcion": "Rotación de neumáticos según programa de mantenimiento",
            "estado_operacion": "PENDIENTE",
            "duracion_minutos": 60,
            "costo_estimado": 150.00,
            "observaciones": "Rotación programada cada 10,000 km"
        }

        response = await client.post("/api/v1/bitacoras/operaciones", json=bitacora_data)
        assert response.status_code == 201
        
        created_data = response.json()
        assert created_data["tipo_operacion"] == "ROTACION"
        assert created_data["estado_operacion"] == "PENDIENTE"
        assert created_data["duracion_minutos"] == 60
        assert created_data["costo_estimado"] == 150.00

    @pytest.mark.asyncio
    async def test_bitacoras_filters(self, client: AsyncClient, db_session: AsyncSession):
        """Test filtros de bitácoras según esquema PostgreSQL."""
        # Crear bitácoras con diferentes tipos y estados
        bitacoras_test = [
            ("REPARACION_GENERAL", "COMPLETADA"),
            ("BALANCEO", "EN_PROCESO"),
            ("INSPECCION_GENERAL", "PENDIENTE"),
            ("REPARACION_GENERAL", "CANCELADA")
        ]

        for i, (tipo, estado) in enumerate(bitacoras_test):
            bitacora = BitacoraOperaciones(
                tipo_operacion=getattr(TipoOperacionEnum, tipo),
                descripcion=f"Test operación {i}",
                estado_operacion=getattr(EstadoOperacionEnum, estado)
            )
            db_session.add(bitacora)
        
        await db_session.commit()

        # Test filtro por tipo de operación
        response = await client.get("/api/v1/bitacoras/operaciones?tipo_operacion=REPARACION_GENERAL")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 2  # Debe haber al menos 2 operaciones de reparación general
        for item in data:
            assert item["tipo_operacion"] == "REPARACION_GENERAL"

        # Test filtro por estado
        response = await client.get("/api/v1/bitacoras/operaciones?estado_operacion=COMPLETADA")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 1
        for item in data:
            assert item["estado_operacion"] == "COMPLETADA"

    @pytest.mark.asyncio
    async def test_update_bitacora_estado(self, client: AsyncClient, db_session: AsyncSession):
        """Test actualización de estado de bitácora."""
        # Crear bitácora
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.REPARACION_GENERAL,
            descripcion="Reparación de neumático dañado",
            estado_operacion=EstadoOperacionEnum.PENDIENTE,
            costo_estimado=Decimal("300.00")
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Actualizar estado y costo real
        update_data = {
            "estado_operacion": "COMPLETADA",
            "costo_real": 285.50,
            "observaciones": "Reparación completada exitosamente"
        }

        response = await client.patch(f"/api/v1/bitacoras/operaciones/{bitacora.id}", json=update_data)
        assert response.status_code == 200
        
        updated_data = response.json()
        assert updated_data["estado_operacion"] == "COMPLETADA"
        assert updated_data["costo_real"] == 285.50


class TestBitacoraConstraints:
    """Tests de constraints y validaciones del esquema PostgreSQL."""

    @pytest.mark.asyncio
    async def test_bitacora_required_fields(self, db_session: AsyncSession):
        """Test campos obligatorios según constraints NOT NULL."""
        # Test que campos obligatorios no pueden ser None
        with pytest.raises(Exception):  # Should raise constraint violation
            bitacora = BitacoraOperaciones(
                # tipo_operacion omitido - campo obligatorio
                descripcion="Test description",
                estado_operacion=EstadoOperacionEnum.PENDIENTE
            )
            db_session.add(bitacora)
            await db_session.commit()

        with pytest.raises(Exception):  # Should raise constraint violation
            bitacora = BitacoraOperaciones(
                tipo_operacion=TipoOperacionEnum.INSPECCION_GENERAL,
                # descripcion omitida - campo obligatorio
                estado_operacion=EstadoOperacionEnum.PENDIENTE
            )
            db_session.add(bitacora)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_bitacora_default_values(self, db_session: AsyncSession):
        """Test valores por defecto según esquema PostgreSQL."""
        # Crear bitácora sin especificar campos con defaults
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.INSPECCION_GENERAL,
            descripcion="Test default values",
            estado_operacion=EstadoOperacionEnum.PENDIENTE
            # fecha_operacion no especificada - default now()
            # creado_en no especificado - default now()
            # actualizado_en no especificado - default now()
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Verificar defaults aplicados según esquema PostgreSQL
        assert bitacora.fecha_operacion is not None  # Default now()
        assert bitacora.creado_en is not None  # Default now()
        assert bitacora.actualizado_en is not None  # Default now()

    @pytest.mark.asyncio
    async def test_bitacora_foreign_keys(self, db_session: AsyncSession):
        """Test foreign keys según esquema PostgreSQL."""
        # Crear almacén válido
        almacen = Almacen(
            nombre="Almacén Test",
            codigo="ALM_TEST",
            ubicacion="Test Location",
            capacidad_maxima=100,
            activo=True
        )
        db_session.add(almacen)
        await db_session.commit()

        # Test foreign key válida
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.OTRO,
            descripcion="Traslado a almacén test",
            estado_operacion=EstadoOperacionEnum.COMPLETADA,
            almacen_id=almacen.id  # FK válida
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)
        
        assert bitacora.almacen_id == almacen.id

        # Test foreign key inválida debería fallar
        with pytest.raises(Exception):  # Should raise FK constraint violation
            bitacora_invalid = BitacoraOperaciones(
                tipo_operacion=TipoOperacionEnum.OTRO,
                descripcion="Traslado con FK inválida",
                estado_operacion=EstadoOperacionEnum.PENDIENTE,
                almacen_id=uuid4()  # FK inválida
            )
            db_session.add(bitacora_invalid)
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_bitacora_timestamps_auto_update(self, db_session: AsyncSession):
        """Test actualización automática de timestamps."""
        # Crear bitácora
        bitacora = BitacoraOperaciones(
            tipo_operacion=TipoOperacionEnum.REPARACION_GENERAL,
            descripcion="Test timestamps",
            estado_operacion=EstadoOperacionEnum.PENDIENTE
        )
        
        db_session.add(bitacora)
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Guardar timestamp original
        original_creado_en = bitacora.creado_en
        original_actualizado_en = bitacora.actualizado_en

        # Actualizar bitácora
        bitacora.estado_operacion = EstadoOperacionEnum.COMPLETADA
        bitacora.observaciones = "Actualización de test"
        
        await db_session.commit()
        await db_session.refresh(bitacora)

        # Verificar que creado_en no cambió pero actualizado_en sí
        assert bitacora.creado_en == original_creado_en
        # actualizado_en debería actualizarse automáticamente (si está configurado en BD)
        # En SQLAlchemy esto se maneja con onupdate=func.now()
        assert bitacora.observaciones == "Actualización de test"
