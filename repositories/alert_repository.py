"""
Repositorio para operaciones de base de datos relacionadas con alertas.

Este módulo maneja todas las operaciones de base de datos para el modelo Alerta,
proporcionando una capa de abstracción sobre las consultas SQL.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from models.alerta import Alerta
from models.usuario import Usuario
from schemas.common import TipoAlertaEnum
from datetime import datetime

class AlertRepository:
    """Repositorio para operaciones CRUD de alertas."""

    def __init__(self, session: AsyncSession):
        ""
        Inicializa el repositorio con una sesión de base de datos.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session

    async def get_alert(self, alert_id: UUID) -> Optional[Alerta]:
        """
        Obtiene una alerta por su ID.
        
        Args:
            alert_id: UUID de la alerta a buscar
            
        Returns:
            Alerta si se encuentra, None en caso contrario
        """
        result = await self.session.exec(
            select(Alerta).where(Alerta.id == alert_id)
        )
        return result.first()

    async def list_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Alerta]:
        """
        Lista alertas con filtros opcionales.
        
        Args:
            skip: Número de registros a saltar (para paginación)
            limit: Número máximo de registros a devolver
            **filters: Filtros opcionales (resuelta, tipo_alerta, etc.)
            
        Returns:
            Lista de alertas que coinciden con los filtros
        """
        query = select(Alerta)
        
        # Aplicar filtros
        if filters.get('resuelta') is not None:
            query = query.where(Alerta.resuelta == filters['resuelta'])
        if filters.get('tipo_alerta'):
            query = query.where(Alerta.tipo_alerta == filters['tipo_alerta'])
        if filters.get('neumatico_id'):
            query = query.where(Alerta.neumatico_id == filters['neumatico_id'])
        if filters.get('vehiculo_id'):
            query = query.where(Alerta.vehiculo_id == filters['vehiculo_id'])
        if filters.get('modelo_id'):
            query = query.where(Alerta.modelo_id == filters['modelo_id'])
        if filters.get('almacen_id'):
            query = query.where(Alerta.almacen_id == filters['almacen_id'])
        
        # Aplicar ordenación y paginación
        query = query.order_by(Alerta.fecha_creacion.desc()).offset(skip).limit(limit)
        
        result = await self.session.exec(query)
        return result.all()

    async def create_alert(self, alert_data: Dict[str, Any]) -> Alerta:
        """
        Crea una nueva alerta.
        
        Args:
            alert_data: Diccionario con los datos de la alerta
            
        Returns:
            La alerta creada con su ID asignado
        """
        alerta = Alerta(**alert_data)
        self.session.add(alerta)
        await self.session.commit()
        await self.session.refresh(alerta)
        return alerta

    async def update_alert(
        self, 
        alert_id: UUID, 
        update_data: Dict[str, Any],
        updated_by: UUID
    ) -> Optional[Alerta]:
        """
        Actualiza una alerta existente.
        
        Args:
            alert_id: ID de la alerta a actualizar
            update_data: Diccionario con los campos a actualizar
            updated_by: ID del usuario que realiza la actualización
            
        Returns:
            La alerta actualizada o None si no se encontró
        """
        alerta = await self.get_alert(alert_id)
        if not alerta:
            return None
            
        # Actualizar solo los campos proporcionados
        for key, value in update_data.items():
            if hasattr(alerta, key):
                setattr(alerta, key, value)
            
        # Actualizar metadatos
        alerta.ultima_actualizacion = datetime.utcnow()
        alerta.actualizado_por = updated_by
        
        self.session.add(alerta)
        await self.session.commit()
        await self.session.refresh(alerta)
        return alerta

    async def get_alert_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de las alertas para el dashboard.
        
        Returns:
            Diccionario con estadísticas de alertas
        """
        # Conteo por tipo de alerta y estado
        stmt = select(
            Alerta.tipo_alerta,
            Alerta.resuelta,
            func.count(Alerta.id).label('count')
        ).group_by(Alerta.tipo_alerta, Alerta.resuelta)
        
        result = await self.session.exec(stmt)
        summary = result.all()
        
        # Procesar resultados para el formato de respuesta
        return {
            'por_tipo': {
                f"{row.tipo_alerta}_{'resuelta' if row.resuelta else 'pendiente'}": row.count
                for row in summary
            },
            'totales': {
                'resueltas': sum(
                    row.count for row in summary 
                    if row.resuelta
                ),
                'pendientes': sum(
                    row.count for row in summary 
                    if not row.resuelta
                )
            },
            'ultima_actualizacion': datetime.utcnow().isoformat()
        }
