# crud/crud_alerta.py
from crud.base import CRUDBase
from models.alerta import Alerta
from schemas.alerta import AlertaCreate, AlertaUpdate

class CRUDAlerta(CRUDBase[Alerta, AlertaCreate, AlertaUpdate]):
    pass # No custom logic needed for now

alerta = CRUDAlerta(Alerta)