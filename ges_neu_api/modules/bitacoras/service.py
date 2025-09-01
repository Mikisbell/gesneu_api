"""
Servicio para el módulo de bitácoras y auditoría.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import Session, select
from ...core.crud import CRUDBase
from .models import (
    BitacoraMantenimiento,
    BitacoraOperaciones,
    BitacoraOperacionesNeumaticos,
    AuditoriaLog,
    ConfiguracionAuditoria,
    ErroresAplicacion,
    ParametrosSistema,
    TareasProgramadas,
    Rutas,
    TiposRuta
)

class BitacoraService:
    """Servicio para gestión de bitácoras y auditoría."""
    
    def __init__(self, db: Session):
        self.db = db
        self.bitacora_mantenimiento_crud = CRUDBase(BitacoraMantenimiento)
        self.bitacora_operaciones_crud = CRUDBase(BitacoraOperaciones)
        self.bitacora_operaciones_neumaticos_crud = CRUDBase(BitacoraOperacionesNeumaticos)
        self.auditoria_log_crud = CRUDBase(AuditoriaLog)
        self.configuracion_auditoria_crud = CRUDBase(ConfiguracionAuditoria)
        self.errores_aplicacion_crud = CRUDBase(ErroresAplicacion)
        self.parametros_sistema_crud = CRUDBase(ParametrosSistema)
        self.tareas_programadas_crud = CRUDBase(TareasProgramadas)
        self.rutas_crud = CRUDBase(Rutas)
        self.tipos_ruta_crud = CRUDBase(TiposRuta)

    # Bitácora de Mantenimiento
    async def create_bitacora_mantenimiento(self, bitacora_data: dict) -> BitacoraMantenimiento:
        """Crear nueva entrada de bitácora de mantenimiento."""
        return await self.bitacora_mantenimiento_crud.create(self.db, obj_in=bitacora_data)

    async def get_bitacoras_mantenimiento(self, skip: int = 0, limit: int = 100) -> List[BitacoraMantenimiento]:
        """Obtener bitácoras de mantenimiento."""
        return await self.bitacora_mantenimiento_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_bitacora_mantenimiento(self, bitacora_id: UUID) -> Optional[BitacoraMantenimiento]:
        """Obtener bitácora de mantenimiento por ID."""
        return await self.bitacora_mantenimiento_crud.get(self.db, id=bitacora_id)

    # Bitácora de Operaciones
    async def create_bitacora_operacion(self, operacion_data: dict) -> BitacoraOperaciones:
        """Crear nueva operación en bitácora."""
        return await self.bitacora_operaciones_crud.create(self.db, obj_in=operacion_data)

    async def get_bitacoras_operaciones(self, skip: int = 0, limit: int = 100) -> List[BitacoraOperaciones]:
        """Obtener bitácoras de operaciones."""
        return await self.bitacora_operaciones_crud.get_multi(self.db, skip=skip, limit=limit)

    # Auditoría
    async def get_auditoria_logs(self, skip: int = 0, limit: int = 100) -> List[AuditoriaLog]:
        """Obtener logs de auditoría."""
        return await self.auditoria_log_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_auditoria_by_tabla(self, tabla: str, skip: int = 0, limit: int = 100) -> List[AuditoriaLog]:
        """Obtener auditoría por tabla específica."""
        stmt = select(AuditoriaLog).where(AuditoriaLog.nombre_tabla == tabla).offset(skip).limit(limit)
        result = self.db.exec(stmt)
        return result.all()

    # Configuración de Auditoría
    async def get_configuracion_auditoria(self) -> List[ConfiguracionAuditoria]:
        """Obtener configuración de auditoría."""
        return await self.configuracion_auditoria_crud.get_multi(self.db)

    async def update_configuracion_auditoria(self, tabla: str, config_data: dict) -> Optional[ConfiguracionAuditoria]:
        """Actualizar configuración de auditoría para una tabla."""
        config = await self.configuracion_auditoria_crud.get(self.db, id=tabla)
        if config:
            return await self.configuracion_auditoria_crud.update(self.db, db_obj=config, obj_in=config_data)
        return None

    # Errores de Aplicación
    async def create_error_aplicacion(self, error_data: dict) -> ErroresAplicacion:
        """Registrar error de aplicación."""
        return await self.errores_aplicacion_crud.create(self.db, obj_in=error_data)

    async def get_errores_aplicacion(self, skip: int = 0, limit: int = 100, resuelto: Optional[bool] = None) -> List[ErroresAplicacion]:
        """Obtener errores de aplicación."""
        if resuelto is not None:
            stmt = select(ErroresAplicacion).where(ErroresAplicacion.resuelto == resuelto).offset(skip).limit(limit)
            result = self.db.exec(stmt)
            return result.all()
        return await self.errores_aplicacion_crud.get_multi(self.db, skip=skip, limit=limit)

    async def resolver_error(self, error_id: UUID, resuelto_por: str, comentario: str) -> Optional[ErroresAplicacion]:
        """Marcar error como resuelto."""
        error = await self.errores_aplicacion_crud.get(self.db, id=error_id)
        if error:
            update_data = {
                "resuelto": True,
                "resuelto_por": resuelto_por,
                "resuelto_en": datetime.utcnow(),
                "comentario_resolucion": comentario
            }
            return await self.errores_aplicacion_crud.update(self.db, db_obj=error, obj_in=update_data)
        return None

    # Parámetros del Sistema
    async def get_parametros_sistema(self) -> List[ParametrosSistema]:
        """Obtener parámetros del sistema."""
        return await self.parametros_sistema_crud.get_multi(self.db)

    async def get_parametro_sistema(self, clave: str) -> Optional[ParametrosSistema]:
        """Obtener parámetro específico del sistema."""
        stmt = select(ParametrosSistema).where(ParametrosSistema.clave == clave)
        result = self.db.exec(stmt)
        return result.first()

    async def update_parametro_sistema(self, clave: str, valor: str, descripcion: Optional[str] = None) -> Optional[ParametrosSistema]:
        """Actualizar parámetro del sistema."""
        parametro = await self.get_parametro_sistema(clave)
        if parametro:
            update_data = {"valor": valor}
            if descripcion:
                update_data["descripcion"] = descripcion
            return await self.parametros_sistema_crud.update(self.db, db_obj=parametro, obj_in=update_data)
        return None

    # Tareas Programadas
    async def get_tareas_programadas(self, activa: Optional[bool] = None) -> List[TareasProgramadas]:
        """Obtener tareas programadas."""
        if activa is not None:
            stmt = select(TareasProgramadas).where(TareasProgramadas.activa == activa)
            result = self.db.exec(stmt)
            return result.all()
        return await self.tareas_programadas_crud.get_multi(self.db)

    async def update_tarea_programada(self, tarea_id: int, tarea_data: dict) -> Optional[TareasProgramadas]:
        """Actualizar tarea programada."""
        tarea = await self.tareas_programadas_crud.get(self.db, id=tarea_id)
        if tarea:
            return await self.tareas_programadas_crud.update(self.db, db_obj=tarea, obj_in=tarea_data)
        return None

    # Rutas
    async def get_rutas(self, skip: int = 0, limit: int = 100) -> List[Rutas]:
        """Obtener rutas."""
        return await self.rutas_crud.get_multi(self.db, skip=skip, limit=limit)

    async def create_ruta(self, ruta_data: dict) -> Rutas:
        """Crear nueva ruta."""
        return await self.rutas_crud.create(self.db, obj_in=ruta_data)

    async def get_ruta(self, ruta_id: UUID) -> Optional[Rutas]:
        """Obtener ruta por ID."""
        return await self.rutas_crud.get(self.db, id=ruta_id)

    # Tipos de Ruta
    async def get_tipos_ruta(self, skip: int = 0, limit: int = 100) -> List[TiposRuta]:
        """Obtener tipos de ruta."""
        return await self.tipos_ruta_crud.get_multi(self.db, skip=skip, limit=limit)

    async def create_tipo_ruta(self, tipo_data: dict) -> TiposRuta:
        """Crear nuevo tipo de ruta."""
        return await self.tipos_ruta_crud.create(self.db, obj_in=tipo_data)

    async def get_tipo_ruta(self, tipo_id: UUID) -> Optional[TiposRuta]:
        """Obtener tipo de ruta por ID."""
        return await self.tipos_ruta_crud.get(self.db, id=tipo_id)
