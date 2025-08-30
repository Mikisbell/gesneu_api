"""Property-based tests for the catalogos module."""
from hypothesis import given, strategies as st
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.catalogos import models, schemas
from ges_neu_api.modules.catalogos.service import CatalogosService
from ges_neu_api.modules.auth.models import Usuario

# Strategies for generating test data
non_empty_text = st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cc', 'Cs')))
positive_int = st.integers(min_value=1, max_value=1000)

# Strategy for FabricanteCreate
fabricante_create_strategy = st.builds(
    schemas.FabricanteCreate,
    nombre=non_empty_text,
    descripcion=st.one_of(st.none(), st.text(max_size=500)),
    activo=st.booleans()
)

# Strategy for CatalogoItemCreate
catalogo_item_create_strategy = st.builds(
    schemas.CatalogoItemCreate,
    nombre=non_empty_text,
    descripcion=st.one_of(st.none(), st.text(max_size=1000)),
    tipo_id=st.uuids(),
    activo=st.booleans()
)

class TestPropertyBasedCatalogos:
    """Property-based tests for the catalogos module."""
    
    @given(fabricante_data=fabricante_create_strategy)
    @pytest.mark.asyncio
    async def test_create_and_retrieve_fabricante_property(
        self, 
        db_session: AsyncSession,
        fabricante_data: schemas.FabricanteCreate,
        admin_user: Usuario
    ):
        """Test that a fabricante can be created and retrieved with the same data."""
        # Arrange
        service = CatalogosService(db_session)
        
        # Act - Create
        created = await service.create_fabricante(fabricante_data, admin_user)
        
        # Assert - Creation
        assert created is not None
        assert created.nombre == fabricante_data.nombre
        assert created.descripcion == fabricante_data.descripcion
        
        # Act - Retrieve
        retrieved = await service.get_fabricante_by_id(created.id, admin_user)
        
        # Assert - Retrieval
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.nombre == created.nombre
        assert retrieved.descripcion == created.descripcion
    
    
    
    @given(
        initial_data=fabricante_create_strategy,
        update_data=fabricante_create_strategy
    )
    @pytest.mark.asyncio
    async def test_update_fabricante_property(
        self,
        db_session: AsyncSession,
        initial_data: schemas.FabricanteCreate,
        update_data: schemas.FabricanteCreate,
        admin_user: Usuario
    ):
        """Test that a fabricante can be updated and maintains data integrity."""
        # Arrange - Create initial fabricante
        service = CatalogosService(db_session)
        created = await service.create_fabricante(initial_data, admin_user)
        
        # Act - Update
        updated = await service.update_fabricante(
            fabricante_id=created.id,
            fabricante_update=schemas.FabricanteUpdate(**update_data.dict()),
            user=admin_user
        )
        
        # Assert
        assert updated is not None
        assert updated.id == created.id
        assert updated.nombre == update_data.nombre
        assert updated.descripcion == update_data.descripcion
        
        # Verify the update is persisted
        retrieved = await service.get_fabricante_by_id(created.id, admin_user)
        assert retrieved.nombre == update_data.nombre
        assert retrieved.descripcion == update_data.descripcion
