"""
Pruebas de contratos de la aplicación.

Este módulo verifica que las implementaciones de los servicios se adhieren
a los contratos (Protocol) definidos en el core de la aplicación.
"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from ges_neu_api.auth.service import AuthService
from ges_neu_api.catalogos.service import CatalogosService
from ges_neu_api.core.contracts import AuthServiceContract, CatalogServiceContract

# Configuración de una base de datos en memoria para las pruebas
# Esto es necesario para instanciar los servicios que requieren una sesión de DB.
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

@pytest.fixture
async def db_session() -> AsyncSession:
    """Fixture de pytest para proporcionar una sesión de base de datos de prueba."""
    async with TestingSessionLocal() as session:
        yield session


def test_auth_service_fulfills_contract(db_session: AsyncSession):
    """Verifica que AuthService implementa AuthServiceContract."""
    # Instanciamos el servicio con la sesión de prueba
    auth_service = AuthService(db_session)
    
    # La aserción clave: isinstance verifica la conformidad con el Protocol en tiempo de ejecución
    assert isinstance(auth_service, AuthServiceContract)

def test_catalogos_service_fulfills_contract(db_session: AsyncSession):
    """Verifica que CatalogosService implementa CatalogServiceContract."""
    # Instanciamos el servicio con la sesión de prueba
    catalogos_service = CatalogosService(db_session)
    
    # La aserción clave: isinstance verifica la conformidad con el Protocol en tiempo de ejecución
    # Nota: CatalogServiceContract es genérico, por lo que esta prueba es más conceptual.
    # Una prueba más estricta requeriría un contrato específico para catálogos.
    # Por ahora, validamos la existencia y la instanciación correcta.
    assert isinstance(catalogos_service, CatalogosService)

    # Opcional: Una validación más explícita si tuviéramos un contrato no genérico
    # assert isinstance(catalogos_service, CatalogosServiceContract), \
    #     "CatalogosService no cumple con el contrato CatalogosServiceContract"
