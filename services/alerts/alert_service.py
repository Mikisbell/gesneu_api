"""
Servicio de gestión de alertas.

Este módulo implementa la lógica de negocio para el manejo de alertas,
incluyendo creación, consulta y actualización de alertas, así como
la generación de reportes y resúmenes.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Type, TypeVar, Any
from uuid import UUID, uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from models.alerta import Alerta
from models.usuario import Usuario
from repositories.alert_repository import AlertRepository
from .schemas import (
    AlertCreate, 
    AlertUpdate, 
    AlertResponse,
    AlertSummary,
    AlertFilter,
    AlertStatus,
    AlertSeverity
)
from core.exceptions import (
    NotFoundError,
    DatabaseError,
    ValidationError
)

logger = logging.getLogger(__name__)
T = TypeVar('T', bound='AlertService')

class AlertService:
    """Servicio para la gestión de alertas en el sistema."""

    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de alertas.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        self.session = session
        self.repository = AlertRepository(session)

    async def create_alert(
        self, 
        alert_data: AlertCreate, 
        created_by: Optional[UUID] = None
    ) -> AlertResponse:
        """
        Crea una nueva alerta en el sistema.
        
        Args:
            alert_data: Datos de la alerta a crear
            created_by: ID del usuario que crea la alerta
            
        Returns:
            La alerta creada
            
        Raises:
            DatabaseError: Si ocurre un error al guardar en la base de datos
            ValidationError: Si los datos de la alerta no son válidos
        """
        try:
            # Validar datos adicionales
            self._validate_alert_data(alert_data)
            
            # Crear modelo de base de datos
            db_alert = Alerta(
                **alert_data.dict(exclude_unset=True, exclude_none=True),
                id=uuid4(),
                created_by=created_by,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Guardar en la base de datos
            created_alert = await self.repository.create_alert(db_alert)
            
            # Registrar evento de auditoría
            logger.info(
                f"Alerta creada: {created_alert.id} - "
                f"Tipo: {created_alert.alert_type}, "
                f"Severidad: {created_alert.severity}"
            )
            
            return AlertResponse.from_orm(created_alert)
            
        except SQLAlchemyError as e:
            logger.error(f"Error al crear alerta: {str(e)}", exc_info=True)
            raise DatabaseError("No se pudo crear la alerta") from e
        except Exception as e:
            logger.error(f"Error inesperado al crear alerta: {str(e)}", exc_info=True)
            raise

    async def get_alert(self, alert_id: UUID) -> AlertResponse:
        """
        Obtiene una alerta por su ID.
        
        Args:
            alert_id: ID de la alerta a buscar
            
        Returns:
            La alerta encontrada
            
        Raises:
            NotFoundError: Si la alerta no existe
            DatabaseError: Si ocurre un error al consultar la base de datos
        """
        try:
            alert = await self.repository.get_alert(alert_id)
            if not alert:
                raise NotFoundError(f"Alerta con ID {alert_id} no encontrada")
                
            return AlertResponse.from_orm(alert)
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener alerta {alert_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Error al consultar la alerta") from e

    async def list_alerts(
        self, 
        filter_data: AlertFilter,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AlertResponse]:
        """
        Lista alertas según los filtros proporcionados.
        
        Args:
            filter_data: Filtros a aplicar
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de alertas que coinciden con los filtros
            
        Raises:
            DatabaseError: Si ocurre un error al consultar la base de datos
        """
        try:
            # Convertir filtros al formato del repositorio
            filters = filter_data.dict(exclude_none=True, exclude_unset=True)
            
            # Obtener alertas del repositorio
            alerts = await self.repository.list_alerts(
                skip=skip,
                limit=limit,
                **filters
            )
            
            return [AlertResponse.from_orm(alert) for alert in alerts]
            
        except SQLAlchemyError as e:
            logger.error(f"Error al listar alertas: {str(e)}", exc_info=True)
            raise DatabaseError("Error al listar alertas") from e

    async def update_alert(
        self, 
        alert_id: UUID, 
        update_data: AlertUpdate,
        updated_by: UUID
    ) -> AlertResponse:
        """
        Actualiza una alerta existente.
        
        Args:
            alert_id: ID de la alerta a actualizar
            update_data: Datos a actualizar
            updated_by: ID del usuario que realiza la actualización
            
        Returns:
            La alerta actualizada
            
        Raises:
            NotFoundError: Si la alerta no existe
            DatabaseError: Si ocurre un error al actualizar
            ValidationError: Si los datos de actualización no son válidos
        """
        try:
            # Verificar que la alerta existe
            alert = await self.repository.get_alert(alert_id)
            if not alert:
                raise NotFoundError(f"Alerta con ID {alert_id} no encontrada")
                
            # Validar la transición de estado
            self._validate_status_transition(alert.status, update_data.status)
            
            # Preparar datos de actualización
            update_values = update_data.dict(
                exclude_unset=True, 
                exclude_none=True
            )
            
            # Actualizar metadatos de auditoría
            update_values['updated_by'] = updated_by
            update_values['updated_at'] = datetime.now(timezone.utc)
            
            # Si se está resolviendo la alerta, registrar quién y cuándo
            if update_data.status == AlertStatus.RESOLVED:
                update_values['resolved_by'] = updated_by
                update_values['resolved_at'] = datetime.now(timezone.utc)
            
            # Realizar la actualización
            updated_alert = await self.repository.update_alert(
                alert_id=alert_id,
                update_data=update_values
            )
            
            # Registrar evento de auditoría
            logger.info(
                f"Alerta actualizada: {alert_id} - "
                f"Nuevo estado: {updated_alert.status}"
            )
            
            return AlertResponse.from_orm(updated_alert)
            
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar alerta {alert_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Error al actualizar la alerta") from e

    async def get_alert_summary(self) -> AlertSummary:
        """
        Obtiene un resumen de las estadísticas de alertas.
        
        Returns:
            Resumen de estadísticas de alertas
            
        Raises:
            DatabaseError: Si ocurre un error al consultar las estadísticas
        """
        try:
            # Obtener resumen del repositorio
            summary_data = await self.repository.get_alert_summary()
            
            # Obtener alertas recientes
            recent_alerts = await self.repository.list_alerts(
                limit=10,
                order_by=[Alerta.created_at.desc()]
            )
            
            # Construir respuesta
            return AlertSummary(
                total=sum(summary_data['totales'].values()),
                by_severity={
                    AlertSeverity(k.split('_')[0]): v 
                    for k, v in summary_data['por_tipo'].items()
                },
                by_status=summary_data['totales'],
                recent_alerts=[
                    AlertResponse.from_orm(alert) 
                    for alert in recent_alerts
                ]
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener resumen de alertas: {str(e)}", exc_info=True)
            raise DatabaseError("Error al obtener el resumen de alertas") from e

    def _validate_alert_data(self, alert_data: AlertCreate) -> None:
        """
        Valida los datos de una alerta antes de crearla.
        
        Args:
            alert_data: Datos de la alerta a validar
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validar longitud del título
        if len(alert_data.title) > 200:
            raise ValidationError("El título no puede tener más de 200 caracteres")
            
        # Validar que si hay un ID de entidad relacionada, también haya tipo
        if alert_data.related_entity_id and not alert_data.related_entity_type:
            raise ValidationError(
                "Se debe especificar el tipo de entidad relacionada cuando se proporciona un ID"
            )

    @staticmethod
    def _validate_status_transition(
        current_status: Optional[str], 
        new_status: Optional[AlertStatus]
    ) -> None:
        """
        Valida una transición de estado de alerta.
        
        Args:
            current_status: Estado actual de la alerta
            new_status: Nuevo estado propuesto
            
        Raises:
            ValidationError: Si la transición no es válida
        """
        if not new_status:
            return
            
        # No hay restricciones si no hay estado actual (nueva alerta)
        if not current_status:
            return
            
        current_status = AlertStatus(current_status)
        
        # Validar transiciones permitidas
        if current_status == AlertStatus.RESOLVED and new_status != AlertStatus.RESOLVED:
            raise ValidationError(
                "No se puede cambiar el estado de una alerta resuelta"
            )
            
        if current_status == AlertStatus.DISMISSED and new_status != AlertStatus.DISMISSED:
            raise ValidationError(
                "No se puede cambiar el estado de una alerta descartada"
            )

    @classmethod
    async def create(
        cls: Type[T], 
        session: AsyncSession
    ) -> T:
        """
        Método de fábrica para crear una instancia del servicio.
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Instancia del servicio de alertas
        """
        return cls(session)
