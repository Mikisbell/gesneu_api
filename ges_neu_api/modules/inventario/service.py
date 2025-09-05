"""
Servicio para el módulo de inventario de neumáticos - Alineado con esquema real PostgreSQL.
"""
import logging
import traceback
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, text

from ...core.exceptions import RecursoNoEncontradoError, InventarioInsuficienteError
from .models import ParametrosInventario, InventarioView, ResumenInventario, TipoParametroInventarioEnum
from ..neumaticos.models import Neumatico, ModeloNeumatico
from ..catalogos.models import Almacen
from ...core.crud import CRUDBase

# Configurar logging
logger = logging.getLogger(__name__)

# CRUD para ParametrosInventario
crud_parametros = CRUDBase(ParametrosInventario)

class InventarioService:
    """Servicio para gestión de inventario basado en tablas reales de PostgreSQL."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============================================================================
    # PARÁMETROS DE INVENTARIO (tabla real)
    # ============================================================================
    
    async def get_parametro_inventario(self, parametro_id: UUID) -> Optional[ParametrosInventario]:
        """Obtener parámetro de inventario por ID."""
        try:
            return await crud_parametros.get(self.db, parametro_id)
        except Exception as e:
            logger.error(f"Error en get_parametro_inventario: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def get_parametros_by_modelo_almacen(
        self, modelo_id: UUID, almacen_id: UUID
    ) -> List[ParametrosInventario]:
        """Obtener parámetros por modelo y almacén."""
        try:
            stmt = select(ParametrosInventario).where(
                and_(
                    ParametrosInventario.modelo_id == modelo_id,
                    ParametrosInventario.ubicacion_almacen_id == almacen_id,
                    ParametrosInventario.activo == True
                )
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error en get_parametros_by_modelo_almacen: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def get_parametros_inventario(
        self, skip: int = 0, limit: int = 100, activo: Optional[bool] = None
    ) -> List[ParametrosInventario]:
        """Listar parámetros de inventario."""
        try:
            logger.info(f"Obteniendo parámetros de inventario - skip: {skip}, limit: {limit}, activo: {activo}")
            
            # Construir consulta base
            stmt = select(ParametrosInventario)
            
            # Aplicar filtro activo si se especifica
            if activo is not None:
                stmt = stmt.where(ParametrosInventario.activo == activo)
            
            # Aplicar paginación
            stmt = stmt.offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            parametros = list(result.scalars().all())
            
            logger.info(f"Parámetros obtenidos exitosamente: {len(parametros)} registros")
            return parametros
            
        except Exception as e:
            logger.error(f"Error en get_parametros_inventario: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    # ============================================================================
    # INVENTARIO DE NEUMÁTICOS (métodos adicionales requeridos)
    # ============================================================================
    
    async def get_inventario_neumaticos(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener inventario de neumáticos con información básica."""
        try:
            logger.info(f"Obteniendo inventario de neumáticos - skip: {skip}, limit: {limit}")
            
            # Consulta básica de neumáticos con información de modelo y fabricante
            stmt = select(Neumatico).offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            neumaticos = list(result.scalars().all())
            
            # Convertir a diccionario para respuesta - alineado con ESQUEMA_COMPLETO_BD.md
            inventario = []
            for neumatico in neumaticos:
                inventario.append({
                    "id": str(neumatico.id),
                    "numero_serie": neumatico.numero_serie,
                    "estado_actual": neumatico.estado_actual.value if neumatico.estado_actual else None,
                    "fecha_compra": neumatico.fecha_compra.isoformat() if neumatico.fecha_compra else None,
                    "costo_compra": float(neumatico.costo_compra) if neumatico.costo_compra else None,
                    "modelo_id": str(neumatico.modelo_id) if neumatico.modelo_id else None,
                    "vida_actual": neumatico.vida_actual,
                    "kilometraje_acumulado": neumatico.kilometraje_acumulado,
                    "profundidad_remanente_actual_mm": float(neumatico.profundidad_remanente_actual_mm) if neumatico.profundidad_remanente_actual_mm else None,
                    "ubicacion_almacen_id": str(neumatico.ubicacion_almacen_id) if neumatico.ubicacion_almacen_id else None,
                    "activo": neumatico.activo
                })
            
            logger.info(f"Inventario obtenido exitosamente: {len(inventario)} neumáticos")
            return inventario
            
        except Exception as e:
            logger.error(f"Error en get_inventario_neumaticos: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def get_movimientos_inventario(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener movimientos de inventario."""
        try:
            logger.info(f"Obteniendo movimientos de inventario - skip: {skip}, limit: {limit}")
            
            # Por ahora retornamos lista vacía ya que no hay tabla específica de movimientos
            # En el futuro se podría implementar con una tabla de auditoría
            movimientos = []
            
            logger.info(f"Movimientos obtenidos: {len(movimientos)} registros")
            return movimientos
            
        except Exception as e:
            logger.error(f"Error en get_movimientos_inventario: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    # ============================================================================
    # INVENTARIO BASADO EN NEUMÁTICOS (tabla real)
    # ============================================================================
    
    async def get_inventario_resumen(
        self, skip: int = 0, limit: int = 100
    ) -> List[ResumenInventario]:
        """Obtener resumen de inventario por modelo basado en tabla neumaticos."""
        try:
            logger.info(f"Generando resumen de inventario - skip: {skip}, limit: {limit}")
            
            # Consulta que agrupa neumáticos por modelo y estado_actual
            stmt = select(
                ModeloNeumatico.id.label('modelo_id'),
                ModeloNeumatico.nombre.label('modelo_nombre'),
                func.count(Neumatico.id).label('total_neumaticos'),
                func.sum(
                    func.case(
                        (Neumatico.estado_actual == 'EN_STOCK', 1),
                        else_=0
                    )
                ).label('en_stock'),
                func.sum(
                    func.case(
                        (Neumatico.estado_actual == 'INSTALADO', 1),
                        else_=0
                    )
                ).label('instalados'),
                func.sum(
                    func.case(
                        (Neumatico.estado_actual == 'EN_MANTENIMIENTO', 1),
                        else_=0
                    )
                ).label('en_mantenimiento'),
                func.sum(
                    func.case(
                        (Neumatico.estado_actual == 'DESECHADO', 1),
                        else_=0
                    )
                ).label('desechados')
            ).select_from(
                ModeloNeumatico
            ).outerjoin(
                Neumatico, ModeloNeumatico.id == Neumatico.modelo_id
            ).group_by(
                ModeloNeumatico.id, ModeloNeumatico.nombre
            ).offset(skip).limit(limit)
            
            result = await self.db.execute(stmt)
            rows = result.all()
            
            resumenes = []
            for row in rows:
                resumen = ResumenInventario(
                    modelo_id=row.modelo_id,
                    modelo_nombre=row.modelo_nombre,
                    total_neumaticos=row.total_neumaticos or 0,
                    en_stock=row.en_stock or 0,
                    instalados=row.instalados or 0,
                    en_mantenimiento=row.en_mantenimiento or 0,
                    desechados=row.desechados or 0,
                    almacenes=[]
                )
                resumenes.append(resumen)
            
            logger.info(f"Generados {len(resumenes)} resúmenes de inventario")
            return resumenes
            
        except Exception as e:
            logger.error(f"Error en get_inventario_resumen: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def get_neumaticos_en_stock(
        self, almacen_id: Optional[UUID] = None, skip: int = 0, limit: int = 100
    ) -> List[Neumatico]:
        """Obtener neumáticos en stock."""
        try:
            logger.info(f"Obteniendo neumáticos en stock - almacen_id: {almacen_id}")
            stmt = select(Neumatico).where(
                Neumatico.estado_actual == 'EN_STOCK'
            )
            
            if almacen_id:
                stmt = stmt.where(Neumatico.ubicacion_almacen_id == almacen_id)
            
            stmt = stmt.offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            neumaticos = list(result.scalars().all())
            logger.info(f"Encontrados {len(neumaticos)} neumáticos en stock")
            return neumaticos
            
        except Exception as e:
            logger.error(f"Error en get_neumaticos_en_stock: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def get_stock_bajo_por_parametros(self) -> List[Dict[str, Any]]:
        """Obtener modelos con stock bajo según parámetros configurados."""
        try:
            logger.info("Calculando stock bajo por parámetros")
            
            # Subconsulta para contar neumáticos en stock por modelo y almacén
            stock_actual = select(
                Neumatico.modelo_id,
                Neumatico.ubicacion_almacen_id,
                func.count(Neumatico.id).label('cantidad_actual')
            ).where(
                Neumatico.estado_actual == 'EN_STOCK'
            ).group_by(
                Neumatico.modelo_id, Neumatico.ubicacion_almacen_id
            ).subquery()
            
            # Consulta principal que compara stock actual vs parámetros
            stmt = select(
                ModeloNeumatico.id.label('modelo_id'),
                ModeloNeumatico.nombre.label('modelo_nombre'),
                Almacen.id.label('almacen_id'),
                Almacen.nombre.label('almacen_nombre'),
                ParametrosInventario.valor_numerico.label('stock_minimo'),
                func.coalesce(stock_actual.c.cantidad_actual, 0).label('stock_actual')
            ).select_from(
                ParametrosInventario
            ).join(
                ModeloNeumatico, ParametrosInventario.modelo_id == ModeloNeumatico.id
            ).join(
                Almacen, ParametrosInventario.ubicacion_almacen_id == Almacen.id
            ).outerjoin(
                stock_actual,
                and_(
                    stock_actual.c.modelo_id == ParametrosInventario.modelo_id,
                    stock_actual.c.ubicacion_almacen_id == ParametrosInventario.ubicacion_almacen_id
                )
            ).where(
                and_(
                    ParametrosInventario.parametro_tipo == 'STOCK_MINIMO',
                    ParametrosInventario.activo == True,
                    func.coalesce(stock_actual.c.cantidad_actual, 0) < ParametrosInventario.valor_numerico
                )
            )
            
            result = await self.db.execute(stmt)
            rows = result.all()
            
            stock_bajo = [
                {
                    'modelo_id': str(row.modelo_id),
                    'modelo_nombre': row.modelo_nombre,
                    'almacen_id': str(row.almacen_id),
                    'almacen_nombre': row.almacen_nombre,
                    'stock_minimo': float(row.stock_minimo),
                    'stock_actual': row.stock_actual
                }
                for row in rows
            ]
            
            logger.info(f"Encontrados {len(stock_bajo)} casos de stock bajo")
            return stock_bajo
            
        except Exception as e:
            logger.error(f"Error en get_stock_bajo_por_parametros: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    # ============================================================================
    # GESTIÓN DE PARÁMETROS
    # ============================================================================
    
    async def crear_parametro_inventario(
        self, parametro_tipo: str, modelo_id: UUID, almacen_id: UUID, 
        valor: Decimal, creado_por: UUID
    ) -> ParametrosInventario:
        """Crear nuevo parámetro de inventario."""
        try:
            logger.info(f"Creando parámetro de inventario - tipo: {parametro_tipo}")
            parametro_data = {
                "parametro_tipo": parametro_tipo,
                "modelo_id": modelo_id,
                "ubicacion_almacen_id": almacen_id,
                "valor_numerico": valor,
                "creado_por": creado_por
            }
            parametro = await crud_parametros.create(self.db, parametro_data)
            logger.info(f"Parámetro creado con ID: {parametro.id}")
            return parametro
        except Exception as e:
            logger.error(f"Error en crear_parametro_inventario: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    async def actualizar_parametro_inventario(
        self, parametro_id: UUID, valor: Decimal, actualizado_por: UUID
    ) -> Optional[ParametrosInventario]:
        """Actualizar valor de parámetro de inventario."""
        try:
            logger.info(f"Actualizando parámetro {parametro_id} con valor {valor}")
            parametro = await self.get_parametro_inventario(parametro_id)
            if parametro:
                update_data = {
                    "valor_numerico": valor,
                    "actualizado_por": actualizado_por
                }
                parametro_actualizado = await crud_parametros.update(self.db, parametro_id, update_data)
                logger.info(f"Parámetro {parametro_id} actualizado exitosamente")
                return parametro_actualizado
            logger.warning(f"Parámetro {parametro_id} no encontrado")
            return None
        except Exception as e:
            logger.error(f"Error en actualizar_parametro_inventario: {str(e)}")
            logger.error(traceback.format_exc())
            raise
