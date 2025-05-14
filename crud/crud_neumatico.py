from crud.base import CRUDBase
from models.neumatico import Neumatico
from schemas.neumatico import NeumaticoCreate, NeumaticoUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text # Importar text para usar vistas
from typing import List, Dict, Any # Importar tipos para la respuesta de la vista

class CRUDNeumatico(CRUDBase[Neumatico, NeumaticoCreate, NeumaticoUpdate]):
    async def get_neumaticos_instalados(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """
        Retrieve a list of currently installed tires from the optimized view.

        Args:
            session: The database session.

        Returns:
            A list of dictionaries representing the installed tires from the view.
        """
        # Asegúrate que la vista 'vw_neumaticos_instalados_optimizada' existe en tu BD
        view_query = text("SELECT * FROM vw_neumaticos_instalados_optimizada")
        # Para consultas SQL directas con text(), debemos seguir usando execute()
        # ya que exec() no funciona con consultas SQL directas
        result = await session.execute(view_query)
        # Obtener como lista de diccionarios (o RowMapping)
        instalados_data = result.mappings().all()
        return instalados_data

neumatico = CRUDNeumatico(Neumatico)