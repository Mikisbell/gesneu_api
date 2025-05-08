from crud.base import CRUDBase
from models.evento_neumatico import EventoNeumatico
from schemas.evento_neumatico import EventoNeumaticoCreate, EventoNeumaticoUpdate

class CRUDEventoNeumatico(CRUDBase[EventoNeumatico, EventoNeumaticoCreate, EventoNeumaticoUpdate]):
    pass # No custom logic needed for now

evento_neumatico = CRUDEventoNeumatico(EventoNeumatico)