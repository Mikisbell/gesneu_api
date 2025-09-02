"""
Servicio para el módulo de sistema.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.crud import CRUDBase
from ..bitacoras.models import ParametrosSistema, TareasProgramadas, Rutas, TiposRuta

class SistemaService:
    """Servicio para gestión de parámetros y configuración del sistema."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.parametros_sistema_crud = CRUDBase(ParametrosSistema)
        self.tareas_programadas_crud = CRUDBase(TareasProgramadas)
        self.rutas_crud = CRUDBase(Rutas)
        self.tipos_ruta_crud = CRUDBase(TiposRuta)

    # Parámetros del Sistema
    async def get_parametros_sistema(self) -> List[ParametrosSistema]:
        """Obtener todos los parámetros del sistema."""
        return await self.parametros_sistema_crud.get_multi(self.db)

    async def get_parametro_sistema(self, clave: str) -> Optional[ParametrosSistema]:
        """Obtener parámetro específico del sistema por clave."""
        stmt = select(ParametrosSistema).where(ParametrosSistema.clave == clave)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_parametro_sistema(self, parametro_data: dict) -> ParametrosSistema:
        """Crear nuevo parámetro del sistema."""
        return await self.parametros_sistema_crud.create(self.db, obj_in=parametro_data)

    async def update_parametro_sistema(self, clave: str, valor: str, descripcion: Optional[str] = None) -> Optional[ParametrosSistema]:
        """Actualizar parámetro del sistema."""
        parametro = await self.get_parametro_sistema(clave)
        if parametro:
            update_data = {
                "valor": valor,
                "actualizado_en": datetime.utcnow(),
                "actualizado_por": "SISTEMA"
            }
            if descripcion:
                update_data["descripcion"] = descripcion
            return await self.parametros_sistema_crud.update(self.db, db_obj=parametro, obj_in=update_data)
        return None

    async def delete_parametro_sistema(self, parametro_id: int) -> bool:
        """Eliminar parámetro del sistema."""
        parametro = await self.parametros_sistema_crud.get(self.db, id=parametro_id)
        if parametro:
            await self.parametros_sistema_crud.remove(self.db, id=parametro_id)
            return True
        return False

    # Tareas Programadas
    async def get_tareas_programadas(self, activa: Optional[bool] = None) -> List[TareasProgramadas]:
        """Obtener tareas programadas, opcionalmente filtradas por estado."""
        if activa is not None:
            stmt = select(TareasProgramadas).where(TareasProgramadas.activa == activa)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        return await self.tareas_programadas_crud.get_multi(self.db)

    async def get_tarea_programada(self, tarea_id: int) -> Optional[TareasProgramadas]:
        """Obtener tarea programada por ID."""
        return await self.tareas_programadas_crud.get(self.db, id=tarea_id)

    async def create_tarea_programada(self, tarea_data: dict) -> TareasProgramadas:
        """Crear nueva tarea programada."""
        return await self.tareas_programadas_crud.create(self.db, obj_in=tarea_data)

    async def update_tarea_programada(self, tarea_id: int, tarea_data: dict) -> Optional[TareasProgramadas]:
        """Actualizar tarea programada."""
        tarea = await self.tareas_programadas_crud.get(self.db, id=tarea_id)
        if tarea:
            tarea_data["actualizado_en"] = datetime.utcnow()
            return await self.tareas_programadas_crud.update(self.db, db_obj=tarea, obj_in=tarea_data)
        return None

    async def activar_desactivar_tarea(self, tarea_id: int, activa: bool) -> Optional[TareasProgramadas]:
        """Activar o desactivar tarea programada."""
        return await self.update_tarea_programada(tarea_id, {"activa": activa})

    async def actualizar_ejecucion_tarea(self, tarea_id: int, proxima_ejecucion: Optional[datetime] = None) -> Optional[TareasProgramadas]:
        """Actualizar fechas de ejecución de tarea."""
        update_data = {
            "ultima_ejecucion": datetime.utcnow()
        }
        if proxima_ejecucion:
            update_data["proxima_ejecucion"] = proxima_ejecucion
        
        return await self.update_tarea_programada(tarea_id, update_data)

    # Rutas
    async def get_rutas(self, skip: int = 0, limit: int = 100, activo: Optional[bool] = None) -> List[Rutas]:
        """Obtener rutas."""
        if activo is not None:
            stmt = select(Rutas).where(Rutas.activo == activo).offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        return await self.rutas_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_ruta(self, ruta_id: UUID) -> Optional[Rutas]:
        """Obtener ruta por ID."""
        return await self.rutas_crud.get(self.db, id=ruta_id)

    async def get_ruta_by_codigo(self, codigo: str) -> Optional[Rutas]:
        """Obtener ruta por código."""
        stmt = select(Rutas).where(Rutas.codigo == codigo)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_ruta(self, ruta_data: dict) -> Rutas:
        """Crear nueva ruta."""
        return await self.rutas_crud.create(self.db, obj_in=ruta_data)

    async def update_ruta(self, ruta_id: UUID, ruta_data: dict) -> Optional[Rutas]:
        """Actualizar ruta."""
        ruta = await self.rutas_crud.get(self.db, id=ruta_id)
        if ruta:
            return await self.rutas_crud.update(self.db, db_obj=ruta, obj_in=ruta_data)
        return None

    async def delete_ruta(self, ruta_id: UUID) -> bool:
        """Eliminar ruta (desactivar)."""
        return await self.update_ruta(ruta_id, {"activo": False}) is not None

    # Tipos de Ruta
    async def get_tipos_ruta(self, skip: int = 0, limit: int = 100, activo: Optional[bool] = None) -> List[TiposRuta]:
        """Obtener tipos de ruta."""
        if activo is not None:
            stmt = select(TiposRuta).where(TiposRuta.activo == activo).offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return result.scalars().all()
        return await self.tipos_ruta_crud.get_multi(self.db, skip=skip, limit=limit)

    async def get_tipo_ruta(self, tipo_id: UUID) -> Optional[TiposRuta]:
        """Obtener tipo de ruta por ID."""
        return await self.tipos_ruta_crud.get(self.db, id=tipo_id)

    async def get_tipo_ruta_by_nombre(self, nombre: str) -> Optional[TiposRuta]:
        """Obtener tipo de ruta por nombre."""
        stmt = select(TiposRuta).where(TiposRuta.nombre == nombre)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_tipo_ruta(self, tipo_data: dict) -> TiposRuta:
        """Crear nuevo tipo de ruta."""
        return await self.tipos_ruta_crud.create(self.db, obj_in=tipo_data)

    async def update_tipo_ruta(self, tipo_id: UUID, tipo_data: dict) -> Optional[TiposRuta]:
        """Actualizar tipo de ruta."""
        tipo = await self.tipos_ruta_crud.get(self.db, id=tipo_id)
        if tipo:
            return await self.tipos_ruta_crud.update(self.db, db_obj=tipo, obj_in=tipo_data)
        return None

    async def delete_tipo_ruta(self, tipo_id: UUID) -> bool:
        """Eliminar tipo de ruta (desactivar)."""
        return await self.update_tipo_ruta(tipo_id, {"activo": False}) is not None

    # Métodos de utilidad
    async def get_configuracion_completa(self) -> dict:
        """Obtener configuración completa del sistema."""
        parametros = await self.get_parametros_sistema()
        tareas = await self.get_tareas_programadas()
        rutas = await self.get_rutas(activo=True)
        tipos_ruta = await self.get_tipos_ruta(activo=True)
        
        return {
            "parametros_sistema": parametros,
            "tareas_programadas": tareas,
            "rutas": rutas,
            "tipos_ruta": tipos_ruta
        }

    async def backup_configuracion(self) -> dict:
        """Crear backup de la configuración del sistema."""
        config = await self.get_configuracion_completa()
        config["timestamp_backup"] = datetime.utcnow()
        return config
