# crud/crud_posicion_neumatico.py
from crud.base import CRUDBase
from models.posicion_neumatico import PosicionNeumatico
from schemas.posicion_neumatico import PosicionNeumaticoCreate, PosicionNeumaticoUpdate


class CRUDPosicionNeumatico(CRUDBase[PosicionNeumatico, PosicionNeumaticoCreate, PosicionNeumaticoUpdate]):
    pass # No custom logic needed for now

posicion_neumatico = CRUDPosicionNeumatico(PosicionNeumatico)