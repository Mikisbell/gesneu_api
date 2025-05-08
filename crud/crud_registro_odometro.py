# crud/crud_registro_odometro.py
from crud.base import CRUDBase
from models.registro_odometro import RegistroOdometro
from schemas.registro_odometro import RegistroOdometroCreate, RegistroOdometroUpdate

class CRUDRegistroOdometro(CRUDBase[RegistroOdometro, RegistroOdometroCreate, RegistroOdometroUpdate]):
    pass # No custom logic needed for now

registro_odometro = CRUDRegistroOdometro(RegistroOdometro)