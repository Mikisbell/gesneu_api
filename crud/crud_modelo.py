# crud/crud_modelo.py
from crud.base import CRUDBase
from models.modelo import Modelo
from schemas.modelo import ModeloCreate, ModeloUpdate

class CRUDModelo(CRUDBase[Modelo, ModeloCreate, ModeloUpdate]):
    pass # No custom logic needed for now

modelo = CRUDModelo(Modelo)