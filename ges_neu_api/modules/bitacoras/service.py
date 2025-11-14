"""
Servicio para el módulo de bitácoras y auditoría.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.crud import CRUDBase
from .models import (
    BitacoraMantenimiento,
    BitacoraOperaciones,
    BitacoraOperacionesNeumaticos,
    AuditoriaLog,
    AuditoriaRolesUsuarios
)
from ..sistema.models import (
    ConfiguracionAuditoria,
    ErroresAplicacion,
    ParametrosSistema,
    TareasProgramadas,
    Rutas,
    TiposRuta
)


class BitacoraService:
    """Servicio para gestión de bitácoras y auditoría."""
    
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db
        # Initialize CRUD operations for all models
        self.bitacora_mantenimiento_crud: CRUDBase = CRUDBase(BitacoraMantenimiento)
        self.bitacora_operaciones_crud: CRUDBase = CRUDBase(BitacoraOperaciones)
        self.bitacora_operaciones_neumaticos_crud: CRUDBase = CRUDBase(BitacoraOperacionesNeumaticos)
        self.auditoria_log_crud: CRUDBase = CRUDBase(AuditoriaLog)
        self.auditoria_roles_usuarios_crud: CRUDBase = CRUDBase(AuditoriaRolesUsuarios)
        self.configuracion_auditoria_crud: CRUDBase = CRUDBase(ConfiguracionAuditoria)
        self.errores_aplicacion_crud: CRUDBase = CRUDBase(ErroresAplicacion)
        self.parametros_sistema_crud: CRUDBase = CRUDBase(ParametrosSistema)
        self.tareas_programadas_crud: CRUDBase = CRUDBase(TareasProgramadas)
        self.rutas_crud: CRUDBase = CRUDBase(Rutas)
        self.tipos_ruta_crud: CRUDBase = CRUDBase(TiposRuta)

    # Bitácora de Mantenimiento
    async def get_bitacoras_mantenimiento(self, skip: int = 0, limit: int = 100) -> List[BitacoraMantenimiento]:
        """Obtener bitácoras de mantenimiento."""
        return await self.bitacora_mantenimiento_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_bitacora_mantenimiento(self, bitacora_id: UUID) -> Optional[BitacoraMantenimiento]:
        """Obtener bitácora de mantenimiento por ID."""
        return await self.bitacora_mantenimiento_crud.get(self.db, id=bitacora_id)

    async def create_bitacora_mantenimiento(self, bitacora_data: dict) -> BitacoraMantenimiento:
        """Crear nueva entrada de bitácora de mantenimiento."""
        return await self.bitacora_mantenimiento_crud.create(self.db, obj_in=bitacora_data)

    # Bitácora de Operaciones
    async def get_bitacoras_operaciones(self, skip: int = 0, limit: int = 100) -> List[BitacoraOperaciones]:
        """Obtener bitácoras de operaciones."""
        return await self.bitacora_operaciones_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_bitacora_operacion(self, operacion_id: UUID) -> Optional[BitacoraOperaciones]:
        """Obtener bitácora de operación por ID."""
        return await self.bitacora_operaciones_crud.get(self.db, id=operacion_id)

    async def create_bitacora_operacion(self, operacion_data: dict) -> BitacoraOperaciones:
        """Crear nueva operación en bitácora."""
        return await self.bitacora_operaciones_crud.create(self.db, obj_in=operacion_data)

    # Auditoría
    async def get_auditoria_logs(self, skip: int = 0, limit: int = 100) -> List[AuditoriaLog]:
        """Obtener logs de auditoría."""
        return await self.auditoria_log_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_auditoria_roles_usuarios(self, skip: int = 0, limit: int = 100) -> List[AuditoriaRolesUsuarios]:
        """Obtener auditoría de roles y usuarios."""
        return await self.auditoria_roles_usuarios_crud.get_multi(self.db, skip=skip, limit=limit)

    # Configuración de Auditoría
    async def get_configuracion_auditoria(self) -> List[ConfiguracionAuditoria]:
        """Obtener configuración de auditoría."""
        return await self.configuracion_auditoria_crud.get_multi(self.db)

    # Errores de Aplicación
    async def get_errores_aplicacion(self, skip: int = 0, limit: int = 100) -> List[ErroresAplicacion]:
        """Obtener errores de aplicación."""
        return await self.errores_aplicacion_crud.get_multi(self.db, skip=skip, limit=limit)

    async def create_error_aplicacion(self, error_data: dict) -> ErroresAplicacion:
        """Registrar error de aplicación."""
        return await self.errores_aplicacion_crud.create(self.db, obj_in=error_data)

    # Parámetros del Sistema
    async def get_parametros_sistema(self) -> List[ParametrosSistema]:
        """Obtener parámetros del sistema."""
        return await self.parametros_sistema_crud.get_multi(self.db)

    # Tareas Programadas
    async def get_tareas_programadas(self) -> List[TareasProgramadas]:
        """Obtener tareas programadas."""
        return await self.tareas_programadas_crud.get_multi(self.db)

    # Rutas
    async def get_rutas(self, skip: int = 0, limit: int = 100) -> List[Rutas]:
        """Obtener rutas."""
        return await self.rutas_crud.get_multi(self.db, skip=skip, limit=limit)

    async def create_ruta(self, ruta_data: dict) -> Rutas:
        """Crear nueva ruta."""
        return await self.rutas_crud.create(self.db, obj_in=ruta_data)

    # Tipos de Ruta
    async def get_tipos_ruta(self, skip: int = 0, limit: int = 100) -> List[TiposRuta]:
        """Obtener tipos de ruta."""
        return await self.tipos_ruta_crud.get_multi(self.db, skip=skip, limit=limit)

    async def create_tipo_ruta(self, tipo_data: dict) -> TiposRuta:
        """Crear nuevo tipo de ruta."""
        return await self.tipos_ruta_crud.create(self.db, obj_in=tipo_data)