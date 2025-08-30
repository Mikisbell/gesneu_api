import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ges_neu_api.modules.vehiculos import models, schemas, service
from core.exceptions import NotFoundException, ConflictException

# Test data
TEST_VEHICULO_DATA = {
    "placa": "ABC123",
    "chasis": "CHS1234567890",
    "marca": "Toyota",
    "modelo": "Corolla",
    "año": 2022,
    "estado": "DISPONIBLE"
}

# Fixtures
@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = AsyncMock()
    session.scalars.return_value = AsyncMock()
    return session

@pytest.fixture
def test_vehiculo():
    """Create a test Vehiculos instance."""
    return models.Vehiculos(
        id=uuid4(),
        placa="ABC123",
        chasis="CHS1234567890",
        marca="Toyota",
        modelo="Corolla",
        año=2022,
        estado="DISPONIBLE",
        activo=True,
        fecha_creacion=datetime.utcnow(),
        fecha_actualizacion=datetime.utcnow()
    )

# Tests
class TestVehiculosService:
    """Test cases for VehiculosService."""
    
    @pytest.mark.asyncio
    async def test_get_vehiculo_found(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = test_vehiculo
        servicio = service.VehiculosService(mock_db_session)
        
        # Act
        result = await servicio.get(test_vehiculo.id)
        
        # Assert
        assert result is not None
        assert result.id == test_vehiculo.id
        assert result.placa == test_vehiculo.placa
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_vehiculo_not_found(self, mock_db_session):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = None
        servicio = service.VehiculosService(mock_db_session)
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            await servicio.get(uuid4())

    @pytest.mark.asyncio
    async def test_create_vehiculo_success(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = None
        mock_db_session.add.return_value = None
        servicio = service.VehiculosService(mock_db_session)
        
        vehiculo_data = schemas.VehiculoCreate(**TEST_VEHICULO_DATA)
        
        # Act
        result = await servicio.create(vehiculo_data)
        
        # Assert
        assert result is not None
        assert result.placa == TEST_VEHICULO_DATA["placa"]
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_vehiculo_duplicate_placa(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = test_vehiculo
        servicio = service.VehiculosService(mock_db_session)
        
        vehiculo_data = schemas.VehiculoCreate(**TEST_VEHICULO_DATA)
        
        # Act & Assert
        with pytest.raises(ConflictException):
            await servicio.create(vehiculo_data)

    @pytest.mark.asyncio
    async def test_update_vehiculo_success(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = test_vehiculo
        servicio = service.VehiculosService(mock_db_session)
        
        update_data = schemas.VehiculoUpdate(marca="Nissan")
        
        # Act
        result = await servicio.update(test_vehiculo.id, update_data)
        
        # Assert
        assert result is not None
        assert result.marca == "Nissan"
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_vehiculo_success(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = test_vehiculo
        servicio = service.VehiculosService(mock_db_session)
        
        # Act
        result = await servicio.delete(test_vehiculo.id)
        
        # Assert
        assert result is True
        mock_db_session.delete.assert_called_once_with(test_vehiculo)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_placa_found(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.first.return_value = test_vehiculo
        servicio = service.VehiculosService(mock_db_session)
        
        # Act
        result = await servicio.get_by_placa(test_vehiculo.placa)
        
        # Assert
        assert result is not None
        assert result.placa == test_vehiculo.placa

    @pytest.mark.asyncio
    async def test_get_vehiculos_por_estado(self, mock_db_session, test_vehiculo):
        # Arrange
        mock_db_session.scalars.return_value.all.return_value = [test_vehiculo]
        servicio = service.VehiculosService(mock_db_session)
        
        # Act
        result = await servicio.get_vehiculos_por_estado("DISPONIBLE")
        
        # Assert
        assert len(result) == 1
        assert result[0].estado == "DISPONIBLE"