"""Unit tests for the CatalogService."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from uuid import uuid4
from hypothesis import given, strategies as st

from ges_neu_api.modules.catalogos.service import CatalogService
from ges_neu_api.modules.catalogos import models, schemas
from ges_neu_api.modules.auth.models import Usuario

# Test constants
TEST_USER_ID = uuid4()
mock_TEST_USER = Usuario(
    id=TEST_USER_ID,
    username="admin",
    email="admin@test.com",
    activo=True,
    nombre_completo="Admin Test User"
)

# Fixtures
@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    
    # Configure the session to return a mock result for execute()
    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result
    
    # Configure other async methods
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    
    return session

@pytest.fixture
def catalogos_service(mock_db_session: AsyncSession) -> CatalogService:
    """Create a CatalogService instance with a mock database session."""
    return CatalogService(mock_db_session)

# Property-based tests
class TestPropertyBasedCatalogService:
    """Property-based tests for CatalogService."""
    
    @pytest.mark.asyncio
    @given(
        nombre=st.text(min_size=1, max_size=150)
    )
    async def test_create_and_retrieve_proveedor_property(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession,
        nombre: str
    ):
        """Test property-based creation and retrieval of proveedor."""
        # Arrange
        proveedor_data = schemas.ProveedorCreate(nombre=nombre)
        
        # Mock the database operations
        mock_proveedor = models.Proveedor(
            id=uuid4(),
            nombre=nombre,
            activo=True,
            creado_en=datetime.now(timezone.utc)
        )
        
        mock_db_session.add = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        mock_db_session.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=AsyncMock(return_value=mock_proveedor)))
        
        # Act
        result = await catalogos_service.create_proveedor(proveedor_data, mock_user)
        
        # Assert
        assert result.nombre == nombre
        assert result.activo == True

# Test cases
class TestCatalogService:
    """Test cases for CatalogService."""
    
    @pytest.mark.asyncio
    async def test_create_fabricante_as_admin(
        self, 
        catalogos_service: CatalogService, 
        mock_db_session: AsyncSession
    ):
        """Test creating a fabricante as an admin user."""
        # Arrange
        fabricante_data = schemas.FabricanteCreate(
            nombre="Test Fabricante",
            descripcion="Test Description",
            activo=True
        )
        
        # Configure the mock to return the admin user
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_user
        
        # Act
        result = await catalogos_service.create_fabricante(
            fabricante_data, 
            current_user_id=TEST_USER_ID
        )
        
        # Assert
        assert result is not None
        assert result.nombre == fabricante_data.nombre
        assert result.descripcion == fabricante_data.descripcion
        assert result.activo == fabricante_data.activo
        
        # Verify the database operations were called
        mock_db_session.add.assert_called_once()
        await mock_db_session.commit.assert_called_once()
        await mock_db_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_fabricante_as_regular_user_fails(
        self, 
        catalogos_service: CatalogService, 
        mock_db_session: AsyncSession
    ):
        """Test that regular users cannot create fabricantes."""
        # Arrange
        fabricante_data = schemas.FabricanteCreate(
            nombre="Test Fabricante",
            descripcion="Test Description",
            activo=True
        )
        
        # Configure the mock to return a regular user
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(PermissionError) as exc_info:
            await catalogos_service.create_fabricante(
                fabricante_data, 
                current_user_id=mock_user.id
            )
        
        assert "No tiene permisos para realizar esta acción" in str(exc_info.value)
        
        # Verify no database operations were performed
        mock_db_session.add.assert_not_called()
        await mock_db_session.commit.assert_not_called()
        await mock_db_session.refresh.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_fabricante_by_id(
        self, 
        catalogos_service: CatalogService, 
        mock_db_session: AsyncSession
    ):
        """Test retrieving a fabricante by ID."""
        # Arrange
        fabricante_id = uuid4()
        test_fabricante = models.Fabricante(
            id=fabricante_id,
            nombre="Test Fabricante",
            descripcion="Test Description",
            activo=True,
            creado_por=TEST_USER_ID,
            fecha_creacion=datetime.utcnow()
        )
        
        # Configure the mock to return the test fabricante
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = test_fabricante
        
        # Act
        result = await catalogos_service.get_fabricante(fabricante_id)
        
        # Assert
        assert result is not None
        assert result.id == fabricante_id
        assert result.nombre == test_fabricante.nombre
    
    @pytest.mark.asyncio
    async def test_list_fabricantes(
        self, 
        catalogos_service: CatalogService, 
        mock_db_session: AsyncSession
    ):
        """Test listing fabricantes with pagination."""
        # Arrange
        test_fabricantes = [
            models.Fabricante(
                id=uuid4(),
                nombre=f"Fabricante {i}",
                descripcion=f"Descripción {i}",
                activo=True,
                creado_por=TEST_USER_ID,
                fecha_creacion=datetime.utcnow() - timedelta(days=i)
            ) for i in range(5)
        ]
        
        # Configure the mock to return the test fabricantes
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = test_fabricantes
        mock_db_session.execute.return_value = mock_result
        
        # Act
        result = await catalogos_service.list_fabricantes(skip=0, limit=10)
        
        # Assert
        assert len(result) == len(test_fabricantes)
        for i, fabricante in enumerate(result):
            assert fabricante.nombre == f"Fabricante {i}"
            assert fabricante.descripcion == f"Descripción {i}"

# Test cases for Fabricante operations
class TestFabricanteOperations:
    """Test cases for Fabricante CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_fabricante_success(
        self, 
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession
    ):
        """Test successful creation of a fabricante."""
        # Arrange
        fabricante_data = schemas.FabricanteCreate(
            nombre="Test Fabricante",
            descripcion="Test Description",
            activo=True
        )
        
        # Configure the mock to return the admin user
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_user
        
        # Act
        result = await catalogos_service._create_fabricante(
            fabricante_data,
            user_id=TEST_USER_ID
        )
        
        # Assert
        assert result is not None
        assert result.nombre == fabricante_data.nombre
        assert result.descripcion == fabricante_data.descripcion
        assert result.activo is True
        assert result.creado_por == TEST_USER_ID
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        await mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_fabricante_exists(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession
    ):
        """Test getting an existing fabricante."""
        # Arrange
        fabricante_id = uuid4()
        expected_fabricante = models.Fabricante(
            id=fabricante_id,
            nombre="Existing Fabricante",
            activo=True
        )
        
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = expected_fabricante
        
        # Act
        result = await catalogos_service._get_fabricante(fabricante_id)
        
        # Assert
        assert result == expected_fabricante
        mock_db_session.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_fabricante_success(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession
    ):
        """Test successful update of a fabricante."""
        # Arrange
        fabricante_id = uuid4()
        existing_fabricante = models.Fabricante(
            id=fabricante_id,
            nombre="Old Name",
            descripcion="Old Description",
            activo=True
        )
        
        update_data = schemas.FabricanteUpdate(
            nombre="Updated Name",
            descripcion="Updated Description",
            activo=False
        )
        
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = existing_fabricante
        
        # Act
        result = await catalogos_service._update_fabricante(
            db_obj=existing_fabricante,
            obj_in=update_data,
            user_id=TEST_USER_ID
        )
        
        # Assert
        assert result.nombre == update_data.nombre
        assert result.descripcion == update_data.descripcion
        assert result.activo is False
        assert result.actualizado_por == TEST_USER_ID
        await mock_db_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_delete_fabricante_success(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession
    ):
        """Test successful deletion of a fabricante."""
        # Arrange
        fabricante_id = uuid4()
        fabricante = models.Fabricante(
            id=fabricante_id,
            nombre="To Be Deleted",
            activo=True
        )
        
        # Act
        await catalogos_service._remove_fabricante(fabricante)
        
        # Assert
        assert fabricante.activo is False
        await mock_db_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_all_fabricantes(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession
    ):
        """Test retrieving all fabricantes with filters."""
        # Arrange
        fabricantes = [
            models.Fabricante(id=uuid4(), nombre="F1", activo=True),
            models.Fabricante(id=uuid4(), nombre="F2", activo=False)
        ]
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = fabricantes
        
        # Act - Get all
        result_all = await catalogos_service._get_all_fabricantes()
        
        # Assert - All returned
        assert len(result_all) == 2
        
        # Act - Get only active
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [f for f in fabricantes if f.activo]
        result_active = await catalogos_service._get_all_fabricantes(activo=True)
        
        # Assert - Only active returned
        assert len(result_active) == 1
        assert all(f.activo for f in result_active)

