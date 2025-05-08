# crud/crud_motivo_desecho.py
from crud.base import CRUDBase
from models.motivo_desecho import MotivoDesecho
from schemas.motivo_desecho import MotivoDesechoCreate, MotivoDesechoUpdate

class CRUDMotivoDesecho(CRUDBase[MotivoDesecho, MotivoDesechoCreate, MotivoDesechoUpdate]):
    pass # No custom logic needed for now

motivo_desecho = CRUDMotivoDesecho(MotivoDesecho)