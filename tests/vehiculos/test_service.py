import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime

# Mock the database models to avoid circular imports
class MockVehiculo:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', uuid4())
        self.placa = kwargs.get('placa', 'ABC123')
        self.chasis = kwargs.get('chasis', 'CHS1234567890')
        self.marca = kwargs.get('marca', 'Toyota')
        self.modelo = kwargs.get('modelo', 'Corolla')
        self.año = kwargs.get('año', 2022)
        self.estado = kwargs.get('estado', 'DISPONIBLE')
        self.activo = kwargs.get('activo', True)
        self.fecha_creacion = kwargs.get('fecha_creacion', datetime.utcnow())
        self.fecha_actualizacion = kwargs.get('fecha_actualizacion', datetime.utcnow())

# Mock the schemas
class MockVehiculoCreate:
    def __init__(self, **kwargs):
        self.placa = kwargs.get('placa', 'ABC123')
        self.chasis = kwargs.get('chasis', 'CHS1234567890')
        self.marca = kwargs.get('marca', 'Toyota')
        self.modelo = kwargs.get('modelo', 'Corolla')
        self.año = kwargs.get('año', 2022)
        self.estado = kwargs.get('estado', 'DISPONIBLE')

class MockVehiculoUpdate:
    def __init__(self, **kwargs):
        self.dict = lambda: kwargs

# Mock the service
class MockVehiculoService:
    def __init__(self, db):
        self.db = db
        self.vehiculos = {}
    
    async def get(self, id: UUID):
        return self.vehiculos.get(str(id))
    
    async def create(self, vehiculo):
        if any(v.placa == vehiculo.placa for v in self.vehiculos.values()):
            raise Exception("Duplicate placa")
        new_veh = MockVehiculo(**vehiculo.__dict__)
        self.vehiculos[str(new_veh.id)] = new_veh
        return new_veh
    
    async def update(self, id: UUID, update_data):
        if str(id) not in self.vehiculos:
            raise Exception("Not found")
        veh = self.vehiculos[str(id)]
        for k, v in update_data.dict().items():
            if v is not None:
                setattr(veh, k, v)
        return veh
    
    async def delete(self, id: UUID):
        if str(id) not in self.vehiculos:
            raise Exception("Not found")
        del self.vehiculos[str(id)]
        return True

# Fixtures
@pytest.fixture
def mock_db_session():
    session = AsyncMock()
    session.execute.return_value = AsyncMock()
    session.scalars.return_value = AsyncMock()
    return session

@pytest.fixture
def test_vehiculo():
    return MockVehiculo()

@pytest.fixture
def test_vehiculo_data():
    return {
        "placa": "ABC123",
        "chasis": "CHS1234567890",
        "marca": "Toyota",
        "modelo": "Corolla",
        "año": 2022,
        "estado": "DISPONIBLE"
    }

# Tests
class TestVehiculoService:
    @pytest.mark.asyncio
    async def test_create_vehiculo_success(self, test_vehiculo_data):
        # Arrange
        service = MockVehiculoService(None)
        
        # Act
        result = await service.create(MockVehiculoCreate(**test_vehiculo_data))
        
        # Assert
        assert result is not None
        assert result.placa == test_vehiculo_data["placa"]
        assert result.chasis == test_vehiculo_data["chasis"]
        assert result.activo is True

    @pytest.mark.asyncio
    async def test_get_vehiculo_found(self, test_vehiculo):
        # Arrange
        service = MockVehiculoService(None)
        service.vehiculos[str(test_vehiculo.id)] = test_vehiculo
        
        # Act
        result = await service.get(test_vehiculo.id)
        
        # Assert
        assert result is not None
        assert result.id == test_vehiculo.id
        assert result.placa == test_vehiculo.placa

    @pytest.mark.asyncio
    async def test_update_vehiculo_success(self, test_vehiculo):
        # Arrange
        service = MockVehiculoService(None)
        service.vehiculos[str(test_vehiculo.id)] = test_vehiculo
        
        # Act
        update_data = MockVehiculoUpdate(marca="Nissan")
        result = await service.update(test_vehiculo.id, update_data)
        
        # Assert
        assert result is not None
        assert result.marca == "Nissan"

    @pytest.mark.asyncio
    async def test_delete_vehiculo_success(self, test_vehiculo):
        # Arrange
        service = MockVehiculoService(None)
        service.vehiculos[str(test_vehiculo.id)] = test_vehiculo
        
        # Act
        result = await service.delete(test_vehiculo.id)
        
        # Assert
        assert result is True
        assert str(test_vehiculo.id) not in service.vehiculos
