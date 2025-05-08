#crud/crud_parametro_inventario.py
from crud.base import CRUDBase
from models.parametro_inventario import ParametroInventario
from schemas.parametro_inventario import ParametroInventarioCreate, ParametroInventarioUpdate

class CRUDParametroInventario(CRUDBase[ParametroInventario, ParametroInventarioCreate, ParametroInventarioUpdate]):
    pass # No custom logic needed for now

parametro_inventario = CRUDParametroInventario(ParametroInventario)