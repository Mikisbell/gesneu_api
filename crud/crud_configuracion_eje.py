# crud/crud_configuracion_eje.py
from crud.base import CRUDBase
from models.configuracion_eje import ConfiguracionEje
from schemas.configuracion_eje import ConfiguracionEjeCreate, ConfiguracionEjeUpdate

class CRUDConfiguracionEje(CRUDBase[ConfiguracionEje, ConfiguracionEjeCreate, ConfiguracionEjeUpdate]):
    pass # No custom logic needed for now

configuracion_eje = CRUDConfiguracionEje(ConfiguracionEje)