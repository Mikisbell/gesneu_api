from typing import Optional, Dict, Any
from schemas.alerta import AlertaRead
from fastapi import BackgroundTasks
import smtplib
from email.message import EmailMessage
from core.config import settings

class NotificationService:
    def __init__(
        self, 
        bg_tasks: Optional[BackgroundTasks] = None,
        email_from: str = None,
        alert_recipients: str = None,
        smtp_host: str = None,
        smtp_port: int = None
    ):
        self.bg_tasks = bg_tasks
        # Usar el valor proporcionado o el de settings si existe, o un valor por defecto
        self.email_from = email_from if email_from is not None else getattr(settings, 'EMAIL_FROM', 'noreply@example.com')
        # Asegurarse de que los destinatarios no tengan espacios después de las comas
        alert_recipients_value = alert_recipients if alert_recipients is not None else getattr(settings, 'ALERT_RECIPIENTS', 'admin@example.com')
        self.alert_recipients = ', '.join([r.strip() for r in alert_recipients_value.split(',')])
        self.smtp_host = smtp_host if smtp_host is not None else getattr(settings, 'SMTP_HOST', 'localhost')
        self.smtp_port = smtp_port if smtp_port is not None else getattr(settings, 'SMTP_PORT', 25)

    async def send_alert_notification(self, alerta: AlertaRead):
        """Envía una notificación por correo electrónico sobre una alerta.
        
        Args:
            alerta: La alerta a notificar
        """
        msg = EmailMessage()
        msg['Subject'] = f'Alerta GesNeu: {alerta.tipo_alerta}'
        msg['From'] = self.email_from
        msg['To'] = self.alert_recipients
        msg.set_content(alerta.descripcion)
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.send_message(msg)
            # Asegurarse de que se cierre la conexión correctamente
            server.quit()

    def enqueue_alert_notification(self, alerta: AlertaRead):
        if self.bg_tasks:
            self.bg_tasks.add_task(self.send_alert_notification, alerta)
