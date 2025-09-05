"""Property-based tests for the catalogos module."""
from hypothesis import given, strategies as st
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from ges_neu_api.modules.catalogos import schemas
from ges_neu_api.modules.catalogos.service import CatalogService
from ges_neu_api.modules.auth.models import Usuario

# Strategies for property-based testing using existing schemas
proveedor_create_strategy = st.builds(
    schemas.ProveedorCreate,
    nombre=st.text(min_size=1, max_size=150)
)

almacen_create_strategy = st.builds(
    schemas.AlmacenCreate,
    codigo=st.text(min_size=1, max_size=20),
    nombre=st.text(min_size=1, max_size=100),
    direccion=st.text(max_size=200) | st.none(),
    responsable=st.text(max_size=200) | st.none(),
    telefono=st.text(max_size=20) | st.none(),
    email=st.text(max_size=100) | st.none(),
    es_principal=st.booleans()
)

class TestPropertyBasedCatalogos:
    """Property-based tests for catalogos module."""
    
    @given(proveedor_data=proveedor_create_strategy)
    @pytest.mark.asyncio
    async def test_create_and_retrieve_proveedor_property(
        self, 
        db_session: AsyncSession,
        proveedor_data: schemas.ProveedorCreate,
        admin_user: Usuario
    ):
        """Test that a proveedor can be created and retrieved with the same data."""
        # Arrange
        service = CatalogService(db_session)
        
        # Act - Create
        created = await service.create_proveedor(proveedor_data, admin_user)
        
        # Assert - Creation
        assert created is not None
        assert created.nombre == proveedor_data.nombre
        
        # Act - Retrieve
        retrieved = await service.get_proveedor_by_id(created.id, admin_user)
        
        # Assert - Retrieval
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.nombre == created.nombre
    
    @given(almacen_data=almacen_create_strategy)
    @pytest.mark.asyncio
    async def test_create_and_retrieve_almacen_property(
        self, 
        db_session: AsyncSession,
        almacen_data: schemas.AlmacenCreate,
        admin_user: Usuario
    ):
        """Test that an almacen can be created and retrieved with the same data."""
        # Arrange
        service = CatalogService(db_session)
        
        # Act - Create
        created = await service.create_almacen(almacen_data, admin_user)
        
        # Assert - Creation
        assert created is not None
        assert created.codigo == almacen_data.codigo
        assert created.nombre == almacen_data.nombre
        
        # Act - Retrieve
        retrieved = await service.get_almacen_by_id(created.id, admin_user)
        
        # Assert - Retrieval
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.codigo == created.codigo
        assert retrieved.nombre == created.nombre