# Property-based tests
class TestPropertyBasedCatalogService:
    """Property-based tests for CatalogService."""
    
    @pytest.mark.asyncio
    @given(
        nombre=st.text(min_size=1, max_size=150)
    )
    async def test_create_and_retrieve_proveedor_property(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession,
        nombre: str
    ):
        """Test property-based creation and retrieval of proveedor."""
        # Arrange
        proveedor_data = schemas.ProveedorCreate(nombre=nombre)
        
        # Mock the database operations
        mock_proveedor = models.Proveedor(
            id=uuid4(),
            nombre=nombre,
            activo=True,
            creado_en=datetime.now(timezone.utc)
        )
        
        mock_db_session.add = AsyncMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        mock_db_session.execute = AsyncMock(return_value=AsyncMock(scalar_one_or_none=AsyncMock(return_value=mock_proveedor)))
        
        # Act
        result = await catalogos_service.create_proveedor(proveedor_data, mock_user)
        
        # Assert
        assert result.nombre == nombre
        assert result.activo == True

    @pytest.mark.asyncio
    @given(
        nombre=st.text(min_size=1, max_size=100),
        descripcion=st.text(max_size=500) | st.none(),
        activo=st.booleans()
    )
    async def test_create_and_retrieve_fabricante_property(
        self,
        catalogos_service: CatalogService,
        mock_db_session: AsyncSession,
        nombre: str,
        descripcion: str,
        activo: bool
    ):
        """Test that a fabricante can be created and retrieved with the same data."""
        # Arrange
        fabricante_data = schemas.FabricanteCreate(
            nombre=nombre,
            descripcion=descripcion,
            activo=activo
        )
        
        # Configure the mock to return the admin user
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_user
        
        # Mock the database add and refresh operations
        created_fabricante = models.Fabricante(
            **fabricante_data.dict(),
            id=uuid4(),
            creado_por=TEST_USER_ID,
            fecha_creacion=datetime.utcnow()
        )
        
        def add_side_effect(instance):
            instance.id = created_fabricante.id
            instance.fecha_creacion = created_fabricante.fecha_creacion
            return instance
            
        mock_db_session.add.side_effect = add_side_effect
        
        # Act - Create the fabricante
        result = await catalogos_service.create_fabricante(
            fabricante_data,
            current_user_id=TEST_USER_ID
        )
        
        # Assert - Verify the created fabricante
        assert result is not None
        assert result.nombre == nombre
        assert result.descripcion == descripcion
        assert result.activo == activo
        
        # Reset the mock for the get operation
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = created_fabricante
        
        # Act - Retrieve the fabricante
        retrieved = await catalogos_service.get_fabricante(created_fabricante.id)
        
        # Assert - Verify the retrieved fabricante matches the created one
        assert retrieved is not None
        assert retrieved.id == created_fabricante.id
        assert retrieved.nombre == nombre
        assert retrieved.descripcion == descripcion
        assert retrieved.activo == activo
        
        # Verify database operations were called
        mock_db_session.add.assert_called_once()
        await mock_db_session.commit.assert_called_once()
        await mock_db_session.refresh.assert_called_once()
