import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.modules.vehiculos import models, schemas, service
from ges_neu_api.core.exceptions import NotFoundException

@pytest.fixture
def mock_db_session():
    """Crea una sesión de base de datos mockeada."""
    session = AsyncMock(spec=AsyncSession)
    # Configura el mock para la cadena de llamadas `execute(...).scalar_one_or_none()`
    session.execute.return_value.scalar_one_or_none = AsyncMock()
    return session

@pytest.fixture
def test_vehiculo():
    """Crea una instancia de Vehiculos para pruebas."""
    return models.Vehiculos(id=uuid4(), placa="TEST123", activo=True)

@pytest.mark.asyncio
async def test_get_vehiculo_found(mock_db_session, test_vehiculo):
    """Prueba que get_vehiculo devuelve un vehículo si lo encuentra."""
    # Arrange
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_vehiculo
    vehiculo_service = service.VehiculosService(mock_db_session)
    
    # Act
    result = await vehiculo_service.get_vehiculo(test_vehiculo.id)
    
    # Assert
    assert result == test_vehiculo

@pytest.mark.asyncio
async def test_get_vehiculo_not_found(mock_db_session):
    """Prueba que get_vehiculo lanza NotFoundException si no encuentra el vehículo."""
    # Arrange
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    vehiculo_service = service.VehiculosService(mock_db_session)
    
    # Act & Assert
    with pytest.raises(NotFoundException):
        await vehiculo_service.get_vehiculo(uuid4())

@pytest.mark.asyncio
async def test_update_vehiculo_success(mock_db_session, test_vehiculo):
    """Prueba que update_vehiculo actualiza un vehículo correctamente."""
    # Arrange
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_vehiculo
    vehiculo_service = service.VehiculosService(mock_db_session)
    update_data = schemas.VehiculosUpdate(marca="NuevaMarca")
    
    # Act
    result = await vehiculo_service.update_vehiculo(test_vehiculo.id, update_data)
    
    # Assert
    assert result.marca == "NuevaMarca"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)

@pytest.mark.asyncio
async def test_update_vehiculo_not_found(mock_db_session):
    """Prueba que update_vehiculo lanza NotFoundException si el vehículo no existe."""
    # Arrange
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    vehiculo_service = service.VehiculosService(mock_db_session)
    update_data = schemas.VehiculosUpdate(marca="NuevaMarca")
    
    # Act & Assert
    with pytest.raises(NotFoundException):
        await vehiculo_service.update_vehiculo(uuid4(), update_data)

@pytest.mark.asyncio
async def test_delete_vehiculo_success(mock_db_session, test_vehiculo):
    """Prueba que delete_vehiculo hace un soft delete del vehículo."""
    # Arrange
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = test_vehiculo
    vehiculo_service = service.VehiculosService(mock_db_session)
    
    # Act
    result_id = await vehiculo_service.delete_vehiculo(test_vehiculo.id)
    
    # Assert
    assert result_id == test_vehiculo.id
    assert test_vehiculo.activo is False
    mock_db_session.commit.assert_called_once()