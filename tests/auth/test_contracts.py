import pytest
from ges_neu_api.modules.auth.service import AuthService, UserService
from ges_neu_api.core.contracts import AuthServiceContract, UserServiceContract
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

# Mock a database session for testing purposes
@pytest.fixture
def mock_db_session():
    return AsyncMock(spec=AsyncSession)

def test_auth_service_implements_contract(mock_db_session):
    """
    Verifica que AuthService implementa correctamente AuthServiceContract.
    """
    auth_service = AuthService(db=mock_db_session)
    assert isinstance(auth_service, AuthServiceContract)

def test_user_service_implements_contract(mock_db_session):
    """
    Verifica que UserService implementa correctamente UserServiceContract.
    """
    user_service = UserService(db=mock_db_session)
    assert isinstance(user_service, UserServiceContract)
