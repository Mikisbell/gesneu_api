from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ges_neu_api.modules.auth.dependencies import get_current_user
from ges_neu_api.modules.auth.models import Usuario
from .service import CatalogosService
# CORRECCIÓN: Importar 'get_db' en lugar de 'get_async_session'
from ges_neu_api.core.database import get_db

def get_catalogos_service(
    # CORRECCIÓN: Usar la dependencia 'get_db'
    db: AsyncSession = Depends(get_db),
) -> CatalogosService:
    """
    Dependencia de FastAPI para obtener una instancia stateless del servicio de catálogos.
    """
    return CatalogosService(db=db)

# ELIMINADO: La dependencia 'CurrentCatalogosService' ha sido removida
# ya que pertenece al antiguo patrón stateful y es obsoleta.