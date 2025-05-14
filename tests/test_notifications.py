import pytest
from unittest.mock import patch, MagicMock, call
from services.notification_service import NotificationService
from schemas.alerta import AlertaRead
from core.config import settings
from email.message import EmailMessage

@pytest.mark.asyncio
async def test_send_alert_notification():
    # Configuración de prueba
    test_config = {
        'email_from': 'test@example.com',
        'alert_recipients': 'admin@example.com,supervisor@example.com',
        'smtp_host': 'smtp.test.com',
        'smtp_port': 587
    }
    
    # Datos de prueba
    alerta_data = {
        'tipo_alerta': 'PRESION_BAJA',
        'descripcion': 'La presión del neumático está por debajo del umbral mínimo',
        'nivel_severidad': 'WARN'
    }
    
    # Mock para SMTP
    with patch('smtplib.SMTP') as mock_smtp_class:
        # Configurar el mock de SMTP
        mock_smtp_instance = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance
        
        # Inicializar el servicio con la configuración de prueba
        service = NotificationService(
            email_from=test_config['email_from'],
            alert_recipients=test_config['alert_recipients'],
            smtp_host=test_config['smtp_host'],
            smtp_port=test_config['smtp_port']
        )
        
        # Crear alerta de prueba
        alerta = AlertaRead(
            id='123e4567-e89b-12d3-a456-426614174000',
            **alerta_data,
            resuelta=False,
            creado_en='2023-01-01T00:00:00',
            actualizado_en='2023-01-01T00:00:00'
        )
        
        # Ejecutar el método a probar
        await service.send_alert_notification(alerta)
        
        # Verificaciones
        # 1. Se creó la instancia de SMTP con los parámetros correctos
        mock_smtp_class.assert_called_once_with(
            test_config['smtp_host'],
            test_config['smtp_port']
        )
        
        # 2. Se llamó a send_message con un mensaje correctamente formateado
        assert mock_smtp_instance.send_message.call_count == 1
        
        # 3. Verificar el contenido del mensaje
        args, _ = mock_smtp_instance.send_message.call_args
        mensaje = args[0]
        
        assert isinstance(mensaje, EmailMessage)
        assert mensaje['From'] == test_config['email_from']
        # Verificar que los destinatarios sean los correctos, ignorando espacios después de comas
        expected_recipients = ', '.join([r.strip() for r in test_config['alert_recipients'].split(',')])
        assert mensaje['To'] == expected_recipients
        assert mensaje['Subject'] == f"Alerta GesNeu: {alerta.tipo_alerta}"
        assert alerta.descripcion in mensaje.get_payload()
        
        # 4. Verificar que se usó el contexto with correctamente
        mock_smtp_instance.quit.assert_called_once()

@pytest.mark.asyncio
async def test_enqueue_alert_notification():
    """Prueba que el método enqueue_alert_notification agrega la tarea correctamente."""
    # Configuración de prueba
    bg_tasks_mock = MagicMock()
    service = NotificationService(bg_tasks=bg_tasks_mock)
    
    # Datos de prueba
    alerta = AlertaRead(
        id='123e4567-e89b-12d3-a456-426614174000',
        tipo_alerta='PRESION_BAJA',
        descripcion='Prueba de notificación en cola',
        nivel_severidad='WARN',
        resuelta=False,
        creado_en='2023-01-01T00:00:00',
        actualizado_en='2023-01-01T00:00:00'
    )
    
    # Ejecutar el método a probar
    service.enqueue_alert_notification(alerta)
    
    # Verificar que se agregó la tarea correctamente
    assert bg_tasks_mock.add_task.called
    assert bg_tasks_mock.add_task.call_args[0][0] == service.send_alert_notification
    assert bg_tasks_mock.add_task.call_args[0][1] == alerta
